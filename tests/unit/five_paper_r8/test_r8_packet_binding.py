from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[3]
PACKET_DIR = ROOT / "papers/five-paper-top-tier-r8"
VALIDATOR = PACKET_DIR / "harness/validate_r8_packet_binding.py"
READER = PACKET_DIR / "harness/read_packet_commit.py"
SUBJECT_COMMIT = "0c451e862a0eeddac7c673813c4dc499f134b088"
SUBJECT_TREE = "dbf96cce53d21d25584479fb740473293fae75e0"


def _load() -> ModuleType:
    assert VALIDATOR.is_file(), "R8 packet binding validator is not implemented"
    spec = importlib.util.spec_from_file_location("r8_packet_binding", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _documents() -> tuple[dict[str, object], dict[str, object]]:
    packet = json.loads((PACKET_DIR / "R8_PACKET_COMMIT.json").read_text())
    binding = json.loads((PACKET_DIR / "R8_PACKET_PUBLICATION_BINDING.json").read_text())
    return packet, binding


def test_validator_exists_before_binding_contract_tests() -> None:
    assert VALIDATOR.is_file()


def test_baseline_binds_distinct_subject_and_packet_publication() -> None:
    validator = _load()
    result = validator.validate_binding(ROOT)
    assert result["terminal"] == "R8_PACKET_SUBJECT_AND_PUBLICATION_IDENTITIES_BOUND"
    assert result["scientific_subject"]["commit"] == SUBJECT_COMMIT
    assert result["scientific_subject"]["tree"] == SUBJECT_TREE
    assert result["packet_publication"]["commit"] != SUBJECT_COMMIT
    assert result["authority"]["scientific_disposition"] == "NONE"
    assert result["authority"]["paper_authority_delta"] == "NONE"


def test_successor_contains_no_self_referential_placeholder() -> None:
    validator = _load()
    packet, binding = _documents()
    assert "TO_BE_BOUND_AFTER_MATERIALIZATION" not in json.dumps(packet, sort_keys=True)
    assert "TO_BE_BOUND_AFTER_MATERIALIZATION" not in json.dumps(binding, sort_keys=True)
    packet["scientific_subject"]["commit"] = "TO_BE_BOUND_AFTER_MATERIALIZATION"
    with pytest.raises(validator.BindingError, match="placeholder"):
        validator.validate_binding(ROOT, packet=packet, binding=binding)


def test_source_ref_drift_fails_closed() -> None:
    validator = _load()
    packet, binding = _documents()
    packet["scientific_subject"]["source_ref_observed_commit"] = "f" * 40
    binding["scientific_subject"]["source_ref_observed_commit"] = "f" * 40
    with pytest.raises(validator.BindingError, match="source ref"):
        validator.validate_binding(ROOT, packet=packet, binding=binding)


def test_packet_publication_blob_tampering_fails_closed() -> None:
    validator = _load()
    packet, binding = _documents()
    binding["packet_publication"]["git_blob"] = "0" * 40
    with pytest.raises(validator.BindingError, match="blob"):
        validator.validate_binding(ROOT, packet=packet, binding=binding)


def test_packet_publication_path_tampering_fails_closed() -> None:
    validator = _load()
    packet, binding = _documents()
    binding["packet_publication"]["path"] = "papers/five-paper-top-tier-r8/OTHER.json"
    with pytest.raises(validator.BindingError, match="path"):
        validator.validate_binding(ROOT, packet=packet, binding=binding)


def test_scientific_subject_tree_tampering_fails_closed() -> None:
    validator = _load()
    packet, binding = _documents()
    packet["scientific_subject"]["tree"] = "0" * 40
    binding["scientific_subject"]["tree"] = "0" * 40
    with pytest.raises(validator.BindingError, match="tree"):
        validator.validate_binding(ROOT, packet=packet, binding=binding)


def test_exact_checkout_reader_resolves_subject_not_publication() -> None:
    validator = _load()
    assert validator.resolve_subject_checkout(ROOT) == SUBJECT_COMMIT
    output = subprocess.check_output([sys.executable, str(READER)], cwd=ROOT, text=True).strip()
    assert output == SUBJECT_COMMIT
    tree = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"{output}^{{tree}}"], text=True
    ).strip()
    assert tree == SUBJECT_TREE


def test_predecessor_bytes_are_preserved_and_bound() -> None:
    validator = _load()
    result = validator.validate_binding(ROOT)
    predecessor = result["predecessor_packet"]
    preserved = PACKET_DIR / "R8_PACKET_COMMIT_V1_PRESERVED.json"
    assert preserved.read_bytes() == subprocess.check_output(
        [
            "git",
            "-C",
            str(ROOT),
            "show",
            f"{predecessor['publication_commit']}:{predecessor['path']}",
        ]
    )
    assert predecessor["git_blob"] == "2712ce1797fcc78d9b5ea9bf533809b2698d106a"
    assert predecessor["sha256"] == "f71faaea81e0a36a71a60ba7ad591682dccbe80d9e4082e02a4402e77a9f9129"


def test_exact_schema_rejects_unregistered_fields() -> None:
    validator = _load()
    packet, binding = _documents()
    binding["unregistered_authority"] = "SCIENTIFICALLY_GREEN"
    with pytest.raises(validator.BindingError, match="schema fields"):
        validator.validate_binding(ROOT, packet=packet, binding=binding)
