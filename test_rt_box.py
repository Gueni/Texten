"""
test_rt_box.py

Tests for RT_Box that run entirely locally — no real RT Box required.

- Disabled-instance tests confirm the "RT" flag makes every method a
  true no-op (no DNS lookup, no network call, safe return values).
- Enabled tests spin up MockRTBoxServer and drive RT_Box against it,
  including the full run() workflow.

Run with:
    python -m pytest test_rt_box.py -v
"""

from __future__ import annotations

import json

import pytest

from mock_rt_box_server import MockRTBoxServer
from RT_Box import RT_Box


# ---------------------------------------------------------------------- #
# Disabled ("RT": false) behaviour
# ---------------------------------------------------------------------- #
class TestDisabledRTBox:
    def test_construction_does_not_resolve_host(self):
        # A bogus hostname would raise on socket.gethostbyname if resolved;
        # with enabled=False it must never be attempted.
        rt = RT_Box(model_name="demo", host_name="this-host-does-not-exist.invalid", enabled=False)
        assert rt.ip == ""
        assert rt.host_address == ""

    def test_all_methods_are_no_ops(self):
        rt = RT_Box(model_name="demo", host_name="nope.invalid", enabled=False)
        rt.rt_connect()  # would raise if it tried to connect
        rt.rt_load()  # would raise: no codegen file on disk
        rt.rt_start()
        rt.rt_set("Input", [1.0])
        assert rt.rt_list() == ([], [])
        assert rt.rt_get(["Capture1"]) == {}
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


# ---------------------------------------------------------------------- #
# Enabled behaviour, against the mock server
# ---------------------------------------------------------------------- #
@pytest.fixture
def mock_server():
    with MockRTBoxServer(host="localhost", port=9998) as server:
        yield server


@pytest.fixture
def rt_box(tmp_path, mock_server):
    # A fake codegen file so rt_load() has something to read.
    codegen_dir = tmp_path / "demo_codegen"
    codegen_dir.mkdir()
    codegen_file = codegen_dir / "demo.elf"
    codegen_file.write_bytes(b"fake-elf-bytes")

    return RT_Box(
        model_name="demo",
        host_name="localhost",
        port=mock_server.port,
        codegen_path=codegen_file,
        enabled=True,
    )


class TestEnabledRTBox:
    def test_connect_load_start_stop(self, rt_box):
        rt_box.rt_connect()
        rt_box.rt_load()
        rt_box.rt_start()
        rt_box.rt_stop()

    def test_rt_list_returns_block_names(self, rt_box):
        rt_box.rt_connect()
        inputs, outputs = rt_box.rt_list()
        assert inputs == ["Input"]
        assert outputs == ["Capture1", "Capture2"]

    def test_rt_set_and_rt_get_round_trip(self, rt_box):
        rt_box.rt_connect()
        rt_box.rt_set("Input", [5.0])
        data = rt_box.rt_get(["Capture1", "Capture2"], poll_interval=0.01)
        assert "Capture1" in data and "Capture2" in data
        assert data["Capture1"]["data"][0] == [1.0, 0.5]

    def test_run_executes_full_workflow(self, rt_box):
        data = rt_box.run(
            set_values={"Input": [5.0]},
            capture_blocks=["Capture1", "Capture2"],
            poll_interval=0.01,
        )
        assert set(data.keys()) == {"Capture1", "Capture2"}

    def test_from_config_respects_rt_true(self, tmp_path, mock_server):
        codegen_dir = tmp_path / "demo_codegen"
        codegen_dir.mkdir()
        codegen_file = codegen_dir / "demo.elf"
        codegen_file.write_bytes(b"fake-elf-bytes")

        config_path = tmp_path / "rt_config.json"
        config_path.write_text(json.dumps({
            "RT": True,
            "model_name": "demo",
            "host_name": "localhost",
            "port": mock_server.port,
            "codegen_path": str(codegen_file),
        }))
        rt = RT_Box.from_config(config_path)
        assert rt.enabled is True
        data = rt.run(capture_blocks=["Capture1"], poll_interval=0.01)
        assert "Capture1" in data
