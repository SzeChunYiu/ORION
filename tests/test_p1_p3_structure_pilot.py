import importlib.util
import json
from pathlib import Path


def load_runner():
    path = Path("research/extensions/p1-p3-structure/run_structure_pilot.py")
    spec = importlib.util.spec_from_file_location("p1p3_structure_pilot", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_frozen_structure_pilot_replays_exactly():
    module = load_runner()
    protocol = json.loads(Path("research/extensions/p1-p3-structure/PROTOCOL_V1.json").read_text())
    expected = json.loads(Path("research/extensions/p1-p3-structure/RESULTS_V1.json").read_text())
    assert module.run(protocol) == expected
    assert expected["projection_alignment_accuracy"] == 1.0
    assert expected["corruption_detection_recall"] == 1.0
    assert expected["transcript_only_pair_accuracy"] < expected["projection_alignment_accuracy"]
    assert expected["terminal"].endswith("P3_METHOD_PROJECTION_NARROWED")
