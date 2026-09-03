#!/usr/bin/env python3
"""Fail-closed verifier for A4_INTERVENTION_PREREG_V1.json.

Live-verifies, against the pinned substrate commit and the committed lane
files, exactly the facts the prereg freezes:

  1. every execution flag is false;
  2. the DRAFT-DECISION-1 rounds-cap citations exist in the pinned gym code
     (test_executor.py:1745 max_rounds = 50; the config.py MAX_ITERATIONS=25
     MCP cap recorded as a different constant);
  3. the shipped proxy base URL the prereg forbids is present in the pinned
     config (the ban is meaningful only if the hazard exists);
  4. the dataset census the prereg cites (solution_steps 53/83 multi, 0/48
     single; tool_expected 131/131; NO domain_knowledge key anywhere);
  5. the transforms script implements the frozen transforms and its
     round-trip identity holds over EVERY dataset record;
  6. bound repo files still carry their frozen git blob SHAs.

This checker never upgrades a CANNOT_CHECK/vacuity terminal and never
executes a model call.

Usage:
  check_a4_intervention_prereg_v1.py --self-test \
      --prereg A4_INTERVENTION_PREREG_V1.json
  check_a4_intervention_prereg_v1.py --prereg A4_INTERVENTION_PREREG_V1.json \
      --gym-dir /tmp/a4gym --multi /tmp/multi.json --single /tmp/single.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Optional

REQUIRED_FLAGS_FALSE = [
    "protected_agent_runs_executed",
    "protected_outcomes_accessed",
    "development_partition_runs_executed",
    "intervention_study_executed",
    "candidate_policy_calibrated",
    "results_exist",
]

EXPECTED_SOLUTION_STEPS = {"multi": 53, "single": 0}
EXPECTED_TOOL_EXPECTED = 131


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def load_transforms(prereg_dir: Path):
    spec = importlib.util.spec_from_file_location(
        "a4_ivt", prereg_dir / "a4_intervention_transforms_v1.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def line_of(text: str, n: int) -> str:
    lines = text.splitlines()
    return lines[n - 1] if 0 < n <= len(lines) else ""


def verify(
    prereg: dict,
    prereg_dir: Path,
    gym_dir: Optional[Path],
    multi: Optional[list],
    single: Optional[list],
) -> dict:
    errors: list[str] = []

    # 1. flags
    for flag in REQUIRED_FLAGS_FALSE:
        if prereg["flags"].get(flag) is not False:
            errors.append(f"execution flag not false: {flag}")

    # 2. DRAFT-DECISION-1 citations against the pinned gym code
    te = (gym_dir / "test_executor.py").read_text() if gym_dir else ""
    cfg = (gym_dir / "config.py").read_text() if gym_dir else ""
    if gym_dir:
        if "max_rounds = 50" not in line_of(te, 1745):
            errors.append("test_executor.py:1745 no longer carries max_rounds = 50 (DRAFT-DECISION-1 citation broken)")
        if "max_rounds: int = 50" not in line_of(te, 809):
            errors.append("test_executor.py:809 simple_test_query default changed")
        if "max_rounds: int = 50" not in line_of(te, 1063):
            errors.append("test_executor.py:1063 simple_test_refine_query default changed")
        if "MAX_ITERATIONS = 25" not in line_of(cfg, 169):
            errors.append("config.py:169 MAX_ITERATIONS = 25 anti-confusion record broken")
        # 3. the forbidden proxy hazard must still be the documented one
        if "35.220.164.252:3888/v1" not in cfg:
            errors.append("shipped proxy base URL not found in pinned config (ban citation broken)")
        if "REACT_TOOL_SYSTEM_PROMPT" not in (gym_dir / "agent.py").read_text():
            errors.append("agent.py no longer defines REACT_TOOL_SYSTEM_PROMPT")

    # 4. dataset census
    if multi is not None and single is not None:
        for name, recs in (("multi", multi), ("single", single)):
            n = sum(1 for r in recs if (r.get("metadata") or {}).get("solution_steps"))
            if n != EXPECTED_SOLUTION_STEPS[name]:
                errors.append(f"{name} solution_steps census {n} != frozen {EXPECTED_SOLUTION_STEPS[name]}")
        if len(multi) + len(single) != 131:
            errors.append("base record count != 131")
        if sum(1 for r in list(multi) + list(single) if (r.get("metadata") or {}).get("tool_expected")) != EXPECTED_TOOL_EXPECTED:
            errors.append("tool_expected census != 131/131")
        mkeys = set()
        for r in multi + single:
            mkeys |= set((r.get("metadata") or {}).keys())
        if "domain_knowledge" in mkeys:
            errors.append("domain_knowledge key appeared in substrate (DRAFT-DECISION-2 finding stale)")

        # 5. transforms round-trip over every record
        ivt = load_transforms(prereg_dir)
        for name, recs in (("multi", multi), ("single", single)):
            for rec in recs:
                ab = ivt.accessibility_block(rec)
                if ab is None:
                    errors.append(f"{name}:{rec.get('id')} accessibility vacuous")
                    continue
                if ivt.accessibility_protocol_roundtrip(ab) != rec["usage_tool_protocol"]:
                    errors.append(f"{name}:{rec.get('id')} protocol round-trip mismatch")
                    break
                ib = ivt.information_block(rec)
                if ib is not None and ivt.information_roundtrip(ib) != rec["metadata"]["solution_steps"]:
                    errors.append(f"{name}:{rec.get('id')} information round-trip mismatch")
                    break

    # 6. bound repo blob SHAs (prereg_dir = <root>/papers/publication_closure/<dir>)
    repo_root = (prereg_dir / "../../..").resolve()
    for key, b in prereg["bindings"].items():
        sha = b.get("git_blob_sha")
        if not sha:
            continue
        p = repo_root / b["path"]
        if not p.exists():
            errors.append(f"bound blob file missing: {b['path']}")
            continue
        if git_blob_sha(p.read_bytes()) != sha:
            errors.append(f"bound blob sha mismatch: {b['path']}")

    # structural: decisions resolved with grounding; terminals present
    grounding_keys = ("citations", "grounding", "inventory", "chosen_mechanism", "decision")
    for d in ("DRAFT-DECISION-1_rounds_cap", "DRAFT-DECISION-2_base_prompt_inventory_and_information_item", "DRAFT-DECISION-3_accessibility_transform"):
        node = prereg["draft_decisions_resolved"].get(d)
        if not isinstance(node, dict) or not any(node.get(k) for k in grounding_keys):
            errors.append(f"draft decision not resolved with citations: {d}")
    body = json.dumps(prereg)
    for terminal in ("INFORMATION_ITEM_ABSENT", "RECONSTRUCTION_TRIGGER_ABSENT", "CANNOT_CHECK_COST"):
        if terminal not in body:
            errors.append(f"predeclared terminal missing: {terminal}")
    if ">=3" not in json.dumps(prereg.get("open_preconditions_before_any_study_model_call", [])):
        errors.append("model-identity >=3-families open precondition missing")

    return {
        "schema": "ORION.A4.InterventionPreregCheckResult.v1",
        "decision": "RED" if errors else "GREEN",
        "errors": errors,
    }


def self_test(prereg: dict, tmp: Path, prereg_dir: Path) -> None:
    # structural green on the committed prereg + pinned fixtures
    (tmp / "a4_intervention_transforms_v1.py").write_bytes(
        (prereg_dir / "a4_intervention_transforms_v1.py").read_bytes()
    )
    gym_dir = tmp / "gym"
    gym_dir.mkdir(parents=True, exist_ok=True)
    te_lines = [""] * 1745
    te_lines[1744] = "        max_rounds = 50  # comment"
    te_lines[808] = "    max_rounds: int = 50,"
    te_lines[1062] = "    max_rounds: int = 50,"
    (gym_dir / "test_executor.py").write_text("\n".join(te_lines[:1745]))
    (gym_dir / "agent.py").write_text("REACT_TOOL_SYSTEM_PROMPT = 'x'\n")
    (gym_dir / "config.py").write_text(
        "\n".join([""] * 168 + ["MAX_ITERATIONS = 25  # mcp cap", "PROXY = 'http://35.220.164.252:3888/v1'"])
    )
    rec_ok = {
        "id": "single:1",
        "metadata": {"tool_expected": ["add"], "solution_steps": ["s1"]},
        "usage_tool_protocol": [{"type": "function", "function": {"name": "add"}}],
    }
    r = verify(json.loads(json.dumps(prereg)), tmp, gym_dir, [rec_ok], [rec_ok])
    # census mismatch is expected here (synthetic record); only citation errors must be absent
    for e in r["errors"]:
        assert "census" in e or "count != 131" in e or e.startswith("bound blob"), f"unexpected error: {e}"

    # hostile: flag flipped true must go RED with that flag named
    forged = json.loads(json.dumps(prereg))
    forged["flags"]["intervention_study_executed"] = True
    r2 = verify(forged, tmp, gym_dir, None, None)
    assert r2["decision"] == "RED" and any("intervention_study_executed" in e for e in r2["errors"])

    # hostile: rounds cap citation broken must go RED
    (gym_dir / "test_executor.py").write_text(
        (gym_dir / "test_executor.py").read_text().replace("max_rounds = 50", "max_rounds = 99")
    )
    r3 = verify(json.loads(json.dumps(prereg)), tmp, gym_dir, None, None)
    assert r3["decision"] == "RED" and any("DRAFT-DECISION-1" in e for e in r3["errors"])

    # hostile: domain_knowledge appearing in substrate must go RED
    rec_dk = json.loads(json.dumps(rec_ok))
    rec_dk["metadata"]["domain_knowledge"] = "x"
    (gym_dir / "test_executor.py").write_text("\n".join(te_lines[:1745]))
    r4 = verify(json.loads(json.dumps(prereg)), tmp, gym_dir, [rec_dk], [rec_dk])
    assert any("domain_knowledge" in e for e in r4["errors"])

    print("A4_INTERVENTION_PREREG_SELF_TEST_GREEN")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg", type=Path, required=True)
    ap.add_argument("--gym-dir", type=Path)
    ap.add_argument("--multi", type=Path)
    ap.add_argument("--single", type=Path)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    prereg = json.loads(a.prereg.read_text())
    if a.self_test:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            self_test(prereg, Path(td), a.prereg.parent)
        return 0
    if not (a.gym_dir and a.multi and a.single):
        ap.error("--gym-dir, --multi and --single required for live verification")
    result = verify(
        prereg,
        a.prereg.parent,
        a.gym_dir,
        json.loads(a.multi.read_text()),
        json.loads(a.single.read_text()),
    )
    print(json.dumps(result, indent=1))
    return 0 if result["decision"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
