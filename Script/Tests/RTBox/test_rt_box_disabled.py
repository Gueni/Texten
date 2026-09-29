

from __future__ import annotations
import json
from Lib.RT_Box import RT_Box


# ---------------------------------------------------------------------- #
# Disabled ("RT": false) behaviour
# ---------------------------------------------------------------------- #
class TestDisabledRTBox:
    def test_construction_does_not_resolve_host(self):
        # with enabled=False it must never be attempted.
        rt = RT_Box(model_name="demo", host_name="this-host-does-not-exist.invalid", enabled=False)
        assert rt.ip == ""
        assert rt.host_address == ""

    def test_set_values_defaults_to_empty_dict(self):
        # no set_values passed -> {}, never None, so `if set_values:` checks stay simple.
        rt = RT_Box(model_name="demo", host_name="nope.invalid", enabled=False)
        assert rt.set_values == {}

    def test_all_methods_are_no_ops(self):
        rt = RT_Box(model_name="demo", host_name="nope.invalid", enabled=False)
        rt.rt_connect()  # would raise if it tried to connect
        rt.rt_load()  # would raise: no codegen file on disk
        rt.rt_start()
        rt.rt_set("Input", [1.0])
        assert rt.rt_list() == ([], [])
        assert rt.rt_get(["Capture1"]) == {}
        assert rt.rt_query() == {}
        assert rt.rt_log() == ""
        rt.rt_reboot()
        rt.rt_stop()

    def test_run_is_a_no_op_and_returns_empty_dict(self):
        rt = RT_Box(model_name="demo", host_name="nope.invalid", enabled=False)
        result = rt.run(set_values={"Input": [1.0]}, capture_blocks=["Capture1"])
        assert result == {}

    def test_from_config_respects_rt_false(self, tmp_path):
        config_path = tmp_path / "rt_config.json"
        config_path.write_text(json.dumps({
            "RT": False,
            "model_name": "demo",
            "host_name": "nope.invalid",
        }))
        rt = RT_Box.from_config(config_path)
        assert rt.enabled is False
        assert rt.run(capture_blocks=["Capture1"]) == {}
