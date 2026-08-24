import importlib.util
import json
from types import SimpleNamespace
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "development/p6-public-selective-revalidation-v1"
RUNNER = BASE / "run_p6_public_selective_revalidation_v1.py"
PROTOCOL = BASE / "P6_PUBLIC_SELECTIVE_REVALIDATION_PROTOCOL_V1.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("p6_public_selective_v1", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_protocol_freezes_three_licensed_domains_and_no_result():
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    runner.validate_protocol(protocol, ROOT)
    assert [row["domain"] for row in protocol["datasets"]] == [
        "scientific_workflow",
        "formal_mathematics",
        "versioned_ontology",
    ]
    assert [row["required_change_sets"] for row in protocol["datasets"]] == [100, 100, 100]
    assert protocol["results_exist"] is False
    assert protocol["authority"]["scientific_authority_delta"] == "NONE"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p.__setitem__("status", "EXECUTED"),
        lambda p: p.__setitem__("results_exist", True),
        lambda p: p["datasets"][0].__setitem__("head_commit", "0" * 40),
        lambda p: p["datasets"][1].__setitem__("license", "UNKNOWN"),
        lambda p: p["datasets"][2].__setitem__("required_change_sets", 100.0),
        lambda p: p["sampling"].__setitem__("population_inference", True),
        lambda p: p["statistics"].__setitem__("bootstrap_draws", 10000.0),
        lambda p: p["acquisition"].__setitem__("materialization", "lazy per-blob"),
        lambda p: p["runtime"].__setitem__("python", "3.12"),
        lambda p: p["selection_contract"].__setitem__("gold_independence_boundary", "independent"),
        lambda p: p["gate"].__setitem__("zero_invalid_certificates_against_native_closure", False),
        lambda p: p["retention"].__setitem__("every_attempted_domain_has_success_or_cannot_check_terminal", False),
        lambda p: p["authority"].__setitem__("closes_issue_box", True),
        lambda p: p["authority"].__setitem__("protected_custody", "PASS"),
        lambda p: p["runner"].__setitem__("sha256", "0" * 64),
    ],
)
def test_protocol_mutations_fail_closed(mutation):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    mutation(protocol)
    with pytest.raises((TypeError, ValueError)):
        runner.validate_protocol(protocol, ROOT)


def test_reverse_closure_matches_dependency_impact_direction():
    runner = load_runner()
    edges = [("analysis", "normalize"), ("normalize", "raw"), ("report", "analysis")]
    assert runner.reverse_closure(["raw"], edges) == {"raw", "normalize", "analysis", "report"}
    assert runner.reverse_closure(["analysis"], edges) == {"analysis", "report"}


def test_mutants_disagree_on_discriminating_graph():
    runner = load_runner()
    edges = [("a", "root"), ("b", "root"), ("c", "a"), ("c", "b")]
    exact = runner.reverse_closure(["a"], edges)
    mutants = runner.mutation_sets(["a"], edges)
    assert exact == {"a", "c"}
    assert all(value != exact for value in mutants.values())


def test_nextflow_parent_segments_are_normalized(monkeypatch):
    runner = load_runner()
    nodes = ["workflows/rnaseq.nf", "modules/foo.nf"]
    monkeypatch.setattr(
        runner,
        "git",
        lambda repo, *args, **kwargs: (
            "include { FOO } from '../modules/foo'\n"
            if args[0] == "show" and args[1].endswith(":workflows/rnaseq.nf")
            else ""
        ),
    )
    edges, audit = runner.dependency_edges(Path("/unused"), "head", "nfcore_rnaseq_nextflow", nodes)
    assert edges == [("workflows/rnaseq.nf", "modules/foo.nf")]
    assert audit == {"candidate_import_count": 1, "resolved_import_count": 1, "unresolved_import_count": 0, "ambiguous_import_count": 0}


def test_ontology_obo_owl_and_ofn_imports_are_parsed(monkeypatch):
    runner = load_runner()
    nodes = ["onto/a.obo", "onto/b.owl", "onto/c.ofn", "onto/d.obo"]
    contents = {
        "onto/a.obo": "import: http://example.test/b.owl\n",
        "onto/b.owl": '<owl:imports rdf:resource="http://example.test/c.ofn"/>\n',
        "onto/c.ofn": "Import(<http://example.test/d.obo>)\n",
        "onto/d.obo": "format-version: 1.2\n",
    }
    monkeypatch.setattr(runner, "git", lambda repo, *args, **kwargs: contents[args[1].split(":", 1)[1]])
    edges, audit = runner.dependency_edges(Path("/unused"), "head", "geneontology_go_ontology", nodes)
    assert edges == [("onto/a.obo", "onto/b.owl"), ("onto/b.owl", "onto/c.ofn"), ("onto/c.ofn", "onto/d.obo")]
    assert audit["candidate_import_count"] == audit["resolved_import_count"] == 3


def test_ontology_unresolved_and_ambiguous_imports_are_counted(monkeypatch):
    runner = load_runner()
    nodes = ["onto/a.obo", "x/common.obo", "y/common.obo"]
    monkeypatch.setattr(
        runner,
        "git",
        lambda repo, *args, **kwargs: "import: common.obo\nimport: missing.obo\n" if "a.obo" in args[1] else "",
    )
    edges, audit = runner.dependency_edges(Path("/unused"), "head", "geneontology_go_ontology", nodes)
    assert edges == []
    assert audit["ambiguous_import_count"] == 1
    assert audit["unresolved_import_count"] == 1


def test_block_bootstrap_is_deterministic_and_positive_for_positive_values():
    runner = load_runner()
    values = [0.5] * 100
    first = runner.block_bootstrap_lower(values, 10, 100, 7, 0.05 / 3)
    second = runner.block_bootstrap_lower(values, 10, 100, 7, 0.05 / 3)
    assert first == second == 0.5


def test_runtime_is_observed_not_hardcoded(monkeypatch):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    monkeypatch.setattr(runner.platform, "python_version", lambda: "3.12.12")
    with pytest.raises((TypeError, ValueError)):
        runner.validate_runtime(protocol)


def test_fetch_head_and_frozen_ref_must_both_match():
    runner = load_runner()
    expected = "a" * 40
    runner.verify_frozen_refs(expected, expected, expected)
    with pytest.raises(ValueError, match="frozen ref"):
        runner.verify_frozen_refs(expected, expected, "b" * 40)
    with pytest.raises(ValueError, match="fetched commit"):
        runner.verify_frozen_refs(expected, "b" * 40, expected)


def test_materialized_head_must_match_frozen_ref(monkeypatch):
    runner = load_runner()
    expected = "a" * 40
    monkeypatch.setattr(runner.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0, stderr=b""))
    monkeypatch.setattr(runner, "git", lambda *args, **kwargs: "b" * 40 + "\n")
    with pytest.raises(ValueError, match="materialized HEAD"):
        runner.materialize_frozen_head(Path("/unused"), expected)


def test_materialization_failure_is_cannot_check_input(monkeypatch):
    runner = load_runner()
    monkeypatch.setattr(runner.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=9, stdout=b"", stderr=b"failed"))
    with pytest.raises(runner.AcquisitionFailure) as raised:
        runner.materialize_frozen_head(Path("/unused"), "a" * 40)
    assert raised.value.receipt["stage"] == "MATERIALIZE_FROZEN_HEAD"
    assert raised.value.receipt["terminal"] == "EXIT_NONZERO"
    assert raised.value.receipt["exit_code"] == 9


def test_timeout_retains_structured_command_receipt(monkeypatch):
    runner = load_runner()
    def timeout(*args, **kwargs):
        raise runner.subprocess.TimeoutExpired(args[0], kwargs["timeout"], output=b"partial", stderr=b"slow")
    monkeypatch.setattr(runner.subprocess, "run", timeout)
    with pytest.raises(runner.AcquisitionFailure) as raised:
        runner.run_acquisition_command("TEST_TIMEOUT", ["git", "fetch"], Path("/unused"), 7)
    assert raised.value.receipt == {
        "stage": "TEST_TIMEOUT",
        "argv": ["git", "fetch"],
        "terminal": "TIMEOUT",
        "timeout_seconds": 7,
        "exit_code": None,
        "stdout_sha256": runner.digest(b"partial"),
        "stderr_sha256": runner.digest(b"slow"),
    }


def test_execute_retains_three_structured_cannot_check_receipts(monkeypatch):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    monkeypatch.setattr(runner, "validate_execution_source", lambda root: {"source_branch": "main", "source_commit": "f" * 40, "committed_blob_equality": {}})
    monkeypatch.setattr(runner, "validate_runtime", lambda protocol: protocol["runtime"])
    receipt = {"stage": "MATERIALIZE_FROZEN_HEAD", "argv": ["git", "checkout"], "terminal": "TIMEOUT", "timeout_seconds": 900, "exit_code": None, "stdout_sha256": None, "stderr_sha256": runner.digest(b"slow")}
    def fail(*args, **kwargs):
        raise runner.AcquisitionFailure(dict(receipt))
    monkeypatch.setattr(runner, "acquire", fail)
    result = runner.execute(protocol, ROOT)
    assert len(result["domains"]) == 3
    assert all(domain["status"] == "CANNOT_CHECK" and domain["acquisition_failure_receipt"] == receipt for domain in result["domains"])
    assert result["data_coverage_gate"] == "NOT_MET"
    assert result["native_conformance_gate"] == "NOT_MET"
    assert result["savings_gate"] == "NOT_MET"
    assert result["scientific_authority_delta"] == "NONE"


def test_execute_retains_real_git_helper_nonzero_receipts(monkeypatch):
    runner = load_runner()
    protocol = json.loads(PROTOCOL.read_text())
    monkeypatch.setattr(runner, "validate_execution_source", lambda root: {"source_branch": "main", "source_commit": "f" * 40, "committed_blob_equality": {}})
    monkeypatch.setattr(runner, "validate_runtime", lambda protocol: protocol["runtime"])
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=17, stdout=b"partial", stderr=b"denied"),
    )
    result = runner.execute(protocol, ROOT)
    assert len(result["domains"]) == 3
    for domain in result["domains"]:
        receipt = domain["acquisition_failure_receipt"]
        assert receipt["stage"] == "GIT_INIT"
        assert receipt["argv"] == ["git", "init", "--quiet"]
        assert receipt["terminal"] == "EXIT_NONZERO"
        assert receipt["exit_code"] == 17
        assert receipt["stdout_sha256"] == runner.digest(b"partial")
        assert receipt["stderr_sha256"] == runner.digest(b"denied")
    assert result["data_coverage_gate"] == "NOT_MET"
    assert result["scientific_authority_delta"] == "NONE"
