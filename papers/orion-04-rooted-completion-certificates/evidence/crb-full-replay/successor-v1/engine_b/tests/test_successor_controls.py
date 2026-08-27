from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import crb_census as cc
import engine_b as eb
import replay_custody as custody
import submission_gate as gate
import verify_positive_witnesses as positive


ENGINE_ROOT = Path(__file__).resolve().parents[1]
SUCCESSOR_ROOT = ENGINE_ROOT.parent
OLD_KEY = "741454d7d6b513ccd80d2aa9a78d2a9f5076fe8075341d0ecc8e95566ecc28ea"


def _authorization(
    *,
    commit: str = "a" * 40,
    source_manifest_sha256: str = "b" * 64,
    durable_root: str = "/durable/orion-04/job-new",
    registry_root: str = "/durable/orion-04/global-registry",
) -> dict[str, object]:
    packet: dict[str, object] = {
        "schema": "ORION.ORION04.CRB.OneShotAuthorization.v1",
        "status": "AUTHORIZED_ONE_SHOT",
        "paper_id": "ORION-04",
        "subject_commit": eb.SUBJECT_COMMIT,
        "successor_commit": commit,
        "source_manifest": {
            "path": (
                "papers/orion-04-rooted-completion-certificates/evidence/"
                "crb-full-replay/successor-v1/engine_b/SOURCE_MANIFEST.json"
            ),
            "sha256": source_manifest_sha256,
        },
        "durable_root": durable_root,
        "global_registry_root": registry_root,
        "attempt_limit": 1,
        "declared_scopes": [
            {"scope": "NQ_D2_NORMALIZED_LENGTH_19", "expected_record_count": 98_622},
            {"scope": "NQ_D3_STRUCTURED_LENGTH_25", "expected_record_count": 230_983},
        ],
        "authorization": {
            "authorized_at_utc": "2026-08-28T00:00:00Z",
            "authorized_by": "EXTERNAL_OPERATOR_REQUIRED",
        },
    }
    packet["nonduplication_key"] = gate.derive_nonduplication_key(packet)
    return packet


def test_elapsed_metrics_are_canonical_integer_milliseconds() -> None:
    assert cc._elapsed_milliseconds(10.0, observed=12.3456) == 2346
    metrics = {"d2_wall_milliseconds": cc._elapsed_milliseconds(10.0, observed=12.3456)}
    receipt = cc.build_generation_receipt(
        (),
        metrics,
        threads=1,
        coverage_argument_sha256="c" * 64,
        matrix_manifest_sha256="d" * 64,
        execution_context="AUTHORIZED_LUNARC_REPLAY",
    )
    assert type(receipt["generation_metrics"]["d2_wall_milliseconds"]) is int
    assert "wall_seconds" not in " ".join(receipt["generation_metrics"])
    assert receipt["lunarc_execution"] == "AUTHORIZED_LUNARC_REPLAY"
    eb.canonical_json_bytes(receipt)


def test_post_d2_d3_failure_still_writes_canonical_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage = tmp_path / "coverage.md"
    coverage.write_text("frozen coverage\n", encoding="utf-8")
    output = tmp_path / "output"
    d2_record = tuple([1] * 19)

    monkeypatch.setattr(
        cc,
        "generate_d2_records",
        lambda **_: ([d2_record], {"d2_wall_milliseconds": 1}),
    )
    monkeypatch.setattr(
        cc,
        "write_scope_streams",
        lambda spec, records, *args, **kwargs: {
            "scope": spec.scope,
            "record_count": len(records),
            "stream_file_sha256": "e" * 64,
        },
    )

    def fail_d3(*args: object, **kwargs: object) -> object:
        raise cc.ResourceBudgetExceeded("post-D2 hostile control")

    monkeypatch.setattr(cc, "generate_d3_records", fail_d3)
    assert (
        cc.main(
            [
                "--scope",
                "both",
                "--output-root",
                str(output),
                "--coverage-argument",
                str(coverage),
                "--threads",
                "1",
            ]
        )
        == 3
    )
    receipt = json.loads((output / "census_generation_receipt.json").read_text())
    assert receipt["terminal"] == cc.RESOURCE_TERMINAL
    assert receipt["scopes"][0]["scope"] == "NQ_D2_NORMALIZED_LENGTH_19"
    assert receipt["generation_metrics"]["d2_wall_milliseconds"] == 1
    eb.canonical_json_bytes(receipt)


def test_phase1_checkpoint_is_complete_and_corruption_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "phase1"
    (source / "input" / "d2").mkdir(parents=True)
    (source / "input" / "d2" / "records.jsonl").write_text("{}\n", encoding="utf-8")
    (source / "census_generation_receipt.json").write_text("{}\n", encoding="utf-8")
    checkpoint = tmp_path / "durable" / "phase-1-checkpoint"
    receipt = custody.create_phase1_checkpoint(source, checkpoint)
    assert receipt["file_count"] == 2
    custody.verify_phase1_checkpoint(checkpoint)
    (checkpoint / "input" / "d2" / "records.jsonl").write_text("tampered\n")
    with pytest.raises(custody.CustodyMismatch, match="mismatch"):
        custody.verify_phase1_checkpoint(checkpoint)

    source_link = tmp_path / "phase1-link"
    source_link.symlink_to(source, target_is_directory=True)
    with pytest.raises(custody.CustodyMismatch, match="unsafe"):
        custody.create_phase1_checkpoint(source_link, tmp_path / "unsafe-checkpoint")


def test_d3_continuation_loads_only_an_exact_checkpointed_d2_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = cc.fm.CensusSpec(
        scope="NQ_D2_NORMALIZED_LENGTH_19",
        kind="d2_witness_census",
        expected_record_count=1,
        sequence_length=19,
        required_bins=2,
        record_id_prefix="nq-d2-",
    )
    monkeypatch.setattr(cc.fm, "D2_SPEC", spec)
    root = tmp_path / "checkpointed-d2"
    root.mkdir()
    record = {
        "schema": cc.SEQUENCE_SCHEMA,
        "record_id": "nq-d2-00000000",
        "scope": spec.scope,
        "sequence": [1] * 19,
        "required_bins": 2,
    }
    (root / "records.jsonl").write_bytes(eb.canonical_json_bytes(record) + b"\n")
    coverage = {
        "schema": cc.COVERAGE_SCHEMA,
        "subject_commit": eb.SUBJECT_COMMIT,
        "scope": spec.scope,
        "declared_complete": True,
        "expected_record_count": 1,
        "coverage_argument_sha256": "c" * 64,
        "generator_identity": cc.GENERATOR_IDENTITY,
        "normalization_identity": cc.NORMALIZATION_IDENTITY_D2,
    }
    (root / "coverage.json").write_bytes(eb.canonical_json_bytes(coverage) + b"\n")
    manifest = cc.batch.build_input_manifest(
        root, stream_path="records.jsonl", coverage_path="coverage.json"
    )
    (root / "input_manifest.json").write_bytes(eb.canonical_json_bytes(manifest) + b"\n")
    records, manifest_sha256 = cc.load_checkpointed_d2_records(root)
    assert records == ((1,) * 19,)
    assert manifest_sha256 == manifest["manifest_sha256"]
    (root / "records.jsonl").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(cc.CensusGenerationMismatch, match="checkpointed D2"):
        cc.load_checkpointed_d2_records(root)


def test_first_failure_is_write_once_and_exit_is_durable(tmp_path: Path) -> None:
    durable = tmp_path / "durable"
    durable.mkdir()
    assert custody.write_first_failure(
        durable,
        exit_code=17,
        line=101,
        command="phase-two-command",
        phase="PHASE_2",
    )
    assert not custody.write_first_failure(
        durable,
        exit_code=99,
        line=202,
        command="later-command",
        phase="EXIT",
    )
    first = json.loads((durable / "FIRST_FAILURE.json").read_text())
    assert first["exit_code"] == 17
    assert first["phase"] == "PHASE_2"
    exit_receipt = custody.write_exit_receipt(durable, exit_code=17, phase="PHASE_2")
    assert exit_receipt["terminal"] == "ORION04_CRB_PROCESS_EXIT_FAILURE"
    assert (durable / "EXIT_RECEIPT.json").is_file()


def test_authorization_gate_refuses_missing_mismatch_and_consumed_key(tmp_path: Path) -> None:
    with pytest.raises(gate.AuthorizationRefused, match="missing"):
        gate.load_authorization(
            tmp_path / "missing.json",
            expected_commit="a" * 40,
            expected_source_manifest_sha256="b" * 64,
        )

    packet = _authorization()
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    with pytest.raises(gate.AuthorizationRefused, match="successor commit"):
        gate.load_authorization(
            path,
            expected_commit="f" * 40,
            expected_source_manifest_sha256="b" * 64,
        )

    packet["nonduplication_key"] = OLD_KEY
    path.write_text(json.dumps(packet), encoding="utf-8")
    with pytest.raises(gate.AuthorizationRefused, match="consumed"):
        gate.load_authorization(
            path,
            expected_commit="a" * 40,
            expected_source_manifest_sha256="b" * 64,
        )

    packet = _authorization()
    packet["authorization"]["authorized_by"] = "reviewer@example.invalid"
    packet["nonduplication_key"] = gate.derive_nonduplication_key(packet)
    path.write_text(json.dumps(packet), encoding="utf-8")
    assert (
        gate.load_authorization(
            path,
            expected_commit="a" * 40,
            expected_source_manifest_sha256="b" * 64,
        )["nonduplication_key"]
        == packet["nonduplication_key"]
    )

    nested = _authorization(
        durable_root="/shared/global/jobs/job-1", registry_root="/shared/global"
    )
    nested["authorization"]["authorized_by"] = "reviewer@example.invalid"
    nested["nonduplication_key"] = gate.derive_nonduplication_key(nested)
    path.write_text(json.dumps(nested), encoding="utf-8")
    with pytest.raises(gate.AuthorizationRefused, match="not isolated"):
        gate.load_authorization(
            path,
            expected_commit="a" * 40,
            expected_source_manifest_sha256="b" * 64,
        )


@pytest.mark.parametrize(
    "timestamp",
    (
        "REPLACE_WITH_EXTERNAL_AUTHORIZATION_TIME",
        "2026-13-99T25:61:61Z",
        "2026-08-28 00:00:00",
        "2026-08-28T00:00:00+00:00",
    ),
)
def test_authorization_gate_rejects_placeholder_or_noncanonical_time(
    tmp_path: Path, timestamp: str
) -> None:
    packet = _authorization()
    packet["authorization"]["authorized_by"] = "operator-ticket-ORION04-20260827"
    packet["authorization"]["authorized_at_utc"] = timestamp
    packet["nonduplication_key"] = gate.derive_nonduplication_key(packet)
    path = tmp_path / "authorization.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    with pytest.raises(gate.AuthorizationRefused, match="time"):
        gate.load_authorization(
            path,
            expected_commit="a" * 40,
            expected_source_manifest_sha256="b" * 64,
        )


def test_authorization_validation_receipt_never_establishes_externality() -> None:
    packet = _authorization()
    packet["authorization"]["authorized_by"] = "arbitrary operator label"
    packet["nonduplication_key"] = gate.derive_nonduplication_key(packet)
    validated = gate.validate_authorization(
        packet,
        expected_commit="a" * 40,
        expected_source_manifest_sha256="b" * 64,
    )
    receipt = gate.authorization_validation_receipt(validated)
    assert receipt["terminal"] == "ORION04_ONE_SHOT_REQUEST_BINDINGS_VALID"
    assert receipt["operator_attestation"] == "USER_SUPPLIED_UNVERIFIED_BY_MACHINE"
    assert receipt["machine_established_externality"] is False
    assert receipt["scientific_authority_delta"] == "NONE"
    assert "authorized_by" not in receipt


def test_global_registry_fails_closed_and_rejects_duplicate(tmp_path: Path) -> None:
    packet = _authorization(
        durable_root=str(tmp_path / "durable"), registry_root=str(tmp_path / "global")
    )
    missing_root = tmp_path / "missing-global"
    with pytest.raises(gate.RegistryRefused, match="unavailable"):
        gate.reserve_submission(
            missing_root,
            SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json",
            packet,
        )

    global_root = tmp_path / "global"
    global_root.mkdir()
    reservation = gate.reserve_submission(
        global_root,
        SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json",
        packet,
    )
    assert reservation["status"] == "RESERVED"
    with pytest.raises(gate.RegistryRefused, match="duplicate"):
        gate.reserve_submission(
            global_root,
            SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json",
            packet,
        )
    registry = json.loads((global_root / gate.REGISTRY_FILENAME).read_text())
    keys = {entry["nonduplication_key"] for entry in registry["submissions"]}
    assert OLD_KEY in keys
    assert packet["nonduplication_key"] in keys
    gate.update_submission(
        global_root,
        SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json",
        key=str(packet["nonduplication_key"]),
        status="SUBMITTED",
        job_id=999,
    )
    gate.assert_submitted_attempt(
        global_root,
        SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json",
        key=str(packet["nonduplication_key"]),
        job_id=999,
        successor_commit="a" * 40,
    )
    with pytest.raises(gate.RegistryRefused, match="job identity"):
        gate.assert_submitted_attempt(
            global_root,
            SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json",
            key=str(packet["nonduplication_key"]),
            job_id=1000,
            successor_commit="a" * 40,
        )


def test_terminalization_consumes_reserved_and_submitted_entries(tmp_path: Path) -> None:
    prebind = SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json"
    for submitted in (False, True):
        suffix = "submitted" if submitted else "reserved"
        global_root = tmp_path / f"global-{suffix}"
        global_root.mkdir()
        packet = _authorization(
            durable_root=str(tmp_path / f"durable-{suffix}"),
            registry_root=str(global_root),
        )
        packet["authorization"]["authorized_by"] = "operator-ticket-ORION04-20260827"
        packet["nonduplication_key"] = gate.derive_nonduplication_key(packet)
        gate.reserve_submission(global_root, prebind, packet)
        job_id = 424242 if submitted else None
        if submitted:
            gate.update_submission(
                global_root,
                prebind,
                key=str(packet["nonduplication_key"]),
                status="SUBMITTED",
                job_id=job_id,
            )
        terminal = gate.terminalize_submission(
            global_root,
            prebind,
            key=str(packet["nonduplication_key"]),
            job_id=job_id,
            failure_stage="RELEASE_HELD_JOB",
            failure_exit_code=42,
            failure_command="scontrol release 424242",
            scheduler_reconciliation="CANCELLED_OR_ABSENT_CONFIRMED",
        )
        assert terminal["status"] == "SUBMISSION_FAILED_KEY_CONSUMED"
        assert terminal["job_id"] == job_id
        assert terminal["failure"]["stage"] == "RELEASE_HELD_JOB"
        assert terminal["failure"]["scheduler_reconciliation"] == ("CANCELLED_OR_ABSENT_CONFIRMED")
        assert terminal["scientific_authority_delta"] == "NONE"


@pytest.mark.parametrize(
    ("process_exit_code", "expected_status", "expected_terminal"),
    (
        (0, "PROCESS_EXIT_SUCCESS_KEY_CONSUMED", "ORION04_CRB_PROCESS_EXIT_SUCCESS"),
        (17, "PROCESS_EXIT_FAILURE_KEY_CONSUMED", "ORION04_CRB_PROCESS_EXIT_FAILURE"),
    ),
)
def test_started_job_terminalization_consumes_key_and_unblocks_next_authorization(
    tmp_path: Path,
    process_exit_code: int,
    expected_status: str,
    expected_terminal: str,
) -> None:
    prebind = SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json"
    global_root = tmp_path / "global"
    global_root.mkdir()
    first = _authorization(
        durable_root=str(tmp_path / "durable-first"), registry_root=str(global_root)
    )
    first["authorization"]["authorized_by"] = "operator-ticket-ORION04-first"
    first["nonduplication_key"] = gate.derive_nonduplication_key(first)
    first_key = str(first["nonduplication_key"])
    gate.reserve_submission(global_root, prebind, first)
    gate.update_submission(
        global_root,
        prebind,
        key=first_key,
        status="SUBMITTED",
        job_id=424242,
    )

    terminal = gate.terminalize_started_submission(
        global_root,
        prebind,
        key=first_key,
        job_id=424242,
        successor_commit="a" * 40,
        process_exit_code=process_exit_code,
        phase="PROCESS_COMPLETE_AWAITING_ADJUDICATION",
    )
    assert terminal["status"] == expected_status
    assert terminal["job_id"] == 424242
    assert terminal["process_exit"] == {
        "terminal": expected_terminal,
        "exit_code": process_exit_code,
        "phase": "PROCESS_COMPLETE_AWAITING_ADJUDICATION",
    }
    assert terminal["scientific_authority_delta"] == "NONE"

    second = _authorization(
        durable_root=str(tmp_path / "durable-second"), registry_root=str(global_root)
    )
    second["authorization"]["authorized_by"] = "operator-ticket-ORION04-second"
    second["nonduplication_key"] = gate.derive_nonduplication_key(second)
    assert gate.reserve_submission(global_root, prebind, second)["status"] == "RESERVED"


def test_started_job_terminalization_identity_mismatch_stays_active(tmp_path: Path) -> None:
    prebind = SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json"
    global_root = tmp_path / "global"
    global_root.mkdir()
    first = _authorization(
        durable_root=str(tmp_path / "durable-first"), registry_root=str(global_root)
    )
    first["authorization"]["authorized_by"] = "operator-ticket-ORION04-first"
    first["nonduplication_key"] = gate.derive_nonduplication_key(first)
    first_key = str(first["nonduplication_key"])
    gate.reserve_submission(global_root, prebind, first)
    gate.update_submission(
        global_root,
        prebind,
        key=first_key,
        status="SUBMITTED",
        job_id=424242,
    )

    with pytest.raises(gate.RegistryRefused, match="job identity"):
        gate.terminalize_started_submission(
            global_root,
            prebind,
            key=first_key,
            job_id=424243,
            successor_commit="a" * 40,
            process_exit_code=0,
            phase="PROCESS_COMPLETE_AWAITING_ADJUDICATION",
        )
    registry = json.loads((global_root / gate.REGISTRY_FILENAME).read_text())
    entry = next(row for row in registry["submissions"] if row["nonduplication_key"] == first_key)
    assert entry["status"] == "SUBMITTED"

    second = _authorization(
        durable_root=str(tmp_path / "durable-second"), registry_root=str(global_root)
    )
    second["authorization"]["authorized_by"] = "operator-ticket-ORION04-second"
    second["nonduplication_key"] = gate.derive_nonduplication_key(second)
    with pytest.raises(gate.RegistryRefused, match="attempt is active"):
        gate.reserve_submission(global_root, prebind, second)


def test_submit_script_cancels_and_terminalizes_held_job_on_release_failure(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    target = repository / (
        "papers/orion-04-rooted-completion-certificates/evidence/crb-full-replay/successor-v1"
    )
    shutil.copytree(
        SUCCESSOR_ROOT,
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    engine = target / "engine_b"
    no_bytecode_environment = os.environ.copy()
    no_bytecode_environment["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run(
        [
            os.fspath(Path(os.sys.executable)),
            "build_manifest.py",
            "--root",
            ".",
            "--output",
            "SOURCE_MANIFEST.json",
        ],
        cwd=engine,
        env=no_bytecode_environment,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(["git", "add", "."], cwd=repository, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=ORION test",
            "-c",
            "user.email=orion-test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        cwd=repository,
        check=True,
    )
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    source_digest = json.loads((engine / "SOURCE_MANIFEST.json").read_text())["manifest_sha256"]
    global_root = tmp_path / "global"
    global_root.mkdir()
    durable_parent = tmp_path / "durable"
    durable_parent.mkdir()
    durable_root = durable_parent / "attempt-1"
    packet = _authorization(
        commit=commit,
        source_manifest_sha256=source_digest,
        durable_root=str(durable_root),
        registry_root=str(global_root),
    )
    packet["authorization"]["authorized_by"] = "operator-ticket-ORION04-20260827"
    packet["nonduplication_key"] = gate.derive_nonduplication_key(packet)
    authorization = tmp_path / "operator-request.json"
    authorization.write_text(json.dumps(packet, sort_keys=True) + "\n", encoding="utf-8")

    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    event_log = tmp_path / "scheduler-events.txt"
    stubs = {
        "squeue": "#!/bin/sh\nexit 0\n",
        "sbatch": "#!/bin/sh\nprintf '424242\\n'\n",
        "scontrol": '#!/bin/sh\nprintf \'scontrol %s\\n\' "$*" >>"$ORION_TEST_EVENT_LOG"\nexit 42\n',
        "scancel": '#!/bin/sh\nprintf \'scancel %s\\n\' "$*" >>"$ORION_TEST_EVENT_LOG"\nexit 0\n',
    }
    for name, source in stubs.items():
        path = fake_bin / name
        path.write_text(source, encoding="utf-8")
        path.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{fake_bin}{os.pathsep}{environment['PATH']}",
            "ORION04_CRB_AUTHORIZATION_PATH": str(authorization),
            "ORION_TEST_EVENT_LOG": str(event_log),
        }
    )
    completed = subprocess.run(
        [
            "bash",
            os.fspath(engine / "slurm" / "submit_orion04_crb_full_replay.sh"),
            os.fspath(repository),
        ],
        cwd=repository,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert completed.returncode == 42, completed.stderr
    assert event_log.read_text().splitlines() == [
        "scontrol release 424242",
        "scancel 424242",
    ]
    registry = json.loads((global_root / gate.REGISTRY_FILENAME).read_text())
    entry = next(
        row
        for row in registry["submissions"]
        if row["nonduplication_key"] == packet["nonduplication_key"]
    )
    assert entry["status"] == "SUBMISSION_FAILED_KEY_CONSUMED"
    assert entry["job_id"] == 424242
    assert entry["failure"]["stage"] == "RELEASE_HELD_JOB"
    assert entry["failure"]["scheduler_reconciliation"] == ("CANCELLED_OR_ABSENT_CONFIRMED")
    failure = json.loads((durable_root / "SUBMISSION_FAILURE.json").read_text())
    assert failure["terminal"] == "ORION04_SUBMISSION_FAILED_KEY_CONSUMED"
    assert failure["machine_established_externality"] is False
    assert failure["scientific_authority_delta"] == "NONE"


def test_independent_positive_witness_gate_rejects_tamper(tmp_path: Path) -> None:
    record = {
        "schema": "ORION.NQ.EngineB.SequenceRecord.v1",
        "record_id": "r0",
        "scope": "CONTROL",
        "sequence": [1, 4, 5, 20],
        "required_bins": 2,
    }
    certificate: dict[str, object] = {
        "schema": "ORION.NQ.EngineB.SATCertificate.v1",
        "subject_commit": eb.SUBJECT_COMMIT,
        "record_id": "r0",
        "status": "SAT_K_DISJOINT_ZERO_SUMS",
        "solver_identity": "CONTROL",
        "sequence_sha256": hashlib.sha256(b"[1,4,5,20]").hexdigest(),
        "required_bins": 2,
        "cnf_sha256": "f" * 64,
        "witness_bins": [[0, 1], [2, 3]],
    }
    certificate["certificate_sha256"] = positive.canonical_digest(certificate)
    records = tmp_path / "records.jsonl"
    certificates = tmp_path / "certificates.jsonl"
    records.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    certificates.write_text(json.dumps(certificate, sort_keys=True, separators=(",", ":")) + "\n")
    receipt = positive.verify_positive_witness_streams(records, certificates)
    assert receipt["sat_witnesses_verified"] == 1
    certificate["witness_bins"] = [[0], [2, 3]]
    certificate["certificate_sha256"] = positive.canonical_digest(certificate)
    certificates.write_text(json.dumps(certificate, sort_keys=True, separators=(",", ":")) + "\n")
    with pytest.raises(positive.PositiveWitnessMismatch, match="zero-sum"):
        positive.verify_positive_witness_streams(records, certificates)


def test_successor_job_orders_checkpoint_before_phase2_and_uses_canonical_path() -> None:
    script = (ENGINE_ROOT / "slurm" / "job_orion04_crb_full_replay.slurm").read_text()
    canonical = (
        "papers/orion-04-rooted-completion-certificates/evidence/"
        "crb-full-replay/successor-v1/engine_b"
    )
    assert canonical in script
    assert "papers/five-paper-top-tier-r8/NQ" not in script
    assert "ORION04_CRB_DURABLE_ROOT" in script
    assert "--execution-context AUTHORIZED_LUNARC_REPLAY" in script
    assert "--untracked-files=all" in script
    assert "PYTHONDONTWRITEBYTECODE=1" in script
    assert "-name '*.pyc'" in script
    assert "trap 'on_err" in script
    assert "trap 'on_exit" in script
    d2_generation = script.index("--scope d2")
    d2_checkpoint = script.index('"${D2_CHECKPOINT}"')
    d3_generation = script.index("--scope d3")
    phase2 = script.index("Phase 2")
    assert d2_generation < d2_checkpoint < d3_generation < phase2
    assert '--d2-input-root "${D2_CHECKPOINT}/input/${D2_SCOPE}"' in script
    assert 'verify-phase1-checkpoint "${D2_CHECKPOINT}"' in script
    assert 'verify-phase1-checkpoint "${D3_CHECKPOINT}"' in script
    assert "98622" in script and "230983" in script
    assert "verify_positive_witnesses.py" in script
    assert "batch_external_drup.py" in script
    assert 'receipt.get("machine_established_externality") is not False' in script
    assert 'receipt.get("operator_attestation") !=' in script
    assert "if value != expected" not in script
    submit = (ENGINE_ROOT / "slurm" / "submit_orion04_crb_full_replay.sh").read_text()
    assert "--untracked-files=all" in submit
    assert "PYTHONDONTWRITEBYTECODE=1" in submit
    assert "-name '*.pyc'" in submit
    assert "--hold" in submit and "scontrol release" in submit
    assert "scancel" in submit
    assert "terminalize" in submit


def test_successor_job_terminalizes_started_registry_on_every_exit() -> None:
    script = (ENGINE_ROOT / "slurm" / "job_orion04_crb_full_replay.slurm").read_text()
    on_exit = script[script.index("on_exit()") : script.index("trap 'on_err")]
    assert "terminalize-started" in on_exit
    assert '--process-exit-code "${status}"' in on_exit
    assert '--phase "${PHASE}"' in on_exit
    assert '--successor-commit "${AUTHORIZED_COMMIT}"' in on_exit
    assert "ORION04_CRB_REGISTRY_TERMINALIZATION_FAILED" in on_exit
    assert "REGISTRY_TERMINALIZATION_FAILURE=70" in script


def test_donor_disposition_classifies_every_immutable_manifest_entry() -> None:
    source = json.loads((SUCCESSOR_ROOT / "DONOR_SOURCE_MANIFEST_V1.json").read_text())
    disposition = json.loads((SUCCESSOR_ROOT / "DONOR_DISPOSITION_V1.json").read_text())
    assert disposition["donor_manifest_semantics"]["canonical_materialization"] == (
        "HISTORICAL_INITIAL_TARGET_NOT_A_CURRENT_BYTE_ASSERTION"
    )
    rows = disposition["files"]
    assert len(rows) == len(source["files"]) == 57
    assert [row["relative_path"] for row in rows] == [
        row["relative_path"] for row in source["files"]
    ]
    assert disposition["classification_counts"] == {
        "EXACT_AT_INITIAL_TARGET": 42,
        "EXACT_MOVED_HISTORICAL": 5,
        "MODIFIED_SUCCESSOR_REPLACEMENT": 10,
    }
    by_source = {row["relative_path"]: row for row in source["files"]}
    observed_counts: dict[str, int] = {}
    repository_root = SUCCESSOR_ROOT.parents[4]
    for row in rows:
        classification = row["classification"]
        observed_counts[classification] = observed_counts.get(classification, 0) + 1
        donor = by_source[row["relative_path"]]
        current = repository_root / row["current_path"]
        assert current.is_file() and not current.is_symlink()
        observed_sha = hashlib.sha256(current.read_bytes()).hexdigest()
        assert observed_sha == row["current_sha256"]
        if classification in {"EXACT_AT_INITIAL_TARGET", "EXACT_MOVED_HISTORICAL"}:
            assert observed_sha == donor["sha256"]
        else:
            assert observed_sha != donor["sha256"]
    assert observed_counts == disposition["classification_counts"]


def test_status_preserves_claim_ceiling_and_round_accounting() -> None:
    status = json.loads((SUCCESSOR_ROOT / "AWAITING_NEW_ONE_SHOT_AUTHORIZATION.json").read_text())
    assert status["terminal"] == "AWAITING_NEW_ONE_SHOT_AUTHORIZATION"
    assert status["science_authority"]["d2"] == "CANNOT_CHECK"
    assert status["science_authority"]["d3"] == "CANNOT_CHECK"
    assert status["science_authority"]["d4"] == "OPEN"
    assert status["science_authority"]["d4_rounds_consumed"] == 0
    assert status["science_authority"]["external_authority"] is False
    assert status["science_authority"]["journal_authority"] is False
    assert status["execution_performed"] is False
    prebind = json.loads((SUCCESSOR_ROOT / "GLOBAL_REGISTRY_PREBIND_V1.json").read_text())
    by_job = {entry["job_id"]: entry for entry in prebind["submissions"]}
    assert set(by_job) == {3542994, 3544050, 3544056}
    assert by_job[3544056]["nonduplication_key"] == OLD_KEY
    assert by_job[3544056]["status"] == "TERMINAL_FAILED_KEY_CONSUMED"
    assert not (ENGINE_ROOT / "FULL_REPLAY_AUTHORIZATION.json").exists()
    consumed = ENGINE_ROOT / "historical" / "JOB_3544056_CONSUMED_AUTHORIZATION.json"
    assert hashlib.sha256(consumed.read_bytes()).hexdigest() == (
        "a9a53fc830f9a71bbaf96768d6c8b478d84fe44a9da02b6ea81932a72fa877e8"
    )
