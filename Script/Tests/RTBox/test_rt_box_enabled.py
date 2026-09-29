
from __future__ import annotations
import json
import os
import pytest
from Lib.RT_Box import RT_Box


# ---------------------------------------------------------------------- #
# Enabled behaviour, against a REAL RT Box -- there is no mock server.
# Skipped entirely (not failed) unless the hardware is actually configured.
#
# Required:
#   RTBOX_TEST_HOST       hostname or IP of a reachable RT Box
#   RTBOX_TEST_CODEGEN    path to a real compiled .elf for a model already
#                          built for that RT Box
# Optional:
#   RTBOX_TEST_MODEL_NAME defaults to "demo"
#   RTBOX_TEST_METHOD     "XML" or "JSON", defaults to "XML"
#   RTBOX_TEST_PORT       defaults to RT_Box.DEFAULT_PORT (9998)
#   RTBOX_TEST_ALLOW_REBOOT   set to "1" to also exercise rt_reboot() --
#                          left opt-in since it reboots the actual box
#
# These tests don't assume any particular block names (the Plexim demo
# models use names like "Input"/"Capture1", but your model won't): rt_set/
# rt_get coverage discovers real block names via rt_list() and skips itself
# if the loaded model happens to have no Programmable Value / Data Capture
# blocks at all, rather than hardcoding a name that may not exist.
# ---------------------------------------------------------------------- #

RTBOX_HOST    = os.environ.get("RTBOX_TEST_HOST")
RTBOX_CODEGEN = os.environ.get("RTBOX_TEST_CODEGEN")

requires_hardware = pytest.mark.skipif(
    not (RTBOX_HOST and RTBOX_CODEGEN),
    reason="Set RTBOX_TEST_HOST and RTBOX_TEST_CODEGEN to run these against a real RT Box.",
)


@pytest.fixture
def rt_box() -> RT_Box:
    """A fresh RT_Box configured for the real hardware named by the RTBOX_TEST_* env vars."""
    return RT_Box(
        model_name      = os.environ.get("RTBOX_TEST_MODEL_NAME", "demo"),
        host_name       = RTBOX_HOST,
        method          = os.environ.get("RTBOX_TEST_METHOD", "XML"),
        port            = int(os.environ.get("RTBOX_TEST_PORT", RT_Box.DEFAULT_PORT)),
        codegen_path    = RTBOX_CODEGEN,
        enabled         = True,
    )


@requires_hardware
class TestEnabledRTBox:
    def test_connect_load_start_stop(self, rt_box):
        rt_box.rt_connect()
        rt_box.rt_load()
        rt_box.rt_start()
        rt_box.rt_stop()

    def test_rt_list_returns_block_names(self, rt_box):
        with rt_box:  # rt_connect() on enter, rt_stop() on exit
            rt_box.rt_load()
            rt_box.rt_start()
            inputs, outputs = rt_box.rt_list()
        assert isinstance(inputs, list)
        assert isinstance(outputs, list)

    def test_rt_query_reports_running(self, rt_box):
        with rt_box:
            rt_box.rt_load()
            rt_box.rt_start()
            info = rt_box.rt_query()
        assert info.get("status") == "running"

    def test_rt_log_does_not_raise(self, rt_box):
        with rt_box:
            rt_box.rt_load()
            rt_box.rt_start()
            rt_box.rt_log()  # exact shape isn't pinned down by the RT Box docs; just confirm it works

    def test_rt_set_and_rt_get_round_trip(self, rt_box):
        with rt_box:
            rt_box.rt_load()
            rt_box.rt_start()
            inputs, outputs = rt_box.rt_list()
            if not inputs or not outputs:
                pytest.skip("Loaded model has no Programmable Value / Data Capture blocks to exercise.")
            rt_box.rt_set(inputs[0], [1.0])
            data = rt_box.rt_get([outputs[0]], poll_interval=0.5, timeout=15)
        assert outputs[0] in data
        assert "data" in data[outputs[0]]

    def test_run_executes_full_workflow(self, rt_box):
        # Discover real block names first (separate connection), then drive run() with them.
        with rt_box:
            rt_box.rt_load()
            rt_box.rt_start()
            inputs, outputs = rt_box.rt_list()

        if not inputs or not outputs:
            pytest.skip("Loaded model has no Programmable Value / Data Capture blocks to exercise.")

        data = rt_box.run(
            set_values      = {inputs[0]: [1.0]},
            capture_blocks  = [outputs[0]],
            poll_interval   = 0.5,
            timeout         = 15,
        )
        assert outputs[0] in data

    def test_from_config_respects_rt_true(self, tmp_path):
        config_path = tmp_path / "rt_config.json"
        config_path.write_text(json.dumps({
            "RT"            : True,
            "model_name"    : os.environ.get("RTBOX_TEST_MODEL_NAME", "demo"),
            "host_name"     : RTBOX_HOST,
            "method"        : os.environ.get("RTBOX_TEST_METHOD", "XML"),
            "port"          : int(os.environ.get("RTBOX_TEST_PORT", RT_Box.DEFAULT_PORT)),
            "codegen_path"  : RTBOX_CODEGEN,
        }))
        rt = RT_Box.from_config(config_path)
        assert rt.enabled is True
        with rt:
            rt.rt_load()
            rt.rt_start()

    @pytest.mark.skipif(
        os.environ.get("RTBOX_TEST_ALLOW_REBOOT") != "1",
        reason="Set RTBOX_TEST_ALLOW_REBOOT=1 to also exercise rt_reboot() -- reboots the actual box.",
    )
    def test_rt_reboot(self, rt_box):
        rt_box.rt_connect()
        rt_box.rt_reboot()
