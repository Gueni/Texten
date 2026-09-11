"""
RT_Box.py

Client-side interface for controlling a PLECS RT Box from a PLECS
Standalone / Python workflow, via XML-RPC or JSON-RPC.

Wraps the RT Box RPC API (rtbox.*) exposed by the RT Box target so that
loading, starting, stopping, and exchanging data with a real-time
simulation can be scripted the same way regardless of which RPC
transport is used.

Typical usage
-------------
    from RT_Box import RT_Box

    with RT_Box(model_name="rlc_network_scripting", host_name="rtbox-123.local") as rt:
        rt.rt_load()
        rt.rt_start()
        rt.rt_set("Input", [5.0])
        data = rt.rt_get(["Capture1", "Capture2"])
        print(data["Capture1"]["data"])
    # rt_stop() is called automatically on exit
"""

from __future__ import annotations

import base64
import collections.abc
import functools
import json
import logging
import socket
import time
from pathlib import Path
from typing import Any, Callable, Sequence

import jsonrpc_requests
import xmlrpc.client

logger = logging.getLogger(__name__)


class RTBoxError(Exception):
    """Raised for RT Box connection, load, or RPC-call failures."""


def _rt_guard(default: Any = None) -> Callable:
    """
    Method decorator that turns RT Box calls into no-ops when the
    instance is disabled (``self.enabled is False``).

    This is what implements the "RT" flag from a config file: every
    method that talks to real hardware is wrapped with this, so a
    single ``enabled=False`` on construction makes the whole class
    silently pass through instead of hitting the network.

    Parameters
    ----------
    default : Any, optional
        Value to return when the call is skipped, matching the shape
        callers expect (e.g. ``{}`` for rt_get, ``([], [])`` for
        rt_list) so downstream code doesn't need extra None-checks.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self: "RT_Box", *args, **kwargs):
            if not self.enabled:
                logger.debug("RT Box disabled (RT=false) — skipping %s()", func.__name__)
                return default
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class RT_Box:
    """
    Client wrapper around a PLECS RT Box's remote-procedure-call API.

    Handles connecting to the RT Box, uploading a compiled model
    (codegen executable), starting/stopping the real-time simulation,
    and exchanging data with Programmable Value and Data Capture
    blocks in the running model.

    Parameters
    ----------
    model_name : str
        Name of the compiled PLECS model. Used to build the default
        codegen executable path: ``<model_name>_codegen/<model_name>.elf``.
    host_name : str
        Hostname or IP address of the RT Box (e.g. ``"rtbox-123.local"``).
    method : str, optional
        RPC transport to use, either ``"XML"`` (XML-RPC) or ``"JSON"``
        (JSON-RPC). Defaults to ``"XML"``.
    port : int, optional
        TCP port the RT Box listens on for RPC connections. Defaults
        to ``9998``.
    codegen_path : str or Path, optional
        Explicit path to the compiled executable. If omitted, it is
        derived from ``model_name``.
    enabled : bool, optional
        Master on/off switch. When ``False``, every method that would
        talk to real hardware (connect/load/start/stop/list/set/get)
        becomes a no-op and returns immediately. This lets the exact
        same calling code run in environments with no RT Box attached
        (e.g. a developer machine) by flipping one flag — typically
        sourced from an external config file via :meth:`from_config`.
        Defaults to ``True``.

    Attributes
    ----------
    server : xmlrpc.client.ServerProxy or jsonrpc_requests.Server
        The connected RPC client, available after :meth:`rt_connect`.
        Remains ``None`` if the instance is disabled.
    """

    DEFAULT_PORT = 9998
    SUPPORTED_METHODS = ("XML", "JSON")

    def __init__(
        self,
        model_name: str = "",
        host_name: str = "",
        method: str = "XML",
        port: int = DEFAULT_PORT,
        codegen_path: str | Path | None = None,
        enabled: bool = True,
    ) -> None:
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(
                f"Unsupported method {method!r}; expected one of {self.SUPPORTED_METHODS}"
            )

        self.model_name = model_name
        self.host_name = host_name
        self.method = method
        self.port = port
        self.enabled = enabled

        # Skip DNS resolution entirely when disabled, so this class can be
        # constructed on a machine with no route to the RT Box at all.
        self.ip = ""
        self.host_address = ""
        if self.enabled and self.host_name:
            self.ip = socket.gethostbyname(self.host_name)
            self.host_address = f"http://{self.ip}:{self.port}/RPC2"

        self.codegen = Path(codegen_path) if codegen_path else Path(
            f"{self.model_name}_codegen/{self.model_name}.elf"
        )

        self.server: Any = None

    @classmethod
    def from_config(cls, config_path: str | Path) -> "RT_Box":
        """
        Build an RT_Box from an external JSON configuration file.

        This is the intended way to toggle real-hardware use on/off
        without touching code: set ``"RT": false`` in the file to make
        every RT Box call a no-op (e.g. for local development or CI),
        and ``"RT": true"`` when running against the client's actual
        RT Box.

        Expected JSON keys
        -------------------
        RT : bool
            Master enable switch. Missing/false disables the instance.
        model_name : str
        host_name : str
        method : str, optional
            ``"XML"`` or ``"JSON"``. Defaults to ``"XML"``.
        port : int, optional
            Defaults to :attr:`DEFAULT_PORT`.
        codegen_path : str, optional

        Parameters
        ----------
        config_path : str or Path
            Path to the JSON config file.

        Returns
        -------
        RT_Box
        """
        config_path = Path(config_path)
        with open(config_path) as f:
            config = json.load(f)

        return cls(
            model_name=config.get("model_name", ""),
            host_name=config.get("host_name", ""),
            method=config.get("method", "XML"),
            port=config.get("port", cls.DEFAULT_PORT),
            codegen_path=config.get("codegen_path"),
            enabled=bool(config.get("RT", False)),
        )

    # ------------------------------------------------------------------ #
    # Context-manager support
    # ------------------------------------------------------------------ #
    def __enter__(self) -> "RT_Box":
        self.rt_connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            self.rt_stop()
        except Exception:
            # Don't mask the original exception (if any) with a stop failure.
            logger.warning("Failed to stop RT Box cleanly on exit.", exc_info=True)

    # ------------------------------------------------------------------ #
    # Connection lifecycle
    # ------------------------------------------------------------------ #
    @_rt_guard()
    def rt_connect(self) -> None:
        """
        Open an RPC connection to the RT Box.

        No-op if the instance was constructed with ``enabled=False``.

        Instantiates :attr:`server` using the transport selected by
        :attr:`method` (``"XML"`` or ``"JSON"``).

        Raises
        ------
        RTBoxError
            If the connection cannot be established.
        """
        logger.info("Connecting to RT Box at %s (%s-RPC)", self.host_address, self.method)
        try:
            if self.method == "JSON":
                # jsonrpc_requests relies on collections.Mapping, removed in
                # Python 3.10+; alias it to collections.abc.Mapping.
                collections.Mapping = collections.abc.Mapping  # type: ignore[attr-defined]
                self.server = jsonrpc_requests.Server(self.host_address)
            else:  # "XML"
                self.server = xmlrpc.client.ServerProxy(self.host_address)
        except Exception as exc:
            raise RTBoxError(f"Could not connect to RT Box at {self.host_address}: {exc}") from exc

    @_rt_guard()
    def rt_load(self) -> None:
        """
        Upload the compiled model executable to the RT Box.

        No-op if the instance was constructed with ``enabled=False``.

        Reads the file at :attr:`codegen`, base64-encodes it, and sends
        it via ``rtbox.load``.

        Raises
        ------
        RTBoxError
            If the executable file is missing/unreadable, or the RT Box
            rejects the upload.
        """
        if not self.codegen.is_file():
            raise RTBoxError(f"Codegen executable not found: {self.codegen}")

        logger.info("Uploading executable: %s", self.codegen)
        try:
            with open(self.codegen, "rb") as f:
                payload = base64.b64encode(f.read()).decode()
            self.server.rtbox.load(payload)
        except Exception as exc:
            raise RTBoxError(f"Failed to load executable onto RT Box: {exc}") from exc
        logger.info("Executable uploaded successfully.")

    @_rt_guard()
    def rt_start(self) -> None:
        """Start real-time execution of the loaded model. No-op if disabled."""
        logger.info("Starting real-time simulation.")
        self.server.rtbox.start()
        logger.info("Real-time simulation running.")

    @_rt_guard()
    def rt_stop(self) -> None:
        """Stop real-time execution of the currently running model. No-op if disabled."""
        logger.info("Stopping real-time simulation.")
        self.server.rtbox.stop()
        logger.info("Real-time simulation stopped.")

    # ------------------------------------------------------------------ #
    # Model introspection
    # ------------------------------------------------------------------ #
    @_rt_guard(default=([], []))
    def rt_list(self) -> tuple[list[str], list[str]]:
        """
        List the Programmable Value and Data Capture blocks available
        in the currently loaded model.

        Returns ``([], [])`` without contacting the RT Box if the
        instance was constructed with ``enabled=False``.

        Returns
        -------
        tuple[list[str], list[str]]
            ``(input_blocks, output_blocks)`` — names of Programmable
            Value blocks and Data Capture blocks, respectively.
        """
        input_blocks = self.server.rtbox.getProgrammableValueBlocks()
        output_blocks = self.server.rtbox.getDataCaptureBlocks()
        logger.info("Available input blocks: %s", input_blocks)
        logger.info("Available output blocks: %s", output_blocks)
        return input_blocks, output_blocks

    # ------------------------------------------------------------------ #
    # Data exchange (generic)
    # ------------------------------------------------------------------ #
    @_rt_guard()
    def rt_set(self, block_name: str, values: Sequence[float]) -> None:
        """
        Write one or more values to a Programmable Value block.

        No-op if the instance was constructed with ``enabled=False``.

        Parameters
        ----------
        block_name : str
            Name of the Programmable Value block to write to, as
            returned by :meth:`rt_list`.
        values : Sequence[float]
            Value(s) to send. Passed to the RT Box as a list.

        Raises
        ------
        RTBoxError
            If the RPC call fails (e.g. unknown block name).
        """
        values = list(values)
        logger.info("Setting block %r to %s", block_name, values)
        try:
            self.server.rtbox.setProgrammableValue(block_name, values)
        except Exception as exc:
            raise RTBoxError(f"Failed to set value on block {block_name!r}: {exc}") from exc

    @_rt_guard(default={})
    def rt_get(
        self,
        capture_blocks: Sequence[str],
        poll_interval: float = 1.0,
        timeout: float | None = None,
        trigger_reference_block: str | None = None,
    ) -> dict[str, Any]:
        """
        Wait for and retrieve captured data from one or more Data
        Capture blocks.

        Returns ``{}`` without contacting the RT Box if the instance
        was constructed with ``enabled=False``.

        Blocks until the reference capture block reports at least one
        trigger (or until ``timeout`` elapses), then reads data from
        every block in ``capture_blocks``.

        Parameters
        ----------
        capture_blocks : Sequence[str]
            Names of the Data Capture blocks to read, as returned by
            :meth:`rt_list`.
        poll_interval : float, optional
            Seconds to wait between trigger-count checks. Defaults to 1.0.
        timeout : float, optional
            Maximum seconds to wait for a trigger before giving up. If
            ``None`` (default), waits indefinitely.
        trigger_reference_block : str, optional
            Which block's trigger count to poll before reading data.
            Defaults to the first entry in ``capture_blocks``.

        Returns
        -------
        dict[str, Any]
            Mapping of block name to the raw capture data returned by
            ``rtbox.getCaptureData`` for that block.

        Raises
        ------
        TimeoutError
            If ``timeout`` is set and no trigger occurs in time.
        """
        if not capture_blocks:
            raise ValueError("capture_blocks must contain at least one block name.")

        reference_block = trigger_reference_block or capture_blocks[0]

        elapsed = 0.0
        while self.server.rtbox.getCaptureTriggerCount(reference_block) == 0:
            if timeout is not None and elapsed >= timeout:
                raise TimeoutError(
                    f"No trigger on {reference_block!r} after {timeout} seconds."
                )
            logger.debug("Waiting for data on %r...", reference_block)
            time.sleep(poll_interval)
            elapsed += poll_interval

        return {
            block: self.server.rtbox.getCaptureData(block) for block in capture_blocks
        }

    # ------------------------------------------------------------------ #
    # High-level orchestration — the single entry point for callers
    # ------------------------------------------------------------------ #
    def run(
        self,
        set_values: dict[str, Sequence[float]] | None = None,
        capture_blocks: Sequence[str] | None = None,
        poll_interval: float = 1.0,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """
        Run the full RT Box workflow end to end: connect, load, start,
        optionally write Programmable Values, optionally read Data
        Capture blocks, then stop — always, even on error.

        This is the method other classes/scripts are meant to call
        instead of sequencing rt_connect/rt_load/.../rt_stop
        themselves. It's also where the ``enabled``/"RT" flag has its
        effect: when disabled, this immediately returns ``{}`` and
        touches nothing (no DNS lookup, no file read, no network call).

        Parameters
        ----------
        set_values : dict[str, Sequence[float]], optional
            Mapping of Programmable Value block name to the values to
            write after the simulation starts, e.g.
            ``{"Input": [5.0]}``.
        capture_blocks : Sequence[str], optional
            Data Capture block names to read before stopping. If
            omitted, no data is captured.
        poll_interval, timeout :
            Forwarded to :meth:`rt_get`.

        Returns
        -------
        dict[str, Any]
            Captured data keyed by capture block name. Empty if
            ``capture_blocks`` was not given, or if the instance is
            disabled.

        Example
        -------
            rt = RT_Box.from_config("rt_config.json")
            data = rt.run(set_values={"Input": [5.0]},
                           capture_blocks=["Capture1", "Capture2"])
        """
        if not self.enabled:
            logger.info("RT Box disabled (RT=false) — run() is a no-op.")
            return {}

        captured: dict[str, Any] = {}
        with self:  # rt_connect() on enter, rt_stop() on exit (even on error)
            self.rt_load()
            self.rt_start()
            if set_values:
                for block_name, values in set_values.items():
                    self.rt_set(block_name, values)
            if capture_blocks:
                captured = self.rt_get(
                    capture_blocks, poll_interval=poll_interval, timeout=timeout
                )
        return captured
