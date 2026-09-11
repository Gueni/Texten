"""
mock_rt_box_server.py

An in-process, fake RT Box RPC server exposing the same XML-RPC
surface (``rtbox.*``) that :class:`RT_Box` calls. Lets you exercise
the full RT_Box workflow locally — connect, load, start, set, get,
stop — with no physical RT Box on the network, before pointing the
same code at the client's real hardware.

Run standalone (e.g. to manually test a script against it):

    python mock_rt_box_server.py --port 9998

Or use it inside a test as a context manager — see test_rt_box.py.
"""

from __future__ import annotations

import argparse
import base64
import threading
import time
from typing import Any
from xmlrpc.server import SimpleXMLRPCServer


class MockRTBoxServer:
    """
    Minimal stand-in for a real RT Box's XML-RPC interface.

    Runs a :class:`~xmlrpc.server.SimpleXMLRPCServer` in a background
    thread and answers the ``rtbox.*`` calls RT_Box makes with
    canned, deterministic responses — enough to test connection
    handling, load/start/stop sequencing, and set/get round-trips
    without a physical device.

    Parameters
    ----------
    host : str, optional
        Interface to bind to. Defaults to ``"localhost"``.
    port : int, optional
        Port to bind to. Defaults to ``9998`` (RT_Box's default).
    trigger_after : int, optional
        Number of ``getCaptureTriggerCount`` polls before reporting a
        trigger, to exercise RT_Box's wait/poll loop. Defaults to 1
        (triggers immediately).

    Example
    -------
        with MockRTBoxServer(port=9998) as mock:
            rt = RT_Box(model_name="demo", host_name="localhost",
                         port=mock.port, enabled=True)
            data = rt.run(capture_blocks=["Capture1"])
    """

    def __init__(self, host: str = "localhost", port: int = 9998, trigger_after: int = 1):
        self.host = host
        self.port = port
        self._trigger_after = trigger_after
        self._trigger_count = 0
        self._last_set: tuple[str, list[float]] | None = None
        self._server: SimpleXMLRPCServer | None = None
        self._thread: threading.Thread | None = None

    # -- lifecycle ------------------------------------------------------ #
    def start(self) -> None:
        """Start the mock server in a background thread."""
        self._server = SimpleXMLRPCServer(
            (self.host, self.port), allow_none=True, logRequests=False
        )
        self._register_handlers()
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the mock server and release its socket."""
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def __enter__(self) -> "MockRTBoxServer":
        self.start()
        return self

    def __exit__(self, *exc_info) -> None:
        self.stop()

    # -- fake rtbox.* API ------------------------------------------------ #
    def _register_handlers(self) -> None:
        assert self._server is not None
        self._server.register_function(self._load, "rtbox.load")
        self._server.register_function(self._start, "rtbox.start")
        self._server.register_function(self._stop, "rtbox.stop")
        self._server.register_function(
            self._get_programmable_value_blocks, "rtbox.getProgrammableValueBlocks"
        )
        self._server.register_function(
            self._get_data_capture_blocks, "rtbox.getDataCaptureBlocks"
        )
        self._server.register_function(
            self._set_programmable_value, "rtbox.setProgrammableValue"
        )
        self._server.register_function(
            self._get_capture_trigger_count, "rtbox.getCaptureTriggerCount"
        )
        self._server.register_function(self._get_capture_data, "rtbox.getCaptureData")

    def _load(self, payload_b64: str) -> bool:
        base64.b64decode(payload_b64)  # just prove it's decodable, like a real load would check
        return True

    def _start(self) -> bool:
        return True

    def _stop(self) -> bool:
        return True

    def _get_programmable_value_blocks(self) -> list[str]:
        return ["Input"]

    def _get_data_capture_blocks(self) -> list[str]:
        return ["Capture1", "Capture2"]

    def _set_programmable_value(self, block_name: str, values: list[float]) -> bool:
        self._last_set = (block_name, list(values))
        return True

    def _get_capture_trigger_count(self, block_name: str) -> int:
        self._trigger_count += 1
        return int(self._trigger_count >= self._trigger_after)

    def _get_capture_data(self, block_name: str) -> dict[str, Any]:
        if block_name == "Capture1":
            return {"data": [[1.0, 0.5], [2.0, 0.6], [3.0, 0.7]]}
        return {"data": [[3.0]]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=9998)
    args = parser.parse_args()

    server = MockRTBoxServer(port=args.port)
    server.start()
    print(f"Mock RT Box server running on localhost:{args.port} (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
