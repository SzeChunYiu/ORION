"""Literature-closure gates for ORION Paper II.

Guards the outcome of the 2026-08 citation-integrity sweep:

* every bibliography entry carries a resolvable identifier;
* every bibliography key is either cited by the manuscript or documented in the
  nearest-work audit, so the bibliography cannot silently accumulate cruft;
* the audit names every protocol task family and every literature family that
  ``JOURNAL_READINESS.md`` section 1 requires;
* every key has a stored fetch record, and any recorded ``MISMATCH`` is
  disclosed in the audit rather than quietly repaired.

Standard library only.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery"
MAIN_TEX = PAPER / "manuscript" / "main.tex"
PROTOCOL = PAPER / "protocol" / "PROTOCOL_V1.json"
READINESS = PAPER / "JOURNAL_READINESS.md"
AUDIT = PAPER / "notes" / "NEAREST_WORK_AUDIT_2026-08.md"
AUDIT_DETAIL_DIR = PAPER / "notes" / "nearest-work"
EVIDENCE_DIR = PAPER / "evidence" / "literature"

# The audit is the read-first core document in a core -> detail -> raw layering.
# It must keep drilling down rather than absorbing the detail files.
AUDIT_MAX_LINES = 180

ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
CITE_RE = re.compile(r"\\cite(?:t|p)?\{([^}]+)\}")
BIBLIOGRAPHY_DECLARATION_RE = re.compile(r"\\bibliography\{([^}]+)\}")
IDENTIFIER_FIELD_RE = re.compile(r"(?:^|,)\s*(doi|eprint|url)\s*=", re.IGNORECASE | re.MULTILINE)

# Literature families required by JOURNAL_READINESS.md section 1 ("Novelty
# closure", lines 8-14) together with the two families named by issue #99 that
# section 1 references only indirectly (ResearchArena, OpenScholar).
# Held as an explicit list rather than parsed out of the prose line: parsing a
# sentence for family names is brittle, so the provenance is stated instead.
REQUIRED_LITERATURE_FAMILIES = {
    "AutoResearchBench": r"\bautoresearchbench\b",
    "SAGE": r"\bsage\b",
    "MetaSyn": r"\bmetasyn\b",
    "ResearchArena": r"\bresearcharena\b",
    "AgentSLR / protocol-driven SLR": r"\bagentslr\b",
    "OpenScholar / scientific RAG": r"\bopenscholar\b",
    "expert literature-review comparison": r"literature-review comparison",
    "systematic-review stopping": r"systematic-review stopping",
    "capture-recapture completeness": r"capture-recapture",
    "query diversification": r"query diversification",
    "federated search": r"federated search",
    "information foraging": r"information foraging",
    "active screening / technology-assisted review": r"technology-assisted review",
}

ALLOWED_VERDICTS = {"VERIFIED", "MISMATCH", "CANNOT_CHECK"}


def _bibliography_paths() -> list[Path]:
    """Every .bib file `main.tex` actually loads, in declaration order.

    Reading one hard-coded path made this suite report every key defined in a
    second bib file as missing from the bibliography. That is a false positive in
    the expensive direction: the failure names real citation keys and reads as a
    broken manuscript, so the manuscript gets edited to satisfy the checker.
    Deriving the set from the `\\bibliography{...}` declaration means adding a bib
    file cannot manufacture a failure, while a key defined in none of them still
    does.
    """

    match = BIBLIOGRAPHY_DECLARATION_RE.search(MAIN_TEX.read_text(encoding="utf-8"))
    assert match, "main.tex declares no \\bibliography{...}"
    names = [part.strip() for part in match.group(1).split(",") if part.strip()]
    paths = [MAIN_TEX.parent / f"{name}.bib" for name in names]
    missing = [path.name for path in paths if not path.exists()]
    assert not missing, f"main.tex loads bibliography files that do not exist: {missing}"
    return paths


def _bib_entries() -> dict[str, str]:
    """Map bibliography key -> entry body, with % comment lines stripped."""
    entries: dict[str, str] = {}
    for path in _bibliography_paths():
        raw = path.read_text(encoding="utf-8")
        text = "\n".join(
            line for line in raw.splitlines() if not line.lstrip().startswith("%")
        )
        starts = [(m.group(2), m.start(), m.end()) for m in ENTRY_RE.finditer(text)]
        for index, (key, _, body_start) in enumerate(starts):
            body_end = starts[index + 1][1] if index + 1 < len(starts) else len(text)
            entries[key] = text[body_start:body_end]
    return entries


def _audit_text() -> str:
    parts = [AUDIT.read_text(encoding="utf-8")]
    parts.extend(
        path.read_text(encoding="utf-8") for path in sorted(AUDIT_DETAIL_DIR.glob("*.md"))
    )
    return "\n".join(parts)


def test_every_bibliography_entry_has_a_verifiable_identifier() -> None:
    entries = _bib_entries()
    assert entries, "bibliography.bib parsed as empty"
    missing = sorted(key for key, body in entries.items() if not IDENTIFIER_FIELD_RE.search(body))
    assert not missing, (
        "bibliography entries without a doi, arXiv eprint or url field "
        f"(cannot be resolved by a reader): {missing}"
    )


def test_every_bibliography_key_is_cited_or_documented() -> None:
    keys = set(_bib_entries())
    cited: set[str] = set()
    for group in CITE_RE.findall(MAIN_TEX.read_text(encoding="utf-8")):
        cited.update(part.strip() for part in group.split(",") if part.strip())

    documented_text = _audit_text()
    orphans = sorted(key for key in keys - cited if key not in documented_text)
    assert not orphans, (
        "bibliography keys that are neither cited by main.tex nor documented in "
        f"the nearest-work audit: {orphans}"
    )

    unresolved = sorted(cited - keys)
    assert not unresolved, f"main.tex cites keys absent from bibliography.bib: {unresolved}"


def test_audit_names_every_protocol_task_family() -> None:
    families = json.loads(PROTOCOL.read_text(encoding="utf-8"))["task_families"]
    assert families, "PROTOCOL_V1.json declares no task_families"
    audit = AUDIT.read_text(encoding="utf-8")
    missing = sorted(family for family in families if family not in audit)
    assert not missing, f"task families absent from the nearest-work audit core: {missing}"


def test_audit_covers_every_required_literature_family() -> None:
    assert READINESS.exists(), "JOURNAL_READINESS.md is the source of the required family list"
    audit = AUDIT.read_text(encoding="utf-8").lower()
    missing = sorted(
        name
        for name, pattern in REQUIRED_LITERATURE_FAMILIES.items()
        if not re.search(pattern, audit, re.IGNORECASE)
    )
    assert not missing, f"literature families absent from the nearest-work audit core: {missing}"


def test_every_bibliography_key_has_a_stored_fetch_record() -> None:
    keys = set(_bib_entries())
    missing = sorted(key for key in keys if not (EVIDENCE_DIR / f"{key}.json").exists())
    assert not missing, f"bibliography keys without a literature evidence record: {missing}"

    for key in sorted(keys):
        record = json.loads((EVIDENCE_DIR / f"{key}.json").read_text(encoding="utf-8"))
        for field in ("bib_key", "claimed_title", "fetch_url", "fetched_utc", "verdict"):
            assert record.get(field), f"{key}.json is missing required field {field!r}"
        assert record["bib_key"] == key, f"{key}.json records bib_key {record['bib_key']!r}"
        assert record["verdict"] in ALLOWED_VERDICTS, (
            f"{key}.json has unknown verdict {record['verdict']!r}; "
            "'could not check' must never be recorded as verified"
        )


def test_recorded_mismatches_are_disclosed_in_the_audit() -> None:
    audit = AUDIT.read_text(encoding="utf-8")
    undisclosed = []
    for path in sorted(EVIDENCE_DIR.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("verdict") in {"MISMATCH", "CANNOT_CHECK"} and record["bib_key"] not in audit:
            undisclosed.append(record["bib_key"])
    assert not undisclosed, (
        "keys with a MISMATCH/CANNOT_CHECK fetch record that the audit does not name; "
        f"a repaired defect must still be reported: {undisclosed}"
    )


def test_audit_core_stays_within_its_line_budget() -> None:
    lines = len(AUDIT.read_text(encoding="utf-8").splitlines())
    assert lines <= AUDIT_MAX_LINES, (
        f"nearest-work audit core is {lines} lines (cap {AUDIT_MAX_LINES}); "
        f"split further into {AUDIT_DETAIL_DIR.name}/ rather than growing the core"
    )
    assert list(AUDIT_DETAIL_DIR.glob("*.md")), "audit core has no detail files to drill into"


FETCHER = EVIDENCE_DIR / "fetch_literature_evidence.py"


def _fetcher_registered_keys() -> set[str]:
    """Keys the fetch script knows how to fetch, read without executing it."""

    tree = ast.parse(FETCHER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
        if target == "ENTRIES" and isinstance(node.value, ast.Dict):
            return {k.value for k in node.value.keys if isinstance(k, ast.Constant)}
    raise AssertionError("ENTRIES dict not found in fetch_literature_evidence.py")


def test_every_bibliography_key_is_registered_with_the_fetcher() -> None:
    """The drift that turned main red at 73e9505.

    `ENTRIES` is a hand-maintained list, so adding a citation and registering it for
    fetching are two disconnected edits. When 73e9505 added `micp2026` to both bib files
    and cited it from `main.tex` without touching the fetcher, the missing-record test
    failed but pointed at the record rather than at the reason there was no way to produce
    one. This test names the reason at the point of the edit.
    """

    keys = set(_bib_entries())
    unregistered = sorted(keys - _fetcher_registered_keys())
    assert not unregistered, (
        "bibliography keys the fetch script cannot fetch, so no evidence record can be "
        f"produced for them: {unregistered}"
    )


def test_the_fetcher_registry_has_no_phantom_keys() -> None:
    """No alarm: a registry entry with no bibliography key is also drift."""

    phantom = sorted(_fetcher_registered_keys() - set(_bib_entries()))
    assert not phantom, f"fetch script registers keys absent from the bibliography: {phantom}"
