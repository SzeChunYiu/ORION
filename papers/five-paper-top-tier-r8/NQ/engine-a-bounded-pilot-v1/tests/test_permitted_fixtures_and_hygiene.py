from __future__ import annotations

import json
from pathlib import Path

from nq_engine_a.group import GroupSpec

ROOT = Path(__file__).resolve().parents[1]


def test_permitted_lower_witness_fixtures_are_strict_c5_cubed_sequences() -> None:
    spec = GroupSpec(5, 3)
    expected_lengths = {"d2_lower_witness.json": 19, "d3_lower_witness.json": 24}
    for name, expected_length in expected_lengths.items():
        payload = json.loads((ROOT / "fixtures" / name).read_text())
        assert payload["exposure_markers"] == [
            "EXPECTED_OUTCOME_EXPOSURE",
            "ENGINE_B_EXPOSURE_IN_PRIOR_CONTEXT__CANNOT_CHECK",
        ]
        sequence = tuple(tuple(vector) for vector in payload["witness"])
        assert len(spec.validate_sequence(sequence)) == expected_length


def test_frozen_full_counts_are_not_encoded_as_targets_or_acceptance_conditions() -> None:
    forbidden = (("98" + "622"), ("230" + "983"))
    for directory in (ROOT / "src", ROOT / "tests"):
        for path in directory.rglob("*.py"):
            text = path.read_text()
            if path.name == __file__.rsplit("/", 1)[-1]:
                text = text.replace('("98" + "622")', "").replace('("230" + "983")', "")
            assert not any(token in text for token in forbidden), path


def test_forbidden_donor_implementations_are_not_imported_or_named() -> None:
    donor_tokens = ("x1f0_", "x1f_")
    for path in (ROOT / "src").rglob("*.py"):
        lowered = path.read_text().lower()
        assert not any(token in lowered for token in donor_tokens), path
