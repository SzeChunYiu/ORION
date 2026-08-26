#!/usr/bin/env python3
"""Fail-closed checker for the ORION V1 freeze control plane."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

PKG = Path("research/orion-v1-freeze")
FILES = {
    "contract": "ORION_V1_FREEZE_CONTRACT_V1.json",
    "components": "V1_COMPONENT_GRAPH_V1.json",
    "theorems": "V1_THEOREM_AUTHORITY_LEDGER_V1.json",
    "issues": "V1_ISSUE_DISPOSITION_LEDGER_V1.json",
    "jobs": "V1_EXECUTION_JOB_LEDGER_V1.json",
    "gaps": "V1_EXECUTION_GAP_LEDGER_V1.json",
    "papers": "V1_PAPER_CANDIDATE_GATE_V1.json",
    "receipt": "V1_BOOTSTRAP_RECEIPT_V1.json",
    "manifest": "V1_FREEZE_MANIFEST_V1.json",
}
FIXED = {
    "development/orion-v1-freeze-control-plane-2026-08-26/DEVELOPMENT_PACKET.md",
    "scripts/check_orion_v1_freeze.py",
    "tests/unit/orion_v1/test_orion_v1_freeze.py",
    ".github/workflows/orion-v1-freeze.yml",
}
FINAL = "ORION_V1_ARCHITECTURE_AND_LOCAL_FORMALISM_FROZEN"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Z0-9][A-Z0-9_.-]*\Z")
EXPERTS = {
    "FORMAL_METHODS_LEAD", "SYSTEMS_REPRODUCIBILITY_LEAD",
    "QUANTUM_TRANSFER_LEAD", "PUBLICATION_AUTHORITY_LEAD",
    "EXECUTION_AND_EMPIRICAL_LEAD",
}
COMPONENTS = {
    "OSTC_FOUNDATIONS", "DYNAMIC_EPISTEMIC_STATE",
    "THEOREM_IDENTIFYING_DISCOVERY", "KNOWLEDGE_WEB_AND_PROOF_ECONOMY",
    "DISCOVERY_SYNTHESIS_MODES", "FRONTIER_DOMINANCE_AND_RESIDUAL_NOVELTY",
    "CERTIFIED_ALGORITHMIC_NAVIGATION", "EXECUTION_INTEGRITY_AND_RECEIPTS",
    "P1_P15_SCIENTIFIC_PROGRAMME", "ORION_Q_TYPED_RESEARCH_STATE",
    "QUANTUM_QG_QN_FRONTIER", "V1_FREEZE_CONTROL_PLANE",
    "P16_P18_PUBLICATION_CANDIDATES", "POST_FREEZE_EXTERNAL_EXECUTION",
}
AUTH_ROWS = {
    "V1-AUTH-OSTC", "V1-AUTH-DES-ALGEBRA", "V1-AUTH-P7",
    "V1-AUTH-DISCOVERY-V3", "V1-AUTH-QUANTUM-TRANSFER",
    "V1-AUTH-FREEZE", "V1-AUTH-EXTERNAL-NOVELTY",
}
CONTROL_ISSUES = {1329, 1357, 1358, 1359, 1360, 1361, 1362}
JOBS = {
    "V1-CENSUS-01", "V1-Q-CENSUS-01", "V1-COMPONENT-BIND-01",
    "V1-THEOREM-CENSUS-01", "V1-RED-CENSUS-01",
    "V1-DISC-V3-SPEC-01", "V1-P7-DENOM-SUCCESSOR-01",
    "V1-Q-RESOURCE-01",
}
PACKET = {
    "FREEZE", "RAW_MANIFEST", "PRIMARY_RESULT", "DONOR_RESULT",
    "NEGATIVE_CONTROLS", "RESOURCE_LEDGER", "TRANSFER_RESULT",
    "RESULT_BINDING_PACKET",
}
GAP_CLASSES = {
    "INTERNAL_LOCAL", "EXTERNAL_AUTHORITY", "EXTERNAL_CUSTODY",
    "HEAVY_COMPUTE", "RIGHTS_OR_ACCESS",
}


class ValidationError(RuntimeError):
    pass


def need(ok: bool, msg: str) -> None:
    if not ok:
        raise ValidationError(msg)


def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in items:
        need(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    except FileNotFoundError as exc:
        raise ValidationError(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc
    need(isinstance(value, dict), f"object required: {path}")
    return value


def schema(data: Mapping[str, Any], value: str, label: str) -> None:
    need(data.get("schema") == value, f"{label}: schema must be {value}")


def rows(data: Mapping[str, Any], key: str, id_key: str, label: str) -> tuple[list[dict[str, Any]], set[Any]]:
    value = data.get(key)
    need(isinstance(value, list) and value, f"{label}: nonempty {key} required")
    need(all(isinstance(row, dict) and id_key in row for row in value), f"{label}: malformed row")
    ids = [row[id_key] for row in value]
    need(len(ids) == len(set(ids)), f"{label}: duplicate {id_key}")
    return value, set(ids)


def text(row: Mapping[str, Any], fields: Sequence[str], label: str) -> None:
    for field in fields:
        need(isinstance(row.get(field), str) and row[field].strip(), f"{label}: {field} missing")


def relative(value: Any, label: str) -> PurePosixPath:
    need(isinstance(value, str) and value, f"{label}: path missing")
    path = PurePosixPath(value)
    need(not path.is_absolute() and ".." not in path.parts and "\\" not in value, f"{label}: unsafe path")
    return path


def dag(graph: Mapping[str, Sequence[str]], label: str) -> None:
    active: set[str] = set()
    done: set[str] = set()
    def visit(node: str) -> None:
        if node in done:
            return
        need(node not in active, f"{label} contains a cycle")
        active.add(node)
        for parent in graph[node]:
            visit(parent)
        active.remove(node)
        done.add(node)
    for node in graph:
        visit(node)


def coverage(data: Mapping[str, Any], label: str) -> tuple[Mapping[str, Any], bool]:
    value = data.get("coverage")
    need(isinstance(value, Mapping), f"{label}: coverage missing")
    complete = value.get("complete")
    need(type(complete) is bool, f"{label}: coverage.complete must be Boolean")
    return value, complete


def contract(data: dict[str, Any]) -> tuple[str, str, set[str]]:
    schema(data, "ORION.V1.FreezeContract.v1", "contract")
    base, tree = data.get("base_main"), data.get("base_tree")
    need(isinstance(base, str) and SHA40.fullmatch(base), "contract.base_main: exact lowercase SHA required")
    need(isinstance(tree, str) and SHA40.fullmatch(tree), "contract.base_tree: exact lowercase SHA required")
    need(str(data.get("lane_branch", "")).startswith("shadow/") and ".." not in data["lane_branch"], "lane must stay in shadow/*")
    need(data.get("parent_issues") == [1357, 1358, 1359], "parent issues mismatch")
    state, terminal = data.get("freeze_state"), data.get("terminal")
    need(state in {"OPEN_BOOTSTRAP", "FROZEN"}, "invalid freeze_state")
    need((state, terminal) in {("OPEN_BOOTSTRAP", "NOT_EARNED"), ("FROZEN", FINAL)}, "state/terminal mismatch")
    role_rows, role_ids = rows(data, "expert_roles", "role_id", "expert_roles")
    need(role_ids == EXPERTS, "expert role set is incomplete or changed")
    for row in role_rows:
        text(row, ("background", "veto"), f"expert {row['role_id']}")
    allowed = data.get("allowed_issue_dispositions")
    need(isinstance(allowed, list) and len(allowed) == len(set(allowed)), "allowed dispositions invalid")
    allowed_set = set(allowed)
    need({"PENDING_ATOMIC_AUDIT", "VALID_NEGATIVE_OR_BOUNDARY_RESULT", "EXTERNAL_AUTHORITY_OR_ACCESS_BLOCKER"} <= allowed_set, "required dispositions missing")
    ceiling = data.get("authority_ceiling")
    need(isinstance(ceiling, Mapping), "authority ceiling missing")
    for key, value in {
        "external_validation": "CANNOT_CHECK", "novelty": "CANNOT_CHECK",
        "physical_quantum_validity": "CANNOT_CHECK", "quantum_advantage": "CANNOT_CHECK",
        "publication": "NONE",
    }.items():
        need(ceiling.get(key) == value, f"bootstrap cannot grant {key.replace('_', ' ')}")
    immutable = "\n".join(map(str, data.get("immutable_boundaries", [])))
    for phrase in ("historical receipts and negative evidence", "protected P1 finalizer", "same-owner replay", "CANNOT_CHECK cannot be rewritten as success"):
        need(phrase in immutable, f"immutable boundary missing: {phrase}")
    return base, state, allowed_set


def components(data: dict[str, Any], base: str, state: str) -> tuple[int, bool]:
    schema(data, "ORION.V1.ComponentGraph.v1", "components")
    need(data.get("base_main") == base, "components: base mismatch")
    values, ids = rows(data, "nodes", "id", "components")
    need(COMPONENTS <= ids, f"components missing: {sorted(COMPONENTS-ids)}")
    graph: dict[str, list[str]] = {}
    for row in values:
        ident = row["id"]
        need(isinstance(ident, str) and ID.fullmatch(ident), f"invalid component id: {ident!r}")
        deps = row.get("depends_on")
        need(isinstance(deps, list) and len(deps) == len(set(deps)), f"component {ident}: dependencies invalid")
        need(ident not in deps and set(deps) <= ids, f"component {ident}: unknown/self dependency")
        graph[ident] = deps
        need(isinstance(row.get("paths"), list), f"component {ident}: paths missing")
        for item in row["paths"]:
            relative(item, f"component {ident}")
        text(row, ("layer", "status", "authority"), f"component {ident}")
    dag(graph, "component dependency graph")
    freeze = next(row for row in values if row["id"] == "V1_FREEZE_CONTROL_PLANE")
    need(freeze["status"] == ("BOOTSTRAP_OPEN" if state == "OPEN_BOOTSTRAP" else "FROZEN"), "control-plane component state mismatch")
    cov, complete = coverage(data, "components")
    need(isinstance(cov.get("completion_job"), str), "components: completion job missing")
    if state == "OPEN_BOOTSTRAP":
        need(not complete, "bootstrap component census cannot claim completeness")
    return len(values), complete


def theorems(data: dict[str, Any], base: str, state: str) -> tuple[int, bool]:
    schema(data, "ORION.V1.TheoremAuthorityLedger.v1", "theorems")
    need(data.get("base_main") == base, "theorems: base mismatch")
    values, ids = rows(data, "entries", "id", "theorems")
    need(AUTH_ROWS <= ids, "required authority rows missing")
    for row in values:
        ident = row["id"]
        need(isinstance(ident, str) and ID.fullmatch(ident), f"invalid authority id: {ident!r}")
        text(row, ("object", "status", "evidence_class", "authority_ceiling"), f"authority {ident}")
        need(isinstance(row.get("source_refs"), list) and row["source_refs"], f"authority {ident}: sources missing")
        need(isinstance(row.get("remaining"), list), f"authority {ident}: remaining missing")
        joined = " ".join(str(row.get(k, "")) for k in ("status", "authority_ceiling", "object"))
        for token in ("PHYSICAL_QUANTUM_VALIDITY_SUPPORTED", "QUANTUM_ADVANTAGE_SUPPORTED", "EXTERNAL_NOVELTY_GREEN", "TOP_TIER_READY"):
            need(token not in joined, f"authority {ident}: forbidden promotion {token}")
    quantum = next(row for row in values if row["id"] == "V1-AUTH-QUANTUM-TRANSFER")
    need("NO_PHYSICAL_VALIDITY_OR_QUANTUM_ADVANTAGE" in quantum["authority_ceiling"], "quantum authority ceiling missing")
    freeze = next(row for row in values if row["id"] == "V1-AUTH-FREEZE")
    need(freeze["status"] == ("NOT_EARNED" if state == "OPEN_BOOTSTRAP" else FINAL), "freeze authority row mismatch")
    if state == "OPEN_BOOTSTRAP":
        need(freeze["authority_ceiling"] == "NONE", "bootstrap freeze authority must be NONE")
    _, complete = coverage(data, "theorems")
    if state == "OPEN_BOOTSTRAP":
        need(not complete, "bootstrap theorem census cannot claim completeness")
    return len(values), complete


def issues(data: dict[str, Any], base: str, allowed: set[str]) -> tuple[int, int, bool]:
    schema(data, "ORION.V1.IssueDispositionLedger.v1", "issues")
    need(data.get("base_main") == base, "issues: base mismatch")
    values, numbers = rows(data, "entries", "number", "issues")
    need(all(type(n) is int and n > 0 for n in numbers), "issue numbers must be positive integers")
    need(CONTROL_ISSUES <= numbers, f"control issue rows missing: {sorted(CONTROL_ISSUES-numbers)}")
    pending = 0
    for row in values:
        number = row["number"]
        need(row.get("disposition") in allowed, f"issue #{number}: invalid disposition")
        pending += row["disposition"] == "PENDING_ATOMIC_AUDIT"
        text(row, ("title_snapshot", "domain", "evidence_status", "next_action", "authority_delta"), f"issue #{number}")
        need(row["authority_delta"] == "NONE", f"issue #{number}: authority delta must be NONE")
    for number in (1360, 1361, 1362):
        need(next(row for row in values if row["number"] == number)["disposition"] == "PAPER_CANDIDATE_BLOCKED", f"issue #{number}: paper candidate must remain blocked")
    cov, complete = coverage(data, "issues")
    need(cov.get("known_entries") == len(values), "issues: known_entries denominator mismatch")
    need(cov.get("unclassified_entries") == pending, "issues: unclassified_entries denominator mismatch")
    total = cov.get("all_open_issue_count")
    need(total is None or (type(total) is int and total >= 0), "issues: invalid all_open_issue_count")
    if complete:
        need(pending == 0 and total == len(values), "issues: complete census denominator invalid")
    else:
        need(pending > 0 or total is None, "issues: incomplete census lacks open reason")
    return len(values), pending, complete


def jobs(data: dict[str, Any], base: str) -> tuple[int, set[str]]:
    schema(data, "ORION.V1.ExecutionJobLedger.v1", "jobs")
    need(data.get("base_main") == base, "jobs: base mismatch")
    need(data.get("execution_owner") == "CODEX_COMPUTATION_SESSION", "execution owner mismatch")
    need(data.get("writing_owner") == "V1_FREEZE_THEORY_AND_SYSTEM_LANE", "writing owner mismatch")
    need(data.get("manuscript_edits_by_execution_owner") == "FORBIDDEN", "Codex manuscript edits must be forbidden")
    values, ids = rows(data, "jobs", "job_id", "jobs")
    need(JOBS <= ids, f"jobs missing: {sorted(JOBS-ids)}")
    graph: dict[str, list[str]] = {}
    for row in values:
        ident = row["job_id"]
        deps = row.get("depends_on")
        need(isinstance(ident, str) and ID.fullmatch(ident), f"invalid job id: {ident!r}")
        need(isinstance(deps, list) and len(deps) == len(set(deps)) and set(deps) <= ids, f"job {ident}: dependencies invalid")
        graph[ident] = deps
        output = row.get("required_outputs")
        need(isinstance(output, list) and len(output) == len(PACKET) and set(output) == PACKET, f"job {ident}: exact eight-file packet required")
        need(row.get("paper_authority_delta") == "NONE", f"job {ident}: paper authority delta must be NONE")
        text(row, ("class", "question", "status", "success_terminal"), f"job {ident}")
        need(isinstance(row.get("protocol"), list) and len(row["protocol"]) >= 3, f"job {ident}: protocol incomplete")
        need(isinstance(row.get("negative_terminals"), list) and "CANNOT_CHECK" in row["negative_terminals"], f"job {ident}: CANNOT_CHECK missing")
    dag(graph, "execution job dependency graph")
    return len(values), ids


def gaps(data: dict[str, Any], base: str, job_ids: set[str]) -> tuple[int, int, int, bool]:
    schema(data, "ORION.V1.ExecutionGapLedger.v1", "gaps")
    need(data.get("base_main") == base, "gaps: base mismatch")
    values, _ = rows(data, "gaps", "gap_id", "gaps")
    open_internal = external = 0
    for row in values:
        ident, kind, status = row["gap_id"], row.get("class"), row.get("status")
        need(isinstance(ident, str) and ID.fullmatch(ident), f"invalid gap id: {ident!r}")
        need(kind in GAP_CLASSES and status in {"OPEN", "CLOSED", "RESOLVED", "CANNOT_CHECK"}, f"gap {ident}: class/status invalid")
        text(row, ("owner",), f"gap {ident}")
        discharge = row.get("discharge_job")
        need(discharge is None or discharge in job_ids, f"gap {ident}: unknown discharge job")
        if kind == "INTERNAL_LOCAL":
            need(row.get("blocks_freeze") is True and discharge is not None, f"internal gap {ident}: freeze/discharge invalid")
            open_internal += status not in {"CLOSED", "RESOLVED"}
        else:
            need(row.get("blocks_local_freeze") is False, f"external/heavy gap {ident}: blocks_local_freeze must be false")
            need(row.get("blocks_external_authority") is True, f"external/heavy gap {ident}: must block external authority")
            need(status == "CANNOT_CHECK", f"external/heavy gap {ident}: status must be CANNOT_CHECK")
            external += 1
    need(external >= 3, "external/heavy blocker ledger incomplete")
    cov, complete = coverage(data, "gaps")
    deps = cov.get("completion_dependencies")
    need(isinstance(deps, list) and set(deps) <= job_ids, "gaps: invalid completion dependencies")
    return len(values), open_internal, external, complete


def papers(data: dict[str, Any], base: str, state: str) -> tuple[int, str]:
    schema(data, "ORION.V1.PaperCandidateGate.v1", "papers")
    need(data.get("base_main") == base, "papers: base mismatch")
    authority = data.get("paper_authority_delta")
    need(authority == "NONE", "paper authority delta must remain NONE")
    values, ids = rows(data, "candidates", "paper_id", "papers")
    need(ids == {"P16", "P17", "P18"}, "paper candidate set must be exactly P16-P18")
    for row in values:
        ident = row["paper_id"]
        need(type(row.get("issue")) is int, f"{ident}: issue missing")
        text(row, ("kind",), ident)
        need(isinstance(row.get("minimum_internal_prerequisites"), list) and row["minimum_internal_prerequisites"], f"{ident}: internal prerequisites missing")
        need(isinstance(row.get("top_tier_prerequisites"), list) and row["top_tier_prerequisites"], f"{ident}: top-tier prerequisites missing")
        if state == "OPEN_BOOTSTRAP":
            need(row.get("status") == "BLOCKED_NO_MANUSCRIPT_AUTHORIZED", f"{ident}: manuscript authorization is premature")
    p18 = next(row for row in values if row["paper_id"] == "P18")
    joined = " ".join(p18["minimum_internal_prerequisites"] + p18["top_tier_prerequisites"])
    for phrase in ("negative twin", "resource accounting", "held-out target-native consequence"):
        need(phrase in joined, f"P18 gate missing: {phrase}")
    return len(values), authority


def manifest(data: dict[str, Any], root: Path, base: str) -> int:
    schema(data, "ORION.V1.FreezeManifest.v1", "manifest")
    need(data.get("base_main") == base, "manifest: base mismatch")
    values, listed = rows(data, "files", "path", "manifest")
    package_files = {
        path.relative_to(root).as_posix() for path in (root / PKG).iterdir()
        if path.is_file() and path.name != FILES["manifest"]
    }
    expected = package_files | FIXED
    need(listed == expected, f"manifest coverage mismatch: missing={sorted(expected-listed)} extra={sorted(listed-expected)}")
    for row in values:
        rel = relative(row["path"], "manifest")
        path = root.joinpath(*rel.parts)
        need(path.is_file(), f"manifest target missing: {rel}")
        raw = path.read_bytes()
        digest = row.get("sha256")
        need(isinstance(digest, str) and SHA256.fullmatch(digest), f"manifest {rel}: SHA-256 invalid")
        need(hashlib.sha256(raw).hexdigest() == digest, f"manifest digest drift: {rel}")
        need(row.get("bytes") == len(raw), f"manifest byte count drift: {rel}")
    return len(values)


def receipt(data: dict[str, Any], base: str, state: str, counts: Mapping[str, int]) -> None:
    schema(data, "ORION.V1.BootstrapReceipt.v1", "receipt")
    need(data.get("base_main") == base and data.get("freeze_state") == state, "receipt identity/state mismatch")
    need(data.get("terminal") == "NOT_EARNED", "bootstrap receipt must retain NOT_EARNED")
    recorded = data.get("counts")
    need(isinstance(recorded, Mapping), "receipt counts missing")
    for key, value in counts.items():
        need(recorded.get(key) == value, f"receipt count mismatch for {key}")
    validation = data.get("validation")
    need(isinstance(validation, Mapping), "receipt validation missing")
    need(validation.get("checker_terminal") == "ORION_V1_FREEZE_BOOTSTRAP_GREEN", "receipt checker terminal mismatch")
    need(type(validation.get("hostile_tests")) is int and validation["hostile_tests"] >= 8, "receipt hostile test count too small")
    need(data.get("paper_authority_delta") == "NONE", "receipt paper authority delta must be NONE")


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    get = lambda name: load(root / PKG / FILES[name])
    base, state, allowed = contract(get("contract"))
    n_components, component_complete = components(get("components"), base, state)
    n_theorems, theorem_complete = theorems(get("theorems"), base, state)
    n_issues, pending, issue_complete = issues(get("issues"), base, allowed)
    n_jobs, job_ids = jobs(get("jobs"), base)
    n_gaps, open_internal, external, gap_complete = gaps(get("gaps"), base, job_ids)
    n_papers, paper_authority = papers(get("papers"), base, state)
    n_manifest = manifest(get("manifest"), root, base)
    requirements: dict[str, Any] = {
        "architecture_and_local_formalism_frozen": component_complete and theorem_complete and open_internal == 0,
        "internal_implementation_gaps_zero": open_internal == 0 and gap_complete,
        "unclassified_open_issues_zero": issue_complete and pending == 0,
        "external_or_heavy_blockers_explicitly_ledgered": gap_complete and external > 0,
        "all_manifest_digests_valid": True,
        "paper_authority_delta": paper_authority,
    }
    need(get("contract").get("terminal_requirements") == requirements, "contract terminal requirements do not equal checker-derived requirements")
    earned = all(v is True for k, v in requirements.items() if k != "paper_authority_delta") and paper_authority == "NONE"
    need((state, get("contract").get("terminal")) == (("FROZEN", FINAL) if earned else ("OPEN_BOOTSTRAP", "NOT_EARNED")), "earned/unearned terminal mismatch")
    counts = {
        "components": n_components, "theorem_authority_rows": n_theorems,
        "issues": n_issues, "pending_issue_audits": pending, "jobs": n_jobs,
        "gaps": n_gaps, "open_internal_gaps": open_internal,
        "external_blockers": external, "paper_candidates": n_papers,
        "manifest_files": n_manifest,
    }
    receipt(get("receipt"), base, state, counts)
    return {
        "status": "PASS", "checker_terminal": FINAL if earned else "ORION_V1_FREEZE_BOOTSTRAP_GREEN",
        "freeze_state": state, "scientific_terminal": get("contract").get("terminal"),
        "base_main": base, "counts": counts, "terminal_requirements": requirements,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = validate(args.root)
    except ValidationError as exc:
        print(f"ORION_V1_FREEZE_INVALID: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        c = result["counts"]
        print(f"{result['checker_terminal']} components={c['components']} authority_rows={c['theorem_authority_rows']} issues={c['issues']} pending={c['pending_issue_audits']} jobs={c['jobs']} open_internal_gaps={c['open_internal_gaps']} manifest_files={c['manifest_files']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
