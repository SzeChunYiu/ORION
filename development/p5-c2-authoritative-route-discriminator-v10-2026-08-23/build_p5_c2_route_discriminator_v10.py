#!/usr/bin/env python3
"""Build the outcome-blind P5 C2 authoritative-route discriminator packet.

This builder performs byte/path/static-route audits only.  It never starts
MOSS, a model, a coding agent, a benchmark, a scorer, or a protected panel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path


FROZEN_AT = "2026-08-23T21:35:04Z"
MOSS_COMMIT = "5453f1feebad44c199f5887f852fc5bc7fb7d4da"
MOSS_MAIN_ARCHIVE_SHA256 = "de6bb0e480749757d8e9b05a66c37c82228ea6d9d1e1cb92b6b32a3b28e5610e"
MOSS_TAG_COMMIT = "9f1b2929a6a1b6d405e0ce378d52cc8c8293618c"
MOSS_TAG_ARCHIVE_SHA256 = "24de890f18f5e744844f7decc0c1c89cd4f0715372d5c8d64b247a4095da3e51"
CLAW_EVAL_COMMIT = "d3f02d4938ab0832377d90535013def2b1a2fdc0"
CLAW_EVAL_ARCHIVE_SHA256 = "20d6ee03aa429d05123e724b8ae9ed8aa2cfd307d3e0c33850d669301dd2aeaf"
ARXIV_SOURCE_SHA256 = "92cb482d252d28eca388b7cc2b69c24a1a1f91080a807aa14ceaba80c3d76d05"
REQUIRED_RUNNER = "benchmark/claw-eval/runner/benchmark.py"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_members(path: Path) -> list[str]:
    with tarfile.open(path, "r:gz") as tf:
        names = tf.getnames()
    out = []
    for name in names:
        parts = name.split("/", 1)
        out.append(parts[1] if len(parts) == 2 else "")
    return out


def excerpt(path: Path, start: int, end: int) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    chosen = lines[start - 1 : end]
    marker = "p5-c2-moss-src/"
    raw_path = str(path)
    rel = raw_path.split(marker, 1)[1] if marker in raw_path else path.name
    return {
        "line_end": end,
        "line_start": start,
        "path": f"upstream://hkgai-official/Moss@{MOSS_COMMIT}/{rel}",
        "source_file_sha256": sha256_file(path),
        "text": "".join(chosen),
        "text_sha256": sha256_bytes("".join(chosen).encode()),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--moss-main-archive", type=Path, required=True)
    ap.add_argument("--moss-tag-archive", type=Path, required=True)
    ap.add_argument("--claw-eval-archive", type=Path, required=True)
    ap.add_argument("--arxiv-source", type=Path, required=True)
    ap.add_argument("--moss-source", type=Path, required=True)
    ap.add_argument("--repo-json", type=Path, required=True)
    ap.add_argument("--branches-json", type=Path, required=True)
    ap.add_argument("--tags-json", type=Path, required=True)
    ap.add_argument("--releases-json", type=Path, required=True)
    ap.add_argument("--owner-repos-json", type=Path, required=True)
    ap.add_argument("--issues-json", type=Path, required=True)
    ap.add_argument("--claw-eval-commit-json", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    a = ap.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    assert sha256_file(a.moss_main_archive) == MOSS_MAIN_ARCHIVE_SHA256
    assert sha256_file(a.moss_tag_archive) == MOSS_TAG_ARCHIVE_SHA256
    assert sha256_file(a.claw_eval_archive) == CLAW_EVAL_ARCHIVE_SHA256
    assert sha256_file(a.arxiv_source) == ARXIV_SOURCE_SHA256

    repo = load(a.repo_json)
    branches = load(a.branches_json)
    tags = load(a.tags_json)
    releases = load(a.releases_json)
    owner_repos = load(a.owner_repos_json)
    issues = load(a.issues_json)
    claw_commit = load(a.claw_eval_commit_json)
    assert isinstance(repo, dict) and repo["default_branch"] == "main"
    assert isinstance(branches, list) and len(branches) == 1
    assert branches[0]["name"] == "main" and branches[0]["commit"]["sha"] == MOSS_COMMIT
    assert isinstance(tags, list) and len(tags) == 1
    assert tags[0]["name"] == "v0.1.0" and tags[0]["commit"]["sha"] == MOSS_TAG_COMMIT
    assert isinstance(releases, list) and len(releases) == 0
    assert isinstance(claw_commit, dict) and claw_commit["sha"] == CLAW_EVAL_COMMIT

    main_members = normalized_members(a.moss_main_archive)
    tag_members = normalized_members(a.moss_tag_archive)
    claw_members = normalized_members(a.claw_eval_archive)
    with tarfile.open(a.arxiv_source, "r:gz") as tf:
        arxiv_members = tf.getnames()
        arxiv_text = "\n".join(
            tf.extractfile(m).read().decode("utf-8", "replace")
            for m in arxiv_members
            if m.endswith((".tex", ".bib", ".json")) and tf.getmember(m).isfile()
        )

    trial = a.moss_source / "host-daemon/src/ops/trial_runner.py"
    user_mode = a.moss_source / "openclaw/src/evolution/modes/user-mode.ts"
    iteration = a.moss_source / "openclaw/src/evolution/iteration.ts"
    task_stage = a.moss_source / "openclaw/src/evolution/stages/task-evaluator.ts"
    task_prompt = a.moss_source / "openclaw/src/evolution/prompts/task-evaluator.md"
    flag_batch = a.moss_source / "openclaw/src/evolution/types/flag-batch.ts"
    for p in [trial, user_mode, iteration, task_stage, task_prompt, flag_batch]:
        assert p.is_file()

    trial_text = trial.read_text(encoding="utf-8")
    user_text = user_mode.read_text(encoding="utf-8")
    iteration_text = iteration.read_text(encoding="utf-8")
    assert REQUIRED_RUNNER in trial_text
    assert '"run", "-d", "--name", name' in trial_text
    assert '"-v", f"{iter_dir}:/iter_dir"' in trial_text
    assert "tools: []" in user_text
    assert "tool_endpoints: []" in user_text
    assert "services: []" in user_text
    assert "scoring_components: []" in user_text
    assert "taskId: t.task_id" in user_text and "userPrompt: t.prompt.text" in user_text
    assert "becomes the sole verdict-grounding signal" in iteration_text

    issue3 = next(i for i in issues if i.get("number") == 3)
    owner_repo_names = sorted(r["name"] for r in owner_repos)
    owner_companion_names = [n for n in owner_repo_names if "eval" in n.lower() or "benchmark" in n.lower()]

    protocol = {
        "authority": "OUTCOME_BLIND_PUBLIC_SOURCE_AND_ROUTE_PREFLIGHT_ONLY",
        "forbidden": [
            "MOSS/model/coding-agent execution",
            "benchmark or evaluator execution",
            "protected/gold/outcome access",
            "treating a proposed successor contract as released MOSS evidence",
        ],
        "frozen_at_utc": FROZEN_AT,
        "primary_question": "Does any public authoritative MOSS route instantiate the V7 C2 LANG-1 session, source, pre-action certificate, closed evaluator, and write-root bytes without changing the released arm?",
        "protocol_id": "P5.C2.AUTHORITATIVE.ROUTE.DISCRIMINATOR.V10",
        "routes": [
            "published demo/benchmark route",
            "released user-mode flag-batch route",
        ],
        "schema_version": "orion.p5.c2.authoritative-route-protocol.v10",
        "success_gate": "At least one released route must carry all five byte classes with explicit rights and no protected outcome, gold patch, hidden evaluator, or candidate feedback.",
    }
    dump(out / "P5_C2_V10_AUDIT_PROTOCOL.json", protocol)

    upstream = {
        "authority": "PUBLIC_GITHUB_PUBLICATION_SURFACE_SNAPSHOT__NOT_LEGAL_ADVICE",
        "checked_at_utc": FROZEN_AT,
        "arxiv_v2_source": {
            "archive_member_count": len(arxiv_members),
            "archive_sha256": ARXIV_SOURCE_SHA256,
            "exact_required_runner_mentions": arxiv_text.count(REQUIRED_RUNNER),
            "moss_github_url_mentions": arxiv_text.count("https://github.com/hkgai-official/Moss"),
            "supplement_or_companion_archive_members": [
                m for m in arxiv_members if "supp" in m.lower() or "companion" in m.lower()
            ],
            "version": "arXiv:2605.22794v2",
            "verdict": "PAPER_SOURCE_POINTS_TO_THE_MOSS_REPOSITORY_BUT_CONTAINS_NO_BENCHMARK_COMPANION_OR_REQUIRED_RUNNER",
        },
        "claw_eval_pinned_companion_candidate": {
            "archive_member_count_including_root": len(claw_members),
            "archive_sha256": CLAW_EVAL_ARCHIVE_SHA256,
            "commit_sha": CLAW_EVAL_COMMIT,
            "exact_required_runner_matches": sum(p == REQUIRED_RUNNER for p in claw_members),
            "license_path_matches": sum(p == "LICENSE" for p in claw_members),
            "manifest_prefix_members": sum(p.startswith("manifests/") for p in claw_members),
            "repository": "https://github.com/claw-eval/claw-eval",
            "src_runner_members": sum(p.startswith("src/claw_eval/runner/") for p in claw_members),
            "task_prefix_members": sum(p.startswith("tasks/") for p in claw_members),
            "tree_sha": claw_commit["commit"]["tree"]["sha"],
            "verdict": "SUBSTANTIVE_BENCHMARK_SOURCE_BUT_NOT_THE_EXACT_RELEASED_MOSS_COMPANION_LAYOUT_AND_NO_ROOT_LICENSE_FILE_AT_PINNED_COMMIT",
        },
        "independent_public_issue": {
            "author": issue3["user"]["login"],
            "comments": issue3["comments"],
            "created_at": issue3["created_at"],
            "maintainer_reply_observed": False if issue3["comments"] == 0 else "CANNOT_INFER_FROM_COUNT",
            "number": 3,
            "role": "INDEPENDENT_CORROBORATION_ONLY__NOT_UPSTREAM_AUTHORITY",
            "state": issue3["state"],
            "title": issue3["title"],
            "url": issue3["html_url"],
        },
        "moss_account_public_repositories": {
            "companion_name_matches": owner_companion_names,
            "names": owner_repo_names,
            "returned_count": len(owner_repo_names),
        },
        "moss_main": {
            "archive_member_count_including_root": len(main_members),
            "archive_sha256": MOSS_MAIN_ARCHIVE_SHA256,
            "benchmark_prefix_members": sum(p.startswith("benchmark/") for p in main_members),
            "commit_sha": MOSS_COMMIT,
            "exact_required_runner_matches": sum(p == REQUIRED_RUNNER for p in main_members),
            "pushed_at": repo["pushed_at"],
        },
        "moss_public_refs": {
            "branches": [{"name": b["name"], "sha": b["commit"]["sha"]} for b in branches],
            "releases": len(releases),
            "tags": [{"name": t["name"], "sha": t["commit"]["sha"]} for t in tags],
        },
        "moss_v0_1_0": {
            "archive_member_count_including_root": len(tag_members),
            "archive_sha256": MOSS_TAG_ARCHIVE_SHA256,
            "benchmark_prefix_members": sum(p.startswith("benchmark/") for p in tag_members),
            "commit_sha": MOSS_TAG_COMMIT,
            "exact_required_runner_matches": sum(p == REQUIRED_RUNNER for p in tag_members),
        },
        "scope_caveat": "This is the unauthenticated public GitHub surface returned at the checked time, not a claim about private or unpublished materials.",
        "schema_version": "orion.p5.c2.upstream-publication-snapshot.v10",
        "source_response_sha256": {
            "branches": sha256_file(a.branches_json),
            "claw_eval_commit": sha256_file(a.claw_eval_commit_json),
            "issues": sha256_file(a.issues_json),
            "owner_repositories": sha256_file(a.owner_repos_json),
            "releases": sha256_file(a.releases_json),
            "repository": sha256_file(a.repo_json),
            "tags": sha256_file(a.tags_json),
        },
    }
    dump(out / "P5_C2_V10_UPSTREAM_PUBLICATION_RECEIPT.json", upstream)

    route = {
        "authority": "PINNED_SOURCE_STATIC_ROUTE_AUDIT_ONLY",
        "commit_sha": MOSS_COMMIT,
        "demo_route": {
            "exact_required_runner_present_in_archive": False,
            "line_evidence": "trial_runner.py:40-45 resolves benchmark/claw-eval/runner/benchmark.py",
            "state": "BLOCKING",
        },
        "excerpts": [
            excerpt(trial, 40, 45),
            excerpt(trial, 599, 612),
            excerpt(trial, 626, 678),
            excerpt(user_mode, 38, 64),
            excerpt(user_mode, 93, 112),
            excerpt(iteration, 291, 301),
            excerpt(task_stage, 25, 42),
        ],
        "schema_version": "orion.p5.c2.pinned-source-route-audit.v10",
        "source_files": {
            "flag_batch.ts": sha256_file(flag_batch),
            "iteration.ts": sha256_file(iteration),
            "task-evaluator.md": sha256_file(task_prompt),
            "task-evaluator.ts": sha256_file(task_stage),
            "trial_runner.py": sha256_file(trial),
            "user-mode.ts": sha256_file(user_mode),
        },
        "user_mode_route": {
            "closed_public_evaluator_implementation_bound": False,
            "common_lang1_source_archive_mount_bound": False,
            "complete_write_root_bound": False,
            "host_pre_action_certificate_forwarded": False,
            "only_task_fields_forwarded": ["task_id", "user_prompt"],
            "task_definition_empty_fields": ["tools", "tool_endpoints", "services", "scoring_components"],
            "trial_worker_volume_mounts": ["iter_dir:/iter_dir"],
            "verdict_signal": "LLM task-evaluator role is the sole verdict-grounding signal when gradeSummaryPath is undefined",
            "state": "BLOCKING_FOR_V7_LANG1_NATIVE_TASK_ENVIRONMENT",
        },
    }
    dump(out / "P5_C2_V10_PINNED_SOURCE_ROUTE_RECEIPT.json", route)

    contract = {
        "authority": "PROSPECTIVE_SUCCESSOR_ACCEPTANCE_CONTRACT_ONLY__NOT_RELEASED_MOSS_EVIDENCE",
        "field_target": "runtime.task_environment",
        "forbidden_keys_recursive": [
            "protected_score", "gold_patch", "gold", "hidden_panel_id", "expected_patch", "scorer_feedback"
        ],
        "required_byte_classes": [
            {
                "id": "session",
                "requirement": "one authored or explicitly licensed FlagSnapshot/session with complete chunk hashes and no outcome-selected content",
            },
            {
                "id": "source_mount",
                "requirement": "the V6 LANG-1 archive mounted read-only, with an ephemeral copy/overlay exposing only NumberUtils.java as writable",
            },
            {
                "id": "pre_action_certificate",
                "requirement": "a host-issued input-native V3 certificate before candidate action; synthetic-domain proof must not be relabelled as a natural-case proof",
            },
            {
                "id": "public_evaluator",
                "requirement": "closed public-development evaluator implementation and setup bytes, held outside the candidate write surface",
            },
            {
                "id": "write_reset_policy",
                "requirement": "complete allowed/forbidden roots, before/after digests, and per-attempt destruction/reset bytes",
            },
            {
                "id": "route_adapter",
                "requirement": "a separately named content-addressed adapter that actually forwards/mounts the preceding bytes; no silent claim that it is released MOSS",
            },
        ],
        "schema_version": "orion.p5.c2.successor-byte-contract.v10",
        "successor_identity_requirement": "Distinct method identity from C2_DIRECT_SELF_EDIT__MOSS at commit 5453f1f unless upstream publishes the exact companion and rights.",
    }
    dump(out / "P5_C2_V10_SUCCESSOR_BYTE_CONTRACT.json", contract)

    result = {
        "arm_id": "C2_DIRECT_SELF_EDIT__MOSS",
        "arm_or_model_executed": False,
        "exact_finding": "Both public MOSS routes are exhausted for the V7 LANG-1 native-environment gate: demo mode resolves an absent benchmark runner; user mode forwards only task_id/user_prompt, mounts only iter_dir, binds no common source/evaluator/certificate/write-root bytes, and uses an LLM task-evaluator as its sole verdict signal.",
        "field_instances_closed": 0,
        "field_target": "runtime.task_environment",
        "next_discriminator": "Either obtain a maintainer-published content-addressed companion with explicit rights, or materialize all six byte classes in P5_C2_V10_SUCCESSOR_BYTE_CONTRACT.json under a distinct successor identity; then rerun only the byte/route gate before any model execution.",
        "preserved": {
            "c2_v4_bound_fields": 7,
            "c2_v4_blocking_fields": 14,
            "panel_confirmatory_ready": "0/6",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "top_tier_publication_readiness": "NOT_ESTABLISHED",
        },
        "protocol_id": protocol["protocol_id"],
        "schema_version": "orion.p5.c2.authoritative-route-result.v10",
        "status": "BLOCKING",
        "terminal": "P5_C2_V10_BOTH_RELEASED_TASK_ROUTES_EXHAUSTED__NO_AUTHORITATIVE_COMPANION__USER_MODE_LACKS_LANG1_SOURCE_CERTIFICATE_CLOSED_EVALUATOR_AND_WRITE_ROOT__RUNTIME_TASK_ENVIRONMENT_BLOCKING__ZERO_OF_SIX_READY__PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK",
    }
    dump(out / "P5_C2_V10_RESULT.json", result)

    ledger = {
        "entries": [
            {
                "cause": "The public main and v0.1.0 publication surfaces contain zero benchmark/ members although the pinned demo trial runner resolves the exact missing runner path.",
                "id": "P5.C2.V10.DEMO.ROUTE",
                "next_discriminator": "Maintainer publishes the exact content-addressed companion plus rights, or the experiment adopts a distinctly named successor.",
                "positive_progress": "The absence is now checked across every returned public MOSS branch, tag and release rather than one commit only.",
                "residual": "Released demo-mode task execution remains unavailable.",
            },
            {
                "cause": "Released user mode reduces each task to task_id/user_prompt, gives the task definition no tools/endpoints/services/scoring components, mounts only iter_dir, and delegates signal to an LLM role.",
                "id": "P5.C2.V10.USER.ROUTE",
                "next_discriminator": "Freeze the six-byte successor contract and prove the source/evaluator/certificate/write roots are actually forwarded outside candidate control.",
                "positive_progress": "A reachable native alternative was evaluated instead of treating the absent demo runner as the only possible route.",
                "residual": "The V6 LANG-1 source, closed evaluator, pre-action certificate and complete write surface do not enter the released route.",
            },
            {
                "cause": "The pinned claw-eval source is substantive but is not a drop-in companion: it has no exact runner/manifests layout and no root LICENSE file at that commit.",
                "id": "P5.C2.V10.CLAW.EVAL.CANDIDATE",
                "next_discriminator": "Obtain an explicit upstream mapping/release and licence bytes; do not infer integration or rights from repository naming or a README badge.",
                "positive_progress": "The nearest public benchmark candidate is separately content-addressed and distinguished from the missing MOSS integration layer.",
                "residual": "It cannot lawfully close runtime.task_environment or task/benchmark rights by silent vendoring.",
            },
        ],
        "schema_version": "orion.p5.c2.negative-ledger.v10",
    }
    dump(out / "P5_C2_V10_NEGATIVE_LEDGER.json", ledger)

    md_rows = [
        "# P5 C2 V10 recursive negative-result ledger",
        "",
        "| ID | Cause | Positive progress | Residual | Next discriminator |",
        "|---|---|---|---|---|",
    ]
    for e in ledger["entries"]:
        md_rows.append("| `{id}` | {cause} | {positive_progress} | {residual} | {next_discriminator} |".format(**e))
    (out / "P5_C2_V10_NEGATIVE_LEDGER.md").write_text("\n".join(md_rows) + "\n", encoding="utf-8")

    report = f"""# P5 C2 authoritative-route discriminator V10

## Terminal

`{result['terminal']}`

## Exact finding

V10 did not run MOSS, a model, a coding agent, a benchmark, a scorer, or any
protected datum. It audited the pinned source routes and the public publication
surface. The released demo route resolves
`benchmark/claw-eval/runner/benchmark.py`, but the current public main archive
and the sole public tag contain zero `benchmark/` members. There are no public
releases in the returned API surface. The arXiv v2 source archive contains 12
members, points readers to the same MOSS repository, and contains neither the
required runner nor a supplementary/companion archive member.

The reachable user-mode route is not a lawful substitute for the V7 LANG-1
task environment. It forwards only `task_id` and `user_prompt`, creates a task
definition with empty tools/endpoints/services/scoring components, mounts only
`iter_dir`, and makes an LLM `task-evaluator` the sole verdict-grounding signal.
It therefore does not carry the frozen common source, a closed public evaluator,
the host pre-action certificate, or the complete write/reset declaration.

## Nearest public benchmark candidate

The issue-linked claw-eval commit `{CLAW_EVAL_COMMIT}` contains substantive
runner and task source, but zero exact `{REQUIRED_RUNNER}` paths, zero
`manifests/` members and no root `LICENSE` file at that commit. It is not the
missing MOSS integration layer and cannot be silently vendored as if it were.

## Scientific delta

The root cause is now a two-route exhaustion result, not merely a missing-file
observation. Zero field instances close: C2 stays 7/21 bound and 14/21 blocking;
the matched panel stays 0/6 ready. Performance and superiority remain
`CANNOT_CHECK`.

## Next discriminator

Upstream can close the released-route question by publishing the exact
content-addressed companion and explicit rights. Independently, a lawful
research successor can proceed only under a distinct identity after
materializing every byte class in `P5_C2_V10_SUCCESSOR_BYTE_CONTRACT.json`:
session, common-source mount, pre-action certificate, closed public evaluator,
complete write/reset policy, and an adapter that actually forwards those bytes.
The contract is prospective and is not evidence that such a successor exists.
"""
    (out / "SCIENTIFIC_REPORT_V10.md").write_text(report, encoding="utf-8")

    readme = """# P5 C2 authoritative-route discriminator V10

Outcome-blind source/publication audit for the next C2 native-environment gate.
Start with `SCIENTIFIC_REPORT_V10.md`, `P5_C2_V10_RESULT.json`, and the two
receipts. No arm/model/benchmark/protected scorer was run. The predecessor V4
and V7 evidence is preserved; this packet does not overwrite it.
    """
    (out / "README.md").write_text(readme, encoding="utf-8")

    artifact_names = [
        "P5_C2_V10_AUDIT_PROTOCOL.json",
        "P5_C2_V10_UPSTREAM_PUBLICATION_RECEIPT.json",
        "P5_C2_V10_PINNED_SOURCE_ROUTE_RECEIPT.json",
        "P5_C2_V10_SUCCESSOR_BYTE_CONTRACT.json",
        "P5_C2_V10_RESULT.json",
        "P5_C2_V10_NEGATIVE_LEDGER.json",
        "P5_C2_V10_NEGATIVE_LEDGER.md",
        "SCIENTIFIC_REPORT_V10.md",
        "README.md",
        "build_p5_c2_route_discriminator_v10.py",
        "validate_p5_c2_route_discriminator_v10.py",
    ]
    artifacts = [
        {
            "path": name,
            "sha256": sha256_file(out / name),
            "size_bytes": (out / name).stat().st_size,
        }
        for name in artifact_names
    ]
    manifest = {
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "exclusions": ["ARTIFACT_MANIFEST_V10.json", "SHA256SUMS", "VALIDATION_RECEIPT_V10.json"],
        "schema_version": "orion.p5.c2.artifact-manifest.v10",
    }
    dump(out / "ARTIFACT_MANIFEST_V10.json", manifest)
    (out / "SHA256SUMS").write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in artifacts),
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
