#!/usr/bin/env python3
"""Run P6 selective revalidation over three frozen public Git histories."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import posixpath
import random
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "development/p6-public-selective-revalidation-v1"
PROTOCOL_PATH = "development/p6-public-selective-revalidation-v1/P6_PUBLIC_SELECTIVE_REVALIDATION_PROTOCOL_V1.json"
RUNNER_PATH = "development/p6-public-selective-revalidation-v1/run_p6_public_selective_revalidation_v1.py"
RESULT_SCHEMA = "ORION.P6.PublicSelectiveRevalidationResult.v1"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def dataset_rows() -> list[dict[str, Any]]:
    return [
        {
            "id": "nfcore_rnaseq_nextflow",
            "domain": "scientific_workflow",
            "repository": "nf-core/rnaseq",
            "clone_url": "https://github.com/nf-core/rnaseq.git",
            "source_url": "https://github.com/nf-core/rnaseq",
            "branch": "master",
            "head_commit": "1f03b53ef799e298f60c813440e961e867017043",
            "license": "MIT",
            "license_path": "LICENSE",
            "license_git_blob_sha1": "d720749d3382f5f8cd4505af8908bb4577f1f240",
            "artifact_rule": "paths ending .nf or .config",
            "dependency_rule": "Nextflow include/from and includeConfig relative paths at the frozen head",
            "history_depth": 2000,
            "required_change_sets": 100,
        },
        {
            "id": "mathlib4_lean",
            "domain": "formal_mathematics",
            "repository": "leanprover-community/mathlib4",
            "clone_url": "https://github.com/leanprover-community/mathlib4.git",
            "source_url": "https://github.com/leanprover-community/mathlib4",
            "branch": "master",
            "head_commit": "dc84fcbe9e049439c1c36d6db290cc0565f77788",
            "license": "Apache-2.0",
            "license_path": "LICENSE",
            "license_git_blob_sha1": "8dada3edaf50dbc082c9a125058f25def75e625a",
            "artifact_rule": "Mathlib/**/*.lean",
            "dependency_rule": "Lean import declarations at the frozen head",
            "history_depth": 2000,
            "required_change_sets": 100,
        },
        {
            "id": "geneontology_go_ontology",
            "domain": "versioned_ontology",
            "repository": "geneontology/go-ontology",
            "clone_url": "https://github.com/geneontology/go-ontology.git",
            "source_url": "https://github.com/geneontology/go-ontology",
            "branch": "master",
            "head_commit": "97b20201b32a62e0ca8a07743743b8fdc1f2a1a1",
            "license": "CC-BY-4.0",
            "license_path": "LICENSE",
            "license_git_blob_sha1": "10fabd90118f7ce38bb2e4753e105e744442a429",
            "artifact_rule": "paths ending .obo, .owl, or .ofn",
            "dependency_rule": "ontology import declarations resolvable to frozen-head repository paths",
            "history_depth": 2000,
            "required_change_sets": 100,
        },
    ]


def expected_protocol(root: Path = ROOT) -> dict[str, Any]:
    return {
        "schema": "ORION.P6.PublicSelectiveRevalidationProtocol.v1",
        "status": "FROZEN_NO_RESULTS",
        "frozen_utc": "2026-08-24T15:10:00Z",
        "issue": 1086,
        "paper": "P6_COMPONENT_OF_P6_P8_UNIFIED_CALCULUS",
        "outcome_accessed": False,
        "results_exist": False,
        "systems": ["SELECTIVE_REVALIDATION", "NATIVE_DEPENDENCY_CLOSURE", "FULL_RESET"],
        "selection_contract": {
            "change_set": "artifact paths changed by one eligible first-parent commit and still present in the frozen-head artifact universe",
            "native_dependency_closure": "changed artifacts plus every frozen-head reverse-transitive dependent under parsed domain-native import/include syntax",
            "selective_revalidation": "same exact reverse-transitive closure; equivalence to native closure is expected and must be retained",
            "full_reset": "every artifact in the frozen-head domain universe",
            "gold": "native dependency closure under the same frozen graph",
            "gold_independence_boundary": "gold and SELECTIVE_REVALIDATION use the same reachability predicate; safety is conformance, not independent semantic validation",
        },
        "datasets": dataset_rows(),
        "sampling": {
            "walk": "first-parent from exact frozen head",
            "eligible": "commit has at least one changed path in the frozen-head artifact universe",
            "take": "first 100 eligible commits in reverse chronological order",
            "inference_unit": "commit_change_set",
            "serial_dependence": True,
            "population_inference": False,
        },
        "statistics": {
            "endpoint": "1 - selected_artifact_count / full_reset_artifact_count",
            "interpretation": "deterministic block-resampling sensitivity analysis only; no stochastic coverage guarantee",
            "block_size": 10,
            "bootstrap_draws": 10000,
            "simultaneous_one_sided_alpha": 0.05,
            "domain_count_for_bonferroni": 3,
            "seed": 660024,
        },
        "gate": {
            "domain_count": 3,
            "change_sets_per_domain": 100,
            "zero_invalid_certificates_against_native_closure": True,
            "positive_savings_every_domain": True,
            "block_resampling_lower_quantile_gt_zero_every_domain": True,
            "mutations_killed_globally": ["OMITTED_READ", "OMITTED_EDGE", "ALTERNATIVE_SUPPORT_ALL_DEPENDENCIES"],
        },
        "runtime": {"python": "3.12.13", "python_implementation": "CPython", "git": "2.51.1", "dependencies": "stdlib_and_git_only"},
        "retention": {
            "every_retained_eligible_change_set": True,
            "every_attempted_domain_has_success_or_cannot_check_terminal": True,
            "null_harmful_and_zero_savings_rows": True,
            "upstream_file_contents": False,
            "commit_ids_changed_paths_graph_and_decision_hashes": True,
        },
        "runner": {"path": RUNNER_PATH, "sha256": digest((root / RUNNER_PATH).read_bytes())},
        "authority": {
            "closes_issue_box": False,
            "scientific_authority_delta": "NONE",
            "independent_adjudication": "CANNOT_CHECK",
            "protected_custody": "CANNOT_CHECK",
            "population_inference": False,
        },
        "non_bypass_boundaries": [
            "The study replays public change sets against dependency syntax parsed by ORION at the frozen head; it is not a historical native build/test or native-tool replay.",
            "Deleted paths and dependencies not representable in the frozen-head graph are outside the estimand.",
            "Native-closure equivalence is implementation conformance, not evidence that the selector is scientifically novel or more precise than native systems.",
            "Public Git history does not create independent adjudication, protected custody, or semantic target-obligation confirmation.",
            "The protocol closes no issue box until a later unchanged clean-main execution passes and is reviewed.",
        ],
    }


def assert_exact(observed: Any, expected: Any, path: str = "protocol") -> None:
    if type(observed) is not type(expected):
        raise TypeError(f"{path}: exact type drift")
    if isinstance(expected, dict):
        if observed.keys() != expected.keys():
            raise ValueError(f"{path}: key/order drift")
        for key in expected:
            assert_exact(observed[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(observed) != len(expected):
            raise ValueError(f"{path}: list-length drift")
        for index, (left, right) in enumerate(zip(observed, expected)):
            assert_exact(left, right, f"{path}[{index}]")
    elif observed != expected:
        raise ValueError(f"{path}: value drift")


def validate_protocol(protocol: Mapping[str, Any], root: Path = ROOT) -> None:
    if not isinstance(protocol, dict):
        raise TypeError("protocol must be a dictionary")
    assert_exact(protocol, expected_protocol(root))


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    raw = subprocess.check_output(["git", *args], cwd=repo)
    return raw if binary else raw.decode()


def validate_execution_source(root: Path = ROOT) -> dict[str, Any]:
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=root).strip():
        raise ValueError("execution requires a clean working tree")
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()
    if branch != "main":
        raise ValueError("execution requires branch main")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    committed = {}
    for relative in (PROTOCOL_PATH, RUNNER_PATH):
        raw = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=root)
        if raw != (root / relative).read_bytes():
            raise ValueError(f"committed byte equality failed: {relative}")
        committed[relative] = digest(raw)
    return {"source_branch": branch, "source_commit": commit, "committed_blob_equality": committed}


def artifact_paths(repo: Path, head: str, dataset_id: str) -> list[str]:
    paths = git(repo, "ls-tree", "-r", "--name-only", head).splitlines()
    if dataset_id == "nfcore_rnaseq_nextflow":
        return sorted(path for path in paths if path.endswith((".nf", ".config")))
    if dataset_id == "mathlib4_lean":
        return sorted(path for path in paths if path.startswith("Mathlib/") and path.endswith(".lean"))
    if dataset_id == "geneontology_go_ontology":
        return sorted(path for path in paths if path.endswith((".obo", ".owl", ".ofn")))
    raise ValueError("unknown dataset")


def resolve_relative(source: str, target: str, nodes: set[str]) -> tuple[str | None, str]:
    candidate = posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
    options = (candidate, candidate + ".nf", candidate + ".config", candidate + "/main.nf")
    matches = [option for option in options if option in nodes]
    if len(matches) == 1:
        return matches[0], "RESOLVED"
    return None, "AMBIGUOUS" if len(matches) > 1 else "UNRESOLVED"


def dependency_edges(repo: Path, head: str, dataset_id: str, nodes: Sequence[str]) -> tuple[list[tuple[str, str]], dict[str, int]]:
    node_set = set(nodes)
    edges: set[tuple[str, str]] = set()
    audit = {"candidate_import_count": 0, "resolved_import_count": 0, "unresolved_import_count": 0, "ambiguous_import_count": 0}
    for source in nodes:
        raw = git(repo, "show", f"{head}:{source}")
        if dataset_id == "nfcore_rnaseq_nextflow":
            targets = re.findall(r"(?:\bfrom\s+|\bincludeConfig\s*)['\"]([^'\"]+)['\"]", raw)
            for target in targets:
                audit["candidate_import_count"] += 1
                resolved, status = resolve_relative(source, target, node_set)
                if resolved:
                    edges.add((source, resolved))
                    audit["resolved_import_count"] += 1
                else:
                    audit[f"{status.lower()}_import_count"] += 1
        elif dataset_id == "mathlib4_lean":
            for line in raw.splitlines():
                if not line.startswith("import "):
                    continue
                for module in line.removeprefix("import ").split():
                    audit["candidate_import_count"] += 1
                    target = module.replace(".", "/") + ".lean"
                    if target in node_set:
                        edges.add((source, target))
                        audit["resolved_import_count"] += 1
                    else:
                        audit["unresolved_import_count"] += 1
        else:
            targets = re.findall(r"(?im)^import:\s*<?([^>\s]+)>?", raw)
            targets += re.findall(r"(?i)<owl:imports\b[^>]*\brdf:resource=['\"]([^'\"]+)['\"]", raw)
            targets += re.findall(r"(?i)\bImport\(\s*<?([^>\s)]+)>?\s*\)", raw)
            for match in targets:
                audit["candidate_import_count"] += 1
                name = match.split("#", 1)[0].rstrip("/").rsplit("/", 1)[-1]
                candidates = [path for path in nodes if path == name or path.endswith("/" + name)]
                if len(candidates) == 1:
                    edges.add((source, candidates[0]))
                    audit["resolved_import_count"] += 1
                elif candidates:
                    audit["ambiguous_import_count"] += 1
                else:
                    audit["unresolved_import_count"] += 1
    return sorted(edges), audit


def reverse_closure(changed: Iterable[str], edges: Sequence[tuple[str, str]]) -> set[str]:
    reverse: dict[str, set[str]] = {}
    for dependent, dependency in edges:
        reverse.setdefault(dependency, set()).add(dependent)
    reached = set(changed)
    frontier = list(reached)
    while frontier:
        node = frontier.pop()
        for dependent in reverse.get(node, set()):
            if dependent not in reached:
                reached.add(dependent)
                frontier.append(dependent)
    return reached


def eligible_changes(repo: Path, head: str, nodes: set[str], count: int) -> list[dict[str, Any]]:
    commits = git(repo, "rev-list", "--first-parent", head).splitlines()
    retained = []
    for commit in commits:
        parents = git(repo, "rev-list", "--parents", "-n", "1", commit).split()
        if len(parents) < 2:
            continue
        parent = parents[1]
        changed = sorted(set(git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit).splitlines()) & nodes)
        if not changed:
            continue
        retained.append({"commit": commit, "parent": parent, "changed_paths": changed})
        if len(retained) == count:
            return retained
    raise ValueError(f"only {len(retained)} eligible changes found")


def mutation_sets(changed: Sequence[str], edges: Sequence[tuple[str, str]]) -> dict[str, set[str]]:
    omitted_read = set(changed)
    exact = reverse_closure(changed, edges)
    edge_omissions = [reverse_closure(changed, edges[:index] + edges[index + 1:]) for index in range(len(edges))]
    omitted_edge = max(edge_omissions, key=lambda value: len(value ^ exact), default=exact)
    dependencies: dict[str, set[str]] = {}
    for dependent, dependency in edges:
        dependencies.setdefault(dependent, set()).add(dependency)
    alternative_support = set(changed)
    changed_flag = True
    while changed_flag:
        changed_flag = False
        for dependent, required in dependencies.items():
            if dependent not in alternative_support and required and required <= alternative_support:
                alternative_support.add(dependent)
                changed_flag = True
    return {
        "OMITTED_READ": omitted_read,
        "OMITTED_EDGE": omitted_edge,
        "ALTERNATIVE_SUPPORT_ALL_DEPENDENCIES": alternative_support,
    }


def block_bootstrap_lower(values: Sequence[float], block_size: int, draws: int, seed: int, alpha: float) -> float:
    if len(values) % block_size:
        raise ValueError("values must divide into exact blocks")
    blocks = [values[index:index + block_size] for index in range(0, len(values), block_size)]
    rng = random.Random(seed)
    means = []
    for _ in range(draws):
        sample = [value for _ in blocks for value in rng.choice(blocks)]
        means.append(sum(sample) / len(sample))
    means.sort()
    return means[int(alpha * draws)]


def validate_runtime(protocol: Mapping[str, Any]) -> dict[str, str]:
    observed = {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "git": subprocess.check_output(["git", "--version"], text=True).strip().removeprefix("git version "),
        "dependencies": "stdlib_and_git_only",
    }
    assert_exact(observed, protocol["runtime"], "runtime")
    return observed


def verify_frozen_refs(expected: str, fetch_head: str, frozen_ref: str) -> None:
    if fetch_head != expected:
        raise ValueError("fetched commit differs from frozen head")
    if frozen_ref != expected:
        raise ValueError("frozen ref differs from frozen head")


def acquire(dataset: Mapping[str, Any], root: Path) -> tuple[Path, dict[str, Any]]:
    path = root / dataset["id"]
    path.mkdir()
    subprocess.run(["git", "init", "--quiet"], cwd=path, capture_output=True, check=True, timeout=60)
    subprocess.run(["git", "remote", "add", "origin", dataset["clone_url"]], cwd=path, capture_output=True, check=True, timeout=60)
    ls_remote_argv = ["git", "ls-remote", "--heads", dataset["clone_url"], dataset["branch"]]
    remote_pre = subprocess.run(ls_remote_argv, capture_output=True, check=True, timeout=120)
    command = ["git", "fetch", "--quiet", "--filter=blob:none", "--depth", str(dataset["history_depth"]), "origin", dataset["head_commit"]]
    completed = subprocess.run(command, cwd=path, capture_output=True, check=False, timeout=600)
    if completed.returncode != 0:
        raise RuntimeError(f"exact frozen-head fetch failed: {dataset['id']}")
    head = dataset["head_commit"]
    observed_fetch_head = git(path, "rev-parse", "FETCH_HEAD").strip()
    git(path, "update-ref", "refs/heads/frozen", head)
    observed_frozen_ref = git(path, "rev-parse", "refs/heads/frozen").strip()
    verify_frozen_refs(head, observed_fetch_head, observed_frozen_ref)
    remote_post = subprocess.run(ls_remote_argv, capture_output=True, check=True, timeout=120)
    license_blob = git(path, "rev-parse", f"{head}:{dataset['license_path']}").strip()
    if license_blob != dataset["license_git_blob_sha1"]:
        raise ValueError("license blob drift")
    return path, {
        "fetch_argv": command,
        "fetch_exit_code": completed.returncode,
        "stderr_sha256": digest(completed.stderr),
        "observed_fetch_head": observed_fetch_head,
        "observed_frozen_ref": observed_frozen_ref,
        "remote_branch_pre_sha256": digest(remote_pre.stdout),
        "remote_branch_post_sha256": digest(remote_post.stdout),
        "remote_branch_moved_during_acquisition": remote_pre.stdout != remote_post.stdout,
        "license_git_blob_sha1": license_blob,
    }


def execute(protocol: Mapping[str, Any], root: Path = ROOT) -> dict[str, Any]:
    validate_protocol(protocol, root)
    source = validate_execution_source(root)
    observed_runtime = validate_runtime(protocol)
    domains = []
    all_mutation_kills = {name: 0 for name in protocol["gate"]["mutations_killed_globally"]}
    with tempfile.TemporaryDirectory(prefix="orion-p6-public-") as temporary:
        acquisition_root = Path(temporary)
        for domain_index, dataset in enumerate(protocol["datasets"]):
            try:
                repo, acquisition = acquire(dataset, acquisition_root)
                nodes = artifact_paths(repo, dataset["head_commit"], dataset["id"])
                edges, import_audit = dependency_edges(repo, dataset["head_commit"], dataset["id"], nodes)
                changes = eligible_changes(repo, dataset["head_commit"], set(nodes), dataset["required_change_sets"])
            except Exception as error:
                domains.append({
                    "dataset_id": dataset["id"],
                    "domain": dataset["domain"],
                    "status": "CANNOT_CHECK",
                    "failure_type": type(error).__name__,
                    "failure_message_sha256": digest(str(error).encode()),
                    "change_set_count": 0,
                    "rows": [],
                })
                continue
            rows = []
            for change in changes:
                native = reverse_closure(change["changed_paths"], edges)
                selective = reverse_closure(change["changed_paths"], edges)
                mutants = mutation_sets(change["changed_paths"], edges)
                for name, mutant in mutants.items():
                    if mutant != native:
                        all_mutation_kills[name] += 1
                rows.append({
                    **change,
                    "changed_path_count": len(change["changed_paths"]),
                    "native_selected_count": len(native),
                    "native_selected_sha256": digest(canonical(sorted(native))),
                    "selective_selected_count": len(selective),
                    "selective_selected_sha256": digest(canonical(sorted(selective))),
                    "full_reset_count": len(nodes),
                    "invalid_certificate_count": len(native - selective),
                    "unnecessary_revalidation_count_vs_native": len(selective - native),
                    "savings_vs_full_reset": 1.0 - len(selective) / len(nodes),
                    "mutation_disagreements": {name: mutant != native for name, mutant in mutants.items()},
                })
            savings = [row["savings_vs_full_reset"] for row in rows]
            alpha = protocol["statistics"]["simultaneous_one_sided_alpha"] / protocol["statistics"]["domain_count_for_bonferroni"]
            lower = block_bootstrap_lower(
                savings,
                protocol["statistics"]["block_size"],
                protocol["statistics"]["bootstrap_draws"],
                protocol["statistics"]["seed"] + domain_index,
                alpha,
            )
            domains.append({
                "dataset_id": dataset["id"],
                "domain": dataset["domain"],
                "status": "EXECUTED",
                "acquisition": acquisition,
                "artifact_count": len(nodes),
                "artifact_universe_sha256": digest(canonical(nodes)),
                "dependency_edge_count": len(edges),
                "dependency_edges_sha256": digest(canonical(edges)),
                "import_resolution_audit": import_audit,
                "change_set_count": len(rows),
                "mean_savings_vs_full_reset": sum(savings) / len(savings),
                "block_resampling_lower_quantile": lower,
                "invalid_certificate_count": sum(row["invalid_certificate_count"] for row in rows),
                "unnecessary_revalidation_count_vs_native": sum(row["unnecessary_revalidation_count_vs_native"] for row in rows),
                "selective_native_exact_agreement": all(row["native_selected_sha256"] == row["selective_selected_sha256"] for row in rows),
                "rows": rows,
            })
    executed = [domain for domain in domains if domain["status"] == "EXECUTED"]
    coverage = len(executed) == 3 and all(domain["change_set_count"] == 100 for domain in executed)
    conformance = coverage and all(domain["invalid_certificate_count"] == 0 and domain["selective_native_exact_agreement"] for domain in executed)
    savings_gate = coverage and all(domain["mean_savings_vs_full_reset"] > 0 and domain["block_resampling_lower_quantile"] > 0 for domain in executed)
    mutation_gate = all(count > 0 for count in all_mutation_kills.values())
    result = {
        "schema": RESULT_SCHEMA,
        "protocol_file_sha256": digest((root / PROTOCOL_PATH).read_bytes()),
        "protocol_sha256": digest(canonical(protocol)),
        "runner_sha256": digest((root / RUNNER_PATH).read_bytes()),
        **source,
        "observed_runtime": observed_runtime,
        "domain_count": len(domains),
        "change_set_count": sum(domain["change_set_count"] for domain in domains),
        "domains": domains,
        "mutation_kill_counts": all_mutation_kills,
        "data_coverage_gate": "MET" if coverage else "NOT_MET",
        "native_conformance_gate": "MET" if conformance else "NOT_MET",
        "savings_gate": "MET" if savings_gate else "NOT_MET",
        "mutation_gate": "MET" if mutation_gate else "NOT_MET",
        "strongest_donor_result": "EXTENSIONALLY_EQUIVALENT" if conformance else "CANNOT_CHECK",
        "scientific_superiority_gate": "NOT_MET",
        "simultaneous_95pct_inferential_gate": "CANNOT_CHECK",
        "historical_native_build_test_replay": "CANNOT_CHECK",
        "independent_adjudication": "CANNOT_CHECK",
        "protected_custody": "CANNOT_CHECK",
        "population_inference": False,
        "scientific_authority_delta": "P6_DATA_AND_COMPARATOR_EXECUTION_ONLY" if coverage else "NONE",
        "terminal": (
            "P6_PUBLIC_SELECTIVE_REVALIDATION_V1_COVERAGE_AND_SAVINGS_MET__NATIVE_EQUIVALENT__SUPERIORITY_NOT_MET"
            if coverage and conformance and savings_gate and mutation_gate
            else "P6_PUBLIC_SELECTIVE_REVALIDATION_V1_GATE_NOT_MET"
        ),
    }
    result["receipt_sha256"] = digest(canonical(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("refusing to overwrite result")
    result = execute(json.loads(args.protocol.read_text()))
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["terminal"])
    return 0 if "COVERAGE_AND_SAVINGS_MET" in result["terminal"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
