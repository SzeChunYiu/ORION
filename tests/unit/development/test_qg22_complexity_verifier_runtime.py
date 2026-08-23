from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "development/orion-qg-regime-geometry/qg22_complexity_separation_verify.py"


def _module():
    spec = importlib.util.spec_from_file_location("qg22_complexity_separation_verify", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extracted_qg22_verifier_has_all_runtime_stdlib_dependencies() -> None:
    module = _module()
    assert module.json is not None
    assert module.hashlib is not None
    assert module.itertools is not None
    assert module.argparse is not None
    assert module.canon({"b": 2, "a": 1}) == '{"a":1,"b":2}'
    assert len(module.sha256_file(module.PROTOCOL_PATH)) == 64
