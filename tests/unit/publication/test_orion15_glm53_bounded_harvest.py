from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "papers/orion-15-self-orion/evidence/glm-5.3-attribution-v2"


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text())


def test_glm53_harvest_preserves_imperfect_bounded_result() -> None:
    report = _load("report.json")
    disposition = _load("AUTHORITY_DISPOSITION_V1.json")

    assert report["arms"]["control"]["correct"] == 22
    assert report["arms"]["treatment"]["correct"] == 23
    assert "PERFECT_CEILING_NOT_REPRODUCED" in disposition["terminal"]
    assert disposition["scientific_authority_delta"] == "BOUNDED_DESCRIPTIVE_DIRECTION_ONLY"
    assert "external independence" in disposition["forbidden_promotions"]
    assert "journal, submission, or peer-review authority" in disposition["forbidden_promotions"]


def test_glm53_harvest_manifest_binds_every_preserved_artifact() -> None:
    lines = (BASE / "SHA256SUMS").read_text().splitlines()
    assert len(lines) == 56

    for line in lines:
        digest, relative = line.split("  ", 1)
        artifact = BASE / relative
        assert artifact.is_file(), relative
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == digest
