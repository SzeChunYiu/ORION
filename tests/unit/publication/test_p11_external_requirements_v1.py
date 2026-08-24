from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/paper-11-state-as-computation"
REQUIREMENTS = PAPER / "P11_EXTERNAL_VALIDATION_REQUIREMENTS_V1.md"
MANIFEST = PAPER / "CONTENT_MANIFEST_V1.json"


def test_requirements_cover_each_open_box_verbatim():
    text = REQUIREMENTS.read_text(encoding="utf-8")
    boxes = (
        "Compare compiled state against strongest retrieval/full-context arms across\n> >=3 model families",
        "Match tokens, latency, memory and embedding/compilation calls",
        "Add future-query/optionality and leave-one-benchmark-out tests",
    )
    for box in boxes:
        assert box in text, box


def test_requirements_state_cannot_check_and_pass_gate():
    text = REQUIREMENTS.read_text(encoding="utf-8")
    assert "**Status:** CANNOT_CHECK (all three open boxes)" in text
    assert "block-bootstrap lower CI >0 for quality, or >=2x resource saving with <=2 pp\n> noninferiority" in text
    assert text.count("Why CANNOT_CHECK now") == 3


def test_p11_authority_unchanged_by_requirements_artifact():
    authority = json.loads((PAPER / "P11_ACTIVE_CLAIM_AUTHORITY_V2.json").read_text(encoding="utf-8"))
    text = REQUIREMENTS.read_text(encoding="utf-8")
    assert "confers no result and no authority" in text
    assert "sole active authority" in text


def test_requirements_bound_in_readme_and_manifest():
    readme = (PAPER / "README.md").read_text(encoding="utf-8")
    assert "P11_EXTERNAL_VALIDATION_REQUIREMENTS_V1.md" in readme
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    bound = {entry.get("path") for entry in manifest.get("bound_files", [])}
    assert "papers/paper-11-state-as-computation/P11_EXTERNAL_VALIDATION_REQUIREMENTS_V1.md" in bound
