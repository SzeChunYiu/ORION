#!/usr/bin/env python3
"""Derive P6-P8 reproducibility-target states from target-specific evidence.

The frozen V1 content manifests used one authored table for all three papers.
That table was useful as an initial warning, but it projected CANNOT_CHECK onto
targets for which the tree already contained partial evidence.  This successor
does not rewrite those historical manifests.  It asks a separate, fail-closed
probe for every target and emits one of five typed states:

* BOUND: all evidence required by this bounded probe is present;
* PARTIAL: concrete evidence is present, with a named missing component;
* CANNOT_CHECK: the evidence needed to perform the check is absent;
* NOT_APPLICABLE: the target does not apply to this paper;
* DEFERRED: a lifecycle action is intentionally unavailable at candidate stage.

The report grants no paper authority.  In particular, PARTIAL is not PASS and
DEFERRED is not a scientific result.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

SCHEMA_VERSION = "orion.candidate-reproducibility-targets.v2"
ALLOWED_STATES = frozenset(
    {"BOUND", "PARTIAL", "CANNOT_CHECK", "NOT_APPLICABLE", "DEFERRED"}
)

PAPERS = {
    "P6": Path("papers/paper-06-formal-epistemic-structures-and-mechanics"),
    "P7": Path("papers/paper-07-epistemic-navigation-open-worlds"),
    "P8": Path("papers/paper-08-epistemic-authority-autonomous-science"),
}
DATASETS = {
    "P6": Path("formal/assumption_countermodels_v2.jsonl"),
    "P7": Path("benchmark/instances_v2.jsonl"),
    "P8": Path("benchmark/authority_cases_v2.jsonl"),
}
TAIL_TARGETS = {
    "P6": "proof_and_checker_reproducibility",
    "P7": "benchmark_generator_and_trace_replay",
    "P8": "protected_labels_custody_and_attack_replay",
}
COMMON_TARGETS = (
    "exact_subject_commit_identities",
    "versioned_protocol_generator_schemas",
    "immutable_raw_result_formats",
    "one_command_regeneration_from_raw",
    "clean_environment_reproduction_instructions",
    "dependency_model_provider_tool_versions",
    "negative_null_history_retained",
    "independent_replay_attestation",
    "permanent_archive_after_authority_stabilizes",
)


@dataclass(frozen=True)
class Assessment:
    """One derived target state with auditable positive and missing evidence."""

    status: str
    evidence: tuple[str, ...]
    blocker: str | None = None

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_STATES:
            raise ValueError(f"unknown target state: {self.status}")
        if self.status in {"PARTIAL", "CANNOT_CHECK", "DEFERRED"} and not self.blocker:
            raise ValueError(f"{self.status} requires a named blocker or lifecycle condition")
        if self.status in {"BOUND", "NOT_APPLICABLE"} and self.blocker is not None:
            raise ValueError(f"{self.status} cannot carry a blocker")

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "evidence": list(self.evidence),
            "blocker": self.blocker,
        }


def _load_json(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _valid_schema(path: Path) -> bool:
    payload = _load_json(path)
    if payload is None:
        return False
    required = payload.get("required")
    properties = payload.get("properties")
    return (
        isinstance(payload.get("$schema"), str)
        and payload.get("type") == "object"
        and isinstance(required, list)
        and bool(required)
        and all(isinstance(field, str) for field in required)
        and isinstance(properties, dict)
        and set(required).issubset(properties)
    )


def _valid_generator(path: Path, dataset_name: str, schema_names: set[str]) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
    except (OSError, SyntaxError):
        return False
    functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    return (
        "main" in functions
        and dataset_name in text
        and any(schema_name in text for schema_name in schema_names)
        and "__main__" in text
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(root: Path, paths: list[Path]) -> tuple[str, ...]:
    return tuple(path.relative_to(root).as_posix() for path in sorted(paths))


def _paper(root: Path, candidate_id: str) -> Path:
    return root / PAPERS[candidate_id]


def _reproduce_text(paper: Path) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(paper.glob("REPRODUCE*.md"))
        if path.is_file()
    )


def _mechanized_json(root: Path, candidate_id: str) -> list[Path]:
    files = sorted((_paper(root, candidate_id) / "formal/mechanized").glob("*.json"))
    return [path for path in files if _load_json(path) is not None]


def _formal_checkers(root: Path, candidate_id: str) -> list[Path]:
    return sorted((_paper(root, candidate_id) / "formal").glob("check*.py"))


def _subject_identity(root: Path, candidate_id: str) -> Assessment:
    paper = _paper(root, candidate_id)
    successor_manifest = paper / "CONTENT_MANIFEST_V2.json"
    manifest_path = successor_manifest if successor_manifest.is_file() else paper / "CONTENT_MANIFEST_V1.json"
    sums_path = paper / "SHA256SUMS"
    manifest = _load_json(manifest_path)
    if manifest is None or not sums_path.is_file():
        return Assessment(
            "CANNOT_CHECK",
            (),
            "CONTENT_MANIFEST_V1.json and SHA256SUMS are both required",
        )

    evidence = (
        manifest_path.relative_to(root).as_posix(),
        sums_path.relative_to(root).as_posix(),
    )
    commit = manifest.get("subject_commit")
    status = manifest.get("subject_commit_status")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        return Assessment("PARTIAL", evidence, "byte digests exist but subject_commit is invalid")
    if status != "BOUND":
        paths = manifest.get("subject_commit_unbound_paths")
        detail = ", ".join(paths) if isinstance(paths, list) else "unspecified paths"
        return Assessment(
            "PARTIAL",
            evidence,
            f"byte digests exist but subject_commit_status is {status}: {detail}",
        )

    if manifest.get("schema_version") == "orion.candidate-content-binding.v2":
        tree = manifest.get("subject_tree")
        if not isinstance(tree, str) or not re.fullmatch(r"[0-9a-f]{40}", tree):
            return Assessment("PARTIAL", evidence, "V2 manifest has no valid subject_tree")
        try:
            actual_tree = subprocess.run(
                ["git", "-C", str(root), "rev-parse", f"{commit}^{{tree}}"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return Assessment("PARTIAL", evidence, "V2 subject tree is unavailable")
        if actual_tree != tree:
            return Assessment("PARTIAL", evidence, "V2 subject_tree disagrees with subject_commit")

        environment = manifest.get("environment_lock")
        if not isinstance(environment, dict):
            return Assessment("PARTIAL", evidence, "V2 manifest has no environment lock")
        lock_path = environment.get("path")
        lock_digest = environment.get("sha256")
        if not (
            isinstance(lock_path, str)
            and isinstance(lock_digest, str)
            and re.fullmatch(r"[0-9a-f]{64}", lock_digest)
        ):
            return Assessment("PARTIAL", evidence, "V2 environment-lock identity is invalid")
        local_lock = root / lock_path
        if not local_lock.is_file() or _sha256_file(local_lock) != lock_digest:
            return Assessment("PARTIAL", evidence, f"V2 environment lock drifted: {lock_path}")
        try:
            committed_lock = subprocess.run(
                ["git", "-C", str(root), "show", f"{commit}:{lock_path}"],
                capture_output=True,
                check=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError):
            return Assessment("PARTIAL", evidence, f"V2 subject commit lacks: {lock_path}")
        if hashlib.sha256(committed_lock).hexdigest() != lock_digest:
            return Assessment("PARTIAL", evidence, f"V2 commit bytes disagree: {lock_path}")

        entries = manifest.get("bound_files")
        if not isinstance(entries, list) or not entries:
            return Assessment("PARTIAL", evidence, "V2 manifest has no bound files")
        seen: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                return Assessment("PARTIAL", evidence, "V2 bound-file entry is malformed")
            relative = entry.get("path")
            digest = entry.get("sha256")
            if not (
                isinstance(relative, str)
                and relative not in seen
                and isinstance(digest, str)
                and re.fullmatch(r"[0-9a-f]{64}", digest)
            ):
                return Assessment("PARTIAL", evidence, "V2 bound-file identity is invalid or duplicate")
            seen.add(relative)
            local_path = root / relative
            if not local_path.is_file() or _sha256_file(local_path) != digest:
                return Assessment("PARTIAL", evidence, f"V2 bound file drifted: {relative}")
            try:
                committed = subprocess.run(
                    ["git", "-C", str(root), "show", f"{commit}:{relative}"],
                    capture_output=True,
                    check=True,
                ).stdout
            except (OSError, subprocess.CalledProcessError):
                return Assessment("PARTIAL", evidence, f"V2 subject commit lacks: {relative}")
            if hashlib.sha256(committed).hexdigest() != digest:
                return Assessment("PARTIAL", evidence, f"V2 commit bytes disagree: {relative}")

    try:
        subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return Assessment(
            "PARTIAL",
            evidence,
            "byte digests exist but the recorded commit is unavailable in this object database",
        )
    bound_files = manifest.get("bound_files")
    subject_paths = []
    if isinstance(bound_files, list):
        subject_paths = [
            str(entry["path"])
            for entry in bound_files
            if isinstance(entry, dict)
            and isinstance(entry.get("path"), str)
            and not str(entry["path"]).endswith("/CONTENT_MANIFEST_V1.json")
        ]
    if not subject_paths:
        return Assessment("PARTIAL", evidence, "manifest contains no usable bound subject paths")
    try:
        drift = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-only", commit, "--", *subject_paths],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return Assessment("PARTIAL", evidence, "git could not compare the bound subject to commit")
    if drift:
        return Assessment(
            "PARTIAL",
            evidence,
            "recorded BOUND status disagrees with current subject bytes: " + ", ".join(drift),
        )
    return Assessment("BOUND", evidence)


def _schema_and_generator(root: Path, candidate_id: str) -> Assessment:
    paper = _paper(root, candidate_id)
    dataset = paper / DATASETS[candidate_id]
    if not dataset.is_file():
        return Assessment("CANNOT_CHECK", (), f"dataset is absent: {dataset.relative_to(root)}")

    stem = dataset.name.removesuffix(".jsonl")
    schema_candidates = sorted(dataset.parent.glob(f"{stem}*schema*.json"))
    schema_candidates += sorted(dataset.parent.glob(f"*schema*{stem.split('_v')[0]}*.json"))
    schemas = list(dict.fromkeys(path for path in schema_candidates if _valid_schema(path)))
    generator_candidates = sorted(dataset.parent.glob("generate*.py"))
    generators = [
        path
        for path in generator_candidates
        if _valid_generator(path, dataset.name, {schema.name for schema in schemas})
    ]
    evidence = [dataset]
    evidence.extend(schemas)
    evidence.extend(generators)
    if schemas and generators:
        return Assessment("BOUND", _relative(root, evidence))
    missing = []
    if not schemas:
        missing.append("versioned machine-readable schema")
    if not generators:
        missing.append("dataset generator")
    state = "PARTIAL" if schemas or generators else "CANNOT_CHECK"
    return Assessment(state, _relative(root, evidence), "missing " + " and ".join(missing))


def _load_machine_output(path: Path):
    """Parse a machine result in either JSON or line-delimited JSON form."""
    if path.suffix == ".json":
        return _load_json(path)
    if path.suffix != ".jsonl" or not path.is_file():
        return None
    try:
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, json.JSONDecodeError):
        return None
    if not rows or not all(isinstance(row, dict) for row in rows):
        return None
    return rows


def _immutable_results(root: Path, candidate_id: str) -> Assessment:
    outputs = _mechanized_json(root, candidate_id)
    checkers = _formal_checkers(root, candidate_id)
    if not outputs:
        return Assessment(
            "CANNOT_CHECK",
            _relative(root, checkers),
            "no valid machine-readable result artifact exists under formal/mechanized",
        )
    local_contracts = sorted(
        (_paper(root, candidate_id) / "evidence/local").glob(
            f"{candidate_id}_LOCAL_REPLAY_CONTRACT_V3.json"
        )
    )
    if local_contracts:
        contract_path = local_contracts[0]
        contract = _load_json(contract_path)
        bound_paths: list[Path] = []
        valid_contract = contract is not None
        if contract is not None:
            valid_contract = valid_contract and (
                contract.get("schema_version") == "orion.local-replay-contract.v3"
                and contract.get("paper_id") == candidate_id
                and contract.get("self_authorizing") is True
                and contract.get("independent_replay") is False
                and contract.get("grants_scientific_authority") == "NONE"
                and isinstance(contract.get("one_command"), str)
                and str(contract.get("one_command")).startswith("make ")
            )
            environment = contract.get("environment_lock")
            if not isinstance(environment, dict):
                valid_contract = False
            else:
                lock_path = environment.get("path")
                lock_digest = environment.get("sha256")
                local_lock = root / str(lock_path)
                valid_contract = valid_contract and (
                    isinstance(lock_path, str)
                    and isinstance(lock_digest, str)
                    and local_lock.is_file()
                    and _sha256_file(local_lock) == lock_digest
                )
            for field in ("raw_inputs", "raw_outputs"):
                artifacts = contract.get(field)
                if not isinstance(artifacts, list) or not artifacts:
                    valid_contract = False
                    continue
                for artifact in artifacts:
                    if not isinstance(artifact, dict):
                        valid_contract = False
                        continue
                    relative = artifact.get("path")
                    digest = artifact.get("sha256")
                    local_path = root / str(relative)
                    if not (
                        isinstance(relative, str)
                        and isinstance(digest, str)
                        and re.fullmatch(r"[0-9a-f]{64}", digest)
                        and local_path.is_file()
                        and _sha256_file(local_path) == digest
                    ):
                        valid_contract = False
                    else:
                        bound_paths.append(local_path)
            output_entries = contract.get("raw_outputs")
            if isinstance(output_entries, list):
                for artifact in output_entries:
                    if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str):
                        valid_contract = False
                        continue
                    output_path = root / str(artifact["path"])
                    if _load_machine_output(output_path) is None:
                        valid_contract = False
        if valid_contract and set(outputs).issubset(bound_paths):
            return Assessment(
                "BOUND",
                _relative(root, [contract_path] + outputs + checkers),
            )
        return Assessment(
            "PARTIAL",
            _relative(root, [contract_path] + outputs + checkers),
            "local replay contract is malformed, stale, lacks raw inputs, or does not bind all outputs",
        )

    manifest = _load_json(_paper(root, candidate_id) / "CONTENT_MANIFEST_V1.json") or {}
    entries = manifest.get("bound_files")
    entry_list = entries if isinstance(entries, list) else []
    bound = {
        str(entry["path"])
        for entry in entry_list
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    unbound_outputs = [path for path in outputs if path.relative_to(root).as_posix() not in bound]
    if unbound_outputs:
        return Assessment(
            "PARTIAL",
            _relative(root, outputs + checkers),
            "machine-readable results exist but are not all covered by the content binding: "
            + ", ".join(path.relative_to(root).as_posix() for path in unbound_outputs),
        )
    if checkers:
        return Assessment(
            "PARTIAL",
            _relative(root, outputs + checkers),
            "machine-readable successor results exist, but legacy formal checkers "
            "remain stdout-only",
        )
    return Assessment(
        "PARTIAL",
        _relative(root, outputs),
        "result artifacts exist but no local checker source is available to reproduce them",
    )


def _one_command(root: Path, candidate_id: str) -> Assessment:
    paper = _paper(root, candidate_id)
    docs = sorted(paper.glob("REPRODUCE*.md"))
    text = _reproduce_text(paper)
    outputs = _mechanized_json(root, candidate_id)
    if not docs:
        return Assessment("CANNOT_CHECK", (), "no REPRODUCE document exists")
    orchestrators = [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^(make|just|nox|tox)\s+\S+", line.strip())
    ]
    evidence = list(docs) + outputs
    if orchestrators and outputs:
        return Assessment("BOUND", _relative(root, evidence))
    if outputs:
        return Assessment(
            "PARTIAL",
            _relative(root, evidence),
            "reproduction commands and result artifacts exist, but no one-command "
            "orchestrator is named",
        )
    return Assessment(
        "CANNOT_CHECK",
        _relative(root, docs),
        "instructions exist but there is no machine-readable result to regenerate",
    )


def _clean_environment(root: Path, candidate_id: str) -> Assessment:
    paper = _paper(root, candidate_id)
    text = _reproduce_text(paper)
    lockfiles = [path for path in (root / "uv.lock", root / "poetry.lock") if path.is_file()]
    images = sorted(paper.glob("**/*container*digest*"))
    evidence = lockfiles + images
    lock_selected = "uv.lock" in text and "uv sync --frozen" in text
    if (lock_selected and lockfiles) or images:
        return Assessment("BOUND", _relative(root, evidence))
    return Assessment(
        "CANNOT_CHECK",
        _relative(root, evidence),
        "a repository lock may exist, but this paper does not select it with a "
        "frozen install command",
    )


def _dependency_versions(root: Path, candidate_id: str) -> Assessment:
    paper = _paper(root, candidate_id)
    text = _reproduce_text(paper)
    files = [path for path in (root / "pyproject.toml", root / "uv.lock") if path.is_file()]
    if not files:
        return Assessment(
            "CANNOT_CHECK",
            (),
            "no machine-readable dependency declaration or lock is present",
        )
    if "uv.lock" in text and "uv sync --frozen" in text:
        return Assessment("BOUND", _relative(root, files))
    return Assessment(
        "PARTIAL",
        _relative(root, files),
        "programme dependency metadata exists, but the paper does not bind its reproduction to it",
    )


def _negative_history(root: Path, candidate_id: str) -> Assessment:
    paper = _paper(root, candidate_id)
    versioned = sorted(paper.glob("CLAIM_LEDGER_V*.md")) + sorted(
        paper.glob("JOURNAL_READINESS_V*.md")
    )
    registries = []
    for pattern in ("*HISTORY*.json", "*HISTORY*.jsonl", "*NEGATIVE*.jsonl", "*NULL*.jsonl"):
        registries.extend(paper.glob(f"**/{pattern}"))
    if registries:
        return Assessment("BOUND", _relative(root, sorted(registries) + versioned))
    if versioned:
        return Assessment(
            "PARTIAL",
            _relative(root, versioned),
            "superseded assessments are retained, but no typed append-only "
            "negative/null registry exists",
        )
    return Assessment(
        "CANNOT_CHECK",
        (),
        "neither versioned assessments nor a typed negative/null history are present",
    )


def _independent_replay(root: Path, candidate_id: str) -> Assessment:
    directory = root / "research/verification/records"
    matches: list[Path] = []
    valid: list[Path] = []
    for path in sorted(directory.glob("*.json")):
        payload = _load_json(path)
        if payload is None or payload.get("paper_id") != candidate_id:
            continue
        matches.append(path)
        subject = payload.get("subject")
        raw_artifacts = payload.get("raw_artifacts")
        scorers = payload.get("scorers")
        artifact_bytes_match = isinstance(raw_artifacts, list) and bool(raw_artifacts)
        if artifact_bytes_match:
            for artifact in raw_artifacts:
                if not isinstance(artifact, dict):
                    artifact_bytes_match = False
                    break
                artifact_path = artifact.get("path")
                artifact_digest = artifact.get("sha256")
                if not isinstance(artifact_path, str) or not isinstance(artifact_digest, str):
                    artifact_bytes_match = False
                    break
                local_path = root / artifact_path
                if (
                    not local_path.is_file()
                    or not re.fullmatch(r"[0-9a-f]{64}", artifact_digest)
                    or _sha256_file(local_path) != artifact_digest
                ):
                    artifact_bytes_match = False
                    break
        if (
            payload.get("schema_version") == "orion.scientific-result-verification.v1"
            and payload.get("verification_state") == "BOUNDED_VERIFIED"
            and payload.get("self_authorizing") is False
            and isinstance(subject, dict)
            and isinstance(subject.get("commit"), str)
            and re.fullmatch(r"[0-9a-f]{40}", str(subject.get("commit")))
            and isinstance(subject.get("tree"), str)
            and re.fullmatch(r"[0-9a-f]{40}", str(subject.get("tree")))
            and artifact_bytes_match
            and isinstance(scorers, dict)
            and scorers.get("independent_from_written_spec") is True
        ):
            valid.append(path)
    if valid:
        return Assessment("BOUND", _relative(root, valid))
    if matches:
        return Assessment(
            "PARTIAL",
            _relative(root, matches),
            "paper-naming records exist but none is an independent BOUNDED_VERIFIED V1 record",
        )
    return Assessment(
        "CANNOT_CHECK",
        (),
        "no ScientificResultVerification.v1 record names this paper",
    )


def _permanent_archive(root: Path, candidate_id: str) -> Assessment:
    paper = _paper(root, candidate_id)
    archive_records = sorted(paper.glob("**/zenodo.json")) + sorted(
        paper.glob("**/ARCHIVE_DEPOSIT*.json")
    )
    stabilization = _load_json(paper / "AUTHORITY_STABILIZATION.json")
    stabilized = (
        stabilization is not None
        and stabilization.get("candidate_id") == candidate_id
        and stabilization.get("authority_status") == "STABILIZED"
        and stabilization.get("independently_attested") is True
    )
    if archive_records and stabilized:
        return Assessment(
            "BOUND", _relative(root, archive_records + [paper / "AUTHORITY_STABILIZATION.json"])
        )
    if archive_records:
        return Assessment(
            "PARTIAL",
            _relative(root, archive_records),
            "deposit metadata exists without independently attested authority stabilization",
        )
    return Assessment(
        "DEFERRED",
        (),
        "permanent deposit is a post-authority lifecycle action; candidate status "
        "does not license it",
    )


def _p6_proof(root: Path) -> Assessment:
    outputs = _mechanized_json(root, "P6")
    checkers = _formal_checkers(root, "P6")
    paper = _paper(root, "P6")
    proof_objects: list[Path] = []
    for suffix in ("*.lean", "*.v", "*.thy", "*.smt2"):
        proof_objects.extend(paper.glob(f"formal/**/*{suffix.removeprefix('*')}"))
    evidence = outputs + checkers + sorted(proof_objects)
    if outputs and checkers and proof_objects:
        return Assessment("BOUND", _relative(root, evidence))
    if outputs or checkers:
        missing = []
        if not outputs:
            missing.append("machine-readable checker result")
        if not checkers:
            missing.append("checker source")
        if not proof_objects:
            missing.append("machine-checkable proof object")
        return Assessment("PARTIAL", _relative(root, evidence), "missing " + ", ".join(missing))
    return Assessment(
        "CANNOT_CHECK",
        (),
        "neither checker source nor machine-readable result nor proof object exists",
    )


def _p7_trace(root: Path) -> Assessment:
    paper = _paper(root, "P7")
    dataset = paper / DATASETS["P7"]
    generators = sorted(dataset.parent.glob("generate*.py"))
    traces = sorted(paper.glob("**/*trace*.json")) + sorted(paper.glob("**/*trace*.jsonl"))
    evidence = ([dataset] if dataset.is_file() else []) + generators + traces
    if generators and traces:
        return Assessment("BOUND", _relative(root, evidence))
    missing = []
    if not generators:
        missing.append("benchmark generator")
    if not traces:
        missing.append("replayable navigation trace")
    state = "PARTIAL" if generators or traces else "CANNOT_CHECK"
    return Assessment(state, _relative(root, evidence), "missing " + " and ".join(missing))


def _p8_custody(root: Path) -> Assessment:
    paper = _paper(root, "P8")
    custody = sorted(paper.glob("**/*custody*.json")) + sorted(paper.glob("**/*custody*.jsonl"))
    attacks = sorted(paper.glob("**/*attack*result*.json")) + sorted(
        paper.glob("**/*attack*replay*.json")
    )
    evidence = custody + attacks
    if custody and attacks:
        return Assessment("BOUND", _relative(root, evidence))
    missing = []
    if not custody:
        missing.append("protected-label custody record")
    if not attacks:
        missing.append("cross-capability attack replay result")
    state = "PARTIAL" if custody or attacks else "CANNOT_CHECK"
    return Assessment(state, _relative(root, evidence), "missing " + " and ".join(missing))


PROBES: dict[str, Callable[[Path, str], Assessment]] = {
    "exact_subject_commit_identities": _subject_identity,
    "versioned_protocol_generator_schemas": _schema_and_generator,
    "immutable_raw_result_formats": _immutable_results,
    "one_command_regeneration_from_raw": _one_command,
    "clean_environment_reproduction_instructions": _clean_environment,
    "dependency_model_provider_tool_versions": _dependency_versions,
    "negative_null_history_retained": _negative_history,
    "independent_replay_attestation": _independent_replay,
    "permanent_archive_after_authority_stabilizes": _permanent_archive,
}
TAIL_PROBES: dict[str, Callable[[Path], Assessment]] = {
    "P6": _p6_proof,
    "P7": _p7_trace,
    "P8": _p8_custody,
}


def assess_targets(root: Path, candidate_id: str) -> dict[str, Assessment]:
    """Run every target's own probe; no status is copied across targets."""

    if candidate_id not in PAPERS:
        raise ValueError(f"unknown candidate: {candidate_id}")
    assessments = {name: PROBES[name](root, candidate_id) for name in COMMON_TARGETS}
    assessments[TAIL_TARGETS[candidate_id]] = TAIL_PROBES[candidate_id](root)
    return assessments


def derive_report(root: Path, candidate_id: str) -> dict[str, object]:
    targets = assess_targets(root, candidate_id)
    counts = Counter(target.status for target in targets.values())
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "grants_authority": "NONE",
        "closes_gate": None,
        "state_counts": {state: counts.get(state, 0) for state in sorted(ALLOWED_STATES)},
        "reproducibility_targets": {
            name: assessment.as_dict() for name, assessment in targets.items()
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--candidate", choices=sorted(PAPERS), action="append")
    parser.add_argument("--json", action="store_true", help="emit the deterministic JSON report")
    parser.add_argument(
        "--fail-on-unresolved",
        action="store_true",
        help="exit 3 if any target is PARTIAL or CANNOT_CHECK",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = args.root.resolve()
    candidate_ids = args.candidate or sorted(PAPERS)
    reports = [derive_report(root, candidate_id) for candidate_id in candidate_ids]
    if args.json:
        print(json.dumps(reports, indent=2, sort_keys=True) + "\n", end="")
    else:
        for report in reports:
            counts = report["state_counts"]
            rendered = ", ".join(f"{state}={counts[state]}" for state in sorted(ALLOWED_STATES))
            print(f"{report['candidate_id']}: {rendered}")
    unresolved = any(
        target["status"] in {"PARTIAL", "CANNOT_CHECK"}
        for report in reports
        for target in report["reproducibility_targets"].values()
    )
    return 3 if args.fail_on_unresolved and unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
