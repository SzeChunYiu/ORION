import importlib.util
import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "development/p13-p14-live-git-acquisition-v1"
PROTOCOL = BASE / "LIVE_GIT_ACQUISITION_PROTOCOL_V1.json"
RUNNER = BASE / "run_live_git_acquisition_v1.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("p13_p14_live_git_v1", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_protocol_binds_corpus_contract_runner_and_no_authority():
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    runner.validate_protocol(protocol, ROOT)
    corpus = json.loads((ROOT / protocol["corpus"]["path"]).read_text())
    runner.validate_corpus(corpus, protocol)
    assert protocol["corpus"]["repository_count"] == 45
    assert protocol["corpus"]["eligible_repository_count"] == 31
    assert protocol["authority"]["creates_campaign_result"] is False
    assert protocol["authority"]["scientific_authority_delta"] == "NONE"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p.__setitem__("issue", 1086.0),
        lambda p: p.__setitem__("status", "EXECUTED"),
        lambda p: p["corpus"].__setitem__("sha256", "0" * 64),
        lambda p: p["runner"].__setitem__("sha256", "0" * 64),
        lambda p: p["authority"].__setitem__("creates_campaign_result", True),
        lambda p: p["authority"].__setitem__("grants_independent_adjudication", True),
        lambda p: p["authority"].__setitem__("scientific_authority_delta", "PROMOTED"),
        lambda p: p["corpus"].__setitem__("repository_count", 45.0),
        lambda p: p.__setitem__("required_observations", []),
        lambda p: p["fetch_contract"].__setitem__("depth", True),
        lambda p: p["retention"].__setitem__("all_45_rows_required", False),
        lambda p: p["retention"].__setitem__("observed_digest_mismatch_rows", "CANNOT_CHECK"),
    ],
)
def test_protocol_authority_and_identity_mutations_fail_closed(mutation):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    mutation(protocol)
    with pytest.raises((TypeError, ValueError)):
        runner.validate_protocol(protocol, ROOT)


def test_license_path_is_extracted_without_traversal():
    runner = load_runner()
    assert runner.license_path("https://github.com/pallets/flask/blob/main/LICENSE.txt") == "LICENSE.txt"
    with pytest.raises(ValueError):
        runner.license_path("https://github.com/o/r/blob/main/../secret")


def test_ineligible_entry_is_retained_without_git_execution(tmp_path):
    runner = load_runner()
    corpus = json.loads((ROOT / "papers/orion-23-responsibility-carrying-state/P13_P14_PINNED_REPOSITORY_CORPUS_V1.json").read_text())
    entry = next(row for row in corpus["entries"] if row["gold_eligible"] is False)
    result = runner.acquire(entry, tmp_path, 1)
    assert result["status"] == "EXCLUDED_LICENSE_CANNOT_CHECK"
    assert result["command_receipts"] == []


def test_eligible_entry_derives_only_bound_object_facts(monkeypatch, tmp_path):
    runner = load_runner()
    corpus = json.loads((ROOT / runner.CORPUS_PATH).read_text())
    entry = deepcopy(next(row for row in corpus["entries"] if row["gold_eligible"] is True))
    license_bytes = b"frozen license bytes\n"
    entry["license"]["evidence_fetch_sha256"] = runner.digest(license_bytes)
    outputs = iter([
        b"", b"", b"", b"", f"{entry['pinned_sha']}\n".encode(), b"",
        f"{entry['pinned_sha']} {'1' * 40}\n".encode(),
        b"1787500000\n",
        b"",
        license_bytes,
        f"{entry['pinned_sha']}\n".encode(),
    ])

    def fake_command(argv, *, cwd, timeout, retain_stdout=False):
        raw = next(outputs)
        completed = subprocess.CompletedProcess(argv, 0, raw, b"")
        receipt = {
            "argv": list(argv),
            "exit_code": 0,
            "stdout_sha256": runner.digest(raw),
            "stdout_bytes": len(raw),
            "stderr_sha256": runner.digest(b""),
            "stderr_bytes": 0,
        }
        if retain_stdout:
            receipt["stdout_utf8"] = raw.decode()
        return completed, receipt

    monkeypatch.setattr(runner, "command", fake_command)
    result = runner.acquire(entry, tmp_path, 300)
    assert result["status"] == "VERIFIED_OBJECT_FACTS"
    assert result["direct_parent_shas"] == ["1" * 40]
    assert result["committer_epoch"] == 1787500000
    assert result["license_sha256"] == runner.digest(license_bytes)
    assert "license_bytes" not in result
    assert len(result["command_receipts"]) == 11
    assert result["command_receipts"][6]["stdout_utf8"].startswith(entry["pinned_sha"])


def test_license_mismatch_is_adverse_not_cannot_check(monkeypatch, tmp_path):
    runner = load_runner()
    corpus = json.loads((ROOT / runner.CORPUS_PATH).read_text())
    entry = deepcopy(next(row for row in corpus["entries"] if row["gold_eligible"] is True))
    outputs = iter([
        b"", b"", b"", b"", f"{entry['pinned_sha']}\n".encode(), b"",
        f"{entry['pinned_sha']}\n".encode(),
        b"1787500000\n",
        b"different license bytes",
        f"{entry['pinned_sha']}\n".encode(),
    ])

    def fake_command(argv, *, cwd, timeout, retain_stdout=False):
        raw = next(outputs)
        completed = subprocess.CompletedProcess(argv, 0, raw, b"")
        receipt = {
            "argv": list(argv), "exit_code": 0,
            "stdout_sha256": runner.digest(raw), "stdout_bytes": len(raw),
            "stderr_sha256": runner.digest(b""), "stderr_bytes": 0,
        }
        if retain_stdout:
            receipt["stdout_utf8"] = raw.decode()
        return completed, receipt

    monkeypatch.setattr(runner, "command", fake_command)
    result = runner.acquire(entry, tmp_path, 300)
    assert result["status"] == "OBJECTIVE_MISMATCH"
    assert result["license_label"] == "DIGEST_MISMATCH"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row.__setitem__("pinned_sha", "0" * 40),
        lambda row: row.__setitem__("retrieval_utc", "9999-01-01T00:00:00+00:00"),
        lambda row: row["license"].__setitem__("evidence_url", "https://github.com/SzeChunYiu/ORION/blob/main/LICENSE"),
        lambda row: row["license"].__setitem__("evidence_url", row["license"]["evidence_url"].replace(f"/blob/{row['pinned_ref']}/", "/blob/wrong-ref/")),
    ],
)
def test_corpus_hostile_identity_and_chronology_mutations_fail(mutation):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    corpus = json.loads((ROOT / runner.CORPUS_PATH).read_text())
    row = next(item for item in corpus["entries"] if item["gold_eligible"] is True)
    mutation(row)
    with pytest.raises((TypeError, ValueError)):
        runner.validate_corpus(corpus, protocol)


def test_every_author_owned_subject_fails_even_when_not_orion():
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    corpus = json.loads((ROOT / runner.CORPUS_PATH).read_text())
    row = corpus["entries"][0]
    row["repo_id"] = "SzeChunYiu/not-orion"
    row["org_login"] = "SzeChunYiu"
    row["url"] = "https://github.com/SzeChunYiu/not-orion"
    with pytest.raises(ValueError, match="SzeChunYiu-owned"):
        runner.validate_corpus(corpus, protocol)


def test_execution_source_binds_clean_main_and_committed_bytes(monkeypatch):
    runner = load_runner()
    source = "a" * 40

    def fake_check_output(argv, cwd=None, text=False):
        if argv[1:3] == ["status", "--porcelain"]:
            return b""
        if argv[1:3] == ["branch", "--show-current"]:
            return "main\n"
        if argv[1:3] == ["rev-parse", "HEAD"]:
            return source + "\n"
        if argv[1] == "show":
            rel = argv[2].split(":", 1)[1]
            return (ROOT / rel).read_bytes()
        raise AssertionError(argv)

    monkeypatch.setattr(runner.subprocess, "check_output", fake_check_output)
    result = runner.validate_execution_source(ROOT)
    assert result["source_commit"] == source
    assert result["source_branch"] == "main"
    assert set(result["committed_blob_equality"]) == {
        runner.PROTOCOL_PATH, runner.RUNNER_PATH, runner.CORPUS_PATH, runner.CONTRACT_PATH
    }


def test_timeout_retains_attempt_receipt(monkeypatch, tmp_path):
    runner = load_runner()

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 1, output=b"partial", stderr=b"late")

    monkeypatch.setattr(runner.subprocess, "run", timeout)
    completed, receipt = runner.command(["git", "fetch"], cwd=tmp_path, timeout=1)
    assert completed is None
    assert receipt["attempted"] is True
    assert receipt["error_type"] == "TimeoutExpired"
    assert receipt["stdout_bytes"] == 7
