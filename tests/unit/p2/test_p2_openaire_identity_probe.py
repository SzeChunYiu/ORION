from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/"
    "probe_autoresearchbench_wide_openaire_identity.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("p2_openaire_identity_probe_tested", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


probe = _load()


def test_explicit_arxiv_pid_is_admitted_and_version_normalized() -> None:
    ids, audit = probe.extract_structured_arxiv_ids(
        {
            "results": [
                {
                    "pid": [
                        {"scheme": "doi", "value": "10.1000/2604.25256"},
                        {"scheme": "arxiv", "value": "arXiv:2604.25256v2"},
                    ]
                }
            ]
        }
    )
    assert ids == ("2604.25256",)
    assert audit["pid_objects_examined"] == 2
    assert audit["arxiv_scheme_objects"] == 1
    assert audit["malformed_arxiv_scheme_objects"] == 0


def test_newer_pids_container_is_supported_without_raw_text_scanning() -> None:
    ids, _ = probe.extract_structured_arxiv_ids(
        {
            "results": [
                {
                    "pids": [
                        {"scheme": "ARXIV", "value": "https://arxiv.org/abs/hep-th/9901001v3"}
                    ],
                    "mainTitle": "A title containing 2604.25256 must not itself establish identity",
                    "originalIds": ["2604.25256"],
                }
            ]
        }
    )
    assert ids == ("hep-th/9901001",)


def test_digit_shaped_doi_issn_and_original_ids_are_rejected() -> None:
    ids, audit = probe.extract_structured_arxiv_ids(
        {
            "results": [
                {
                    "pid": [
                        {"scheme": "doi", "value": "10.1234/2026.37053"},
                        {"scheme": "issn", "value": "1048.2026"},
                    ],
                    "originalIds": ["2604.25256"],
                    "description": "mentions 2604.25256 in arbitrary text",
                }
            ]
        }
    )
    assert ids == ()
    assert audit["arxiv_scheme_objects"] == 0


def test_malformed_arxiv_scheme_value_is_rejected_not_coerced() -> None:
    ids, audit = probe.extract_structured_arxiv_ids(
        {
            "results": [
                {
                    "pid": [
                        {"scheme": "arxiv", "value": "doi:10.2604/25256"},
                        {"scheme": "arxiv", "value": "some text 2604.25256"},
                    ]
                }
            ]
        }
    )
    assert ids == ()
    assert audit["arxiv_scheme_objects"] == 2
    assert audit["malformed_arxiv_scheme_objects"] == 2


def test_versioned_and_unversioned_duplicates_collapse_to_one_identity() -> None:
    ids, _ = probe.extract_structured_arxiv_ids(
        {
            "results": [
                {"pid": [{"scheme": "arxiv", "value": "2604.25256v1"}]},
                {"pid": [{"scheme": "arxiv", "value": "2604.25256"}]},
            ]
        }
    )
    assert ids == ("2604.25256",)


def test_missing_results_array_fails_closed() -> None:
    with pytest.raises(ValueError, match="results array"):
        probe.extract_structured_arxiv_ids({"items": []})


def test_candidate_record_rejects_hidden_gold_fields() -> None:
    probe.validate_public_record({"task_id": "arb-wide-0001", "question": "public text"})
    with pytest.raises(AssertionError, match="schema drift|hidden"):
        probe.validate_public_record(
            {
                "task_id": "arb-wide-0001",
                "question": "public text",
                "arxiv_id": ["2604.25256"],
            }
        )


def test_query_derivation_uses_public_topical_terms_and_url_is_v3() -> None:
    query = probe.derive_openaire_query(
        "Identify papers on conformal adaptive stopping for scientific retrieval with censored routes"
    )
    assert "scientific" in query or "conformal" in query
    url = probe.build_url(query, page_size=20)
    assert url.startswith("https://api.openaire.eu/graph/v3/research-products?")
    assert "pageSize=20" in url
    assert "type=publication" in url
