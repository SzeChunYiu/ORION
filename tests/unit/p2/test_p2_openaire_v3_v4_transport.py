from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "papers/paper-02-open-world-scientific-discovery/scripts/probe_openaire_v4_doi_filter_transport.py"
FREEZE = ROOT / "papers/paper-02-open-world-scientific-discovery/protocol/P2_WIDE_OPENAIRE_MATCHED_FREEZE_V3.json"


def _load():
    spec = importlib.util.spec_from_file_location("p2_v3_v4_transport_test_subject", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _payload(*, doi: str = "10.1038/s41586-023-06221-2") -> bytes:
    return json.dumps(
        {
            "header": {"numFound": 1},
            "results": [
                {
                    "id": "example",
                    "type": "publication",
                    "pids": [
                        {"scheme": "doi", "value": doi},
                        {"scheme": "arxiv", "value": "2305.07759"},
                    ],
                }
            ],
        }
    ).encode()


def test_v4_builder_is_one_documented_identity_filter_request():
    mod = _load()
    dois = ["10.5281/zenodo.8217359", "10.1038/s41586-023-06221-2"]
    url = mod.build_v4_crosswalk_url(dois, page_size=10)
    parsed = urlparse(url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "api-beta.openaire.eu"
    assert parsed.path == "/graph/v4/research-products"
    query = parse_qs(parsed.query, keep_blank_values=True)
    assert query == {
        "filter": [
            "ids.doi:10.5281/zenodo.8217359|10.1038/s41586-023-06221-2,type:publication"
        ],
        "page": ["1"],
        "page_size": ["10"],
        "select": ["id,pids,type"],
    }


def test_v4_builder_normalizes_and_deduplicates_in_frozen_order():
    mod = _load()
    url = mod.build_v4_crosswalk_url(
        [
            "HTTPS://DOI.ORG/10.1038/S41586-023-06221-2",
            "10.1038/s41586-023-06221-2",
            "doi:10.5281/zenodo.8217359",
        ],
        page_size=10,
    )
    filter_value = parse_qs(urlparse(url).query)["filter"][0]
    assert filter_value == (
        "ids.doi:10.1038/s41586-023-06221-2|10.5281/zenodo.8217359,type:publication"
    )


def test_structured_v4_pids_only_admit_requested_doi():
    mod = _load()
    payload = json.loads(_payload())
    requested = ["10.5281/zenodo.8217359", "10.1038/s41586-023-06221-2"]
    assert mod.extract_requested_doi_matches(payload, requested) == (
        "10.1038/s41586-023-06221-2",
    )
    payload["results"][0]["pids"] = []
    payload["results"][0]["mainTitle"] = "mentions 10.1038/s41586-023-06221-2"
    assert mod.extract_requested_doi_matches(payload, requested) == ()


def test_freeze_binds_exact_v2_parent_and_forbids_gold():
    mod = _load()
    freeze = mod.load_and_validate_freeze(FREEZE)
    assert freeze["transport_probe"]["benchmark_gold_access"] == "NONE"
    assert freeze["scientific_inheritance"]["effect_thresholds"] == "EXACT_PARENT_V2"
    assert freeze["scientific_inheritance"]["evaluation"] == "EXACT_PARENT_V2"


class _Response:
    status = 200

    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._body


def test_zero_yield_failure_persists_raw_and_pending_before_assertion(tmp_path, monkeypatch):
    mod = _load()
    body = json.dumps({"header": {"numFound": 0}, "results": []}).encode()
    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda *a, **k: _Response(body))
    with pytest.raises(ValueError, match="zero/low yield"):
        mod.capture_probe(FREEZE, tmp_path)
    assert (tmp_path / "transport_probe_response.json").read_bytes() == body
    pending = json.loads((tmp_path / "transport_probe.pending.json").read_text())
    assert pending["response_sha256"] == mod.sha256_bytes(body)
    assert pending["terminal"] == "PENDING_VALIDATION"
    assert pending["benchmark_gold_accessed"] is False
    assert not (tmp_path / "transport_probe.json").exists()


def test_final_receipt_rejects_noncanonical_matched_doi_text(tmp_path, monkeypatch):
    mod = _load()
    body = _payload()
    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda *a, **k: _Response(body))
    mod.capture_probe(FREEZE, tmp_path)
    receipt_path = tmp_path / "transport_probe.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["matched_dois"] = [receipt["matched_dois"][0].upper()]
    receipt_path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="matched DOI list"):
        mod.validate_final_receipt(
            receipt_path,
            tmp_path / "transport_probe_response.json",
            mod.load_and_validate_freeze(FREEZE),
        )
