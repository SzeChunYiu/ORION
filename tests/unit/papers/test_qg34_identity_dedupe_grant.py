"""The QG-34 identity-dedupe grant must stay content-verifying.

Issue #1034 granted `check_q_qg_publication.py` a narrow carve-out so the welded
QG-34 committed result could be de-duplicated. The safety property of that grant
is that it admits *only* a change it can mechanically prove leaves every
measurement field byte-identical and invents no identity value. These tests pin
that property: each `refuses_*` case is a way the carve-out could become a hole.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
CHECKER = ROOT / "papers" / "check_q_qg_publication.py"


@pytest.fixture(scope="module")
def guard():
    spec = importlib.util.spec_from_file_location("q_qg_publication_guard", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NEW_BLOB = b"0fb6e2a0b6ff7d9960ab09942a402a304a890d71"
STALE_PIN = b"61ad64ed01036b1dd44d7c684c35e43c62534c29"

# A welded committed result: two identity blocks, one measurement block.
WELDED = b"""{
  "class_depths": [0, 1, 2, 3],
  "issue": "SzeChunYiu/ORION#924",
  "schema": "ORION.QG.QG34.CommittedResult.v1",
  "terminal": "QG34_SUPERSEDED",
  "worst_case_depth": 3,
  "schema": "ORIONQG.QG34.CommittedResult.v1",
  "terminal": "QG34_PRODUCER_NATIVE"
}"""

DEDUPED = json.dumps(
    {
        "class_depths": [0, 1, 2, 3],
        "issue": "SzeChunYiu/ORION#924",
        "schema": "ORIONQG.QG34.CommittedResult.v1",
        "terminal": "QG34_PRODUCER_NATIVE",
        "worst_case_depth": 3,
        "freeze_registry": {
            "schema": "ORION.QG.QG34.CommittedResult.v1",
            "terminal": "QG34_SUPERSEDED",
        },
    }
).encode()


def _mutate(**changes) -> bytes:
    body = json.loads(DEDUPED)
    for key, value in changes.items():
        if value is _DROP:
            body.pop(key)
        else:
            body[key] = value
    return json.dumps(body).encode()


_DROP = object()


def test_accepts_the_real_dedupe(guard):
    assert guard.is_qg34_committed_result_dedupe(WELDED, DEDUPED) is True


@pytest.mark.parametrize(
    "case, head",
    [
        ("measurement value changed", lambda: _mutate(worst_case_depth=2)),
        ("measurement list changed", lambda: _mutate(class_depths=[9, 1, 2, 3])),
        ("identity value invented", lambda: _mutate(terminal="QG34_BRAND_NEW_CLAIM")),
        ("demoted identity discarded", lambda: _mutate(freeze_registry=_DROP)),
        ("measurement key dropped", lambda: _mutate(worst_case_depth=_DROP)),
        ("extra top-level key added", lambda: _mutate(new_authority_flag=True)),
    ],
)
def test_refuses_tampered_committed_result(guard, case, head):
    assert guard.is_qg34_committed_result_dedupe(WELDED, head()) is False, case


def test_refuses_head_that_still_carries_duplicates(guard):
    assert guard.is_qg34_committed_result_dedupe(WELDED, WELDED) is False


def test_is_inert_when_base_was_never_welded(guard):
    assert guard.is_qg34_committed_result_dedupe(DEDUPED, DEDUPED) is False


LOADER_BASE = b"""import json
Q34_GIT_BLOB_SHA1="%s"
def main():
 a=json.loads(Q34.read_text());assert len(D)==92
""" % STALE_PIN

LOADER_HEAD = (
    b'import json\nQ34_GIT_BLOB_SHA1="'
    + NEW_BLOB
    + b'"\n'
    + b'def no_dupes(pairs):\n'
    b' d={}\n'
    b' for k,v in pairs:\n'
    b'  if k in d:raise ValueError("duplicate committed-result keys: "+k)\n'
    b'  d[k]=v\n'
    b' return d\n'
    b'def load_committed_result(p):return json.loads(p.read_text(),object_pairs_hook=no_dupes)\n'
    b'def main():\n a=load_committed_result(Q34);assert len(D)==92\n'
)


def test_accepts_loader_pin_rebind_plus_strict_parser(guard):
    assert guard.is_qg34_loader_rebind(LOADER_BASE, LOADER_HEAD, NEW_BLOB) is True


@pytest.mark.parametrize(
    "case, head",
    [
        ("assertion weakened", LOADER_HEAD.replace(b"len(D)==92", b"len(D)>=0")),
        ("extra code smuggled in", LOADER_HEAD + b"import os\n"),
        ("strict parser omitted", LOADER_BASE.replace(STALE_PIN, NEW_BLOB)),
    ],
)
def test_refuses_tampered_loader(guard, case, head):
    assert guard.is_qg34_loader_rebind(LOADER_BASE, head, NEW_BLOB) is False, case


def test_refuses_loader_rebound_to_a_foreign_sha(guard):
    assert guard.is_qg34_loader_rebind(LOADER_BASE, LOADER_HEAD, b"f" * 40) is False


DOC_BASE = b"frozen into QG-36 by exact Git blob SHA `" + STALE_PIN + b"`. It must provide:\n"
DOC_HEAD = b"frozen into QG-36 by exact Git blob SHA `" + NEW_BLOB + b"`. It must provide:\n"


def test_accepts_doc_pin_rebind(guard):
    assert guard.is_qg34_pin_rebind_only(DOC_BASE, DOC_HEAD, NEW_BLOB) is True


def test_refuses_doc_changed_beyond_the_pin(guard):
    tampered = DOC_HEAD.replace(b"It must provide:", b"It need not provide:")
    assert guard.is_qg34_pin_rebind_only(DOC_BASE, tampered, NEW_BLOB) is False
