#!/usr/bin/env python3
"""Build the outcome-blind P5 V7 native task-environment packet.

The V7 protocol was frozen before this builder and its outputs.  This builder
does not execute any arm, model, benchmark, test suite, or protected scorer.
It binds C1 only, because that arm's remaining setup/configuration bytes can be
materialized from the already rights-cleared V6 case.  Every other arm remains
fail-closed on the smallest missing byte artifacts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DEVELOPMENT = HERE.parent
FROZEN_AT = "2026-08-23T20:25:39Z"
PROTOCOL = HERE / "P5_NATIVE_TASK_ENVIRONMENT_PROTOCOL_V7.json"
PROTOCOL_SHA256 = "3a6cc70a0f91957ef4e7fbc5ec42e66875084f7985c2250c056e00d865aa4fe0"
V6 = DEVELOPMENT / "p5-common-visible-case-rights-v6-2026-08-23"

ARM_PACKETS = {
    "C1": "p5-swe-agent-execution-binding-v4-2026-08-23",
    "C2": "p5-moss-execution-binding-v4-2026-08-23",
    "C3": "p5-dgm-execution-binding-v4-2026-08-23",
    "C4": "p5-adias-execution-binding-v4-2026-08-23",
    "C5": "p5-double-ratchet-execution-binding-v4-2026-08-23",
    "C6": "p5-scienceclaw-execution-binding-v4-2026-08-23",
}

ARM_IDS = {
    "C1": "C1_FIXED_AGENT__SWE_AGENT",
    "C2": "C2_DIRECT_SELF_EDIT__MOSS",
    "C3": "C3_ARCHIVE_BASED_SELF_EDIT__DGM",
    "C4": "C4_ISSUE_CENTRIC_OPTIMIZATION__ADIAS",
    "C5": "C5_EVALUATOR_ONLY__DOUBLE_RATCHET_METRIC_ONLY",
    "C6": "C6_MODERN_SOURCE_GROUNDED__SCIENCECLAW",
}

TERMINAL = (
    "P5_V7_C1_NATIVE_TASK_ENVIRONMENT_BOUND__ONE_OF_SIX_ENVIRONMENTS_CLOSED__"
    "FIFTY_FIVE_OF_ONE_HUNDRED_TWENTY_SIX_FIELDS_BOUND__SEVENTY_ONE_BLOCKING__"
    "FIVE_R2_NATIVE_ENVIRONMENT_INSTANCES_REMAIN__ZERO_OF_SIX_READY__"
    "PERFORMANCE_AND_SUPERIORITY_CANNOT_CHECK"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_json(name: str, value: Any) -> None:
    (HERE / name).write_text(canonical(value), encoding="utf-8")


def write_text(name: str, value: str) -> None:
    (HERE / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(DEVELOPMENT.parent))


def reference(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}


def v4_reference(code: str, name: str) -> dict[str, Any]:
    return reference(DEVELOPMENT / ARM_PACKETS[code] / name)


def common_references() -> dict[str, Any]:
    return {
        "core_index": reference(V6 / "P5_SHARED_CASE_CORE_INDEX_V6.json"),
        "rights_manifest": reference(V6 / "P5_SHARED_CASE_RIGHTS_MANIFEST_V6.json"),
        "case_body": reference(V6 / "candidate_visible" / "CASE_BODY_V6.json"),
        "task_specification": reference(V6 / "candidate_visible" / "TASK_SPECIFICATION_V6.md"),
        "source_archive": reference(
            V6
            / "candidate_visible"
            / "source"
            / "commons-lang-396afc3e4693cfee182efe582455f2d97058c068.tar.gz"
        ),
    }


def materialize_c1_environment() -> dict[str, Any]:
    setup = r'''#!/bin/sh
set -eu

EXPECTED_ARCHIVE_SHA256="f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08"
MUTABLE_RELATIVE_PATH="src/main/java/org/apache/commons/lang3/math/NumberUtils.java"

if [ "$#" -ne 2 ]; then
  echo "usage: $0 SOURCE_ARCHIVE EMPTY_TASK_ROOT" >&2
  exit 64
fi

archive=$1
task_root=$2

actual_sha256=$(python3 - "$archive" <<'PY'
import hashlib, pathlib, sys
p = pathlib.Path(sys.argv[1])
h = hashlib.sha256()
with p.open("rb") as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        h.update(chunk)
print(h.hexdigest())
PY
)

if [ "$actual_sha256" != "$EXPECTED_ARCHIVE_SHA256" ]; then
  echo "source archive SHA-256 mismatch" >&2
  exit 65
fi

if [ -e "$task_root" ]; then
  echo "task root must not exist before setup" >&2
  exit 66
fi

mkdir -p "$task_root"
tar -xzf "$archive" --strip-components=1 -C "$task_root"

if [ ! -f "$task_root/$MUTABLE_RELATIVE_PATH" ]; then
  echo "required mutable file missing after extraction" >&2
  exit 67
fi

# Candidate task setup is offline.  The host runner separately enforces the
# V4 write-surface receipt.  These modes make every existing member read-only
# except the single declared source file, without granting directory creation.
find "$task_root" -type d -exec chmod 0555 {} +
find "$task_root" -type f -exec chmod 0444 {} +
chmod 0644 "$task_root/$MUTABLE_RELATIVE_PATH"

printf '%s\n' "P5_C1_TASK_SETUP_V7_OK"
'''
    write_text("P5_C1_TASK_SETUP_V7.sh", setup)
    setup_ref = reference(HERE / "P5_C1_TASK_SETUP_V7.sh")

    config = {
        "schema_version": "orion.p5.c1.effective-agent-config.v7",
        "arm_id": ARM_IDS["C1"],
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "agent": {
            "type": "default",
            "action_sampler": None,
            "retry_agent": False,
            "max_candidate_attempts": 1,
            "review_on_submit_m": False,
            "chooser_or_reviewer_loop": False,
            "tools_bundles": ["tools/registry", "tools/edit_anthropic"],
            "actions": {"open_pr": False, "apply_patch_locally": False},
        },
        "task": {
            "repository": "https://github.com/apache/commons-lang",
            "commit": "396afc3e4693cfee182efe582455f2d97058c068",
            "tree": "34e33cca607f33ffcf8661e3a6c4b7fc5aca9701",
            "archive_sha256": "f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08",
            "problem_statement_sha256": "a455eec2d32b031b6e49d06c73e0cf3befbe9e2cd461e5417efbade5f39f5098",
            "mutable_paths": ["src/main/java/org/apache/commons/lang3/math/NumberUtils.java"],
            "all_other_archive_members_read_only": True,
            "network_during_setup": "DENY",
        },
        "setup": setup_ref,
        "outcome_and_gold_payloads_present": False,
        "execution_authorized_by_v7": False,
    }
    write_json("P5_C1_EFFECTIVE_AGENT_CONFIG_V7.json", config)
    return {
        "setup": setup_ref,
        "effective_agent_config": reference(HERE / "P5_C1_EFFECTIVE_AGENT_CONFIG_V7.json"),
    }


def blocked_manifest(
    code: str,
    *,
    satisfied: list[str],
    missing: list[str],
    residual: str,
    next_discriminator: str,
    observations: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "orion.p5.native-task-environment-manifest.v7",
        "arm_code": code,
        "arm_id": ARM_IDS[code],
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "status": "BLOCKING",
        "authority": "BYTE_LEVEL_PREFLIGHT_ONLY",
        "satisfied_criteria": satisfied,
        "missing_byte_artifacts": missing,
        "observations": observations,
        "residual": residual,
        "next_discriminator": next_discriminator,
        "future_or_planned_bytes_promoted_to_evidence": False,
        "arm_or_model_executed": False,
        "predecessor": {
            "field_registry": v4_reference(code, f"P5_{code}_V4_FIELD_REGISTRY.json"),
            "candidate_requirements": v4_reference(
                code, f"P5_{code}_V4_CANDIDATE_VISIBLE_CASE_REQUIREMENTS.json"
            ),
        },
        "shared_core": common_references(),
    }


def main() -> None:
    if sha256(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("V7 protocol changed after freeze")

    common = common_references()
    if common["source_archive"]["sha256"] != "f97c316795a6ba124f693bce9e8019b1735bc976affa9bce8d4c52f668575f08":
        raise RuntimeError("V6 source archive identity changed")

    c1_artifacts = materialize_c1_environment()
    c1 = {
        "schema_version": "orion.p5.native-task-environment-manifest.v7",
        "arm_code": "C1",
        "arm_id": ARM_IDS["C1"],
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "status": "BOUND",
        "authority": "OUTCOME_BLIND_BYTE_LEVEL_TASK_ENVIRONMENT_ONLY",
        "environment_id": "P5-C1-LANG1-FIXED-AGENT-V7",
        "shared_core": common,
        "task_seed": {
            "repository": "https://github.com/apache/commons-lang",
            "commit": "396afc3e4693cfee182efe582455f2d97058c068",
            "tree": "34e33cca607f33ffcf8661e3a6c4b7fc5aca9701",
            "archive": common["source_archive"],
        },
        "environment_artifacts": c1_artifacts,
        "native_binding": {
            "protocol": v4_reference("C1", "P5_C1_V4_EXECUTION_BINDING_PROTOCOL.json"),
            "field_registry": v4_reference("C1", "P5_C1_V4_FIELD_REGISTRY.json"),
            "source_rights": v4_reference("C1", "P5_C1_V4_SOURCE_RIGHTS_MANIFEST.json"),
            "runner": v4_reference("C1", "p5_c1_isolated_runner.py"),
            "parser": v4_reference("C1", "p5_c1_native_parser.py"),
            "dependency_lock": v4_reference("C1", "SWE_AGENT_DEPENDENCY_LOCK_V4.uv.lock"),
        },
        "policy": {
            "retry_agent": False,
            "action_sampler": None,
            "review_on_submit_m": False,
            "chooser_or_reviewer_loop": False,
            "open_pr": False,
            "setup_network": "DENY",
            "gold_or_outcome_payloads": False,
        },
        "criteria_satisfied": [
            "exact shared source archive/repository identity",
            "byte-frozen setup specification",
            "byte-frozen effective default-agent configuration",
            "retry agent disabled",
            "action sampler disabled",
            "review disabled",
            "open-PR behavior disabled",
            "native tool/write policy",
        ],
        "field_scope": "runtime.task_environment only",
        "arm_or_model_executed": False,
        "runtime_or_container_identity_claimed": False,
        "performance_or_superiority_claimed": False,
        "residual_outside_field": "C1 remains non-ready because nine unrelated V6 field instances remain blocking.",
    }

    c2 = blocked_manifest(
        "C2",
        satisfied=["shared core identity and rights"],
        missing=[
            "case-specific authored/licensed native session bytes",
            "host-issued pre-action minimal-class certificate instance",
            "closed public evaluator implementation bytes",
            "complete write-root declaration bytes",
        ],
        residual=(
            "MOSS commit 5453f1feebad44c199f5887f852fc5bc7fb7d4da requires but omits "
            "benchmark/claw-eval/runner/benchmark.py, benchmark/claw-eval/src, and the "
            "manifests/tasks/results layout; V4 schemas do not instantiate the four missing artifacts."
        ),
        next_discriminator=(
            "Freeze one separately named P5-native MOSS successor containing the session, "
            "certificate, evaluator, and write-root bytes with explicit rights, or obtain the "
            "authoritative benchmark companion release."
        ),
        observations=["No benchmark companion payload was found in the V4 packet or development tree."],
    )

    c3 = blocked_manifest(
        "C3",
        satisfied=[
            "shared core identity and rights",
            "DGM source identity and outcome-prefix names",
            "native parser and fail-closed runner identity",
        ],
        missing=[
            "content-addressed filtered DGM seed excluding initial/, initial_polyglot/, and swe_bench/ref_agent_results/",
            "case-specific pre-action input-native certificate instance",
            "byte-level mutable-agent versus immutable-host split manifest",
            "case-specific endpoint/tool/write policy bytes",
            "exact P5 DGM invocation/environment bytes",
        ],
        residual=(
            "V4 records 1,595 excluded outcome/initial files and a full archive identity, but no "
            "candidate-safe filtered seed or case-specific certificate/policy/environment artifact exists."
        ),
        next_discriminator=(
            "Build a filtered DGM seed from commit a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2, "
            "then freeze the pre-action certificate, tree split, and exact deny-default P5 invocation."
        ),
        observations=["The full DGM archive cannot substitute for the required outcome-free candidate seed."],
    )

    c4 = blocked_manifest(
        "C4",
        satisfied=[
            "shared core identity and rights",
            "ADIAS source identity, parser, and runner identity",
            "six retained native-domain names are known",
        ],
        missing=[
            "P5 LANG-1-compatible ADIAS domain adapter implementation bytes",
            "domain data/environment bytes for the shared Java repair case",
            "case-specific task-id/seed/turn/step/evaluation-limit configuration",
        ],
        residual=(
            "The six retained native ADIAS domains are alfworld, taubench_return, taubench_retail, "
            "textcraft, webshop, and scienceworld; none implements the V6 Apache Commons Lang patch task. "
            "Choosing one by name or declaring limits without adapter bytes would change task semantics."
        ),
        next_discriminator=(
            "Preregister a separately named ADIAS P5 software-repair domain successor, implement its "
            "environment against only the V6 core, and freeze task ID, seed, turns, steps, samples, and "
            "all implementation/data hashes while continuing to exclude bundled ADIAS task data."
        ),
        observations=["No ADIAS domain/model job or bundled task data was accessed or executed."],
    )

    c5 = blocked_manifest(
        "C5",
        satisfied=[
            "shared core identity and rights",
            "Double Ratchet source identity",
            "solver.py and prompts.py source hashes recorded by V4",
        ],
        missing=[
            "fixed train membership bytes",
            "fixed eval-dev membership bytes",
            "fixed development-only locked-surrogate membership bytes",
            "frozen solver outputs for every development item",
            "development soft-anchor bytes and provenance",
            "external pre-action EVALUATOR_REPAIR certificate instance",
            "generated-output rights disposition",
        ],
        residual=(
            "The workspace contains schemas and source metadata but no frozen solver-output artifact or "
            "complete development membership/anchor/certificate/rights bundle; the official runner "
            "regenerates hosted outputs and reports eval_locked each round."
        ),
        next_discriminator=(
            "Acquire or lawfully generate solver outputs before metric evolution, then freeze disjoint "
            "development memberships, soft anchors, the external certificate, and generated-output rights."
        ),
        observations=["No schema or planned future solver output was promoted to byte evidence."],
    )

    c6 = blocked_manifest(
        "C6",
        satisfied=[
            "shared core identity and rights",
            "ScienceClaw source commit/tree and prior-outcome prefix names",
            "native draft parser and outer wallclock identity",
        ],
        missing=[
            "case-specific topic byte artifact",
            "allowed source-corpus manifest bytes",
            "allowed skill and exact tool-parameter bytes",
            "candidate-safe filtered ScienceClaw source seed bytes",
            "outcome-prefix exclusion receipt over the actual seed",
            "exact profile and memory/artifact reset policy bytes",
        ],
        residual=(
            "V4 records the ScienceClaw tree and excluded prefixes but no actual filtered seed, topic, "
            "corpus, skill/tool, profile, or reset artifacts exist; a free-form topic declaration is not "
            "a native task environment."
        ),
        next_discriminator=(
            "Construct a prior-outcome-free source seed from commit 38b2f681e87272cd505c9b2671760fc3729756c2, "
            "then freeze one V6-derived topic, local allowed corpus, rights-cleared skills/tools, and an "
            "exact clean-profile/reset manifest."
        ),
        observations=["Source-bundled benchmarks/, categoryscienceclaw/HEA/, and tracked bytecode remain excluded."],
    )

    manifests = {"C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5, "C6": c6}

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://orion.invalid/p5/v7/native-task-environment-manifest.schema.json",
        "title": "P5 V7 native task-environment manifest",
        "type": "object",
        "required": ["schema_version", "arm_code", "arm_id", "case_id", "status", "authority", "shared_core"],
        "properties": {
            "schema_version": {"const": "orion.p5.native-task-environment-manifest.v7"},
            "arm_code": {"enum": sorted(ARM_IDS)},
            "arm_id": {"enum": [ARM_IDS[c] for c in sorted(ARM_IDS)]},
            "case_id": {"const": "P5-PUBLIC-LANG1-COMMON-001"},
            "status": {"enum": ["BOUND", "BLOCKING"]},
            "authority": {"type": "string", "minLength": 1},
            "shared_core": {"type": "object"},
        },
        "additionalProperties": True,
    }
    write_json("P5_NATIVE_TASK_ENVIRONMENT_MANIFEST_SCHEMA_V7.json", schema)

    receipts = []
    for code in sorted(manifests):
        manifest_name = f"P5_{code}_NATIVE_TASK_ENVIRONMENT_MANIFEST_V7.json"
        write_json(manifest_name, manifests[code])
        manifest_ref = reference(HERE / manifest_name)
        status = manifests[code]["status"]
        receipt = {
            "schema_version": "orion.p5.native-task-environment-acceptance.v7",
            "arm_code": code,
            "arm_id": ARM_IDS[code],
            "case_id": "P5-PUBLIC-LANG1-COMMON-001",
            "field": "runtime.task_environment",
            "status": status,
            "manifest": manifest_ref,
            "protocol_sha256": PROTOCOL_SHA256,
            "arm_or_model_executed": False,
            "field_instances_closed": 1 if status == "BOUND" else 0,
            "residual": manifests[code].get("residual") if status == "BLOCKING" else None,
        }
        receipt_name = f"P5_{code}_NATIVE_TASK_ENVIRONMENT_ACCEPTANCE_V7.json"
        write_json(receipt_name, receipt)
        receipts.append({**receipt, "receipt": reference(HERE / receipt_name)})

    aggregate = {
        "schema_version": "orion.p5.six-arm-native-task-environment-acceptance.v7",
        "protocol_sha256": PROTOCOL_SHA256,
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "authority": "OUTCOME_BLIND_BYTE_LEVEL_TASK_ENVIRONMENT_ACCEPTANCE_ONLY",
        "accepted_arm_count": 1,
        "blocking_arm_count": 5,
        "accepted_arms": ["C1"],
        "blocking_arms": ["C2", "C3", "C4", "C5", "C6"],
        "receipts": receipts,
        "arm_or_model_executions": 0,
    }
    write_json("P5_SIX_ARM_NATIVE_TASK_ENVIRONMENT_ACCEPTANCE_V7.json", aggregate)

    after_per_arm = {
        "C1": {"bound": 12, "blocking": 9},
        "C2": {"bound": 9, "blocking": 12},
        "C3": {"bound": 8, "blocking": 13},
        "C4": {"bound": 8, "blocking": 13},
        "C5": {"bound": 11, "blocking": 10},
        "C6": {"bound": 7, "blocking": 14},
    }
    result = {
        "schema_version": "orion.p5.native-task-environment-fanout-result.v7",
        "protocol_id": "P5.NATIVE.TASK.ENVIRONMENT.FANOUT.V7",
        "protocol_sha256": PROTOCOL_SHA256,
        "authority": "OUTCOME_BLIND_BYTE_LEVEL_TASK_ENVIRONMENT_ACCEPTANCE_ONLY",
        "case_id": "P5-PUBLIC-LANG1-COMMON-001",
        "field_delta": {
            "before_bound": 54,
            "before_blocking": 72,
            "new_bindings": 1,
            "after_bound": 55,
            "after_blocking": 71,
            "ready_arms": 0,
            "per_arm": after_per_arm,
        },
        "root_r2": {
            "before_blocking_instances": 6,
            "native_environment_instances_closed": 1,
            "after_blocking_instances": 5,
            "smallest_remaining_root": "Five arm-specific environment artifact bundles, not one shared blocker.",
        },
        "executions": {"arms": 0, "models": 0, "benchmarks": 0, "protected_scorers": 0, "outcomes_accessed": 0},
        "preserved_claims": {
            "H1_H4": "CANNOT_CHECK",
            "performance": "CANNOT_CHECK",
            "superiority": "CANNOT_CHECK",
            "top_tier_publication_readiness": "NOT_ESTABLISHED",
        },
        "terminal": TERMINAL,
    }
    write_json("P5_NATIVE_TASK_ENVIRONMENT_RESULT_V7.json", result)

    ledger_entries = []
    for code in ["C2", "C3", "C4", "C5", "C6"]:
        m = manifests[code]
        ledger_entries.append(
            {
                "id": f"V7-{code}-TASK-ENVIRONMENT-BYTES",
                "arm_id": ARM_IDS[code],
                "cause": m["observations"][0],
                "residual": m["residual"],
                "next_discriminator": m["next_discriminator"],
                "missing_byte_artifacts": m["missing_byte_artifacts"],
            }
        )
    ledger = {
        "schema_version": "orion.p5.native-task-environment-negative-ledger.v7",
        "authority": "MATHEMATICAL_AND_SCIENTIFIC_RESIDUAL_PROVENANCE",
        "entries": ledger_entries,
        "terminal": TERMINAL,
    }
    write_json("P5_NATIVE_TASK_ENVIRONMENT_NEGATIVE_LEDGER_V7.json", ledger)
    md = [
        "# P5 V7 native task-environment residual ledger",
        "",
        "C1 is closed. The five remaining entries are concrete research/engineering discriminators; no schema or future promise is counted as evidence.",
        "",
    ]
    for entry in ledger_entries:
        md += [
            f"## {entry['id']}",
            "",
            f"- **Cause:** {entry['cause']}",
            f"- **Residual:** {entry['residual']}",
            f"- **Next discriminator:** {entry['next_discriminator']}",
            "- **Missing bytes:**",
        ]
        md.extend(f"  - {item}" for item in entry["missing_byte_artifacts"])
        md.append("")
    write_text("P5_NATIVE_TASK_ENVIRONMENT_NEGATIVE_LEDGER_V7.md", "\n".join(md))

    report = f"""# P5 native task-environment fan-out — V7

## Result

V7 uses the V6 common LANG-1 case and the six V4 arm contracts. It closes the
C1 `runtime.task_environment` field by materializing exact offline setup bytes
and an effective fixed-agent configuration. It does not run an arm or model.

| Quantity | V6 | V7 | Delta |
|---|---:|---:|---:|
| Bound field instances | 54 | 55 | +1 |
| Blocking field instances | 72 | 71 | -1 |
| R2 task-environment blockers | 6 | 5 | -1 |
| Execution-ready arms | 0 | 0 | 0 |

## Why only C1 closes

C1's missing environment consisted of setup/configuration bytes that can be
authored without native data, outcomes, or execution. The setup verifies the
rights-cleared V6 source archive, stages it offline, and makes only
`NumberUtils.java` writable. The config disables retries, sampling, review,
chooser/reviewer loops, local patch application, and open-PR behavior.

C2 lacks a substantive session/certificate/evaluator/write-root packet; C3
lacks a filtered DGM seed and case-specific certificate/policies; C4 has no
retained native domain implementing the shared Java repair task; C5 lacks
frozen solver outputs and development memberships; C6 lacks an actual filtered
seed/topic/corpus/skill/profile environment. Creating filenames or pointing to
schemas would not satisfy the preregistered byte-level rule.

## Boundary

This is task-environment evidence only. It does not bind the other 120 field
instances, authorize execution, measure performance, or establish superiority.

**Terminal:** `{TERMINAL}`
"""
    write_text("SCIENTIFIC_REPORT_V7.md", report)
    write_text("TERMINAL_V7.txt", TERMINAL)


if __name__ == "__main__":
    main()
