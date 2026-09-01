"""Validation of the P2 claim-ledger checker against injected defects.

A checker is only worth its exit code if it has been shown to fire on real
defects *and* to stay quiet on a clean tree.  Every test here mutates a
throwaway copy of the paper directory; the committed manuscript is never
touched.  The no-alarm case is asserted first, because a checker that cries wolf
on its first honest run gets switched off.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery"
CHECKER = PAPER / "scripts" / "check_claim_ledger.py"
LEDGER_RELATIVE = Path("protocol") / "CLAIM_LEDGER_V1.json"

EXIT_CLEAN = 0
EXIT_VIOLATIONS = 1
EXIT_HARNESS = 2


def run(paper_root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--check", "--paper-root", str(paper_root), *extra],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.fixture(scope="module")
def pristine(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """One clean copy of the paper tree, shared read-only across tests."""
    target = tmp_path_factory.mktemp("p2-paper-pristine") / "paper"
    shutil.copytree(PAPER, target)
    return target


@pytest.fixture
def paper(pristine: Path, tmp_path: Path) -> Path:
    """A per-test mutable copy.  Tests may vandalise this freely."""
    target = tmp_path / "paper"
    shutil.copytree(pristine, target)
    return target


def load_ledger(paper: Path) -> dict:
    return json.loads((paper / LEDGER_RELATIVE).read_text(encoding="utf-8"))


def save_ledger(paper: Path, ledger: dict) -> None:
    (paper / LEDGER_RELATIVE).write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


def claim(ledger: dict, claim_id: str) -> dict:
    for entry in ledger["claims"]:
        if entry["claim_id"] == claim_id:
            return entry
    raise AssertionError(f"claim {claim_id} not in ledger")


def region_file(paper: Path, region: str = "results") -> Path:
    """Return the manuscript file the committed ledger actually audits."""
    relative = load_ledger(paper)["regions"][region]["file"]
    return paper / "manuscript" / relative


def inject_defect(paper: Path) -> dict:
    """Recreate the archived-only defect pattern the committed ledger used to carry.

    The pristine tree now has an empty ``known_defects`` list (its two defects
    were fixed and retired), so every test that exercises defect machinery
    first rebuilds the pattern: a manuscript sentence tolerated as an open
    defect instead of a ledgered claim.  P2-R07 is un-claimed and re-entered
    as defect ``P2-DTEST``; its sentence stays in ``results.tex``.
    """
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-R07")
    ledger["claims"].remove(entry)
    ledger["known_defects"].append(
        {
            "defect_id": "P2-DTEST",
            "region": "results",
            "sentence": entry["sentence"],
            "contradicted_by": {
                "artifact": "results_summary",
                "key": "systems.orion_full.premature_task_closure_rate",
            },
            "owner": "test harness",
            "required_fix": "restore the ledgered claim",
        }
    )
    save_ledger(paper, ledger)
    return ledger


def messages(proc: subprocess.CompletedProcess[str]) -> str:
    return proc.stdout + proc.stderr


# --------------------------------------------------------------------------- #
# The no-alarm case
# --------------------------------------------------------------------------- #


def test_clean_tree_reports_no_violation() -> None:
    """The committed ledger must be green against the committed manuscript."""
    proc = run(PAPER)
    assert proc.returncode == EXIT_CLEAN, messages(proc)
    assert "VIOLATION" not in messages(proc)
    assert "claim ledger clean" in proc.stdout


def test_copied_tree_is_also_clean(paper: Path) -> None:
    """The fixture itself is not the source of any alarm."""
    proc = run(paper)
    assert proc.returncode == EXIT_CLEAN, messages(proc)


def test_open_defects_stay_visible_as_advisory_on_a_green_run(paper: Path) -> None:
    """Known manuscript defects stay visible on a green run rather than vanishing.

    The pristine tree now carries zero open defects, so the advisory channel is
    exercised on a copy with a defect re-injected; the pristine tree must state
    its zero-advisory count honestly.
    """
    proc = run(PAPER)
    assert proc.returncode == EXIT_CLEAN, messages(proc)
    assert "0 advisory" in proc.stdout

    inject_defect(paper)
    proc = run(paper)
    assert proc.returncode == EXIT_CLEAN, messages(proc)
    assert "KNOWN_DEFECT_OPEN" in proc.stdout


# --------------------------------------------------------------------------- #
# Injected defect: a claim removed from the manuscript
# --------------------------------------------------------------------------- #


def test_claim_deleted_from_manuscript_is_caught(paper: Path) -> None:
    target = claim(load_ledger(paper), "P2-I-A01")["sentence"]
    main = paper / "manuscript" / "main.tex"
    source = main.read_text(encoding="utf-8")
    # Delete a current integrated abstract claim by its source spelling.  The
    # checker expands the generated task-count macro before matching it to the
    # ledger sentence, so this mutation intentionally targets the macro form.
    start = source.index(r"A \OfflineTaskCount{}-task controlled")
    end_text = "external screening does not establish superiority."
    end = source.index(end_text, start) + len(end_text)
    main.write_text(source[:start] + source[end:], encoding="utf-8")

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "LEDGER_SENTENCE_MISSING" in messages(proc)
    assert "P2-I-A01" in messages(proc)
    assert target.startswith("A 390-task controlled index")


def test_reworded_claim_is_caught(paper: Path) -> None:
    """A softened verb must not slip through numeric tolerance."""
    main = paper / "manuscript" / "main.tex"
    source = main.read_text(encoding="utf-8")
    main.write_text(
        source.replace(
            "external screening does not establish superiority",
            "external screening does not demonstrate superiority",
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "LEDGER_SENTENCE_MISSING" in messages(proc)


# --------------------------------------------------------------------------- #
# Injected defect: a fabricated artifact path or key
# --------------------------------------------------------------------------- #


def test_fabricated_artifact_path_is_caught(paper: Path) -> None:
    ledger = load_ledger(paper)
    ledger["artifacts"]["results_summary"] = "evidence/offline_results/DOES_NOT_EXIST_V9.json"
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "ARTIFACT_MISSING" in messages(proc)
    assert "DOES_NOT_EXIST_V9.json" in messages(proc)


def test_key_absent_from_artifact_is_caught(paper: Path) -> None:
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-R05")
    entry["numeric_bindings"][0]["key"] = "systems.orion_full.mean_invented_metric"
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "ARTIFACT_KEY_MISSING" in messages(proc)
    assert "mean_invented_metric" in messages(proc)


def test_unparseable_artifact_is_a_violation_not_a_pass(paper: Path) -> None:
    (paper / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json").write_text(
        "{not json", encoding="utf-8"
    )
    proc = run(paper)
    assert proc.returncode != EXIT_CLEAN, messages(proc)


# --------------------------------------------------------------------------- #
# Injected defect: a CONFIRMATORY claim with no support
# --------------------------------------------------------------------------- #


def test_confirmatory_claim_without_support_is_caught(paper: Path) -> None:
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-C03")  # the CANNOT_CHECK external-status row
    entry["strength"] = "CONFIRMATORY"
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "OVERSTATED_STRENGTH" in messages(proc)
    assert "P2-C03" in messages(proc)


def test_unsupported_claim_may_not_be_downgraded_to_descriptive(paper: Path) -> None:
    """The current asserted NONE_YET claim must stay CANNOT_CHECK, not DESCRIPTIVE."""
    ledger = load_ledger(paper)
    claim(ledger, "P2-X25")["strength"] = "DESCRIPTIVE"
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "OVERSTATED_STRENGTH" in messages(proc)


def test_confirmatory_claim_must_name_its_authority(paper: Path) -> None:
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-X01")
    assert entry["strength"] == "CONFIRMATORY", "fixture assumption: X01 is the confirmatory row"
    del entry["confirmatory_authority"]
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "OVERSTATED_STRENGTH" in messages(proc)


# --------------------------------------------------------------------------- #
# Injected defect: a new unledgered claim in a hard-fail region
# --------------------------------------------------------------------------- #


def test_new_unledgered_abstract_claim_is_caught(paper: Path) -> None:
    main = paper / "manuscript" / "main.tex"
    source = main.read_text(encoding="utf-8")
    main.write_text(
        source.replace(
            "\\end{abstract}",
            "ORION outperforms every published deep-research system on real scientific "
            "literature. \\end{abstract}",
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "UNLEDGERED_CLAIM" in messages(proc)
    assert "outperforms" in messages(proc)


def test_new_unledgered_conclusion_claim_is_caught(paper: Path) -> None:
    main = paper / "manuscript" / "main.tex"
    source = main.read_text(encoding="utf-8")
    marker = "\n\\bibliographystyle{plain}\n"
    assert marker in source
    main.write_text(
        source.replace(
            marker,
            "\nThe system achieves a recall of 0.93 on the open web.\n" + marker,
            1,
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "UNLEDGERED_CLAIM" in messages(proc)


def test_unledgered_claim_cannot_be_silenced_by_allowlisting_a_number(paper: Path) -> None:
    """The allowlist must refuse to absorb a numeric result."""
    main = paper / "manuscript" / "main.tex"
    source = main.read_text(encoding="utf-8")
    sentence = "The system achieves a recall of 0.93 on the open web."
    main.write_text(
        source.replace("\\end{abstract}", sentence + " \\end{abstract}"), encoding="utf-8"
    )
    ledger = load_ledger(paper)
    ledger["non_claim_sentences"].append(
        {"region": "abstract", "sentence": sentence, "reason": "not really a claim, honestly"}
    )
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "ILLEGAL_ALLOWLIST" in messages(proc)


def test_unledgered_claim_cannot_be_silenced_by_allowlisting_a_comparative(paper: Path) -> None:
    main = paper / "manuscript" / "main.tex"
    source = main.read_text(encoding="utf-8")
    sentence = "ORION is superior to every dense retriever we tested."
    main.write_text(
        source.replace("\\end{abstract}", sentence + " \\end{abstract}"), encoding="utf-8"
    )
    ledger = load_ledger(paper)
    ledger["non_claim_sentences"].append(
        {"region": "abstract", "sentence": sentence, "reason": "framing"}
    )
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "ILLEGAL_ALLOWLIST" in messages(proc)


def test_allowlist_entry_without_reason_is_caught(paper: Path) -> None:
    ledger = load_ledger(paper)
    ledger["non_claim_sentences"][0]["reason"] = ""
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "MISSING_REASON" in messages(proc)


# --------------------------------------------------------------------------- #
# Numeric binding: the manuscript must agree with its own evidence
# --------------------------------------------------------------------------- #


def test_manuscript_number_diverging_from_artifact_is_caught(paper: Path) -> None:
    """A number edited in the prose but not in the archive is the core defect."""
    results = region_file(paper)
    source = results.read_text(encoding="utf-8")
    assert "The governed system attains mean complete-gold recall 0.979487" in source
    results.write_text(
        source.replace(
            "The governed system attains mean complete-gold recall 0.979487",
            "The governed system attains mean complete-gold recall 0.999999",
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "NUMERIC_MISMATCH" in messages(proc)
    assert "0.999999" in messages(proc)


def test_sign_flip_is_caught(paper: Path) -> None:
    """-1.0 and 1.0 must not be treated as the same value."""
    results = region_file(paper)
    source = results.read_text(encoding="utf-8")
    assert "premature-closure difference of -1.0" in source
    results.write_text(
        source.replace(
            "premature-closure difference of -1.0", "premature-closure difference of 1.0"
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "NUMERIC_MISMATCH" in messages(proc)


def test_unbound_number_is_caught(paper: Path) -> None:
    """Every number in a ledgered sentence must be bound to an artifact key."""
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-R05")
    entry["numeric_bindings"] = entry["numeric_bindings"][:1]
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "SLOT_COUNT_MISMATCH" in messages(proc)


def test_number_added_to_a_ledgered_sentence_is_caught(paper: Path) -> None:
    """A new number in the prose must not slip past the ledger."""
    results = region_file(paper)
    source = results.read_text(encoding="utf-8")
    assert "Its premature-task-closure rate is\n0." in source
    results.write_text(
        source.replace(
            "Its premature-task-closure rate is\n0.",
            "Its premature-task-closure rate is\n0 over 20 tasks.",
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "LEDGER_SENTENCE_MISSING" in messages(proc)


def test_ledger_number_rotting_away_from_the_manuscript_is_caught(paper: Path) -> None:
    """If prose and archive move together but the ledger does not, the ledger fails."""
    summary_path = paper / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["systems"]["orion_full"]["mean_precision"] = 0.97
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    results = region_file(paper)
    results.write_text(
        results.read_text(encoding="utf-8").replace(
            "recall 0.979487 and precision 1.0.", "recall 0.979487 and precision 0.97."
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "LEDGER_STALE_NUMBER" in messages(proc)


def test_role_swap_is_caught_by_positional_binding(paper: Path) -> None:
    """Same numbers, swapped systems: unordered matching would pass this."""
    results = region_file(paper)
    source = results.read_text(encoding="utf-8")
    results.write_text(
        source.replace(
            "requires 385 tasks, which the assembled \\OfflineTaskCount{} tasks reach",
            "requires 390 tasks, which the assembled 385 tasks reach",
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "NUMERIC_MISMATCH" in messages(proc)


def test_coordinated_regeneration_stays_green(paper: Path) -> None:
    """A legitimate re-run that moves a number in BOTH prose and archive is clean.

    This is what protects the ledger from going red every time the offline world
    is regenerated: the ledger binds meaning, not digits.
    """
    summary_path = paper / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["systems"]["orion_full"]["mean_complete_gold_recall"] = 0.981111
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    for path, old, new in (
        (paper / "manuscript" / "main.tex", "mean recall 0.979487", "mean recall 0.981111"),
        (region_file(paper), "complete-gold recall 0.979487", "complete-gold recall 0.981111"),
    ):
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    ledger = load_ledger(paper)
    for claim_id in ("P2-C01", "P2-R05"):
        entry = claim(ledger, claim_id)
        entry["sentence"] = entry["sentence"].replace("0.979487", "0.981111")
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_CLEAN, messages(proc)


def test_declared_scale_is_required_not_inferred(paper: Path) -> None:
    """Removing the declared percentage scale must fail rather than auto-adapt."""
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-R14")
    scaled = [b for b in entry["numeric_bindings"] if b.get("scale")]
    assert scaled, "fixture assumption: R14 carries a scaled binding"
    for binding in scaled:
        del binding["scale"]
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "NUMERIC_MISMATCH" in messages(proc)


# --------------------------------------------------------------------------- #
# Cross-artifact agreement and schema integrity
# --------------------------------------------------------------------------- #


def test_task_count_disagreement_is_caught(paper: Path) -> None:
    """The world and the results summary must describe the same suite."""
    manifest_path = paper / "evidence" / "offline_gold" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["task_count"] = 120
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "TASK_COUNT_DISAGREEMENT" in messages(proc)


def test_duplicate_claim_id_is_caught(paper: Path) -> None:
    ledger = load_ledger(paper)
    ledger["claims"].append(dict(claim(ledger, "P2-C01")))
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "DUPLICATE_CLAIM_ID" in messages(proc)


def test_invalid_support_type_is_caught(paper: Path) -> None:
    ledger = load_ledger(paper)
    claim(ledger, "P2-C01")["support_type"] = "PROBABLY_FINE"
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "BAD_SUPPORT_TYPE" in messages(proc)


def test_archived_only_row_must_give_a_reason(paper: Path) -> None:
    ledger = load_ledger(paper)
    # X01 is ASSERTED in the committed ledger; demote it to archived-only with
    # an empty reason to exercise the reason requirement.
    entry = claim(ledger, "P2-X01")
    entry["manuscript_status"] = "NOT_ASSERTED_ARCHIVED_ONLY"
    entry["not_asserted_reason"] = ""
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "MISSING_REASON" in messages(proc)


def test_archived_only_row_asserted_in_manuscript_must_be_promoted(paper: Path) -> None:
    """If the text starts asserting an archived-only row, the ledger must say so."""
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-X01")
    entry["manuscript_status"] = "NOT_ASSERTED_ARCHIVED_ONLY"
    entry["not_asserted_reason"] = "not yet reported in the manuscript"
    save_ledger(paper, ledger)
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "STALE_NOT_ASSERTED" in messages(proc)


# --------------------------------------------------------------------------- #
# Known defects: recorded, visible, and enforceable
# --------------------------------------------------------------------------- #


def test_strict_mode_promotes_known_defects_to_violations(paper: Path) -> None:
    inject_defect(paper)
    proc = run(paper, "--strict")
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "KNOWN_DEFECT" in messages(proc)


def test_defect_entry_becomes_stale_once_the_manuscript_is_fixed(paper: Path) -> None:
    """A fixed manuscript must force the defect entry to be retired."""
    inject_defect(paper)
    results = region_file(paper)
    source = results.read_text(encoding="utf-8")
    start = source.index("Its premature-task-closure rate is")
    end = source.index("The strongest of the six protocol-frozen")
    results.write_text(source[:start] + source[end:], encoding="utf-8")
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "STALE_DEFECT_ENTRY" in messages(proc)


def test_defect_entry_needs_a_provable_contradiction(paper: Path) -> None:
    inject_defect(paper)
    ledger = load_ledger(paper)
    ledger["known_defects"][0]["contradicted_by"]["key"] = "coverage.invented_field"
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "ARTIFACT_KEY_MISSING" in messages(proc)


def test_defect_entry_may_not_park_an_overclaim(paper: Path) -> None:
    """A known-defect entry suppresses the unledgered scan, so it must never
    be usable to record a comparative-superiority claim as a tolerated issue."""
    sentence = "ORION outperforms every published deep-research baseline on the open web."
    main = paper / "manuscript" / "main.tex"
    main.write_text(
        main.read_text(encoding="utf-8").replace(
            "\\end{abstract}", sentence + " \\end{abstract}"
        ),
        encoding="utf-8",
    )
    ledger = load_ledger(paper)
    ledger["known_defects"].append(
        {
            "defect_id": "P2-DXX",
            "region": "abstract",
            "sentence": sentence,
            "contradicted_by": {"artifact": "results_summary", "key": "analysis_authority"},
            "owner": "someone else",
            "required_fix": "will get to it",
        }
    )
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "ILLEGAL_DEFECT" in messages(proc)


def test_defect_entry_needs_an_owner_and_a_fix(paper: Path) -> None:
    inject_defect(paper)
    ledger = load_ledger(paper)
    ledger["known_defects"][0]["required_fix"] = ""
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "DEFECT_INCOMPLETE" in messages(proc)


# --------------------------------------------------------------------------- #
# "Could not check" is never reported as "checked and fine"
# --------------------------------------------------------------------------- #


def test_missing_ledger_is_a_harness_error(tmp_path: Path) -> None:
    proc = run(tmp_path / "no-such-paper")
    assert proc.returncode == EXIT_HARNESS, messages(proc)
    assert "HARNESS ERROR" in proc.stderr
    assert "not a pass" in proc.stderr


def test_unparseable_ledger_is_a_harness_error(paper: Path) -> None:
    (paper / LEDGER_RELATIVE).write_text("{oops", encoding="utf-8")
    proc = run(paper)
    assert proc.returncode == EXIT_HARNESS, messages(proc)


def test_missing_manuscript_region_is_a_harness_error(paper: Path) -> None:
    main = paper / "manuscript" / "main.tex"
    source = main.read_text(encoding="utf-8")
    main.write_text(source.replace("\\section{Conclusion}", "\\section{Wrap up}"), encoding="utf-8")
    proc = run(paper)
    assert proc.returncode == EXIT_HARNESS, messages(proc)
    assert "Conclusion" in proc.stderr


def test_missing_manuscript_file_is_a_harness_error(paper: Path) -> None:
    region_file(paper).unlink()
    proc = run(paper)
    assert proc.returncode == EXIT_HARNESS, messages(proc)


# --------------------------------------------------------------------------- #
# Ledger coverage of the surfaces that matter
# --------------------------------------------------------------------------- #


def test_new_unledgered_results_claim_is_caught(paper: Path) -> None:
    """Results prose is hard-failing: a new outcome sentence there must not pass."""
    results = region_file(paper)
    results.write_text(
        results.read_text(encoding="utf-8")
        + "\nORION reaches a recall of 0.99 on real scientific literature.\n",
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "UNLEDGERED_CLAIM" in messages(proc)


def test_drift_failure_names_the_current_manuscript_text(paper: Path) -> None:
    """A drift failure must be reviewable without a manual sweep of the region."""
    main = paper / "manuscript" / "main.tex"
    main.write_text(
        main.read_text(encoding="utf-8").replace(
            "external screening does not establish superiority.",
            "external screening does not demonstrate superiority.",
        ),
        encoding="utf-8",
    )
    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "LEDGER_SENTENCE_MISSING" in messages(proc)
    assert "manuscript:" in messages(proc)
    assert "does not demonstrate superiority" in messages(proc)


def test_sentence_matching_only_as_a_substring_is_refused(paper: Path) -> None:
    """A hand-trimmed ledger sentence must not silently disable the numeric check."""
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-R05")
    entry["sentence"] = entry["sentence"].rstrip(".").split(" and precision")[0]
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "SENTENCE_NOT_ISOLABLE" in messages(proc)


def test_named_list_selector_must_resolve_uniquely(paper: Path) -> None:
    """The tier binding is addressed by name; a wrong name must fail, not fall back."""
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-R03")
    binding = entry["numeric_bindings"][0]
    assert "[tier=" in binding["key"], "fixture assumption: R03 uses a named selector"
    binding["key"] = "precision_plan.precision_tiers.[tier=TIER_Z_nonexistent].required_n"
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "ARTIFACT_KEY_MISSING" in messages(proc)


def test_tier_binding_points_at_the_tier_the_prose_names() -> None:
    """The internal binding names a real plan tier without leaking it into prose."""
    plan = json.loads(
        (PAPER / "protocol" / "STATISTICAL_PLAN_V1.json").read_text(encoding="utf-8")
    )
    tiers = {t["tier"]: t for t in plan["precision_plan"]["precision_tiers"]}
    ledger = json.loads((PAPER / LEDGER_RELATIVE).read_text(encoding="utf-8"))
    bound = {
        binding["key"]
        for entry in ledger["claims"]
        for binding in entry.get("numeric_bindings", [])
        if "precision_tiers" in binding["key"]
    }
    assert bound, "expected at least one tier binding"
    named = [name for name in tiers if any(f"[tier={name}]" in key for key in bound)]
    assert named, "tier bindings must address a tier in the frozen plan"
    for key in bound:
        assert any(f"[tier={name}]" in key for name in named), (
            f"binding {key} does not address a frozen plan tier ({named})"
        )

    evidence = json.loads(
        (PAPER / "evidence" / "offline_results" / "OFFLINE_MECHANISMS_V1.json").read_text(
            encoding="utf-8"
        )
    )
    for name in named:
        assert evidence["n_tasks"] >= tiers[name]["required_n"], (
            f"prose names {name} (required_n={tiers[name]['required_n']}) but the "
            f"archived offline world has only n={evidence['n_tasks']} tasks"
        )


def test_every_hard_fail_region_has_at_least_one_claim() -> None:
    ledger = json.loads((PAPER / LEDGER_RELATIVE).read_text(encoding="utf-8"))
    hard = {
        name for name, spec in ledger["regions"].items() if spec.get("hard_fail_unledgered")
    }
    assert hard, "at least one region must be hard-failing"
    covered = {entry["region"] for entry in ledger["claims"]}
    assert hard <= covered, f"hard-fail regions without claims: {hard - covered}"


def test_no_claim_is_confirmatory_on_offline_mechanism_support() -> None:
    """The offline campaign is DESCRIPTIVE_ONLY; nothing from it may be confirmatory."""
    ledger = json.loads((PAPER / LEDGER_RELATIVE).read_text(encoding="utf-8"))
    offenders = [
        entry["claim_id"]
        for entry in ledger["claims"]
        if entry["support_type"] == "OFFLINE_MECHANISM" and entry["strength"] == "CONFIRMATORY"
    ]
    assert not offenders, f"offline support cannot be confirmatory: {offenders}"


# --------------------------------------------------------------------------- #
# Generated-macro resolution
#
# The manuscript splices suite facts in as macros (``\OfflineTaskCount{}``) so
# prose cannot hardcode a count.  Before the checker resolved them, the generic
# command strip deleted the invocation silently and the abstract read "a frozen
# -task index" -- a claim quietly lost a number and the ledger still matched.
# That silent deletion is what drifted this ledger red, so each property the
# resolver relies on gets an injected-defect test of its own.
# --------------------------------------------------------------------------- #


def test_undeclared_value_macro_is_caught(paper: Path) -> None:
    """An unresolved ``\\Name{}`` must fail loudly instead of vanishing from prose."""
    main = paper / "manuscript" / "main.tex"
    source = main.read_text(encoding="utf-8")
    assert "\\OfflineTaskCount{}-task" in source
    main.write_text(
        source.replace("\\OfflineTaskCount{}-task", "\\FabricatedCount{}-task", 1),
        encoding="utf-8",
    )

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "UNRESOLVED_MACRO" in messages(proc)
    assert "FabricatedCount" in messages(proc)


def test_dropping_macro_sources_cannot_silence_the_resolver(paper: Path) -> None:
    """Un-declaring the macro file must fail, not restore the old silent strip."""
    ledger = load_ledger(paper)
    assert ledger.get("macro_sources"), "committed ledger must declare its macro sources"
    del ledger["macro_sources"]
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "UNRESOLVED_MACRO" in messages(proc)


def test_generated_macro_value_must_agree_with_the_archive(paper: Path) -> None:
    """Macro resolution transitively verifies the generated file against evidence.

    Editing the rendered suite fact -- without touching prose or the ledger --
    must be caught, otherwise the macro layer would be a hole through which a
    number could reach the page without ever meeting its artifact.
    """
    facts = paper / "manuscript" / "generated" / "suite_facts.tex"
    source = facts.read_text(encoding="utf-8")
    assert "{\\OfflineTaskCount}{390}" in source
    facts.write_text(
        source.replace("{\\OfflineTaskCount}{390}", "{\\OfflineTaskCount}{391}"),
        encoding="utf-8",
    )

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "LEDGER_STALE_NUMBER" in messages(proc) or "NUMERIC_MISMATCH" in messages(proc)


def test_missing_macro_source_is_a_harness_error_not_a_clean_run(paper: Path) -> None:
    """A macro file that cannot be read is 'could not check', never 'checked and fine'."""
    (paper / "manuscript" / "generated" / "suite_facts.tex").unlink()

    proc = run(paper)
    assert proc.returncode == EXIT_HARNESS, messages(proc)
    assert "declared macro source missing" in messages(proc)


# --------------------------------------------------------------------------- #
# SHA-256 digest binding
#
# Numeric slots deliberately skip hex digests so ``SHA-256`` and a 64-char hash
# do not inflate the slot count.  That exclusion used to let a stale record
# digest ride in both the ledger sentence and the manuscript while the
# support_artifacts key merely *existed*.  DIGEST_MISMATCH is the class that
# exclusion would otherwise skip.
# --------------------------------------------------------------------------- #


def test_stale_record_digest_is_caught(paper: Path) -> None:
    """A SHA-256 in the sentence that is not the archived digest must fail."""
    results = paper / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
    payload = json.loads(results.read_text(encoding="utf-8"))
    current = payload["frozen_run"]["record_digest_sha256"]
    fake = "a" * 64
    assert current != fake
    results_tex = region_file(paper)
    source = results_tex.read_text(encoding="utf-8")
    assert current in source
    results_tex.write_text(source.replace(current, fake, 1), encoding="utf-8")
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-R04")
    entry["sentence"] = entry["sentence"].replace(current, fake, 1)
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "DIGEST_MISMATCH" in messages(proc)


def test_missing_bound_digest_is_caught(paper: Path) -> None:
    """Dropping the archived digest from the sentence must fail even if numbers match."""
    results = paper / "evidence" / "offline_results" / "RESULTS_SUMMARY_V1.json"
    current = json.loads(results.read_text(encoding="utf-8"))["frozen_run"][
        "record_digest_sha256"
    ]
    results_tex = region_file(paper)
    source = results_tex.read_text(encoding="utf-8")
    results_tex.write_text(source.replace(current, "not-a-digest", 1), encoding="utf-8")
    ledger = load_ledger(paper)
    entry = claim(ledger, "P2-R04")
    entry["sentence"] = entry["sentence"].replace(current, "not-a-digest", 1)
    save_ledger(paper, ledger)

    proc = run(paper)
    assert proc.returncode == EXIT_VIOLATIONS, messages(proc)
    assert "DIGEST_MISMATCH" in messages(proc)
