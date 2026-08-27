#!/usr/bin/env python3
"""Fail-closed verifier for the ORION-01--05 convergence evidence layer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any
import zipfile


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "DONOR_MANIFEST_V1.json"
STATUS = HERE / "SCIENCE_STATUS_V1.json"

CONVERGENCE_TERMINAL = (
    "ORION_01_05_CONVERGENCE_V1_EVIDENCE_BOUND__SCIENCE_CLOSURE_OPEN__"
    "SUBMISSION_NOT_YET_AUTHORIZED"
)
R30_TERMINAL = "R30_NOT_MATERIALIZED__CUSTODY_AND_FINAL_BINDING_FAILED"
R18_TERMINAL = "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE"
R19_TERMINAL = "FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS"
BNSL_NULL = "C_R20_BNSL_ADAPTIVE_NULL__FREE_STATIC_REPRESENTATION_ALREADY_VBS"
BNSL_QUARANTINE = "QUARANTINED_OVERLAPPING_MATERIAL_AND_NULL_PREDICATES_AT_ZERO"
NQ_FAILURE = (
    "NQ_CRB_FULL_REPLAY_JOB_3544056_FAILED_CENSUS_RECEIPT_SERIALIZATION__"
    "D2_D3_AUTHORITY_CANNOT_CHECK"
)
CANNOT_REVERIFY_DONOR = "CANNOT_REVERIFY_COMMIT_PATH__DESTINATION_BLOB_ONLY"

ALLOWED_EXACT_PATHS = {
    ".github/workflows/orion-01-05-convergence-v1.yml",
    "papers/README.md",
}
ALLOWED_ADDITIVE_PREFIXES = (
    "papers/orion-01-certificate-realization/evidence/convergence-v1/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r11/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r14/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r15/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r16/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r17/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r18-relative/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r18/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r19/",
    "papers/orion-02-fiberguard-finite-fibre/extensions/r20/",
    "papers/orion-03-typed-merge-falsification/evidence/convergence-v1/",
    "papers/orion-04-rooted-completion-certificates/evidence/convergence-v1/",
    "papers/orion-04-rooted-completion-certificates/evidence/crb-full-replay/"
    "post-execution/job-3544056/",
    "papers/orion-05-tare-expressivity/evidence/convergence-v1/",
    "research/orion-01-05-convergence-v1/",
)

COMMON_FALSE_AUTHORITY_KEYS = (
    "production_authority_established",
    "external_independence_established",
    "novelty_authority_established",
    "journal_authority_established",
    "submission_authorized",
)

EXPECTED_ROUNDS = {
    "ORION-01": {
        "consumed": 0,
        "maximum": 3,
        "current": "ROUND_1_DESIGNED_NOT_EXECUTED",
    },
    "ORION-02": {
        "consumed": 1,
        "maximum": 3,
        "current": "ROUND_1_CONSUMED_AS_NULL",
    },
    "ORION-03": {
        "consumed": 0,
        "maximum": 3,
        "current": "ROUND_1_DESIGNED_NOT_EXECUTED",
    },
    "ORION-04": {
        "d4_consumed": 0,
        "maximum": 3,
        "current": "FULL_REPLAY_PREREQUISITE_FAILED",
    },
    "ORION-05": {
        "consumed": 0,
        "maximum": 3,
        "current": "ROUND_1_THEOREM_CANDIDATE_UNDER_DISPOSITION",
    },
}

EXPECTED_COORDINATOR_ISSUES = {
    "ORION-01": [1513, 1520],
    "ORION-02": [1512, 1519],
    "ORION-03": [1514, 1521],
    "ORION-04": [1516, 1522],
    "ORION-05": [1511, 1518, 1523],
}

EXPECTED_CLAIM_LEDGER_DISPOSITIONS = {
    "ORION-01": [
        {
            "path": "papers/orion-01-certificate-realization/theory-A-CLAIM_LEDGER_R2.md",
            "baseline_blob": "c69b3ea30e3ffe440d75b258183ac9f80bdc4a12",
            "sha256": "3c2a7771774856e2de2d18cf38f2b62c0e069301925a40624105349dd46d03db",
            "claim_dispositions": {
                "established_at_stated_ceiling": [
                    "A2-C1", "A2-C2", "A2-C3", "A2-C4", "A2-C5"
                ],
                "open_not_claimed": ["A2-C6", "A2-C7"],
                "forbidden": ["A2-C8"],
                "donor_owned": ["A2-C9"],
            },
        },
        {
            "path": "papers/orion-01-certificate-realization/theory-B-CLAIM_LEDGER_R2.md",
            "baseline_blob": "1d162bf1785aedd9f895f5030d2aa2a7b8257b27",
            "sha256": "d0a9539d27321dceb22df2717c795cede7358040537f2ded023fa5aa41446ea3",
            "claim_dispositions": {
                "established_at_stated_ceiling": [
                    "B2-C1", "B2-C2", "B2-C3", "B2-C4", "B2-C5", "B2-C6"
                ],
                "open_not_claimed": ["B2-C7"],
                "forbidden": ["B2-C8", "B2-C9"],
                "donor_owned": [],
            },
        },
    ],
    "ORION-02": [
        {
            "path": "papers/orion-02-fiberguard-finite-fibre/CLAIM_LEDGER_R2.md",
            "baseline_blob": "1be657586a176ad38adb6aa9c71154536e19df94",
            "sha256": "ed3401efb252526756451f5564154d4dce0fd991799d762631f01c95223558ab",
            "claim_dispositions": {
                "established_at_stated_ceiling": [
                    "C2-C1", "C2-C2", "C2-C3", "C2-C4", "C2-C5",
                    "C2-C6", "C2-C7", "C2-C8", "C2-C9",
                ],
                "open_not_claimed": ["C2-C10"],
                "forbidden": ["C2-C12"],
                "donor_owned": ["C2-C11"],
            },
        }
    ],
    "ORION-03": [
        {
            "path": "papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_R2.md",
            "baseline_blob": "d74eaab6b503e8c5dc4397431811ddb03f8a287c",
            "sha256": "cf0beac7ee9d9eb8003b0dbbe4922043a7e1ec78579820e8bdb21f722d84c339",
            "claim_dispositions": {
                "established_at_stated_ceiling": [
                    "D2-C1", "D2-C2", "D2-C3", "D2-C4",
                    "D2-C5", "D2-C6", "D2-C7",
                ],
                "open_not_claimed": ["D2-C9"],
                "forbidden": ["D2-C10"],
                "donor_owned": ["D2-C8"],
            },
        }
    ],
    "ORION-04": [
        {
            "path": "papers/orion-04-rooted-completion-certificates/CLAIM_LEDGER_R2.md",
            "baseline_blob": "4d92a18faa2087222f50e51dd874ce04b5e2fcc2",
            "sha256": "8b8998a517c1562033d7516ed2858287640e673e14c25a10c358e3d3c3932f41",
            "claim_dispositions": {
                "established_at_stated_ceiling": [
                    "N2-C1", "N2-C2", "N2-C3", "N2-C4",
                    "N2-C5", "N2-C6", "N2-C7",
                ],
                "bounded_computational_only": ["N2-C8"],
                "open_top_tier_blocker": ["N2-C9", "N2-C10", "N2-C11"],
                "forbidden": ["N2-C12", "N2-C13"],
            },
        }
    ],
    "ORION-05": [
        {
            "path": "papers/orion-05-tare-expressivity/CLAIM_LEDGER_V3.md",
            "baseline_blob": "527478f89f801ecd0e123fa44d3ef370bdfb5d28",
            "sha256": "c651a1c9fe49a4b3535b00e16353a16249a9e890de60dcd801e5c2b2db714aa7",
            "historical_header_disposition": (
                "Q1 maps to ORION-05; the stale ORION-01 heading is not canonical identity"
            ),
            "claim_dispositions": {
                "established_at_stated_ceiling": ["Q1V3-1", "Q1V3-2", "Q1V3-3"],
                "bounded_count_corollary_only": ["Q1V3-4"],
                "supporting_evidence_only": ["Q1V3-5"],
                "novelty_not_established": ["Q1V3-6"],
                "targeting_only": ["Q1V3-7"],
            },
        }
    ],
}

EXPECTED_CROSS_PAPER_OWNERS = {
    "ABSTRACT_CERTIFICATE_AND_PRODUCTION_REALIZATION": "ORION-01",
    "R6M_TARE_SUPPORT_EXPRESSIVITY": "ORION-05",
    "TYPED_AUTHORITY_OVER_D4_EVIDENCE": "ORION-03",
    "ROOTED_COMPLETION_AND_EXACT_D4": "ORION-04",
}

EXPECTED_STACK_PRS = {
    1471: ("375ce7bde60ab49abb46fa09f96cfc49b363dba8", 11),
    1475: ("0879974cfdfb2cccb8d50d1c9ed5f44b165e171f", 5),
    1485: ("e4e504fc94b86511040b484bc56496c6c70b10c9", 7),
    1488: ("4f957b1c308566300bd412605a63f29ca86a4399", 11),
    1489: ("64091190ff3386d08f8033885e37b0389b535f76", 11),
    1492: ("3c7ea359065be2b72953ea5aed60ebfec787a6dc", 54),
    1503: ("d8d71370f547031862cbf4376e88fa8e6be519fb", 3),
    1506: ("0caeb162b96cd965491f75012930de784cdfcbc8", 3),
    1534: ("d31075ee07a0a870b5705e6b149b9fa75029c2f5", 4),
}

EXPECTED_ACTION_ARTIFACTS = {
    (
        33023149716,
        9627389618,
        "fiberguard-paired-route-r18-recovery-ac4a50f85a147f5933cd2055809c7ac30b29e3c1",
        "a750d59572d28d17f63329bfb2ce2c633a081063f19d0d8c3c4bdbf45edb1fa1",
    ): {
        "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json": (
            255051,
            "e5a4bb3c913405ec10be0cd8db3e8091deb3a3f14a855f2a5402770071e336b9",
        ),
        "SHA256SUMS": (
            464,
            "dfbd5f433027ba4f527a85f7544f3c9c4ce78cf8279e6590617f820122020cf7",
        ),
        "RECOVERY_COMMENT.md": (
            1157,
            "41a5de9b857db02bbde9465a3c1345fde19f30dc07719f878a96f3741a457680",
        ),
        "TERMINAL.txt": (
            158,
            "e213fa6f4084ea9ed6b6b38504188d664675e919c23bc7f6111424b5463401cf",
        ),
    },
    (
        33047609008,
        9636339561,
        "five-paper-r30-final",
        "5b6188d5276dba7f081c7d2d3106cb2cef92588c577d15394848949ae7ffdba3",
    ): {
        "SHA256SUMS": (
            0,
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        ),
    },
    (
        33049783681,
        9637176781,
        "fiberguard-r20-bnsl-adaptive",
        "c5f2d5b5e93596ab82c03a2bd75cd441c74e6ac08b0265b281c3be7a516ab186",
    ): {
        "SHA256SUMS": (
            275,
            "218182b928149fe1b6b2d390886c3b5429fda0ae8142fadbb8b2482aedef0bb4",
        ),
        "TERMINAL.txt": (
            130,
            "d98dfd9b0bd7938b811c733a616dd7b7c30eef6a3b07c98eac8c2588873ff5fe",
        ),
        "FIBERGUARD_BNSL_ADAPTIVE_R20_RESULTS.json": (
            114803,
            "c843a0cb1c0a5a13863f27518e721cf8786334fba21a088f8ca4350ec947c49e",
        ),
    }
}

EXPECTED_R30_FAILURES = {
    33047609008: {
        "workflow": "one-shot-r30-finalize-internal-programme",
        "head_sha": "95592385f3d6dba64335d602a7d723212c8b21ad",
        "failed_step": "Materialize exact R18 result and R19 current subject",
        "cause": "STALE_R18_RESULT_SHA256",
    },
    33048246343: {
        "workflow": "one-shot-r30-recover-latest-failure",
        "head_sha": "0670f3c7379c8e29ec449cde2f3772cb8355ce22",
        "failed_step": "Diagnose, harden, and schedule one retry",
        "cause": "GITHUB_APP_WORKFLOW_UPDATE_REJECTED",
    },
    33048471274: {
        "workflow": "one-shot-r30-final-ensure",
        "head_sha": "155ac91341c3a6c00e621ae0eeb8207b1bfd3128",
        "failed_step": "Diagnose latest failed finalizer and schedule hardened retry",
        "cause": "GITHUB_APP_WORKFLOW_UPDATE_REJECTED",
    },
    33048664001: {
        "workflow": "one-shot-r30-clean-branch-recovery",
        "head_sha": "4f5fec5197e179a7364fce3d7a753a718de49f78",
        "failed_step": "Inspect clean-branch custody",
        "cause": "INTENDED_CLEAN_BRANCH_NOT_FOUND_HTTP_404",
    },
    33048836610: {
        "workflow": "one-shot-r30-author-handoff",
        "head_sha": "3b8da33ca691f7329b7d939e85940fa723f7dc5f",
        "failed_step": "Wait for green clean current-main custody",
        "cause": "INTENDED_CLEAN_BRANCH_NOT_FOUND_HTTP_404",
    },
    33048974820: {
        "workflow": "one-shot-r30-bind-final-status",
        "head_sha": "3c7ea359065be2b72953ea5aed60ebfec787a6dc",
        "failed_step": "Wait for author handoff and green clean custody",
        "cause": "INTENDED_CLEAN_BRANCH_NOT_FOUND_HTTP_404",
    },
}


def load(path: Path) -> Any:
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise AssertionError(f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result

    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    return subprocess.check_output(
        ["git", *args], cwd=repo, text=not binary
    )


def git_object_exists(repo: Path, spec: str) -> bool:
    return (
        subprocess.run(
            ["git", "cat-file", "-e", spec],
            cwd=repo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        == 0
    )


def validate_git_donor(
    repo: Path,
    *,
    destination: Path,
    destination_label: str,
    source: dict[str, Any],
    require_donor_objects: bool,
) -> None:
    destination_blob = str(git(repo, "hash-object", destination_label)).strip()
    require(destination_blob == source["blob"], f"donor blob drift: {destination_label}")
    source_spec = f"{source['commit']}:{source['path']}"
    if git_object_exists(repo, source_spec):
        require(
            str(git(repo, "rev-parse", source_spec)).strip() == source["blob"],
            f"donor commit/path blob drift: {destination_label}",
        )
        require(
            git(repo, "show", source_spec, binary=True) == destination.read_bytes(),
            f"donor byte drift: {destination_label}",
        )
        return

    require(
        not require_donor_objects,
        f"required donor commit/path unavailable: {destination_label}",
    )
    require(
        source.get("object_required_in_checkout") is False
        and source.get("object_absence_disposition") == CANNOT_REVERIFY_DONOR,
        f"missing donor object lacks explicit CANNOT_REVERIFY disposition: {destination_label}",
    )
    print(f"{CANNOT_REVERIFY_DONOR}: {destination_label}")


def validate_entry(
    repo: Path,
    entry: dict[str, Any],
    *,
    require_donor_objects: bool = False,
) -> None:
    destination = repo / entry["destination"]
    require(destination.is_file(), f"missing destination: {entry['destination']}")
    payload = destination.read_bytes()
    require(len(payload) == entry["bytes"], f"byte count drift: {entry['destination']}")
    require(
        sha256_bytes(payload) == entry["sha256"],
        f"SHA-256 drift: {entry['destination']}",
    )

    source = entry["source"]
    if source["kind"] == "git":
        validate_git_donor(
            repo,
            destination=destination,
            destination_label=entry["destination"],
            source=source,
            require_donor_objects=require_donor_objects,
        )
    elif source["kind"] == "github_actions_artifact":
        identity = (
            source["run"],
            source["artifact_id"],
            source.get("artifact_name"),
            source.get("artifact_zip_sha256"),
        )
        require(identity in EXPECTED_ACTION_ARTIFACTS, "unregistered artifact identity")
        expected_members = EXPECTED_ACTION_ARTIFACTS[identity]
        require(source.get("member") in expected_members, "unregistered artifact member")
        expected_member = expected_members[source["member"]]
        require(
            bool(source.get("member"))
            and source.get("member_bytes") == entry["bytes"]
            and source.get("member_sha256") == entry["sha256"],
            "artifact member binding absent or inconsistent",
        )
        require(
            (entry["bytes"], entry["sha256"]) == expected_member,
            "artifact member differs from independently registered custody",
        )
    elif source["kind"] == "github_actions_artifact_archive":
        identity = (
            source["run"],
            source["artifact_id"],
            source.get("artifact_name"),
            entry["sha256"],
        )
        require(identity in EXPECTED_ACTION_ARTIFACTS, "unregistered artifact archive")
        require(source.get("artifact_zip_bytes") == entry["bytes"], "artifact ZIP bytes")
    elif source["kind"] == "convergence_generated":
        require(source["generator"] == "ORION-01-05 convergence V1", "bad generator")
    else:
        raise AssertionError(f"unknown source kind: {source['kind']}")


def validate_action_artifact_archive(repo: Path, custody: dict[str, Any]) -> None:
    require(
        custody.get("schema") == "ORION.FiberGuard.BNSLActionArtifactCustody.v1",
        "artifact custody schema",
    )
    action = custody["github_actions"]
    archive = custody["archive"]
    identity = (
        action["run"],
        action["artifact_id"],
        action["artifact_name"],
        archive["sha256"],
    )
    require(identity in EXPECTED_ACTION_ARTIFACTS, "artifact custody identity")
    require(
        action
        == {
            "repository": "SzeChunYiu/ORION",
            "run": 33049783681,
            "workflow": "FiberGuard R20 BNSL adaptive",
            "head_branch": "chatgpt/c-r20-bnsl-adaptive-20260827",
            "head_sha": "911ac9876c97b78e4c5e50654251a3f59dac9257",
            "conclusion": "success",
            "artifact_id": 9637176781,
            "artifact_name": "fiberguard-r20-bnsl-adaptive",
            "artifact_created_at": "2026-08-27T07:30:53Z",
        },
        "artifact Actions provenance",
    )
    expected = EXPECTED_ACTION_ARTIFACTS[identity]
    archive_path = repo / archive["path"]
    require(archive_path.is_file(), "artifact archive absent")
    require(archive_path.stat().st_size == archive["bytes"], "artifact archive bytes")
    require(sha256(archive_path) == archive["sha256"], "artifact archive SHA")
    require(archive["bytes"] == 4997, "unexpected artifact archive size")

    with zipfile.ZipFile(archive_path) as bundle:
        infos = bundle.infolist()
        names = [row.filename for row in infos]
        require(len(names) == len(set(names)), "duplicate artifact ZIP member")
        require(set(names) == set(expected), "artifact ZIP member set")
        require(
            all("/" not in name and "\\" not in name and name not in {".", ".."}
                for name in names),
            "unsafe artifact ZIP member",
        )
        payloads = {name: bundle.read(name) for name in names}

    custody_members = custody["members"]
    require(set(custody_members) == set(expected), "artifact custody member set")
    for name, (expected_bytes, expected_sha) in expected.items():
        payload = payloads[name]
        require(len(payload) == expected_bytes, f"artifact member bytes: {name}")
        require(sha256_bytes(payload) == expected_sha, f"artifact member SHA: {name}")
        row = custody_members[name]
        require(
            row["bytes"] == expected_bytes and row["sha256"] == expected_sha,
            f"artifact custody member binding: {name}",
        )
        canonical_path = row.get("canonical_copy")
        if canonical_path is not None:
            require(
                (repo / canonical_path).read_bytes() == payload,
                f"artifact canonical-copy drift: {name}",
            )

    checksum_lines = payloads["SHA256SUMS"].decode("utf-8").splitlines()
    checksum_rows = {
        line.split()[1].rsplit("/", 1)[-1]: line.split()[0]
        for line in checksum_lines
        if len(line.split()) == 2
    }
    require(
        checksum_rows
        == {
            name: expected[name][1]
            for name in ("FIBERGUARD_BNSL_ADAPTIVE_R20_RESULTS.json", "TERMINAL.txt")
        },
        "artifact internal SHA256SUMS",
    )
    require(custody["authority"]["adaptive_superiority"] is False, "artifact authority")
    require(custody["authority"]["external_independence"] is False, "artifact independence")


def validate_r18_action_artifact_archive(repo: Path, custody: dict[str, Any]) -> None:
    require(
        custody.get("schema") == "ORION.FiberGuard.ActionArtifactArchiveCustody.v1",
        "R18 artifact custody schema",
    )
    require(
        custody.get("terminal")
        == "R18_ACTION_ARTIFACT_ARCHIVED__NULL_AND_RETRACTION_PRESERVED",
        "R18 artifact custody terminal",
    )
    api = custody["api_snapshot"]
    require(
        api
        == {
            "repository": "SzeChunYiu/ORION",
            "verified_at": "2026-08-27T10:27:38Z",
            "run": 33023149716,
            "workflow_id": 343322586,
            "workflow": "five-paper-r18-c-paired-route-recovery",
            "event": "push",
            "head_branch": "chatgpt/r18-c-paired-route-20260826",
            "head_sha": "ac4a50f85a147f5933cd2055809c7ac30b29e3c1",
            "run_conclusion": "success",
            "artifact_id": 9627389618,
            "artifact_name": (
                "fiberguard-paired-route-r18-recovery-"
                "ac4a50f85a147f5933cd2055809c7ac30b29e3c1"
            ),
            "artifact_size_in_bytes": 22592,
            "artifact_created_at": "2026-08-26T23:25:52Z",
            "artifact_expires_at": "2026-09-25T23:25:51Z",
            "artifact_expired_at_snapshot": False,
        },
        "R18 artifact Actions provenance",
    )
    archive = custody["archive"]
    identity = (
        api["run"],
        api["artifact_id"],
        api["artifact_name"],
        archive["sha256"],
    )
    require(identity in EXPECTED_ACTION_ARTIFACTS, "R18 artifact custody identity")
    expected = EXPECTED_ACTION_ARTIFACTS[identity]
    archive_path = repo / archive["path"]
    require(archive_path.is_file(), "R18 artifact archive absent")
    require(
        archive_path.stat().st_size == archive["bytes"] == 22592,
        "R18 artifact archive bytes",
    )
    require(sha256(archive_path) == archive["sha256"], "R18 artifact archive SHA")

    with zipfile.ZipFile(archive_path) as bundle:
        infos = bundle.infolist()
        names = [row.filename for row in infos]
        require(len(names) == len(set(names)), "duplicate R18 artifact ZIP member")
        require(set(names) == set(expected), "R18 artifact ZIP member set")
        require(bundle.testzip() is None, "R18 artifact ZIP CRC")
        require(
            all(
                not row.is_dir()
                and not row.flag_bits & 0x1
                and "/" not in row.filename
                and "\\" not in row.filename
                and row.filename not in {".", ".."}
                for row in infos
            ),
            "unsafe R18 artifact ZIP member",
        )
        payloads = {name: bundle.read(name) for name in names}

    custody_members = custody["members"]
    require(set(custody_members) == set(expected), "R18 artifact custody member set")
    for name, (expected_bytes, expected_sha) in expected.items():
        payload = payloads[name]
        require(len(payload) == expected_bytes, f"R18 artifact member bytes: {name}")
        require(
            sha256_bytes(payload) == expected_sha,
            f"R18 artifact member SHA: {name}",
        )
        row = custody_members[name]
        require(
            row["bytes"] == expected_bytes and row["sha256"] == expected_sha,
            f"R18 artifact custody member binding: {name}",
        )
        canonical_path = row.get("canonical_copy")
        if canonical_path is not None:
            require(
                (repo / canonical_path).read_bytes() == payload,
                f"R18 artifact canonical-copy drift: {name}",
            )

    checksum_rows = {
        line.split()[1].rsplit("/", 1)[-1]: line.split()[0]
        for line in payloads["SHA256SUMS"].decode("utf-8").splitlines()
        if len(line.split()) == 2
    }
    require(
        checksum_rows
        == {
            name: expected[name][1]
            for name in (
                "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json",
                "RECOVERY_COMMENT.md",
                "TERMINAL.txt",
            )
        },
        "R18 artifact internal SHA256SUMS",
    )
    require(
        custody["scientific_disposition"]
        == {
            "terminal": R18_TERMINAL,
            "former_positive_terminal": "RETRACTED_UNSUPPORTED_EXECUTION_IDENTITY",
            "outcome_exposed_recovery": True,
        },
        "R18 artifact scientific disposition",
    )
    authority = custody["authority"]
    require(authority["artifact_custody"] is True, "R18 artifact custody authority")
    require(authority["same_owner_execution"] is True, "R18 same-owner boundary")
    for key in (
        "external_independence",
        "production_value",
        "novelty_authority",
        "journal_authority",
        "submission_authorized",
    ):
        require(authority[key] is False, f"R18 artifact authority promoted: {key}")

    registered = load(
        repo
        / "papers/orion-02-fiberguard-finite-fibre/extensions/r18/"
        "R18_RECOVERY_CUSTODY_V2.json"
    )
    registered_artifact = registered["artifact"]
    require(
        registered_artifact["id"] == api["artifact_id"]
        and registered_artifact["name"] == api["artifact_name"]
        and registered_artifact["zip_sha256"] == archive["sha256"],
        "R18 registered artifact identity drift",
    )
    for name in (
        "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json",
        "RECOVERY_COMMENT.md",
        "TERMINAL.txt",
    ):
        require(
            registered_artifact["files"][name]["bytes"] == expected[name][0]
            and registered_artifact["files"][name]["sha256"] == expected[name][1],
            f"R18 registered artifact member drift: {name}",
        )


def validate_manifest(
    repo: Path, *, require_donor_objects: bool = False
) -> dict[str, Any]:
    manifest = load(repo / MANIFEST.relative_to(ROOT))
    require(
        manifest["schema"] == "ORION.ORION0105.ScienceConvergenceDonorManifest.v1",
        "manifest schema",
    )
    require(manifest["terminal"] == CONVERGENCE_TERMINAL, "manifest terminal")
    require(
        manifest.get("donor_object_policy")
        == {
            "pull_request_verification": (
                "REQUIRE_EVERY_GIT_COMMIT_PATH_OBJECT_AND_EXACT_BYTES"
            ),
            "later_merged_main_when_historical_object_absent": CANNOT_REVERIFY_DONOR,
            "destination_blob_and_sha256_remain_content_integrity_only": True,
            "absence_never_promotes_provenance_or_scientific_authority": True,
        },
        "donor object policy",
    )
    destinations = [row["destination"] for row in manifest["files"]]
    require(len(destinations) == len(set(destinations)), "duplicate manifest destinations")
    manifest_path = MANIFEST.relative_to(ROOT).as_posix()
    self_binding = manifest["manifest_self_binding"]
    require(self_binding.get("path") == manifest_path, "manifest self-binding path")
    require(
        self_binding.get("excluded_from_own_hash_list") is True
        and self_binding.get("reason") == "SELF_REFERENTIAL_HASH_IS_NOT_WELL_DEFINED",
        "manifest self-binding rule",
    )
    require(manifest_path not in destinations, "manifest self listed as ordinary file")
    expected_paths = set(manifest["expected_changed_paths"])
    require(
        set(destinations) | {manifest_path} == expected_paths,
        "manifest destination coverage mismatch",
    )
    baseline = manifest["baseline"]
    observed_baseline_tree = str(
        git(repo, "rev-parse", f"{baseline['commit']}^{{tree}}")
    ).strip()
    require(observed_baseline_tree == baseline["tree"], "baseline tree mismatch")

    artifact_member_mappings: set[tuple[int, int, str]] = set()
    for row in manifest["files"]:
        source = row["source"]
        if source["kind"] == "github_actions_artifact":
            mapping = (source["run"], source["artifact_id"], source["member"])
            require(
                mapping not in artifact_member_mappings,
                "duplicate artifact member mapping",
            )
            artifact_member_mappings.add(mapping)
    for row in manifest["files"]:
        validate_entry(repo, row, require_donor_objects=require_donor_objects)

    for row in manifest["bound_existing_files"]:
        path = row["path"]
        require(
            row.get("baseline_commit") == baseline["commit"],
            f"existing binding baseline drift: {path}",
        )
        current = repo / path
        require(current.is_file(), f"missing existing binding: {path}")
        require(current.stat().st_size == row["bytes"], f"existing byte drift: {path}")
        require(sha256(current) == row["sha256"], f"existing SHA drift: {path}")
        base_blob = str(git(repo, "rev-parse", f"{manifest['baseline']['commit']}:{path}")).strip()
        head_blob = str(git(repo, "rev-parse", f"HEAD:{path}")).strip()
        require(base_blob == row["blob"] == head_blob, f"existing blob drift: {path}")
    return manifest


def json_pointer(document: Any, pointer: str) -> Any:
    """Resolve the small RFC 6901 subset used by exact-terminal bindings."""
    require(pointer.startswith("/"), f"invalid JSON pointer: {pointer}")
    current = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            require(token in current, f"JSON pointer key absent: {pointer}")
            current = current[token]
        elif isinstance(current, list):
            require(token.isdigit(), f"JSON pointer index invalid: {pointer}")
            index = int(token)
            require(index < len(current), f"JSON pointer index absent: {pointer}")
            current = current[index]
        else:
            raise AssertionError(f"JSON pointer traverses scalar: {pointer}")
    return current


def claim_ledger_ids(path: Path) -> list[str]:
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] == "ID" or set(cells[0]) <= {"-"}:
            continue
        ids.append(cells[0])
    require(ids, f"claim ledger has no rows: {path}")
    require(len(ids) == len(set(ids)), f"claim ledger has duplicate IDs: {path}")
    return ids


def validate_preserved_exact_terminals(
    repo: Path,
    status: dict[str, Any],
    *,
    require_donor_objects: bool = False,
) -> None:
    allowed_kinds = {
        "RAW_SCIENCE_TERMINAL",
        "AUDIT_DISPOSITION",
        "AUTHORITY_VERDICT",
        "COMPOSITE_INTERPRETATION",
    }
    noncontrolling_dispositions = {
        "PRESERVED_NONCONTROLLING_KNOWN_PREDICATE_DEFECT",
        "RETRACTED_UNSUPPORTED_EXECUTION_IDENTITY",
        "QUARANTINED_OVERLAPPING_MATERIAL_AND_NULL_PREDICATES_AT_ZERO",
    }

    for paper_id in (f"ORION-{index:02d}" for index in range(1, 6)):
        evidence = status["papers"][paper_id].get("evidence_status", {})
        summary = evidence.get("convergence_summary", {})
        require(
            summary.get("label", "").startswith(f"{paper_id}_")
            and summary.get("kind") == "CONVERGENCE_GENERATED_SUMMARY"
            and summary.get("is_exact_donor_terminal") is False,
            f"{paper_id} convergence summary label",
        )
        records = evidence.get("preserved_records", [])
        require(records, f"{paper_id} exact evidence records absent")
        ids = [record["id"] for record in records]
        require(len(ids) == len(set(ids)), f"{paper_id} duplicate evidence record IDs")
        require(
            set(summary.get("derived_from", [])) == set(ids),
            f"{paper_id} summary omits or invents an evidence record",
        )

        for record in records:
            require(record["record_kind"] in allowed_kinds, "evidence record kind")
            source = record["source"]
            canonical = repo / source["canonical_copy"]
            require(canonical.is_file(), f"evidence canonical copy absent: {canonical}")
            require(
                json_pointer(load(canonical), source["json_pointer"])
                == record["value"],
                f"evidence record pointer mismatch: {record['id']}",
            )

            if source["kind"] == "git_donor_canonical_copy":
                require(
                    set(source) >= {"commit", "path", "blob"},
                    f"evidence donor source incomplete: {record['id']}",
                )
                canonical_blob = str(
                    git(repo, "hash-object", source["canonical_copy"])
                ).strip()
                require(
                    canonical_blob == source["blob"],
                    f"evidence canonical blob drift: {record['id']}",
                )
                source_spec = f"{source['commit']}:{source['path']}"
                if git_object_exists(repo, source_spec):
                    require(
                        str(git(repo, "rev-parse", source_spec)).strip()
                        == source["blob"],
                        f"evidence donor source drift: {record['id']}",
                    )
                    require(
                        git(repo, "show", source_spec, binary=True)
                        == canonical.read_bytes(),
                        f"evidence donor byte drift: {record['id']}",
                    )
                else:
                    require(
                        not require_donor_objects,
                        f"required evidence donor commit/path unavailable: {record['id']}",
                    )
                    require(
                        source.get("object_absence_disposition")
                        == CANNOT_REVERIFY_DONOR,
                        f"evidence donor absence not explicit: {record['id']}",
                    )
                    print(f"{CANNOT_REVERIFY_DONOR}: evidence {record['id']}")
            elif source["kind"] == "canonical_convergence_file":
                require(
                    sha256(canonical) == source["sha256"],
                    f"evidence convergence SHA drift: {record['id']}",
                )
            else:
                raise AssertionError(f"unknown evidence source kind: {source['kind']}")

            if record["disposition"] in noncontrolling_dispositions:
                require(
                    record["controls_current_science_status"] is False,
                    f"noncontrolling evidence promoted: {record['id']}",
                )

        candidates = evidence.get("pending_candidates", [])
        candidate_ids = [candidate["id"] for candidate in candidates]
        require(
            len(candidate_ids) == len(set(candidate_ids)),
            f"{paper_id} duplicate pending-candidate IDs",
        )
        for candidate in candidates:
            require(candidate.get("emitted_terminal") is None, "candidate terminal promoted")


def validate_publication_controls(repo: Path, status: dict[str, Any]) -> None:
    gate = load(repo / "research/orion-01-05-convergence-v1/PUBLICATION_GATE_V1.json")
    require(gate["schema"] == "ORION.ORION0105.PublicationGate.v1", "publication gate schema")
    require(
        gate["terminal"]
        == "ORION_01_05_PUBLICATION_GATE__ALL_SCIENCE_OPEN__NO_SUBMISSION_AUTHORITY",
        "publication gate terminal",
    )
    require(set(gate["papers"]) == set(status["papers"]), "publication paper IDs")
    require(gate["rules"]["top_tier_first"] is True, "top-tier-first rule")
    require(
        gate["rules"]["maximum_distinct_frozen_rounds_before_fallback_disposition"]
        == 3,
        "publication round limit",
    )
    require(
        gate["rules"]["adverse_null_retracted_and_cannot_check_results_must_remain_visible"]
        is True,
        "publication adverse-result rule",
    )
    for paper_id, paper_gate in gate["papers"].items():
        require(paper_gate["science_status"] == "OPEN", f"{paper_id} publication science")
        require(
            paper_gate["top_tier_submission_ready"] is False
            and paper_gate["specialist_submission_ready"] is False
            and paper_gate["submission_authorized"] is False,
            f"{paper_id} publication readiness promoted",
        )
        require(
            paper_gate["mandatory_adverse_or_boundary_results"]
            and paper_gate["forbidden_claims"]
            and paper_gate["fallback_scientific_core"],
            f"{paper_id} publication boundary incomplete",
        )
    require(not any(gate["global_authority"].values()), "publication global authority")
    ladder = (
        repo / "research/orion-01-05-convergence-v1/PROVISIONAL_VENUE_LADDER_V1.md"
    ).read_text(encoding="utf-8")
    require("Recheck official venue criteria" in ladder, "venue live-recheck rule")
    for paper_id in gate["papers"]:
        require(paper_id in ladder, f"venue ladder omits {paper_id}")


def validate_stack_dispositions(
    repo: Path, *, require_donor_objects: bool = False
) -> None:
    ledger = load(
        repo / "research/orion-01-05-convergence-v1/STACK_ARTIFACT_DISPOSITIONS_V1.json"
    )
    require(
        ledger["schema"] == "ORION.ORION0105.StackArtifactDispositions.v1",
        "stack disposition schema",
    )
    require(
        ledger.get("source_object_absence_disposition") == CANNOT_REVERIFY_DONOR,
        "stack object-absence policy",
    )
    expected_counts = {str(number): count for number, (_, count) in EXPECTED_STACK_PRS.items()}
    require(ledger["source_pr_file_counts"] == expected_counts, "stack PR file counts")
    snapshots = ledger["source_pr_snapshots"]
    require(set(snapshots) == set(expected_counts), "stack PR snapshot keys")
    for number, (head, count) in EXPECTED_STACK_PRS.items():
        snapshot = snapshots[str(number)]
        require(snapshot["headRefOid"] == head, f"stack PR {number} head")
        require(snapshot["file_count"] == count, f"stack PR {number} file count")

    allowed = {
        "BYTE_MATERIALIZED_CANONICAL_DONOR",
        "SEMANTICALLY_REPLACED_BY_CANONICAL_STATUS_OR_POLICY",
        "HISTORICAL_ONLY_NOT_CANONICALIZED",
        "FAILED_OR_SUPERSEDED_WORKFLOW_HISTORICAL_ONLY",
        "CONSUMED_AUTHORIZATION_WITH_FAILURE_CUSTODY_PRESERVED",
    }
    rows = ledger["files"]
    keys = [(row["source_pr"], row["source_path"]) for row in rows]
    require(len(keys) == len(set(keys)) == sum(expected_counts.values()), "stack row coverage")
    for number in EXPECTED_STACK_PRS:
        snapshot = snapshots[str(number)]
        expected_paths = {
            row["source_path"] for row in rows if row["source_pr"] == number
        }
        base = snapshot["baseRefOid"]
        head = snapshot["headRefOid"]
        if git_object_exists(repo, f"{base}^{{commit}}") and git_object_exists(
            repo, f"{head}^{{commit}}"
        ):
            observed_paths = set(
                str(git(repo, "diff", "--name-only", f"{base}..{head}")).splitlines()
            )
            require(observed_paths == expected_paths, f"stack PR {number} path coverage")
        else:
            require(
                not require_donor_objects,
                f"required stack PR range unavailable: {number}",
            )
            print(f"{CANNOT_REVERIFY_DONOR}: PR {number} diff range")
    for row in rows:
        require(row["disposition"] in allowed, "stack disposition value")
        expected_head = EXPECTED_STACK_PRS[row["source_pr"]][0]
        require(row["source_head"] == expected_head, "stack row head")
        require(len(row["source_blob"]) == 40, "stack source blob")
        require(row["canonical_paths"], "stack canonical disposition path absent")
        for path in row["canonical_paths"]:
            require((repo / path).is_file(), f"stack canonical path absent: {path}")
        source_spec = f"{row['source_head']}:{row['source_path']}"
        if git_object_exists(repo, source_spec):
            require(
                str(git(repo, "rev-parse", source_spec)).strip() == row["source_blob"],
                "stack source blob drift",
            )
        else:
            require(
                not require_donor_objects,
                f"required stack source unavailable: {row['source_pr']}:{row['source_path']}",
            )
            print(
                f"{CANNOT_REVERIFY_DONOR}: PR {row['source_pr']} {row['source_path']}"
            )
        if row["disposition"] == "BYTE_MATERIALIZED_CANONICAL_DONOR":
            require(
                all(
                    str(git(repo, "hash-object", path)).strip() == row["source_blob"]
                    for path in row["canonical_paths"]
                ),
                "stack byte-materialized destination drift",
            )
    coverage = ledger["coverage"]
    require(
        coverage["complete"] is True
        and coverage["expected_file_count"] == len(rows)
        and coverage["observed_file_count"] == len(rows)
        and coverage["unique_source_pr_path_pairs"] == len(rows),
        "stack coverage terminal",
    )
    require(ledger["protected_task3_touched"] is False, "stack touches Task-3")


def validate_science(repo: Path, *, require_donor_objects: bool = False) -> None:
    status = load(repo / STATUS.relative_to(ROOT))
    require(status["terminal"] == CONVERGENCE_TERMINAL, "status terminal")
    require(set(status["papers"]) == {f"ORION-{i:02d}" for i in range(1, 6)}, "paper IDs")
    for paper_id, expected_rounds in EXPECTED_ROUNDS.items():
        paper = status["papers"][paper_id]
        require(paper.get("science_status") == "OPEN", f"{paper_id} science status")
        require(paper.get("rounds") == expected_rounds, f"{paper_id} round accounting")
        require(
            paper.get("coordinator_issues") == EXPECTED_COORDINATOR_ISSUES[paper_id],
            f"{paper_id} coordinator issue roles",
        )
        expected_ledgers = EXPECTED_CLAIM_LEDGER_DISPOSITIONS[paper_id]
        require(
            paper.get("claim_ledgers") == expected_ledgers,
            f"{paper_id} structured claim-ledger disposition drift",
        )
        for ledger in expected_ledgers:
            ledger_path = repo / ledger["path"]
            require(ledger_path.is_file(), f"{paper_id} claim ledger absent")
            require(sha256(ledger_path) == ledger["sha256"], f"{paper_id} claim ledger SHA")
            require(
                str(git(repo, "hash-object", ledger["path"])).strip()
                == ledger["baseline_blob"],
                f"{paper_id} claim ledger blob",
            )
            disposition_ids = [
                claim_id
                for ids in ledger["claim_dispositions"].values()
                for claim_id in ids
            ]
            require(
                len(disposition_ids) == len(set(disposition_ids)),
                f"{paper_id} claim listed in multiple dispositions",
            )
            require(
                set(disposition_ids) == set(claim_ledger_ids(ledger_path)),
                f"{paper_id} claim-ledger row coverage",
            )
        authority = paper.get("authority", {})
        for key in COMMON_FALSE_AUTHORITY_KEYS:
            require(authority.get(key) is False, f"{paper_id} authority promoted: {key}")
    require(all(not row["science_closed"] for row in status["readiness"].values()), "science closure")
    require(
        all(not row["top_tier_submission_ready"] for row in status["readiness"].values()),
        "top-tier readiness",
    )
    require(
        all(not row["specialist_submission_ready"] for row in status["readiness"].values()),
        "specialist readiness",
    )
    require(not any(status["global_authority"].values()), "global authority promoted")
    validate_publication_controls(repo, status)
    validate_stack_dispositions(repo, require_donor_objects=require_donor_objects)
    require(
        status["papers"]["ORION-02"].get("completed_round_issues") == [1533]
        and status["papers"]["ORION-02"].get("absorbed_science_pull_requests")
        == [1534],
        "ORION-02 completed issue/absorbed PR roles",
    )
    require(
        status["papers"]["ORION-05"].get("active_science_pull_requests") == [1524],
        "ORION-05 active theorem PR role",
    )
    ownership = status.get("cross_paper_claim_ownership", {})
    require(set(ownership) == set(EXPECTED_CROSS_PAPER_OWNERS), "claim ownership keys")
    for claim_family, primary in EXPECTED_CROSS_PAPER_OWNERS.items():
        require(ownership[claim_family].get("primary") == primary, "claim primary owner")
        require("double-count" in ownership[claim_family].get("rule", "") or (
            claim_family != "R6M_TARE_SUPPORT_EXPRESSIVITY"
        ), "R6M double-novelty guard")
    validate_preserved_exact_terminals(
        repo, status, require_donor_objects=require_donor_objects
    )

    expected_q1_candidate = {
        "id": "ORION05_R11_DIRECT_SOLVER",
        "source_pr": 1524,
        "source_head": "80226cc5b46bf3b5a0987e3b4d6bcf2366b8ecf7",
        "source_pr_snapshot": {
            "state": "OPEN",
            "is_draft": True,
            "base_ref": "main",
            "base_sha": "6d2d1699be7b5dfc1dd8b2721829b908ff4fb3d8",
            "head_ref": "chatgpt/q1-r11-n9-runtime-theorem-20260827",
            "head_sha": "80226cc5b46bf3b5a0987e3b4d6bcf2366b8ecf7",
            "verified_at": "2026-08-27T09:35:00Z",
        },
        "finite_check_issue": 1523,
        "finite_check_token": "Q1_R11_INDEPENDENT_FINITE_CHECK_PASS",
        "finite_check_authority": "FINITE_CONFORMANCE_ONLY",
        "proposed_terminals": [
            "Q1_R11_PAIR_COUNT_ONLY__RUNTIME_HIDDEN_DEPENDENCY",
            "Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM",
        ],
        "emitted_terminal": None,
        "disposition": "UNDER_INDEPENDENT_THEOREM_DISPOSITION",
        "current_main_authority": False,
        "merged_main_verification": False,
        "claim_boundary": (
            "PAIR_COUNT_AND_O_N9_RUNTIME_REMAIN_CANDIDATE_ONLY__"
            "NO_PRODUCTION_RESOURCE_VALUE"
        ),
        "successor_conditions": [
            "clean current-main child with no protected Task-3/P9 diff",
            "no-production-DP sparse enumerator and hidden-n-dependency audit",
            "exact optimum and witness equivalence against the frozen R6M reference",
            "independent hostile theorem review",
            "merged-main verifier PASS before authority promotion",
        ],
    }
    for paper_id, paper in status["papers"].items():
        candidates = paper["evidence_status"].get("pending_candidates", [])
        if paper_id == "ORION-05":
            require(candidates == [expected_q1_candidate], "ORION-05 candidate identity drift")
        else:
            require(not candidates, f"{paper_id} unexpected pending candidate")
    require(
        status["current_main_baseline"]["commit"]
        == "b1e65d4445a9b2ef5aa44f7adc2838f968f84ff1",
        "current-main baseline drift",
    )

    aliases = (repo / "papers/PAPER_ALIASES.md").read_text(encoding="utf-8")
    for old, new in (
        ("NQ", "ORION-04"),
        ("theory-A", "ORION-01"),
        ("theory-B", "ORION-01"),
        ("theory-C", "ORION-02"),
        ("theory-D", "ORION-03"),
        ("Q1", "ORION-05"),
    ):
        require(f"old: {old}" in aliases and f"new: {new}" in aliases, f"alias {old}")
    paper_readme = (repo / "papers/README.md").read_text(encoding="utf-8")
    require("### ORION-05 theorem status" in paper_readme, "TARE heading identity")
    require("pre-review for ORION-05" in paper_readme, "TARE review identity")
    require("### ORION-01 theorem status" not in paper_readme, "stale TARE heading")

    d = status["papers"]["ORION-03"]
    d_records = {
        record["value"]: record
        for record in d["evidence_status"]["preserved_records"]
    }
    require(
        "TYPED_AUTHORITY_FIRST_MIXING_R12_PASS" in d_records,
        "ORION-03 raw theorem terminal erased",
    )
    require(
        d_records["D_PR1466_THEOREM_AUTHORITY_NOT_ESTABLISHED"]["disposition"]
        == "PRESERVED_NONCONTROLLING_KNOWN_PREDICATE_DEFECT",
        "ORION-03 conflicting wrapper audit disposition",
    )
    require(
        d["authority"]["bounded_internal_first_mixing_theorem"] is True
        and d["authority"]["external_domain_validation_established"] is False,
        "ORION-03 authority boundary drift",
    )
    audit_dispositions = load(
        repo / "research/orion-01-05-convergence-v1/AUDIT_DISPOSITIONS_V1.json"
    )
    require(
        audit_dispositions["known_conflicts"][0]["disposition"]
        == "KNOWN_PREDICATE_FALSE_NEGATIVE",
        "ORION-03 audit defect custody",
    )

    croot = repo / "papers/orion-02-fiberguard-finite-fibre"
    r18root = croot / "extensions/r18"
    r18 = load(r18root / "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json")
    r18_custody = load(r18root / "R18_RECOVERY_CUSTODY_V2.json")
    require(r18["terminal"] == R18_TERMINAL, "R18 terminal")
    require(r18["development"]["candidate_count"] == 99, "R18 candidate denominator")
    require(r18["development"]["feasible_candidate_count"] == 0, "R18 feasible denominator")
    require(
        all(r18[panel]["selected_route"]["metrics"]["route_change_coverage"] == 0.0
            for panel in ("development", "validation", "test")),
        "R18 zero route coverage",
    )
    require(r18["authority"]["external_independence"] is False, "R18 external ceiling")
    require(r18["authority"]["grants_journal_authority"] is False, "R18 journal ceiling")
    require(r18_custody["terminal"] == R18_TERMINAL, "R18 custody terminal")
    require(
        r18_custody["former_positive_terminal"]["disposition"]
        == "RETRACTED_UNSUPPORTED_EXECUTION_IDENTITY",
        "R18 positive retraction",
    )
    r18_registered = r18_custody["artifact"]["files"][
        "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json"
    ]
    require(r18_registered["sha256"] == sha256(r18root / "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json"), "R18 custody SHA")
    r18_action_custody = load(r18root / "R18_ACTION_ARTIFACT_ARCHIVE_CUSTODY_V1.json")
    validate_r18_action_artifact_archive(repo, r18_action_custody)

    r19root = croot / "extensions/r19"
    r19 = load(r19root / "JOINT_ROUTE_R19_RESULTS.json")
    require(r19["terminal"] == R19_TERMINAL, "R19 terminal")
    require(r19["invalid_R19_pairing_counterexample"]["original_randomized_value"] == "35", "R19 35")
    require(r19["invalid_R19_pairing_counterexample"]["shortcut_randomized_value"] == "70", "R19 70")
    require(r19["same_marginals_different_joint_system"]["full_pair_randomized_value"] == "0", "R19 0")
    require(r19["same_marginals_different_joint_system"]["diagonal_pair_randomized_value"] == "50", "R19 50")
    require(r19["authority"]["paired_ASlib_experiment_executed"] is False, "R19 application ceiling")
    require(r19["authority"]["grants_journal_authority"] is False, "R19 journal ceiling")

    r20root = croot / "extensions/r20"
    bnsl = load(r20root / "FIBERGUARD_BNSL_ADAPTIVE_R20_RESULTS.json")
    bnsl_custody = load(r20root / "BNSL_R20_CUSTODY_V1.json")
    require(bnsl["terminal"] == "C_R20_BNSL_ADAPTIVE_MATERIAL_VALUE", "BNSL raw terminal")
    require(bnsl["corpus"]["instance_count"] == 1179, "BNSL denominator")
    require(bnsl["best_static"]["fibre_count"] == 1179, "BNSL fibre count")
    require(bnsl["best_static"]["maximum_fibre_size"] == 1, "BNSL singleton fibres")
    require(bnsl["best_static"]["robust_total_excess_cost"] == 0.0, "BNSL static zero")
    require(bnsl["adaptive_one_step"]["robust_total_excess_cost"] == 0.0, "BNSL adaptive zero")
    require(bnsl_custody["raw_terminal_disposition"] == BNSL_QUARANTINE, "BNSL quarantine")
    require(bnsl_custody["additive_interpretation"] == BNSL_NULL, "BNSL null interpretation")
    require(bnsl_custody["authority"]["adaptive_superiority"] is False, "BNSL superiority ceiling")
    action_custody = load(r20root / "BNSL_R20_ACTION_ARTIFACT_CUSTODY_V1.json")
    validate_action_artifact_archive(repo, action_custody)

    results = croot / "experiments/results"
    cnbr = load(results / "CERTIFIED_NEIGHBORHOOD_RESULT_V1.json")
    cnbr2 = load(results / "CERTIFIED_NEIGHBORHOOD_CONFORMAL_RECOVERY_RESULT_V2.json")
    cnbr2_custody = load(results / "CERTIFIED_NEIGHBORHOOD_CONFORMAL_RECOVERY_CUSTODY_V2.json")
    require(cnbr["overall_verdict"] == "CERTIFICATE_INVALID", "C-NBR terminal")
    require(cnbr2["overall_verdict"] == "VALID_WITHOUT_COVERAGE_OR_VALUE", "C-NBR2 terminal")
    require(cnbr2_custody["terminal"] == "VALID_WITHOUT_COVERAGE_OR_VALUE", "C-NBR2 custody")
    require(cnbr2_custody["authority"]["production_value"] is False, "C-NBR2 value ceiling")
    require(cnbr2_custody["authority"]["former_V1_result"] == "QUARANTINED_IMPLEMENTATION_DEVIATION", "C-NBR2 quarantine")

    nqroot = repo / "papers/orion-04-rooted-completion-certificates/evidence/crb-full-replay/post-execution/job-3544056"
    nq_status = status["papers"]["ORION-04"]
    nq_scope_source = nq_status["claim_ledgers"][0]
    nq_ledger = repo / nq_scope_source["path"]
    require(nq_ledger.is_file(), "ORION-04 established-scope ledger absent")
    require(
        sha256(nq_ledger) == nq_scope_source["sha256"],
        "ORION-04 established-scope ledger SHA drift",
    )
    require(
        str(git(repo, "hash-object", nq_scope_source["path"])).strip()
        == nq_scope_source["baseline_blob"],
        "ORION-04 established-scope ledger blob drift",
    )
    require(
        any("exact D_4" in claim and "remain open" in claim
            for claim in nq_status["established_scope"]),
        "ORION-04 open exact-D4 boundary erased",
    )
    nq = load(nqroot / "POST_EXECUTION_FAILURE_RECEIPT.json")
    require(nq["terminal"] == NQ_FAILURE, "ORION-04 failure terminal")
    require(nq["execution"]["job_id"] == 3544056, "ORION-04 job")
    require(nq["execution"]["elapsed_seconds"] == 29322, "ORION-04 elapsed")
    require(nq["failure"]["observed_exception"] == "TypeError: value is not canonical JSON: float", "ORION-04 exception")
    require(nq["phase_status"]["phase_2_per_record_sat_execution"] == "NOT_RUN", "ORION-04 SAT ceiling")
    require(nq["phase_status"]["phase_3_external_drup_verification"] == "NOT_RUN", "ORION-04 DRUP ceiling")
    require(nq["authority"]["d2_numerical_replay_authority"] is False, "ORION-04 D2 ceiling")
    require(nq["authority"]["d3_numerical_replay_authority"] is False, "ORION-04 D3 ceiling")
    require(nq["supersession"]["d4_rounds_consumed"] == 0, "ORION-04 D4 rounds")

    r30runs = load(repo / "research/orion-01-05-convergence-v1/R30_FAILURE_RUNS_V1.json")
    r30 = load(repo / "research/orion-01-05-convergence-v1/R30_FAILURE_CUSTODY_V1.json")
    require(r30runs["disposition"] == R30_TERMINAL, "R30 run disposition")
    require(r30runs["r30_run_count"] == len(EXPECTED_R30_FAILURES), "R30 run denominator")
    observed_r30_failures = {
        row["run"]: {
            "workflow": row["workflow"],
            "head_sha": row["head_sha"],
            "failed_step": row["failed_step"],
            "cause": row["cause"],
        }
        for row in r30runs["r30_runs"]
    }
    require(observed_r30_failures == EXPECTED_R30_FAILURES, "R30 failure receipt drift")
    require(all(row["conclusion"] == "failure" for row in r30runs["r30_runs"]), "R30 failures")
    require(
        all(
            row["url"]
            == f"https://github.com/SzeChunYiu/ORION/actions/runs/{row['run']}"
            for row in r30runs["r30_runs"]
        ),
        "R30 failure URL drift",
    )
    require(
        r30runs["authoritative_successful_r30_finalizer"] is False
        and r30runs["final_receipts_materialized"] is False,
        "R30 all-failed disposition",
    )
    require(33048978721 not in {row["run"] for row in r30runs["r30_runs"]}, "R18 mixed into R30")
    require(r30["terminal"] == R30_TERMINAL, "R30 custody terminal")
    require(r30["related_non_r30_custody_failure"]["run"] == 33048978721, "R18 custody separation")
    require(r30["live_repository_observations"]["intended_clean_branch_exists"] is False, "R30 branch")
    require(r30["live_repository_observations"]["final_outputs_present_on_current_main"] is False, "R30 outputs")
    rust = r30["unmaterialized_cross_language_claim"]
    require(
        rust["workflow_id"] == 343511583
        and rust["live_run_census"]
        == {
            "total": 47,
            "success": 0,
            "failure": 37,
            "action_required": 9,
            "cancelled": 1,
        }
        and rust["durable_result_or_terminal_present"] is False
        and rust["disposition"]
        == "CHECKER_CANDIDATE_AND_PROSE_ONLY__NO_EXECUTED_PASS",
        "R30 Rust checker execution promoted",
    )
    package_state = r30["source_tree_package_state"]
    require(
        package_state
        == {
            "head": "3c7ea359065be2b72953ea5aed60ebfec787a6dc",
            "release_fileset_terminal": (
                "ORION02_R30_RELEASE_FILESET_FROZEN__RESULT_RECEIPT_REQUIRED"
            ),
            "scientific_internal": "PENDING_CI",
            "manuscript_internal_compile": "PENDING_CI",
            "data_rights": "OPEN",
            "external_replay": "OPEN",
            "novelty": "CANNOT_CHECK_EXTERNAL",
            "archive": "OPEN",
            "submission": "NOT_AUTHORIZED",
            "rights_audit_terminal": (
                "ASLIB_REPOSITORY_LICENSE_PRESENT__"
                "SCENARIO_DATA_RIGHTS_REQUIRE_AUTHOR_REVIEW"
            ),
        },
        "R30 source-tree package state promoted",
    )
    failed_artifact = r30["failed_finalization_artifact"]
    require(
        failed_artifact["run"] == 33047609008
        and failed_artifact["artifact_id"] == 9636339561
        and failed_artifact["artifact_name"] == "five-paper-r30-final"
        and failed_artifact["reported_size_bytes"] == 136
        and failed_artifact["downloaded_zip_sha256"]
        == "5b6188d5276dba7f081c7d2d3106cb2cef92588c577d15394848949ae7ffdba3"
        and failed_artifact["disposition"]
        == "EMPTY_CHECKSUM_MEMBER_ONLY__NO_R30_STATUS_PDF_OR_RELEASE_PACKET",
        "R30 failed artifact identity drift",
    )
    failed_archive = repo / failed_artifact["archive_path"]
    require(
        failed_archive.is_file()
        and failed_archive.stat().st_size == failed_artifact["reported_size_bytes"]
        and sha256(failed_archive) == failed_artifact["downloaded_zip_sha256"],
        "R30 failed artifact archive drift",
    )
    with zipfile.ZipFile(failed_archive) as bundle:
        require(bundle.namelist() == ["SHA256SUMS"], "R30 failed artifact member set")
        empty_checksum = bundle.read("SHA256SUMS")
    require(empty_checksum == b"", "R30 failed artifact member is not empty")
    require(
        failed_artifact["members"]
        == {
            "SHA256SUMS": {
                "bytes": 0,
                "sha256": (
                    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                ),
            }
        },
        "R30 failed artifact member custody drift",
    )

    supersession = load(
        repo / "research/orion-01-05-convergence-v1/SUPERSESSION_PLAN_V1.json"
    )
    require(
        supersession["global_rule"]
        == "CLOSE_ONLY_AFTER_SUCCESSOR_MERGE_AND_MERGED_MAIN_VERIFICATION",
        "premature supersession rule",
    )
    require(
        set(supersession["after_convergence_merge"]["close_pull_requests"])
        == {1471, 1475, 1485, 1488, 1489, 1492, 1503, 1506, 1534},
        "unsupported pull-request supersession",
    )
    require(
        "unabsorbed_manuscript_package_and_policy_pull_requests"
        not in supersession["keep_open_after_convergence"],
        "absorbed coordination PRs still marked unabsorbed",
    )
    require(supersession["protected_task3_touched"] is False, "supersession touches Task-3")


def diff_records(repo: Path, base: str) -> list[tuple[str, str]]:
    raw = str(git(repo, "diff", "--name-status", "-M", f"{base}..HEAD"))
    records: list[tuple[str, str]] = []
    for line in raw.splitlines():
        fields = line.split("\t")
        require(len(fields) == 2, f"rename/copy/delete not allowed: {line}")
        records.append((fields[0], fields[1]))
    return records


def validate_changed_paths(records: list[tuple[str, str]], expected: set[str]) -> None:
    actual: set[str] = set()
    for status, path in records:
        require(status in {"A", "M"}, f"destructive diff status: {status} {path}")
        require(path not in actual, f"duplicate changed path: {path}")
        require(
            path in ALLOWED_EXACT_PATHS or path.startswith(ALLOWED_ADDITIVE_PREFIXES),
            f"path outside strict convergence allowlist: {path}",
        )
        actual.add(path)
        if path == "papers/README.md":
            require(status == "M", "papers README must be the sole modified existing file")
        else:
            require(status == "A", f"non-additive convergence path: {path}")
    require(actual == expected, f"changed-path mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")


def validate_diff(repo: Path, manifest: dict[str, Any]) -> None:
    base = manifest["baseline"]["commit"]
    expected = set(manifest["expected_changed_paths"])
    validate_changed_paths(diff_records(repo, base), expected)

    forbidden_prefixes = tuple(manifest["protected_path_policy"]["forbidden_prefixes"])
    require(not any(path.startswith(forbidden_prefixes) for path in expected), "protected path in allowlist")
    for row in manifest["protected_blob_guards"]:
        base_blob = str(git(repo, "rev-parse", f"{base}:{row['path']}")).strip()
        head_blob = str(git(repo, "rev-parse", f"HEAD:{row['path']}")).strip()
        require(base_blob == row["blob"] == head_blob, f"protected blob changed: {row['path']}")


def validate_event_base(repo: Path, manifest: dict[str, Any], event_base: str) -> None:
    require(event_base == manifest["baseline"]["commit"], "event base commit mismatch")
    observed_tree = str(git(repo, "rev-parse", f"{event_base}^{{tree}}")).strip()
    require(observed_tree == manifest["baseline"]["tree"], "event base tree mismatch")


def verify(
    repo: Path,
    check_diff: bool,
    event_base: str | None = None,
    *,
    require_donor_objects: bool = False,
) -> None:
    manifest_path = repo / MANIFEST.relative_to(ROOT)
    raw_manifest = load(manifest_path)
    if event_base is not None:
        validate_event_base(repo, raw_manifest, event_base)
    manifest = validate_manifest(
        repo, require_donor_objects=require_donor_objects
    )
    validate_science(repo, require_donor_objects=require_donor_objects)
    if check_diff:
        validate_diff(repo, manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--check-diff", action="store_true")
    parser.add_argument("--event-base")
    parser.add_argument("--require-donor-objects", action="store_true")
    args = parser.parse_args()
    verify(
        args.repo.resolve(),
        args.check_diff,
        args.event_base,
        require_donor_objects=args.require_donor_objects,
    )
    print(CONVERGENCE_TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
