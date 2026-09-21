
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                                                ____ _____   ____   _____  __
#?                                                               |  _ \_   _| | __ ) / _ \ \/ /
#?                                                               | |_) || |   |  _ \| | | \  /
#?                                                               |  _ < | |   | |_) | |_| /  \
#?                                                               |_| \_\|_|   |____/ \___/_/\_\
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#*  Client-side interface for controlling a Plexim RT Box from a PLECS Standalone / Python workflow, via XML-RPC or JSON-RPC.
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
from    pathlib    import Path
from    typing     import Any, Callable, Sequence

import  jsonrpc_requests
import  xmlrpc.client
import  time
import  base64
import  collections.abc
import  functools
import  traceback
import  os
import  glob
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

class RTBoxError(Exception):
    """
    Raised for RT Box connection, load, or RPC-call failures.

    ?NOTE:
        Deliberately a thin subclass of Exception with no extra state or behavior of its own
        every failure it wraps (a DNS/socket error from rt_connect, a file error from rt_load,
        an RPC fault from rt_set) is already a real exception with its own message. 
        
        The point of giving it its own type is so callers can write except RTBoxError: to react to something
        went wrong talking to the RT Box specifically, without also catching unrelated bugs that a
        blanket except Exception: would swallow. 
        
        The original low-level exception is preserved via raise RTBoxError(...) from exc wherever this is raised
        so it's still available as err.__cause__ for debugging.
    """


def _rt_guard(default: Any = None) -> Callable:
    """
    Method decorator that turns RT Box calls into no-ops when the instance is disabled (self.enabled is False).

    ?NOTE:
        Every method that talks to real hardware is wrapped with this, so a single enabled=False on construction
        makes the whole class silently pass through instead of hitting the network.

    *Args:
        default (Any, optional) :   Value to return when the call is skipped, matching the shape
                                    expected ({} for rt_get, ([], []) for rt_list) so downstream
                                    code doesn't need extra checks.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self: "RT_Box", *args, **kwargs):
            if not self.enabled:
                print(f"RT Box disabled (RT=false) — skipping {func.__name__}()")
                return default
            return func(self, *args, **kwargs)

        return wrapper

    return decorator

class RT_Box:

    """
    Handles connecting to the RT Box, uploading a compiled model (codegen executable), starting/stopping the real-time simulation,
    and exchanging data with Programmable Value and Data Capture blocks in the running model.

    ?NOTE:
        url/port/method are deliberately the same shape as PlecsRPC's own constructor params, so a caller
        that already has dp.url/dp.port/dp.METHOD for talking to PLECS can pass the same kind of values here
        for the RT Box -- but they are NOT the same values: PLECS (dp.url, e.g. "http://127.0.0.1") runs
        locally alongside the script, while the RT Box is separate physical hardware elsewhere on the network
        (e.g. "http://rtbox-123.local"), so give it its own url. Unlike PlecsRPC, the RT Box's own RPC
        server requires the URL to end in "/RPC2" -- rt_connect() appends that itself, so pass url without it.

    *Args:
        url             : (str)             :   Full address of the RT Box, e.g. "http://rtbox-123.local" or "http://10.0.0.5" -- same
                                                shape as PlecsRPC's own url param (scheme included), just pointed at different hardware.
        port            : (str)             :   TCP port the RT Box listens on for RPC connections. Defaults to '9998'.
        model_name      : (str, optional)   :   Used to build the default codegen executable path: '<model_name>_codegen/<model_name>.elf'.
        method          : (str, optional)   :   RPC transport to use, either "XML" (XML-RPC) or "JSON" (JSON-RPC). Defaults to "XML".
        codegen_path    : (str, optional)   :   Explicit path to the compiled executable. If omitted, rt_load() searches the project
                                                tree for '<model_name>.elf' itself (see _find_codegen()), the same way PlecsRPC.Open_Model()
                                                finds a .plecs file -- no fixed folder layout assumed.
        set_values      : (dict[str, Sequence[float]], optional) : Default Programmable Value block name -> values mapping, e.g. {"Input": [5.0]}.
                                                run() writes these via rt_set() right after starting the simulation whenever it is
                                                called without its own set_values argument. Defaults to {}.

        enabled         : (bool, optional)  :   When 'False', every method that would talk to real hardware (connect/load/start/stop/reboot/list/query/set/get/log)
                                                becomes a no-op and returns immediately. This lets the exact same calling code run in environments
                                                with no RT Box attached by flipping one flag. Defaults to 'True'.
    """

    DEFAULT_PORT        = 9998
    SUPPORTED_METHODS   = ("XML", "JSON")

    def __init__(
                    self                                      ,
                    url             : str   = ""              ,
                    port            : str   = str(DEFAULT_PORT),
                    model_name      : str   = ""              ,
                    method          : str   = "XML"           ,
                    codegen_path    : str   = ""              ,
                    enabled         : bool  = True             ,
                    set_values      : dict[str, Sequence[float]] | None = None
                ) -> None:

        if method not in self.SUPPORTED_METHODS :   raise ValueError(f"Unsupported method {method}; expected one of {self.SUPPORTED_METHODS}")

        self.model_name         = model_name
        self.url                = url
        self.port               = port
        self.method             = method
        self.enabled            = enabled
        self.set_values         = dict(set_values) if set_values else {}

        # host_address stays "" when disabled or no url was given, so this class can be constructed
        # with no link to the RT Box at all. xmlrpc.client/jsonrpc_requests resolve the hostname
        # themselves on connect -- no DNS pre-resolution needed here.
        self.host_address        = f"{self.url}:{self.port}/RPC2" if (self.enabled and self.url) else ""

        # None (rather than a guessed path) when codegen_path isn't given: rt_load() searches the
        # project tree for it lazily, via _find_codegen(), instead of assuming a fixed folder layout.
        self.codegen             = Path(codegen_path) if codegen_path else None
        self.server              = None

    @classmethod
    def from_dependencies(cls) -> "RT_Box":
        """
        Build an RT_Box from the project's shared Dependencies state, the same way RunScripts.py
        builds a PlecsRPC from dp.url/dp.port/etc. Assumes the caller already checked
        dp.JSON["RT"] before deciding to call this -- enabled is unconditionally True here.

        ?NOTE:
            Imports assets.Dependencies locally (not at module level), so RT_Box.py itself stays
            importable on its own -- the whole Dependencies chain only loads if this specific
            classmethod is actually called, not just because RT_Box.py was imported.

        !Returns:
            RT_Box  :   A new, enabled instance, sourced entirely from dp.
        """
        import assets.Dependencies as dp

        return cls(
            url         = dp.url                               ,
            port        = dp.port                              ,
            model_name  = dp.JSON["modelname"].split(".")[0]    ,
            method      = dp.METHOD                             ,
            enabled     = True                                  ,
            set_values  = dp.JSON.get("set_values")             ,
        )

    def _find_codegen(self) -> Path:
        """
        Search the project tree for a compiled <model_name>.elf, the same way PlecsRPC.Open_Model()
        finds a PLECS model file: crawl every top-level project folder (excluding the usual
        non-model folders, same exclusion list as Open_Model's) for *.elf files, and match by
        filename against self.model_name.

        !Returns:
            Path      :   The found .elf file's path.

        !Raises:
            RTBoxError If no .elf file named "<model_name>.elf" is found anywhere in the project tree.
        """
        root_dir            = os.getcwd()

        # Same exclusion list as PlecsRPC.Open_Model(), so both searches agree on where models live.
        excluded_folders    = ["Script", "Thermal Models", "MyLibraries", "FMU", "wheelhouse", "venv", "build", "PyPLECS.egg-info"]

        allowed_dirs         = [
                                    os.path.join(root_dir, d) for d in os.listdir(root_dir)
                                    if os.path.isdir(os.path.join(root_dir, d)) and d not in excluded_folders
                                ] + [root_dir]

        all_matches          = sum((glob.glob(p, recursive=True) for p in [os.path.join(d, "**", "*.elf") for d in allowed_dirs]), [])

        target_name          = f"{self.model_name}.elf".lower()
        found                = next((p for p in all_matches if os.path.basename(p).lower() == target_name), None)

        if not found:
            raise RTBoxError(f"Could not find {self.model_name}.elf anywhere in the project tree.")

        return Path(found)

    #?--------------------------------------------------------------------
    #? Context-manager support
    #?--------------------------------------------------------------------

    def __enter__(self) -> "RT_Box":
        """
        Context-manager entry point: connects to the RT Box and returns this same instance,
        so "with self:" (used internally by run()) can be written without a separate helper class.

        !Returns:
            RT_Box  :   self, already connected via rt_connect().
        """

        self.rt_connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context-manager exit point: always attempts rt_stop(), even if the "with" block raised.

        ?NOTE:
            A failure here is deliberately caught and only printed, never re-raised. 
            
            __exit__ runs while an exception from inside the "with" block may already be propagating 
            if this method raised too, Python would silently replace that original exception with this
            cleanup failure, and a caller doing "except RTBoxError:" around the "with" block could
            miss the real problem entirely. Swallowing rt_stop() failures here keeps cleanup best-effort 
            without ever masking the exception that actually caused the block to fail. When nothing went 
            wrong inside the block, returning None (no explicit `return`) suppresses nothing.
        """
        try:
            self.rt_stop()
        except Exception:
            # Don't mask the original exception (if any) with a stop failure.
            print("Failed to stop RT Box cleanly on exit.")
            traceback.print_exc()

    #?--------------------------------------------------------------------
    #? Connection
    #?--------------------------------------------------------------------
    @_rt_guard()
    def rt_connect(self) -> None:
        """
        Open an RPC connection to the RT Box.No-op if the instance was constructed with enabled=False.

        !Raises:
            RTBoxError If the connection cannot be established.
        """
        print(f"Connecting to RT Box at {self.host_address} ({self.method}-RPC)")
        try:

            if self.method == "JSON":
                # jsonrpc_requests relies on collections.Mapping, removed in Python 3.10+
                collections.Mapping = collections.abc.Mapping
                self.server         = jsonrpc_requests.Server(self.host_address)
            else:  # "XML"
                self.server         = xmlrpc.client.ServerProxy(self.host_address)
        except Exception as exc :
            raise RTBoxError(f"Could not connect to RT Box at {self.host_address}: {exc}") from exc

    @_rt_guard()
    def rt_load(self) -> None:
        """
        Upload the compiled model executable to the RT Box. No-op if the instance was constructed with enabled=False.
        Read the codegen file and send it via rtbox.load as a proper RPC binary object: an xmlrpc.client.Binary
        for XML-RPC (xmlrpc.client base64-encodes it on the wire and the RT Box decodes it back to raw bytes),
        or a base64-encoded string for JSON-RPC (JSON has no native binary type, so the RT Box expects the
        base64 text itself). See the RT Box Scripting reference for both forms.

        !Raises:
            RTBoxError If codegen_path wasn't given and no matching .elf could be found, or if the
                      resolved file is missing/unreadable, or the RT Box rejects the upload.
        """

        if self.codegen is None         :   self.codegen = self._find_codegen()
        if not self.codegen.is_file()   :   raise RTBoxError(f"Codegen executable not found: {self.codegen}")

        print(f"Uploading executable: {self.codegen}")

        try:

            with open(self.codegen, "rb") as f:
                payload =  base64.b64encode(f.read()).decode()
                self.server.rtbox.load(payload)
            f.close()

        except Exception as exc:
            raise RTBoxError(f"Failed to load executable onto RT Box: {exc}") from exc
        print("Executable uploaded successfully.")

    @_rt_guard()
    def rt_start(self) -> None:
        """
        Start real-time execution of the loaded simulation model,No-op if disabled.
        """
        print("Starting real-time simulation.")
        self.server.rtbox.start()
        print("Real-time simulation running.")

    @_rt_guard()
    def rt_stop(self) -> None:
        """
        Stop real-time execution of the currently running model, No-op if disabled.
        """
        print("Stopping real-time simulation.")
        self.server.rtbox.stop()
        print("Real-time simulation stopped.")

    @_rt_guard()
    def rt_reboot(self) -> None:
        """
        Stop the currently running model and reboot the RT Box itself (not just the simulation),
        No-op if disabled.
        """
        print("Rebooting RT Box.")
        self.server.rtbox.reboot("reboot")
        print("RT Box reboot requested.")

    #?--------------------------------------------------------------------
    #? Model introspection
    #?--------------------------------------------------------------------

    @_rt_guard(default=([], []))
    def rt_list(self) -> tuple[list[str], list[str]]:
        """
        List the Programmable Value and Data Capture blocks available in the currently loaded model.
        Returns ([], []) without contacting the RT Box if the instance was constructed with enabled=False

        !Returns:
            tuple[list[str], list[str]] (input_blocks, output_blocks) : names of Programmable Value blocks and Data Capture blocks, respectively.
        """
        input_blocks    = self.server.rtbox.getProgrammableValueBlocks()
        output_blocks   = self.server.rtbox.getDataCaptureBlocks()

        print(f"Available input blocks : {input_blocks}")
        print(f"Available output blocks: {output_blocks}")

        return input_blocks, output_blocks

    @_rt_guard(default={})
    def rt_query(self) -> dict[str, Any]:
        """
        Query the RT Box for information about the currently executing simulation.

        !Returns:
            dict    :   Struct with "modelName", "sampleTime", and "status" keys, where
                        "status" is one of "stopped", "running", or "error".
        """
        info = self.server.rtbox.querySimulation()

        print(f"Simulation status: {info}")

        return info

    #?--------------------------------------------------------------------
    #? Data exchange
    #?--------------------------------------------------------------------

    @_rt_guard()
    def rt_set(self, block_name: str, values: Sequence[float]) -> None:
        """
        Write one or more values to a Programmable Value block.
        No-op if the instance was constructed with enabled=False

        *Args:
            block_name (str)    :   Name of the Programmable Value block to write to, as returned by rt_list()
            values              :   Sequence[float] Value(s) to send p,assed to the RT Box as a list

        !Raises:
            RTBoxError If the RPC call fails (unknown block name).

        ?Example:
            rt.rt_set("Value1", [5.0, 7.0])   # width-2 signal: channel 0 -> 5.0, channel 1 -> 7.0
            rt.rt_set("Value1", [7])          # width-1 signal: still passed as a one-element list
            
        """
        values      = list(values)
        print(f"Setting block {block_name} to {values}")

        try:
            self.server.rtbox.setProgrammableValue(block_name, values)
        except Exception as exc:
            raise RTBoxError(f"Failed to set value on block {block_name}: {exc}") from exc

    @_rt_guard(default={})
    def rt_get(
                self                                            ,
                capture_blocks          : Sequence[str]         ,
                poll_interval           : float = 1.0           ,
                timeout                 : float | None = None   ,
                trigger_reference_block : str   | None = None
            ) -> dict[str, Any]:

        """
        Wait for and retrieve captured data from one or more Data Capture blocks.
        Returns {} without contacting the RT Box if the instance was constructed with enabled=False

        Blocks until the reference capture block reports at least one trigger (or until timeout elapses),
        then reads data from every block in capture_blocks

        *Args:
            capture_blocks          (Sequence[str])         :   Names of the Data Capture blocks to read, as returned by rt_list
            poll_interval           (float, optional)       :   Seconds to wait between trigger-count checks. Defaults to 1.0.
            timeout                 (float, optional)       :   Maximum seconds to wait for a trigger before giving up. If None (default), waits indefinitely.
            trigger_reference_block (str, optional)         :   Which block's trigger count to poll before reading data. Defaults to the first entry in capture_blocks.

        !Returns:
                                    (dict)                  :   Mapping of block name to the raw capture data returned by rtbox.getCaptureData for that block.

        !Raises:
            TimeoutError If timeout is set and no trigger occurs in time.
        """
        if not capture_blocks:
            raise ValueError("capture_blocks must contain at least one block name.")

        reference_block = trigger_reference_block or capture_blocks[0]
        elapsed         = 0.0

        while self.server.rtbox.getCaptureTriggerCount(reference_block) == 0:
            if timeout is not None and elapsed >= timeout:
                raise TimeoutError(f"No trigger on {reference_block} after {timeout} seconds.")
            print(f"Waiting for data on {reference_block}...")
            time.sleep(poll_interval)
            elapsed += poll_interval

        return {block: self.server.rtbox.getCaptureData(block) for block in capture_blocks}

    #?--------------------------------------------------------------------
    #? Diagnostics
    #?--------------------------------------------------------------------

    @_rt_guard(default="")
    def rt_log(self) -> Any:
        """
        Retrieve the application log messages from the running simulation. Useful for diagnosing
        a failed rt_load()/rt_start(), or a model reporting status "error" from rt_query().
        Returns "" without contacting the RT Box if the instance was constructed with enabled=False

        !Returns:
                (Any)   :   Log messages as returned by rtbox.getApplicationLog(); the RT Box scripting
                            reference doesn't pin down the exact shape, so this is passed through as-is.
        """
        log = self.server.rtbox.getApplicationLog()

        print(f"Application log: {log}")

        return log

    #?--------------------------------------------------------------------
    #? Main orchestration method
    #?--------------------------------------------------------------------

    def run(
            self                                                        ,
            set_values      : dict[str, Sequence[float]] | None = None  ,
            capture_blocks  : Sequence[str] | None = None               ,
            poll_interval   : float = 1.0                               ,
            timeout         : float | None = None
        ) -> dict[str, Any]:
        """
        Run the full RT Box workflow end to end: connect, load, start,optionally write Programmable Values, optionally read Data Capture blocks, then stop.

        *Args:
            set_values              (dict[str, Sequence[float]])    :   Mapping of Programmable Value block name to the values to write after the simulation starts, e.g. {"Input": [5.0]}
            capture_blocks          (Sequence[str])                 :   Data Capture block names to read before stopping. If omitted, no data is captured.
            poll_interval, timeout  (float)                         :   Forwarded to rt_get

        !Returns:
                                    (dict)                          :   Captured data keyed by capture block name. Empty if capture_blocks was not given, or if the instance is disabled

        ?Example:
            rt      = RT_Box(url=dp.url, port=dp.port, model_name="psfbConverterFBR", method=dp.METHOD, enabled=dp.JSON["RT"], set_values=dp.JSON.get("set_values"))
            data    = rt.run(capture_blocks=["Capture1", "Capture2"])
        """
        if not self.enabled:
            print("RT Box disabled (RT=false) — run() is a no-op.")
            return {}

        captured    : dict[str, Any] = {}

        with self:  # rt_connect() on enter, rt_stop() on exit (even on error)

            self.rt_load()
            self.rt_start()
            self.rt_list()

            if set_values:
                for block_name, values in set_values.items():   
                    self.rt_set(block_name, values)

            if capture_blocks:
                captured = self.rt_get(capture_blocks, poll_interval=poll_interval, timeout=timeout)

        return captured

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------