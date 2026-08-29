#!/usr/bin/env python3
"""Re-run each cited receipt's generator and compare it to the committed artifact.

`JOURNAL_READINESS.md` leaves "independently replay every headline receipt on the
submission commit" (ORION-06) and "independent replay of the selected QG receipt
set" (ORION-09) open. A receipt whose generator has never been re-run since the
bytes were committed is a claim about a computation nobody has repeated.

Comparison is on canonicalised JSON -- `sort_keys=True`, tight separators -- so
that indentation and key order, which carry no meaning, cannot mask or fabricate
a difference. Committed artifacts here are written with `indent=2` while several
generators print compact JSON to stdout; without canonicalisation every receipt
would report a spurious mismatch.

**The canonical form is this script's own choice.** The ORION-08 replay harness
this was to be modelled on is not in the tree at the path it was cited from
(`papers/orion-08-typed-state/submission/independent-replay-v1/`), nor anywhere
under `origin/main`, nor on any remote branch. The three fixes it is credited
with are honoured below; the serialisation is not a match to an existing
artifact, so a future cross-paper comparison needs the two reconciled rather than
assumed identical.

**Provenance policy, fixed before any receipt was run.** Some receipt fields
cannot reproduce across runs or hosts -- a timestamp, a commit sha, a temporary
path. Those are excluded by *name*, from the list below, and the names actually
found in each receipt are reported. The alternative -- dropping whichever keys
happen to differ -- would let any mismatch be explained away after the fact, and
a receipt that matches only once a post-hoc exclusion is applied has not been
replayed. Anything that still differs is reported as a difference. If a
generator turns out to be non-deterministic beyond provenance, that is
CANNOT_CHECK with the reason, not a near-miss.

Three fixes carried over from the harness this follows:

* `.git` is a *file*, not a directory, inside a git worktree, so the repository
  root is located with `os.path.exists`.
* Several generators write their artifact to an output flag and print only a
  summary, so reading stdout for those yields a false CANNOT_CHECK. Each target
  declares how its bytes are captured.
* Extra keys present in the committed artifact are reported as
  `committed_only_keys` rather than quietly accepted as provenance.

Exit codes: ``0`` every target replayed and matched, ``1`` at least one
difference, ``3`` at least one target could not be checked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

#: Excluded by name at any depth. Fixed before the first run; see the docstring.
NON_REPRODUCIBLE_KEYS = frozenset({
    "generated_at", "generated_on", "created_at", "run_at", "timestamp", "date",
    "commit", "git_commit", "subject_commit", "head_commit", "revision",
    "host", "hostname", "user", "username",
    "python_version", "platform", "interpreter",
    "duration_s", "elapsed_s", "runtime_s", "wall_clock_s", "cpu_seconds",
    "output_path", "tmpdir", "root",
})

# receipt_id, committed artifact, generator, argv template, capture mode
TARGETS = {
    "orion-06": (
        ("negative_coverage_result",
         "papers/orion-06-recursive-recovery/revival/ORION06_NEGATIVE_COVERAGE_RESULT.json",
         "papers/orion-06-recursive-recovery/revival/verify_orion06_negative_coverage.py",
         ["--root", "{repo}", "--output", "{out}"], "output_flag"),
        ("negative_revival_r1_successor",
         "papers/orion-06-recursive-recovery/revival/ORION06_NEGATIVE_REVIVAL_R1_SUCCESSOR.json",
         "papers/orion-06-recursive-recovery/revival/verify_orion06_negative_revival_successor.py",
         ["--root", "{repo}"], "stdout"),
    ),
    "orion-09": (
        ("size_transfer_invariant_result",
         "papers/orion-09-compilation-regime-geometry/size-transfer-invariant-v1/RESULT_V1.json",
         "papers/orion-09-compilation-regime-geometry/size-transfer-invariant-v1/check_size_transfer_invariant.py",
         [], "stdout"),
        ("size_transfer_invariant_theory_result",
         "papers/orion-09-compilation-regime-geometry/theory/size-transfer-invariant-v1/RESULT_V1.json",
         "papers/orion-09-compilation-regime-geometry/theory/size-transfer-invariant-v1/check_size_transfer_invariant.py",
         [], "stdout"),
    ),
}


def find_repo_root(start: Path) -> Path:
    """Walk up to the checkout root.

    `.git` is a *file* inside a worktree and a directory in a normal clone, so
    the test is existence. `is_dir()` here silently walks past the root of every
    worktree and lands on the filesystem root.
    """
    current = start.resolve()
    for candidate in (current, *current.parents):
        if os.path.exists(candidate / ".git"):
            return candidate
    raise SystemExit(f"CANNOT_CHECK: no repository root above {start}")


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def strip_provenance(value: object, found: set[str]) -> object:
    """Drop non-reproducible keys at any depth, recording which were present."""
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if key in NON_REPRODUCIBLE_KEYS:
                found.add(key)
                continue
            out[key] = strip_provenance(item, found)
        return out
    if isinstance(value, list):
        return [strip_provenance(item, found) for item in value]
    return value


def first_json_object(text: str) -> object:
    """Parse the first complete JSON value in stdout, ignoring any preamble.

    Generators print warnings (a deprecation notice, a progress line) before the
    payload often enough that `json.loads(stdout)` is not safe.
    """
    start = min((i for i in (text.find("{"), text.find("[")) if i != -1), default=-1)
    if start == -1:
        raise ValueError("no JSON value in stdout")
    decoder = json.JSONDecoder()
    return decoder.raw_decode(text[start:])[0]


def replay_one(repo: Path, target: tuple, python: str) -> dict:
    receipt_id, committed_rel, generator_rel, argv_template, capture = target
    record: dict[str, object] = {
        "receipt_id": receipt_id,
        "committed_artifact": committed_rel,
        "generator": generator_rel,
        "capture": capture,
    }
    committed_path = repo / committed_rel
    generator_path = repo / generator_rel
    if not committed_path.is_file():
        return {**record, "outcome": "CANNOT_CHECK",
                "reason": f"committed artifact absent: {committed_rel}"}
    if not generator_path.is_file():
        return {**record, "outcome": "CANNOT_CHECK",
                "reason": f"generator absent: {generator_rel}"}

    record["committed_sha256"] = hashlib.sha256(committed_path.read_bytes()).hexdigest()
    try:
        committed = json.loads(committed_path.read_text(encoding="utf-8"))
    except ValueError as error:
        return {**record, "outcome": "CANNOT_CHECK",
                "reason": f"committed artifact is not JSON: {error}"}

    with tempfile.TemporaryDirectory() as work:
        out_path = Path(work) / "replay.json"
        argv = [python, str(generator_path)] + [
            item.format(repo=str(repo), out=str(out_path)) for item in argv_template]
        record["argv"] = " ".join(argv[1:])
        try:
            completed = subprocess.run(argv, cwd=repo, capture_output=True,
                                       text=True, timeout=900)
        except (OSError, subprocess.TimeoutExpired) as error:
            return {**record, "outcome": "CANNOT_CHECK",
                    "reason": f"generator did not run: {error}"}
        record["generator_exit_code"] = completed.returncode
        try:
            if capture == "output_flag":
                if not out_path.is_file():
                    return {**record, "outcome": "CANNOT_CHECK",
                            "reason": "generator wrote no file to its output flag",
                            "stderr_tail": completed.stderr[-400:]}
                replayed = json.loads(out_path.read_text(encoding="utf-8"))
            else:
                replayed = first_json_object(completed.stdout)
        except ValueError as error:
            return {**record, "outcome": "CANNOT_CHECK",
                    "reason": f"replay output is not JSON: {error}",
                    "stderr_tail": completed.stderr[-400:]}

    excluded: set[str] = set()
    left = strip_provenance(committed, excluded)
    right = strip_provenance(replayed, excluded)
    record["provenance_keys_excluded"] = sorted(excluded)
    # An exclusion that changes the verdict is worth knowing about: a receipt
    # matching only because a key was dropped has not really been replayed. Where
    # both sides agree on an excluded key anyway, the exclusion did no work and
    # the match is unconditional. Recorded per key rather than asserted.
    agreed, disagreed = [], []
    if isinstance(committed, dict) and isinstance(replayed, dict):
        for key in sorted(excluded):
            if key in committed or key in replayed:
                target = agreed if committed.get(key) == replayed.get(key) else disagreed
                target.append(key)
    record["excluded_keys_that_agreed_anyway"] = agreed
    record["excluded_keys_that_actually_differed"] = disagreed
    record["match_depends_on_exclusion"] = bool(disagreed)
    if isinstance(committed, dict) and isinstance(replayed, dict):
        record["committed_only_keys"] = sorted(set(committed) - set(replayed))
        record["replay_only_keys"] = sorted(set(replayed) - set(committed))
        record["compared_keys"] = sorted(set(left) & set(right)) if isinstance(left, dict) else []
    match = canonical(left) == canonical(right)
    record["outcome"] = "MATCH" if match else "DIFFERS"
    if not match:
        record["differing_top_level_keys"] = sorted(
            key for key in set(left) | set(right)
            if canonical(left.get(key)) != canonical(right.get(key))
        ) if isinstance(left, dict) and isinstance(right, dict) else ["<not an object>"]
    return record


#: ORION-06's gate list also asks to "regenerate/verify RECEIPT_INDEX.md against
#: the final manuscript claim set". That is two obligations. The digest half --
#: does every indexed receipt exist, and does its recorded sha256 prefix still
#: describe the committed bytes -- is checkable here. The claim-set half is not:
#: it needs a mapping from index entries to the claims the manuscript makes, and
#: no such mapping is committed. Only the first is reported, and it is reported
#: as index integrity rather than as the gate.
RECEIPT_INDEX = "papers/orion-06-recursive-recovery/RECEIPT_INDEX.md"
RECEIPT_ROOT = "research/extensions/orion-q"


def verify_receipt_index(repo: Path) -> dict:
    index_path = repo / RECEIPT_INDEX
    if not index_path.is_file():
        return {"outcome": "CANNOT_CHECK", "reason": f"absent: {RECEIPT_INDEX}"}
    rows, missing, mismatched, matched = [], [], [], []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not cells[2].startswith("`"):
            continue
        name = cells[0].strip("`")
        prefix = cells[2].strip("`")
        if len(prefix) != 16:
            continue
        rows.append(name)
        target = repo / RECEIPT_ROOT / name
        if not target.is_file():
            missing.append(name)
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()[:16]
        (matched if actual == prefix else mismatched).append(name)
    return {
        "outcome": ("CANNOT_CHECK" if not rows
                    else "MATCH" if not (missing or mismatched) else "DIFFERS"),
        "index": RECEIPT_INDEX,
        "receipt_root": RECEIPT_ROOT,
        "entries_parsed": len(rows),
        "digest_matches": len(matched),
        "missing_receipts": missing,
        "digest_mismatches": mismatched,
        "claim_set_correspondence": "CANNOT_CHECK",
        "claim_set_reason": ("no committed mapping from index entries to manuscript "
                             "claims; index integrity does not establish it"),
    }


def tracked_digests(repo: Path, paths: list[str]) -> dict[str, str]:
    out = {}
    for rel in paths:
        target = repo / rel
        if target.is_file():
            out[rel] = hashlib.sha256(target.read_bytes()).hexdigest()
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", choices=sorted(TARGETS), required=True)
    parser.add_argument("--out", type=Path, help="write the receipt here")
    arguments = parser.parse_args(argv)

    repo = find_repo_root(Path(__file__).parent)
    targets = TARGETS[arguments.paper]

    # A generator that writes into the tree would corrupt the very bytes under
    # test. Digest every committed artifact first and re-check afterwards.
    watched = [t[1] for t in targets]
    before = tracked_digests(repo, watched)

    results = [replay_one(repo, target, sys.executable) for target in targets]

    after = tracked_digests(repo, watched)
    mutated = sorted(k for k in before if before.get(k) != after.get(k))

    outcomes = [r["outcome"] for r in results]
    report = {
        "schema_version": "orion.independent-replay-receipt.v1",
        "paper": arguments.paper,
        "claim_scope": ("Records whether each cited receipt's generator reproduces its "
                        "committed artifact. Not a readiness verdict and not scientific "
                        "authority; a replayed receipt is attributable, not thereby valid."),
        "grants_authority": "NONE",
        "canonicalisation": "json.dumps(sort_keys=True, separators=(',',':'), ensure_ascii=False)",
        "non_reproducible_keys_policy": sorted(NON_REPRODUCIBLE_KEYS),
        "targets": len(results),
        "matched": outcomes.count("MATCH"),
        "differed": outcomes.count("DIFFERS"),
        "cannot_check": outcomes.count("CANNOT_CHECK"),
        "committed_artifacts_mutated_by_replay": mutated,
        "results": results,
    }
    if arguments.paper == "orion-06":
        report["receipt_index_integrity"] = verify_receipt_index(repo)
    if arguments.out:
        arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
    print(f"{arguments.paper}: {report['matched']}/{report['targets']} matched, "
          f"{report['differed']} differed, {report['cannot_check']} CANNOT_CHECK")
    for item in results:
        print(f"  {item['outcome']:<12} {item['receipt_id']}"
              + (f"  ({item['reason']})" if item.get("reason") else "")
              + (f"  differing={item['differing_top_level_keys']}"
                 if item.get("differing_top_level_keys") else ""))
    if mutated:
        print(f"  WARNING: replay mutated committed artifacts: {mutated}")
        return 1
    if report["cannot_check"]:
        return 3
    return 1 if report["differed"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
