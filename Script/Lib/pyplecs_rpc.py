#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#?                                            ______   ______  _     _____ ____ ____        ____  ____   ____
#?                                           |  _ / / / /  _ /| |   | ____/ ___/ ___|      |  _ /|  _ / / ___|
#?                                           | |_) / V /| |_) | |   |  _|| |   /___ / _____| |_) | |_) | |
#?                                           |  __/ | | |  __/| |___| |__| |___ ___) |_____|  _ <|  __/| |___
#?                                           |_|    |_| |_|   |_____|_____/____|____/      |_| /_/_|    /____|
#?
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
#*  PlecsRPC also carries the RT Box workflow directly (LoadModel/rt_start/.../rtbox_run,
#*  generate_code) -- fused in from what used to be a separate RT_Box class, so callers (RunScripts.py)
#*  only ever deal with one object instead of constructing PlecsRPC and RT_Box separately.
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------
import base64
import collections
import copy
import glob
import json
import jsonrpc_requests
import os
import time
import xmlrpc.client
import functools
from    pathlib import Path
from    typing  import Any, Callable, Sequence
import  assets.Dependencies         as        dp

#Calling on Enviromment variables
for key in ["HTTP_PROXY", "HTTPS_PROXY"]:
    if key in list(dict(os.environ).keys()):os.environ.pop(key)
#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

def _rt_guard(default: Any = None) -> Callable:
    """
    Method decorator that turns RT Box calls into no-ops when the instance's RT Box side is
    disabled (self.rtbox_enabled is False).

    ?NOTE:
        Every method that talks to RT Box hardware is wrapped with this, so a single
        rtbox_enabled=False on construction makes the whole RT Box side of PlecsRPC silently pass
        through instead of hitting the network. This only guards the RT Box methods -- it has no
        effect on PlecsRPC's own PLECS-facing methods (PlecsConnect, LaunchSim, etc.), which are
        never disabled.

    *Args:
        default (Any, optional) :   Value to return when the call is skipped, matching the shape
                                    expected ({} for rt_get, ([], []) for rt_list) so downstream
                                    code doesn't need extra checks.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self: "PlecsRPC", *args, **kwargs):
            if not self.rtbox_enabled:
                print(f"RT Box disabled (RT=false) — skipping {func.__name__}()")
                return default
            return func(self, *args, **kwargs)

        return wrapper

    return decorator

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------

class PlecsRPC:

    def __init__(
                    self                                              ,
                    url                 : str                         ,
                    port                : str                         ,
                    mdlVars             : dict                        ,
                    slvOpts             : dict                        ,
                    anlOpts             : dict                        ,
                    METHOD              : str  = "JSON"                ,
                    rtbox_enabled       : bool = True                  ,
                    rtbox_codegen_only  : bool = False
                ) :
        """
        PlecsRPC Constructor to initialize global variables.

        *Args:
            url         (string)        : Could be a local address, an ip adress  or a link : http//:127.0.0.1 for localhost.
            port        (string)        : Port to connect to the xmlrpc server over.
            path        (string)        : String leading to the path of the model.
            mdlVars     (dictionary)    : Dictionary to specify variable values.
            solverOpts  (dictionary)    : Dictionary to specify solver settings.
            METHOD      (string)        : RPC connection medium, XML or JSON.

            rtbox_enabled       (bool, optional)  :   When 'False', every RT Box method (LoadModel's RT branch, rt_start/.../rtbox_run) becomes a
                                                       no-op and returns immediately -- lets the exact same calling code run in
                                                       environments with no RT Box attached by flipping one flag. Defaults to 'True'.
            rtbox_codegen_only  (bool, optional)  :   When 'True', rtbox_run() stops right after generating code -- it never connects
                                                       to, uploads to, or starts anything on actual RT Box hardware. Has no effect when
                                                       rtbox_enabled=False. Defaults to 'False' (the full connect/load/start/.../stop routine).

        ?NOTE:
            The RT Box connection reuses url/port/METHOD/self.server as-is -- no separate rtbox_url/
            rtbox_port/rtbox_method/rtbox_server. Since simRun() only ever does one or the other (a
            normal PLECS simulation OR the RT Box routine, never both in the same run), there's no
            actual conflict in sharing them. If the RT Box genuinely needs a different address than
            PLECS, that's a Dependencies.py change (dp.url/dp.port), not a separate parameter here.

            No rtbox_model_name/rtbox_codegen_path parameters either -- the model name is available
            from the model path (dp.cp_mdl, set by Open_Model()) once that's been called, and
            self.rtbox_codegen (the file LoadModel() uploads) is always set by generate_code(), not
            given upfront. It starts as None; LoadModel() raises clearly if called before that happens.
        """

        self.url                        =   url                                  # Host Local address    : http://localhost
        self.port                       =   port                                 # Port to connect over  : exemple 61677, default is 1080
        self.mdlVars                    =   mdlVars                              # Assign Parameters Dictionary "Modelvars"
        self.slvOpts                    =   slvOpts                              # Assign Parameters Dictionary "SolverOpts"
        self.anlOpts                    =   anlOpts                              # Assign Parameters Dictionary "AnalysisOpts"
        self.OptStruct                  =   []                                   # Initialize simulation parameters vector
        self.METHOD			            =   METHOD				                 # Desired RPC connection medium. Default is JSON. Alternative is XML.
        self.path                       =   ''                                   # Path to the plecs model file

        # RT Box side -- reuses self.url/self.port/self.METHOD/self.server above rather than its own copies.
        self.rtbox_enabled              =   rtbox_enabled
        self.rtbox_codegen_only         =   rtbox_codegen_only
        self.rtbox_codegen              =   None                                 # set by generate_code(), read by LoadModel()

    def optStruct(self,instances=1,iteration_range=[0],parallel=False):
        """
        Reconstructs the simstruct for the model
        based on the modelvar and solveropt dictionaries
        passed in from the local dependecies.

        *Args:
            instances (int)       : Number of instances to be generated, default is 1.
            parallel  (bool)      : Flag to indicate if parallel simulations will be performed.
        """

        # if only one instance is required and parallel simulations are not needed
        # return a single dictionary containing the model variables, solver options, analysis options and name
        if (instances == 1 and not parallel):
            self.OptStruct  =   {'ModelVars':self.mdlVars, 'SolverOpts':self.slvOpts, 'AnalysisOpts':self.anlOpts, 'Name':'Iter_1'}
            return

        # if multiple instances are required or parallel simulations are needed
        # create a list of dictionaries containing the model variables, solver options, analysis options and name
        # each dictionary corresponds to one instance of the simulation
        mdl_list        =   [copy.deepcopy(self.mdlVars) for _ in range(instances)]
        slv_list        =   [copy.deepcopy(self.slvOpts) for _ in range(instances)]
        anl_list        =   [copy.deepcopy(self.anlOpts) for _ in range(instances)]
        nms_list        =   ["Iter_"+str(iteration_range[i]+1) for i in range(len(iteration_range))]
        self.OptStruct  =   [{'ModelVars':mdl_list[x],'SolverOpts':slv_list[x],'AnalysisOpts':anl_list[x], 'Name':nms_list[x]} for x in range(instances)]

    def PlecsConnect(self):
        """
        Establishes a connection over XML-RPC or JSON-RPC to PLECS -- and, since PLECS and the RT
        Box are assumed to share this same address/port with no distinguishing URL suffix, this
        exact same self.server connection is reused directly for RT Box calls too: rtbox.*/plecs.*
        are just different method-name namespaces on the one endpoint self.server connects to here.

        *Args:
            url         (str)       : the URL of the remote server running the Plecs simulation
            port        (str)       : the port number used for the XML-RPC or JSON-RPC connection
            METHOD      (str)       : the protocol used for the connection, either "XML" or "JSON"
            server      (object)    : the server object used for the XML-RPC or JSON-RPC connection

        ?NOTE:
            Assumes the RT Box's own RPC server does NOT require anything the plain PLECS address
            doesn't already have (no "/RPC2" or similar suffix) -- per the RT Box XML/JSON-RPC
            scripting reference, its own RPC server is documented as requiring a URL ending in
            "/RPC2", so this assumption should be confirmed against real hardware before relying
            on it. If it turns out not to hold, this (and generate_code(), which currently also
            just reuses self.server directly) would need to go back to distinguishing the two.
        """

        address       =   f"{self.url}:{self.port}"

        # import RPC module based on the desired connection method and
        # establish connection to the plecs server using the specified method
        # raise an exception if the connection cannot be established
        if self.METHOD == "JSON":
            #? Will be removed once python version upgraded above 3.10.8
            for _name in ("Mapping", "MutableMapping", "Callable", "Iterable","Iterator", "Sequence", "MutableSequence", "Set"):
                if not hasattr(collections, _name): setattr(collections, _name, getattr(collections.abc, _name))

            self.server  = jsonrpc_requests.Server(address)

        elif self.METHOD == "XML":
            self.server  = xmlrpc.client.Server(address)

    def Open_Model(self, modelname):
        """
        this function takes the name of the model and searches for the
        corresponding Plecs model then opens it before the simulation.


        *Args:
            modelname (string)       : The name of the plecs model.
        """

        # get pyplecs root directory
        root_dir            = os.getcwd()

        # folders to exclude from top-level folders parsing
        excluded_folders    = ["Script","Thermal Models","MyLibraries","FMU","wheelhouse","venv","build","PyPLECS.egg-info"]

        # Build allowed top-level paths with root project level folder included
        allowed_dirs        = [
                                # crawl project directory and list sub directories
                                os.path.join(root_dir, d) for d in os.listdir(root_dir)
                                # with the condition that it is an actual folder not a file and is not from the excluded folders
                                if os.path.isdir(os.path.join(root_dir, d)) and d not in excluded_folders
                                # add pyplecs root dir in case a loose model is added there
                                ] + [root_dir]

        # Flatten all matches into one list
        all_matches         = sum((glob.glob(p, recursive=True) for p in [os.path.join(d, "**", "*.plecs") for d in allowed_dirs]), [])

        # Case-insensitive filter to find matches
        model_path          = next((p for p in all_matches if os.path.basename(p).lower() == modelname.lower()),None)

        if model_path:
            self.path       = model_path
            dp.cp_mdl       = model_path
            os.startfile(model_path)
            dp.scopes       = self.PlecsScopes(self.path)
        else:
            print("Check the model name please.")
            os._exit(0)

    def LoadModel(self,path):
        """
        Loads the PLECS model file specified by the path -- or, when rtbox_enabled, generates
        real-time code for it and uploads the result to the RT Box instead. This is the RT Box's
        equivalent of "loading" a model: done here, before LaunchSim() runs, the same way a normal
        PLECS model is already loaded by the time LaunchSim() simulates it -- so by the time
        LaunchSim()/rtbox_run() actually runs, self.server is already correctly connected to the RT
        Box and the program is already uploaded; rtbox_run() only needs to start it.

        *Args   :
            path (str)  :   string that represents the path to the PLECS model file.

        !Returns:
            If the path is valid and refers to a PLECS file, the model will be loaded over the XML-RPC server. Otherwise, it returns an error message.
            For the RT Box path, returns None (codegen_only) or nothing meaningful -- self.rtbox_codegen is what callers actually want afterward.

        !Raises:
            Exception If (rtbox_enabled) generate_code() succeeds but the RT Box rejects the upload, or the generated file is missing/unreadable.
        """

        if self.rtbox_enabled:
            self.rtbox_codegen = self.generate_code()  # uses its own separate connection, not self.server

            if self.rtbox_codegen_only:
                print("RT Box rtbox_codegen_only=True — code generated, skipping upload.")
                return

            # Upload it to the RT Box now, while we have it -- same upload logic rt_load() used to do.
            # self.server is already correctly connected to the RT Box here -- set by modelinit_opts()'s
            # PlecsConnect() call, which connects to the RT Box whenever rtbox_enabled and not
            # codegen_only (exactly the branch we're in) -- so no reconnect needed at this point.

            if self.rtbox_codegen is None or not self.rtbox_codegen.is_file() :
                raise Exception(f"Codegen executable not found or not yet generated: {self.rtbox_codegen}")

            print(f"Uploading executable: {self.rtbox_codegen}")
            try:
                with open(self.rtbox_codegen, "rb") as f:
                    payload =  base64.b64encode(f.read()).decode()
                    self.server.rtbox.load(payload)
            except Exception as exc:
                raise Exception(f"Failed to load executable onto RT Box: {exc}") from exc
            print("Executable uploaded successfully.")
            return

        # get the file extension of the path
        # if the path is valid and refers to a plecs file load it over the xmlrpc server otherwise print an error message
        ext = os.path.splitext(path)[-1].lower()
        if (path is not None) and (ext == ".plecs"):
            try :
                self.server.plecs.load(path)
            except Exception as e:
                return e
        else:
            print('Simulation Path is invalid or Empty')

    def LaunchSim(self,instances,path,parallel=False,callback=""):
        """
        Launches a simulation using the given path to the simulation model file.

        When rtbox_enabled is True, code generation (and, unless rtbox_codegen_only, upload to the
        RT Box) already happened earlier via LoadModel() (called from modelinit_opts(), before this
        runs) -- LaunchSim() doesn't repeat that here.

        When rtbox_enabled and rtbox_codegen_only are both True, this just returns the already-
        generated .elf's Path -- no simulation, no RT Box hardware touched at all.

        When rtbox_enabled is True (and codegen_only is False), this instead runs the RT Box workflow
        (rtbox_run(): start the already-uploaded program, optionally set/get values, stop) on the real
        hardware, and returns its captured-data dict -- no normal PLECS simulation happens in that case.

        Callers don't need their own branch for any of this; LaunchSim() always does the right thing
        for however this instance is configured.

        *Args   :
            path (str)  : The path to the simulation model file.

        !Returns:
            dict        : A dictionary containing the results of the simulation, including the time values and the corresponding simulated values.
                          When rtbox_enabled and rtbox_codegen_only are both True, this is instead the already-generated .elf's Path.
                          When rtbox_enabled is True and rtbox_codegen_only is False, this is instead whatever rtbox_run() returns
                          (captured Data Capture block values, if any).
        """

        if self.rtbox_enabled and self.rtbox_codegen_only:
            return self.rtbox_codegen  # already generated by LoadModel(), called earlier via modelinit_opts()
        elif self.rtbox_enabled:
            return self.rtbox_run()

        # Extract the model name from the given path and launch the simulation
        # if only one instance is required and parallel simulations are not needed
        # launch the simulation without a callback function
        # otherwise, launch the simulation with a callback function
        SIM_NAME     =  os.path.split(path)
        modelname    =  (list(SIM_NAME)[-1]).split('.')[0]

        if (instances == 1 and not parallel)    :   results =   self.server.plecs.simulate(modelname,self.OptStruct)
        else                                    :   results =   self.server.plecs.simulate(modelname,self.OptStruct,callback)

        return results

    def LaunchAnalysis(self,instances,path,analysisName,parallel=False,callback=""):
        """
        Interfaces with Plecs and launches the analysis.

        *Args   :
            path            (str)           : the path to the Plecs simulation file to be analyzed.
            analysisName    (str, optional) : the name of the analysis to be launched. Defaults to 'Steady_State_Analysis'.

        !Returns:
            Any                             : the results of the analysis, which may vary depending on the type of analysis.

        """

        # Extract the model name from the given path and launch the analysis
        # and if only one instance is required and parallel simulations are not needed
        # launch the analysis without a callback function
        # otherwise, launch the analysis with a callback function
        SIM_NAME     =  os.path.split(path)
        modelname    =  (list(SIM_NAME)[-1]).split('.')[0]

        if (instances == 1 and not parallel)    :   results =   self.server.plecs.analyze(modelname,analysisName,self.OptStruct)
        else                                    :   results =   self.server.plecs.analyze(modelname,analysisName,self.OptStruct,callback)

        return results

    def CloseModel(self,path):
        """
        Close a PLECS model file.

        *Args   :
            path (str)  : The path to the PLECS model file that should be closed.

        """

        # Close the plecs model specified by the path over the xmlrpc server
        self.server.plecs.close(path)

    def ClearTrace(self, modelname, scopes):
        """
        Clears the traces for specified scopes in a given model.

        *Args   :
            modelname   (str)   : The name of the model, which may include a file extension.
            scopes      (list)  : A list of scope names within the model whose traces should be cleared.
        """

        # Extract the base model name by removing any file extension
        # Attempt to clear traces for each specified scope
        # Silently ignore any errors that occur during the clearing process
        modelname = (modelname.split('.'))[0]

        try:
            for scope in scopes:
                self.server.plecs.scope(modelname+'/'+scope, 'ClearTraces')
        except:
            pass

    def SaveTraces(self, modelname, scopes, path):
        """
        Saves trace data from specified scopes to a designated directory.

        *Args   :
            modelname   (str)   : The name of the model, which may include a file extension.
            scopes      (list)  : A list of scope names within the model whose traces should be saved.
            path        (str)   : The base directory path where the trace files will be saved.
        """

        # Ensure the target directory exists
        # Create a subdirectory named 'Scopes_Traces' within the specified path
        # Extract the base model name by removing any file extension
        # Attempt to save traces for each specified scope to the designated directory
        # Silently ignore any errors that occur during the saving process
        modelname   = (modelname.split('.'))[0]
        path        = path + '/Scopes_Traces'

        try:
            for scope in scopes:
                self.server.plecs.scope(modelname+'/'+scope, 'SaveTraces', path+'/'+scope.replace("/", "_"))
        except:
            pass

    def holdTrace(self, modelname, scopes):
        """
        Holds (pauses) the tracing for specified scopes in a given model.

        *Args   :
            modelname   (str)   : The name of the model, which may include a file extension.
            scopes      (list)  : A list of scope names within the model whose tracing should be paused.

        """

        # Extract the base model name by removing any file extension
        # Attempt to hold traces for each specified scope
        # Silently ignore any errors that occur during the process
        modelname = (modelname.split('.'))[0]

        try:
            for scope in scopes:
                self.server.plecs.scope(modelname+'/'+scope, 'HoldTrace')
        except:
            pass

    def holdTraceCallback(self, scopes):
        """
        Generates a callback script for holding traces of specified scopes.

        *Args   :
            scopes (list)   : A list of scope names for which the hold trace callback should be generated.

        !Returns:
            str             : A string containing the PLECS callback script with commands to hold traces for all specified scopes.
        """

        # Generate a PLECS callback script to hold traces for the specified scopes
        # Return the generated script as a string
        # Each scope will have a command to hold its trace
        callback = """"""
        if not dp.scopes == [None] :
            for scope in scopes:
                callback = callback + f"plecs('scope', './{scope}', 'HoldTrace', name);"

        return callback

    def modelinit_opts(self,maxThreads=1,iteration_range=[0],parallel=False):
        """
        Initialize simulation options and prepare for parallel execution if enabled.

        This method configures the simulation environment by setting up thread structures
        for parallel processing, establishing connection to the PLECS model, and loading
        the model for simulation. It includes a brief delay to ensure proper initialization
        before attempting to connect.

        *Args   :
            maxThreads      (int)   : Maximum number of threads to use for parallel simulation.Defaults to 1
            iteration_range (list)  : Range of iterations to simulate. Defaults to [0].
            parallel        (bool)  : Flag indicating whether to enable parallel execution.Defaults to False.
        """

        # Set up thread structures for parallel execution if enabled
        # Establish connection to PLECS (also reused directly for RT Box calls -- see PlecsConnect())
        # Load the PLECS model for simulation, or (if rtbox_enabled) generate/upload the RT Box program
        # Include a brief delay to ensure proper initialization before connecting
        self.optStruct(maxThreads,iteration_range,parallel)
        time.sleep(5)
        self.PlecsConnect()
        self.LoadModel(self.path)

    def PlecsScopes(self,model_path):
        """
        Get the list of scopes in a given plecs model.

        *Args   :
            model_path (str)    : path of the current plecs model.

        !Returns:
            List                : _description_
        """
        #?----------------------------------
        #? NO SCOPES
        #?----------------------------------
        if dp.JSON["scopes"] == [None]  :   scopes = []

        #?----------------------------------
        #? ALL SCOPES
        #?----------------------------------
        elif dp.JSON["scopes"] == [] :

            # get plecs model tree
            tree    = json.loads(base64.b64decode(self.server.plecs.getModelTree(model_path)).decode('utf-8'))

            # List to store the full paths of all scopes
            scopes  = []

            # Recursive scan function
            def scan(node, path=""):
                """
                Recursively scan nodes and build paths.

                *Args:
                    node (obj)          : node is a plecs xml dictionary block or property
                    path (str, optional): node or component kind path. Defaults to "".
                """
                if isinstance(node, dict):                      # If node is a dictionary (block or property)
                    name            = node.get("name", "")      # Get block name, default empty string
                    kind            = node.get("kind", "")      # Get kind of element :  'circuit', 'scope'

                    # Build full path by appending current node name
                    current_path    = f"{path}/{name}" if path else name

                    # If node represents a scope, add it to the scopes list
                    if kind.lower() == "scope" or node.get("type") == "Scope":scopes.append(current_path)

                    # Recursively scan all children nodes
                    for child in node.get("children", []):scan(child, current_path)

                # If node is a list of nodes
                elif isinstance(node, list):
                    # Recursively scan each item
                    for item in node    :   scan(item, path)

            # Start scanning from the root of the tree
            scan([tree] if isinstance(tree, dict) else tree)

            # Return collected scopes
            scopes = [s.replace("\\", "/").split("/")[-1] for s in scopes]

        #?----------------------------------
        #? SELECTED SCOPES
        #?----------------------------------
        else    :   scopes = dp.JSON["scopes"]

        return scopes

    #?--------------------------------------------------------------------
    #? RT Box: code generation (still a PLECS-side operation, via self.server --
    #? nothing here talks to RT Box hardware, so it's never guarded by rtbox_enabled)
    #?--------------------------------------------------------------------

    def generate_code(self) -> Path:
        """
        Triggers PLECS Coder to generate real-time code, over RPC, using this instance's own
        OptStruct (ModelVars/SolverOpts/AnalysisOpts, built by optStruct() from dp.mdlVars etc.) --
        the exact same values already used for a normal simulation run via LaunchSim(). This is the
        RPC equivalent of clicking the Coder Options window's Build button.

        ?NOTE:
            PLECS requires every Target I/O Block (Analog In/Out, PWM Out, PWM Capture, ...) to sit at
            the TOP LEVEL of whatever the build target is -- and per PLECS's own docs, "Enable code
            generation" is exclusively a per-SUBSYSTEM setting (Subsystem Settings dialog); it doesn't
            exist at all for the bare top-level model. So the target almost always needs to be a
            subsystem path (e.g. "Boost_integrated/Plant + Controller"), not just the model name --
            passing the bare model name fails with "Cannot generate target code for Target I/O Block
            '<path>' because it is not on the top level." This can't be auto-derived from the model
            file name -- it's specific to how each model is structured (whichever subsystem has
            "Enable code generation" checked on it). Input_vars.json's "codegen_target" entry only
            needs to be the subsystem's own name (e.g. "Plant + Controller") -- the model name gets
            prepended here automatically to build the full path PLECS expects.

            The output is assumed to be "<model_name>.elf" in the model's own folder -- which requires
            the model's own Coder Options "Base name" to be explicitly set to the model's name (rather
            than left at its default, which for a subsystem target would otherwise be the subsystem's
            own, sanitized name). Whoever configures the model's Coder Options is responsible for that;
            if it's not set this way, LoadModel() will fail to find the expected file to upload.

            Uses self.server directly (set by PlecsConnect(), called earlier -- e.g. from
            modelinit_opts()) rather than its own connection: PLECS and the RT Box are assumed to
            share the same address/port with no distinguishing URL suffix, so the one connection
            self.server already holds works for this plecs.* call the same as it does for rtbox.*
            calls elsewhere. See PlecsConnect()'s own docstring for the assumption this rests on.

        !Returns:
            Path    :   Path to "<model_name>.elf", expected next to the model file (dp.cp_mdl).
        """
        modelname       = os.path.splitext(os.path.basename(dp.cp_mdl))[0]
        codegen_target  = dp.JSON.get("codegen_target")
        target          = f"{modelname}/{codegen_target}"
        outputDir       = os.path.dirname(dp.cp_mdl)

        self.server.plecs.codegen(target, self.OptStruct, outputDir)

        result          = os.path.join(outputDir, f"{modelname}.elf")

        return Path(result)

    #?--------------------------------------------------------------------
    #? RT Box: hardware
    #?--------------------------------------------------------------------
    @_rt_guard()
    def rt_start(self) -> None:
        """
        Start real-time execution of the loaded simulation model. No-op if rtbox_enabled is False.
        """
        print("Starting real-time simulation.")
        self.server.rtbox.start()
        print("Real-time simulation running.")

    @_rt_guard()
    def rt_stop(self) -> None:
        """
        Stop real-time execution of the currently running model. No-op if rtbox_enabled is False.
        """
        print("Stopping real-time simulation.")
        self.server.rtbox.stop()
        print("Real-time simulation stopped.")

    @_rt_guard()
    def rt_reboot(self) -> None:
        """
        Stop the currently running model and reboot the RT Box itself (not just the simulation).
        No-op if rtbox_enabled is False.
        """
        print("Rebooting RT Box.")
        self.server.rtbox.reboot("reboot")
        print("RT Box reboot requested.")

    #?--------------------------------------------------------------------
    #? RT Box: model introspection
    #?--------------------------------------------------------------------

    @_rt_guard(default=([], []))
    def rt_list(self) -> tuple[list[str], list[str]]:
        """
        List the Programmable Value and Data Capture blocks available in the currently loaded model.
        Returns ([], []) without contacting the RT Box if rtbox_enabled is False.

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
    #? RT Box: data exchange
    #?--------------------------------------------------------------------

    @_rt_guard()
    def rt_set(self, block_name: str, values: Sequence[float]) -> None:
        """
        Write one or more values to a Programmable Value block.
        No-op if rtbox_enabled is False.

        *Args:
            block_name (str)    :   Name of the Programmable Value block to write to, as returned by rt_list()
            values              :   Sequence[float] Value(s) to send, passed to the RT Box as a list

        !Raises:
            Exception If the RPC call fails (unknown block name).

        ?Example:
            self.rt_set("Value1", [5.0, 7.0])   # width-2 signal: channel 0 -> 5.0, channel 1 -> 7.0
            self.rt_set("Value1", [7])          # width-1 signal: still passed as a one-element list

        """
        values      = list(values)
        print(f"Setting block {block_name} to {values}")

        try:
            self.server.rtbox.setProgrammableValue(block_name, values)
        except Exception as exc:
            raise Exception(f"Failed to set value on block {block_name}: {exc}") from exc

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
        Returns {} without contacting the RT Box if rtbox_enabled is False.

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
    #? RT Box: diagnostics
    #?--------------------------------------------------------------------

    @_rt_guard(default="")
    def rt_log(self) -> Any:
        """
        Retrieve the application log messages from the running simulation. Useful for diagnosing
        a failed LoadModel() upload/rt_start(), or a model reporting status "error" from rt_query().
        Returns "" without contacting the RT Box if rtbox_enabled is False.

        !Returns:
                (Any)   :   Log messages as returned by rtbox.getApplicationLog(); the RT Box scripting
                            reference doesn't pin down the exact shape, so this is passed through as-is.
        """
        log = self.server.rtbox.getApplicationLog()

        print(f"Application log: {log}")

        return log

    #?--------------------------------------------------------------------
    #? RT Box: main orchestration method
    #?--------------------------------------------------------------------

    def rtbox_run(
            self                                                        ,
            set_values      : dict[str, Sequence[float]] | None = None  ,
            capture_blocks  : Sequence[str] | None = None               ,
            poll_interval   : float = 1.0                               ,
            timeout         : float | None = None
        ) -> dict[str, Any]:
        """
        Start, interact with, and stop the RT Box program -- code generation and upload already
        happened earlier, via LoadModel() (called from modelinit_opts(), before LaunchSim() runs),
        the same way a normal PLECS model is already loaded by the time LaunchSim() simulates it.
        self.server is therefore already correctly connected to the RT Box by the time this runs; no
        separate connect step is needed here.

        *Args:
            set_values              (dict[str, Sequence[float]])    :   Mapping of Programmable Value block name to the values to write after the simulation starts, e.g. {"Input": [5.0]}
            capture_blocks          (Sequence[str])                 :   Data Capture block names to read before stopping. If omitted, no data is captured.
            poll_interval, timeout  (float)                         :   Forwarded to rt_get

        !Returns:
                                    (dict)                          :   Captured data keyed by capture block name. Empty if capture_blocks was not given,
                                                                        or if rtbox_enabled is False.

        ?Example:
            rpc = PlecsRPC(dp.url, dp.port, dp.mdlVars, dp.slvOpts, dp.anlOpts, rtbox_enabled=dp.JSON["RT"])
            rpc.Open_Model("psfbConverterFBR.plecs")
            rpc.optStruct()
            rpc.LoadModel(rpc.path)  # generates + uploads
            data = rpc.rtbox_run(capture_blocks=["Capture1", "Capture2"])
        """
        if not self.rtbox_enabled:
            print("RT Box disabled (RT=false) — rtbox_run() is a no-op.")
            return {}

        captured    : dict[str, Any] = {}

        try:
            self.rt_start()
            self.rt_list()

            if set_values:
                for block_name, values in set_values.items():
                    self.rt_set(block_name, values)

            if capture_blocks:
                captured = self.rt_get(capture_blocks, poll_interval=poll_interval, timeout=timeout)
        finally:
            # Always attempt to stop, even if something above raised -- matches what __exit__ used
            # to guarantee, without needing the context-manager machinery for it. A stop failure
            # here is deliberately swallowed (only printed), so it can never mask whatever exception
            # actually caused the block to fail.
            try:
                self.rt_stop()
            except Exception:
                print("Failed to stop RT Box cleanly.")

        return captured

#?-------------------------------------------------------------------------------------------------------------------------------------------------------------