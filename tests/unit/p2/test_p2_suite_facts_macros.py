"""Scale facts must be derived, and re-hardcoding one must fail here.

A suite change previously falsified six files at once — prose in three manuscript
files, a run manifest, an analysis guard and two snapshot tests — because each
had its own copy of the task count. Updating those copies is a patch; making the
copies impossible is the fix. These tests enforce the fix in both directions: the
generated macros must match the artifacts, and the manuscript must not reintroduce
a literal that the macros already carry.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery"
MANIFEST = PAPER / "evidence" / "offline_gold" / "MANIFEST.json"
RESULTS = PAPER / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
GENERATED = PAPER / "manuscript" / "generated" / "suite_facts.tex"
SCRIPT = PAPER / "scripts" / "render_suite_facts.py"
MANUSCRIPT_FILES = [PAPER / "manuscript" / "main.tex"] + sorted(
    (PAPER / "manuscript" / "sections").glob("*.tex")
)

#: The scan is unit-aware, not digit-aware. Its first draft flagged ``100\\%`` and
#: "100 route-stop events" as the document count, which is the cry-wolf failure that
#: gets a checker switched off: a bare number is not a claim about the suite, a
#: number next to its unit is. Facts with no unit word are matched only in the
#: ``$n=...$`` form.
FACT_UNITS = {
    "OfflineTaskCount": ("task", "tasks"),
    "OfflineSystemCount": ("system", "systems"),
    "OfflineTopicCount": ("topic", "topics"),
    "OfflineDocumentCount": ("document", "documents"),
    "OfflineRunRecordCount": ("record", "records", "run", "runs", "execution", "executions"),
}

#: No manuscript file is excluded. The worldscale merge landed; results.tex
#: must use generated macros rather than literal scale facts.
PENDING_EXCLUSIONS: set[str] = set()


def _module():
    spec = importlib.util.spec_from_file_location("render_suite_facts", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def scan_for_hardcoded_facts(facts: dict, paths: list[Path]) -> list[str]:
    """Flag a literal only where it appears *as* the fact, not merely as a digit."""

    offences: list[str] = []
    for path in paths:
        if path.name in PENDING_EXCLUSIONS:
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.lstrip().startswith("%"):
                continue
            for name, units in FACT_UNITS.items():
                value = facts.get(name)
                if not isinstance(value, int) or value <= 0:
                    continue
                unit_pattern = "|".join(units)
                with_unit = rf"(?<![\d.]){value}(?![\d.])(?:[\s~]|-|\\,)*(?:{unit_pattern})\b"
                as_n = rf"n\s*=\s*(?<![\d.]){value}(?![\d.])"
                if re.search(with_unit, line) or re.search(as_n, line):
                    offences.append(f"{path.name}:{line_number} hardcodes {value} ({name})")
    return offences


def test_generated_macros_match_the_artifacts():
    module = _module()
    assert GENERATED.is_file(), "the generated macro file must be committed"
    assert GENERATED.read_text(encoding="utf-8") == module.render(module.collect()), (
        "suite_facts.tex is stale; regenerate with scripts/render_suite_facts.py"
    )


def test_check_mode_agrees_with_the_committed_file():
    module = _module()
    assert module.main(["--check"]) == 0


def test_check_mode_actually_fails_on_a_stale_file(tmp_path):
    """The guard has to fire, or it is decoration."""

    module = _module()
    stale = tmp_path / "suite_facts.tex"
    stale.write_text("\\newcommand{\\OfflineTaskCount}{999999}\n", encoding="utf-8")
    assert module.main(["--check", "--out", str(stale)]) == 1
    missing = tmp_path / "absent.tex"
    assert module.main(["--check", "--out", str(missing)]) == 1


def test_manuscript_uses_the_macros():
    used = set()
    for path in MANUSCRIPT_FILES:
        used.update(re.findall(r"\\(Offline[A-Za-z]+)", path.read_text(encoding="utf-8")))
    assert used, "the manuscript must cite the generated macros rather than literal counts"
    defined = set(
        re.findall(r"\\newcommand\{\\(Offline[A-Za-z]+)\}", GENERATED.read_text(encoding="utf-8"))
    )
    undefined = sorted(used - defined)
    assert not undefined, f"manuscript uses undefined suite-fact macros: {undefined}"


def test_no_manuscript_file_rehardcodes_a_scale_fact():
    """The tripwire: a literal count in prose is how the last drift happened."""

    module = _module()
    facts = module.collect()
    offences = scan_for_hardcoded_facts(facts, MANUSCRIPT_FILES)
    assert not offences, (
        "use the generated macro instead of a literal scale fact:\n" + "\n".join(offences)
    )


def test_achieved_tier_tracks_n_rather_than_a_hardcoded_threshold():
    """Authority must follow the plan's tiers, at any N, in both directions."""

    module = _module()
    assert module.achieved_tier(20)[0] == "BELOW_TIER_D"
    assert module.achieved_tier(97)[0] == "TIER_D_minimum_inferential"
    assert module.achieved_tier(390)[0] == "TIER_B_committed"
    assert module.achieved_tier(1068)[0] == "TIER_A_full"
    # And the underpowered label must survive good news: TIER_B still exceeds the
    # 0.03 superiority margin, so scaling up must not read as "now powered".
    _, half_width = module.achieved_tier(390)
    assert half_width > module.DELTA_SUP


def test_facts_are_read_from_the_artifacts_not_the_script():
    """A fact must change when the artifact changes, or it is still hardcoded."""

    module = _module()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    facts = module.collect()
    assert facts["OfflineTaskCount"] == int(manifest["task_count"])
    assert facts["OfflineDocumentCount"] == int(manifest["document_count"])
    assert facts["OfflineSuiteFingerprintShort"] == str(manifest["suite_fingerprint"])[:12]
    if RESULTS.is_file():
        results = json.loads(RESULTS.read_text(encoding="utf-8"))
        assert facts["OfflineRunRecordCount"] == int(results["frozen_run"]["n_result_records"])


def test_seed_is_rendered_as_an_identifier_not_a_quantity():
    module = _module()
    rendered = module.render(module.collect())
    assert "\\newcommand{\\OfflineSuiteSeed}{20260816}" in rendered, (
        "a seed must not be thousands-separated; it is an identifier"
    )


@pytest.mark.parametrize("count", [20, 390, 1068])
def test_render_is_deterministic_for_a_given_fact_set(count):
    module = _module()
    facts = dict(module.collect())
    facts["OfflineTaskCount"] = count
    assert module.render(facts) == module.render(facts)


def test_the_scanner_fires_on_a_planted_literal_and_not_on_a_bare_number(tmp_path):
    """Validate the checker itself: it must catch the real pattern and ignore noise."""

    facts = {"OfflineTaskCount": 390, "OfflineDocumentCount": 100}
    planted = tmp_path / "planted.tex"
    planted.write_text(
        "The suite carries 390 tasks over five families.\n"
        "The completed offline suite has $n=390$, below the tier.\n",
        encoding="utf-8",
    )
    offences = scan_for_hardcoded_facts(facts, [planted])
    assert len(offences) == 2, offences

    quiet = tmp_path / "quiet.tex"
    quiet.write_text(
        "Premature closure stays at 100\\% for that comparator.\n"
        "Full ORION makes one false positive in 100 route-stop events.\n"
        "The macro form \\OfflineTaskCount{} tasks must not be flagged.\n"
        "% 390 tasks in a comment is not a claim\n",
        encoding="utf-8",
    )
    assert scan_for_hardcoded_facts(facts, [quiet]) == []
