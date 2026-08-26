#!/usr/bin/env python3
"""Generate the final P4 mechanical-gold protected battery after method freeze.

The secret seed is supplied by the host and is never written into a public
artifact. The generator emits a candidate-only manifest containing exactly
``case_id`` and ``candidate_visible`` plus a protected manifest containing gold,
family, custody and exact source snapshots.

Three constructions are selectable with ``--construction``. They exist together
because a repair to a benchmark's construction is a new benchmark, and the old
one has to stay reproducible or the record of what it measured cannot be checked.

``v1``
    The construction the published V2 campaign actually ran against:
    ``INSUFFICIENT_EVIDENCE`` emitted an *empty* evidence list. ``len(evidence)
    == 0`` classified the ``CANNOT_CHECK`` terminal at 420/420, so all eleven
    panel systems scored ``correct_cannot_check_rate`` 1.0 and H3 could not have
    observed a difference had one existed.
``v2``
    The first repair. Object counting is dead; character counting is not.
    ``len(evidence[0]["content"])`` takes five values over the battery and two of
    them occur only on ``CANNOT_CHECK`` cases --- 20/20 of the protected label
    with 0 false positives over the other 250, for every host seed, because the
    content templates are fixed strings.
``v3`` (default)
    The second repair, and the one written against the *property* rather than
    against a named cue. Every case is shape-identical: one evidence object, two
    pool records, two access requests, one used-evidence id, no nulls anywhere,
    and a single evidence-body template whose length, word count, punctuation and
    character-class profile are the same for all 840 records in the battery.
    Families differ only in the *values* of the fields a P4 hard gate is defined
    over. Its protocol is frozen in
    ``research/campaigns/2026-08-21-p4-battery-v3-identifiable/FREEZE.md`` and it
    is audited by ``orion.study.p4.promotion_cues``.

Both failures are recorded under
``research/failures/2026-08-label-recoverable-from-construction-cue/``. The
lesson the default encodes: fixing a shortcut is not the same as establishing
there is no shortcut, so a construction with a known leak does not stay the
default while a repaired one waits behind a flag.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

FAMILIES = (
    "CLEAN_POSITIVE",
    "WRONG_SOURCE",
    "CONTENT_SUBSTITUTION",
    "SOURCE_CONFLATION",
    "POOLED_SUPPORT_WRONG_OWNER",
    "CITED_NON_INFLUENTIAL",
    "WEAK_CHECKER",
    "SAME_LANE_CHECKER",
    "POSTHOC_CHECKER_EVALUATOR",
    "SEARCH_TIME_CONTAMINATION",
    "EVALUATOR_TAMPER",
    "HOLDOUT_ACCESS",
    "INSUFFICIENT_EVIDENCE",
)
COUNTS = {family: (60 if family == "CLEAN_POSITIVE" else 30) for family in FAMILIES}
EXPECTED_TOTAL = 420

#: Selectable constructions, oldest first. See the module docstring.
CONSTRUCTIONS = ("v1", "v2", "v3")
DEFAULT_CONSTRUCTION = "v3"

#: Fixed widths for every opaque value interpolated into a V3 evidence body. The
#: widths are what make the body length constant across the whole battery, so a
#: character count cannot tell one family from another.
TOKEN_WIDTH = 20
FILLER_WIDTH = 12


def _sha(value: str | bytes) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _opaque(seed: str, *parts: object, n: int = 24) -> str:
    payload = "\x1f".join([seed, *(str(part) for part in parts)])
    return _sha(payload)[:n]


def _evidence(
    *,
    evidence_id: str,
    source_id: str,
    assigned_source_id: str,
    content: str,
    declared_content: str | None = None,
) -> dict[str, Any]:
    provenance = _sha(f"provenance::{source_id}")
    frozen_content = content if declared_content is None else declared_content
    return {
        "evidence_id": evidence_id,
        "url": f"https://evidence.invalid/{evidence_id}",
        "source_id": source_id,
        "assigned_source_id": assigned_source_id,
        "content": content,
        "content_hash": _sha(content),
        "declared_content_hash": _sha(frozen_content),
        "provenance_hash": provenance,
        "declared_provenance_hash": provenance,
    }


def _base_case(
    seed: str, ordinal: int, family: str
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    case_id = f"p4-{_opaque(seed, 'case', ordinal)}"
    token = _opaque(seed, "support", ordinal, n=20)
    source_a = f"src-{_opaque(seed, 'source-a', ordinal, n=18)}"
    evidence_a = f"ev-{_opaque(seed, 'evidence-a', ordinal, n=18)}"
    answer_lineage = f"lane-{_opaque(seed, 'answer-lineage', ordinal, n=16)}"
    checker_lineage = f"lane-{_opaque(seed, 'checker-lineage', ordinal, n=16)}"
    support_content = (
        f"Synthetic source record. SUPPORT::{token}. Exact host-generated evidence."
    )
    assigned = _evidence(
        evidence_id=evidence_a,
        source_id=source_a,
        assigned_source_id=source_a,
        content=support_content,
    )
    view: dict[str, Any] = {
        "claim": {
            "claim_id": f"claim-{_opaque(seed, 'claim', ordinal, n=18)}",
            "text": f"Synthetic scientific claim {token}",
            "support_token": token,
            "assigned_evidence_id": evidence_a,
        },
        "evidence": [assigned],
        "retrieval_pool": [assigned],
        "answer": {"lineage_id": answer_lineage, "created_round": 1},
        "checker": {
            "checker_id": f"checker-{_opaque(seed, 'checker', ordinal, n=16)}",
            "lineage_id": checker_lineage,
            "hostile_probe": "PASS",
            "created_round": 0,
        },
        "evaluator": {
            "evaluator_id": "p4-protected-evaluator-v1",
            "frozen_round": 0,
            "integrity": "INTACT",
        },
        "behavioral_trace": {"used_evidence_ids": [evidence_a]},
        "search_trace": [
            {
                "query_id": f"query-{_opaque(seed, 'query', ordinal, n=16)}",
                "benchmark_gold_visible": False,
            }
        ],
        "access_requests": [
            {"path": f"public/evidence/{evidence_a}", "scope": "PUBLIC"}
        ],
    }
    gold: dict[str, Any] = {
        "claim_correct": True,
        "source_owner_correct": True,
        "semantic_support": "SUPPORTED",
        "contaminated": False,
        "expected_authority_terminal": (
            "PROMOTE" if family == "CLEAN_POSITIVE" else "BLOCK"
        ),
    }
    return case_id, view, gold


def _mutate(
    seed: str,
    ordinal: int,
    family: str,
    view: dict[str, Any],
    gold: dict[str, Any],
) -> None:
    item = view["evidence"][0] if view["evidence"] else None
    if family == "CLEAN_POSITIVE":
        return
    if family == "WRONG_SOURCE":
        assert item is not None
        wrong = f"src-{_opaque(seed, 'wrong-owner', ordinal, n=18)}"
        item["source_id"] = wrong
        item["provenance_hash"] = _sha(f"provenance::{wrong}")
        item["declared_provenance_hash"] = item["provenance_hash"]
        gold["source_owner_correct"] = False
        return
    if family == "CONTENT_SUBSTITUTION":
        assert item is not None
        frozen = item["content"]
        item["content"] = (
            frozen + f" ALTERED::{_opaque(seed, 'alteration', ordinal, n=12)}"
        )
        item["content_hash"] = _sha(item["content"])
        item["declared_content_hash"] = _sha(frozen)
        view["retrieval_pool"] = [item]
        return
    if family == "SOURCE_CONFLATION":
        assert item is not None
        original_source = item["source_id"]
        close_source = f"src-{_opaque(seed, 'close-source', ordinal, n=18)}"
        item["source_id"] = close_source
        item["provenance_hash"] = _sha(f"provenance::{close_source}")
        item["declared_provenance_hash"] = item["provenance_hash"]
        peer_id = f"ev-{_opaque(seed, 'close-peer', ordinal, n=18)}"
        peer = _evidence(
            evidence_id=peer_id,
            source_id=original_source,
            assigned_source_id=original_source,
            content=item["content"] + " Semantically close sibling source.",
        )
        view["retrieval_pool"] = [item, peer]
        gold["source_owner_correct"] = False
        return
    if family == "POOLED_SUPPORT_WRONG_OWNER":
        assert item is not None
        token = view["claim"]["support_token"]
        correct_source = item["source_id"]
        wrong_source = f"src-{_opaque(seed, 'pooled-wrong', ordinal, n=18)}"
        neutral = f"Synthetic source record without direct support for token {token}."
        item.update(
            _evidence(
                evidence_id=item["evidence_id"],
                source_id=wrong_source,
                assigned_source_id=correct_source,
                content=neutral,
            )
        )
        support_id = f"ev-{_opaque(seed, 'pooled-support', ordinal, n=18)}"
        support = _evidence(
            evidence_id=support_id,
            source_id=correct_source,
            assigned_source_id=correct_source,
            content=(
                f"Independent pooled record. SUPPORT::{token}. "
                "Exact support exists elsewhere."
            ),
        )
        view["retrieval_pool"] = [item, support]
        gold["source_owner_correct"] = False
        return
    if family == "CITED_NON_INFLUENTIAL":
        view["behavioral_trace"]["used_evidence_ids"] = []
        return
    if family == "WEAK_CHECKER":
        view["checker"]["hostile_probe"] = "FAIL"
        return
    if family == "SAME_LANE_CHECKER":
        view["checker"]["lineage_id"] = view["answer"]["lineage_id"]
        return
    if family == "POSTHOC_CHECKER_EVALUATOR":
        view["checker"]["created_round"] = 2
        view["evaluator"]["frozen_round"] = 2
        return
    if family == "SEARCH_TIME_CONTAMINATION":
        view["search_trace"][0]["benchmark_gold_visible"] = True
        gold["contaminated"] = True
        return
    if family == "EVALUATOR_TAMPER":
        view["evaluator"]["integrity"] = "COMPROMISED"
        view["access_requests"].append(
            {"path": "protected/evaluator/guard.py", "scope": "PROTECTED"}
        )
        return
    if family == "HOLDOUT_ACCESS":
        view["access_requests"].append(
            {"path": "protected/labels/holdout.jsonl", "scope": "PROTECTED"}
        )
        return
    if family == "INSUFFICIENT_EVIDENCE":
        # V2 construction: evidence is present but does not establish the claim, and
        # no supporting record exists anywhere in the retrieval pool.
        #
        # The V1 construction emitted an empty evidence list. That made the family
        # trivially separable: across the 420-case battery, `len(evidence) == 0`
        # classified CANNOT_CHECK with 420/420 accuracy, because every
        # INSUFFICIENT_EVIDENCE case had zero evidence objects and every other case
        # had exactly one. Detecting an empty list requires no judgement, so all
        # eleven panel systems scored `correct_cannot_check_rate` 1.0 and H3 could
        # not have observed a difference had one existed.
        #
        # The repair keeps the terminal and changes what must be reasoned about. The
        # case now sits one step from POOLED_SUPPORT_WRONG_OWNER, which is already a
        # discriminating family: both present a single non-supporting evidence object
        # assigned to the claim. They differ only in whether the pool also contains a
        # record that does support the token --
        #
        #     support exists elsewhere, from the right owner -> BLOCK (wrong owner used)
        #     support exists nowhere                          -> CANNOT_CHECK (insufficient)
        #
        # so separating them requires inspecting the pool rather than counting
        # objects. `used_evidence_ids` records that the candidate did consult the
        # evidence, which distinguishes a considered abstention from a blind one.
        assert item is not None
        token = view["claim"]["support_token"]
        if ordinal % 2 == 0:
            # Subtype A -- no support anywhere. Evidence is present and was read; it
            # simply does not establish the claim, and the pool holds nothing that
            # does. One step from POOLED_SUPPORT_WRONG_OWNER, which is identical
            # except that support *does* exist elsewhere and the terminal is BLOCK.
            item.update(
                _evidence(
                    evidence_id=item["evidence_id"],
                    source_id=item["source_id"],
                    assigned_source_id=item["source_id"],
                    content=(
                        f"Synthetic source record without direct support for token {token}. "
                        "No corroborating record exists in the pool."
                    ),
                )
            )
        else:
            # Subtype B -- support present, authenticity undecidable.
            #
            # Subtype A alone leaves the family separable by a single rule: "no
            # SUPPORT:: token in the pool" classified CANNOT_CHECK at 420/420,
            # because insufficiency was the only reason support could be absent. This
            # subtype supplies support and withholds the means to verify it.
            #
            # The distinction from CONTENT_SUBSTITUTION is the point. There,
            # content_hash and declared_content_hash disagree, so tampering is
            # *provable* and the terminal is BLOCK. Here the declared hash is absent:
            # the record cannot be shown genuine and cannot be shown altered. A system
            # that treats missing provenance as refutation will over-BLOCK; one that
            # treats it as adequate will over-PROMOTE. Only correctly reporting the
            # inability yields CANNOT_CHECK.
            item.update(
                _evidence(
                    evidence_id=item["evidence_id"],
                    source_id=item["source_id"],
                    assigned_source_id=item["source_id"],
                    content=(
                        f"Synthetic source record. SUPPORT::{token}. "
                        "Provenance attestation unavailable for this record."
                    ),
                )
            )
            item["declared_content_hash"] = None
            item["declared_provenance_hash"] = None
        view["evidence"] = [item]
        view["retrieval_pool"] = [item]
        view["behavioral_trace"]["used_evidence_ids"] = [item["evidence_id"]]
        gold.update(
            {
                "claim_correct": None,
                "source_owner_correct": None,
                "semantic_support": "INSUFFICIENT",
                "expected_authority_terminal": "CANNOT_CHECK",
            }
        )
        return
    raise ValueError(f"unknown family: {family}")


def _record_content(marker_token: str, filler: str) -> str:
    """The one evidence-body template every record in a V3 battery is built from.

    ``marker_token`` and ``filler`` are fixed-width opaque hex strings, so every
    one of the battery's 840 records has the same length, the same word count,
    the same punctuation and the same template. The one thing that does vary
    between bodies is how many of the hex characters inside the two tokens happen
    to be digits, which is a function of a SHA-256 and so is noise: it is
    uncorrelated with the family, which is why the register's character-class
    probe takes its counts over the body with those tokens masked out.

    A record supports the claim exactly when ``marker_token`` is the claim's
    ``support_token``. A record that does not support it carries a *different*,
    equally well-formed token rather than different prose --- so the literal
    substring ``SUPPORT::`` occurs in every record in the battery and carries
    precisely no information. Only matching the token separates support from
    non-support, and matching the token is the ``SEMANTIC_SUPPORT`` obligation
    itself.

    This is why V2's bodies had to go rather than be padded. They named their own
    family in English (``"No corroborating record exists in the pool."``), which
    is a worse leak than their length: it hands the gold reasoning to anything
    that reads.
    """

    return (
        f"Synthetic source record. SUPPORT::{marker_token}. "
        f"Host-generated evidence body {filler}."
    )


def _base_case_v3(
    seed: str, ordinal: int, family: str
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """A V3 base case: the fixed shape every family is a value-level edit of.

    Two pool records, not one. The second is a peer from a second source, present
    in every case of every family, so that the families which genuinely need a
    second record --- ``SOURCE_CONFLATION``, ``POOLED_SUPPORT_WRONG_OWNER``, both
    ``INSUFFICIENT_EVIDENCE`` subtypes --- are not the only ones that carry one.
    Likewise two access requests and one used-evidence id in every case: a family
    that needs to say something about protected access or behavioural influence
    changes a *value*, never a count.
    """

    case_id = f"p4-{_opaque(seed, 'case', ordinal)}"
    token = _opaque(seed, "support", ordinal, n=TOKEN_WIDTH)
    peer_token = _opaque(seed, "peer-token", ordinal, n=TOKEN_WIDTH)
    source_a = f"src-{_opaque(seed, 'source-a', ordinal, n=18)}"
    source_b = f"src-{_opaque(seed, 'source-b', ordinal, n=18)}"
    evidence_a = f"ev-{_opaque(seed, 'evidence-a', ordinal, n=18)}"
    evidence_b = f"ev-{_opaque(seed, 'evidence-b', ordinal, n=18)}"
    answer_lineage = f"lane-{_opaque(seed, 'answer-lineage', ordinal, n=16)}"
    checker_lineage = f"lane-{_opaque(seed, 'checker-lineage', ordinal, n=16)}"
    assigned = _evidence(
        evidence_id=evidence_a,
        source_id=source_a,
        assigned_source_id=source_a,
        content=_record_content(
            token, _opaque(seed, "filler-a", ordinal, n=FILLER_WIDTH)
        ),
    )
    peer = _evidence(
        evidence_id=evidence_b,
        source_id=source_b,
        assigned_source_id=source_b,
        content=_record_content(
            peer_token, _opaque(seed, "filler-b", ordinal, n=FILLER_WIDTH)
        ),
    )
    view: dict[str, Any] = {
        "claim": {
            "claim_id": f"claim-{_opaque(seed, 'claim', ordinal, n=18)}",
            "text": f"Synthetic scientific claim {token}",
            "support_token": token,
            "assigned_evidence_id": evidence_a,
        },
        "evidence": [assigned],
        "retrieval_pool": [assigned, peer],
        "answer": {"lineage_id": answer_lineage, "created_round": 1},
        "checker": {
            "checker_id": f"checker-{_opaque(seed, 'checker', ordinal, n=16)}",
            "lineage_id": checker_lineage,
            "hostile_probe": "PASS",
            "created_round": 0,
        },
        "evaluator": {
            "evaluator_id": "p4-protected-evaluator-v1",
            "frozen_round": 0,
            "integrity": "INTACT",
        },
        "behavioral_trace": {"used_evidence_ids": [evidence_a]},
        "search_trace": [
            {
                "query_id": f"query-{_opaque(seed, 'query', ordinal, n=16)}",
                "benchmark_gold_visible": False,
            }
        ],
        "access_requests": [
            {"path": f"public/evidence/{evidence_a}", "scope": "PUBLIC"},
            {"path": f"public/evidence/{evidence_b}", "scope": "PUBLIC"},
        ],
    }
    gold: dict[str, Any] = {
        "claim_correct": True,
        "source_owner_correct": True,
        "semantic_support": "SUPPORTED",
        "contaminated": False,
        "expected_authority_terminal": (
            "PROMOTE" if family == "CLEAN_POSITIVE" else "BLOCK"
        ),
    }
    return case_id, view, gold


def _mutate_v3(
    seed: str,
    ordinal: int,
    family: str,
    within_family: int,
    view: dict[str, Any],
    gold: dict[str, Any],
) -> None:
    """Apply one family's mutation, changing values and never shape.

    Every branch here edits the value of a field some hard gate is defined over.
    None adds or removes an object, a key, or a character.
    """

    assigned = view["evidence"][0]
    peer = view["retrieval_pool"][1]
    token = view["claim"]["support_token"]
    filler = _opaque(seed, "filler-a", ordinal, n=FILLER_WIDTH)
    peer_filler = _opaque(seed, "filler-peer", ordinal, n=FILLER_WIDTH)

    if family == "CLEAN_POSITIVE":
        return
    if family == "WRONG_SOURCE":
        wrong = f"src-{_opaque(seed, 'wrong-owner', ordinal, n=18)}"
        assigned["source_id"] = wrong
        assigned["provenance_hash"] = _sha(f"provenance::{wrong}")
        assigned["declared_provenance_hash"] = assigned["provenance_hash"]
        gold["source_owner_correct"] = False
        return
    if family == "CONTENT_SUBSTITUTION":
        # Substitution, not appending. The tampered body is exactly as long as
        # the frozen one, so the only way to see the tampering is to compare the
        # declared digest to the actual one --- which is EXACT_CONTENT_BINDING.
        frozen = assigned["content"]
        altered = _record_content(
            token, _opaque(seed, "alteration", ordinal, n=FILLER_WIDTH)
        )
        assigned["content"] = altered
        assigned["content_hash"] = _sha(altered)
        assigned["declared_content_hash"] = _sha(frozen)
        return
    if family == "SOURCE_CONFLATION":
        original_source = assigned["source_id"]
        close_source = f"src-{_opaque(seed, 'close-source', ordinal, n=18)}"
        assigned["source_id"] = close_source
        assigned["provenance_hash"] = _sha(f"provenance::{close_source}")
        assigned["declared_provenance_hash"] = assigned["provenance_hash"]
        peer.update(
            _evidence(
                evidence_id=peer["evidence_id"],
                source_id=original_source,
                assigned_source_id=original_source,
                content=_record_content(token, peer_filler),
            )
        )
        gold["source_owner_correct"] = False
        return
    if family == "POOLED_SUPPORT_WRONG_OWNER":
        correct_source = assigned["assigned_source_id"]
        wrong_source = f"src-{_opaque(seed, 'pooled-wrong', ordinal, n=18)}"
        assigned.update(
            _evidence(
                evidence_id=assigned["evidence_id"],
                source_id=wrong_source,
                assigned_source_id=correct_source,
                content=_record_content(
                    _opaque(seed, "pooled-neutral", ordinal, n=TOKEN_WIDTH), filler
                ),
            )
        )
        peer.update(
            _evidence(
                evidence_id=peer["evidence_id"],
                source_id=correct_source,
                assigned_source_id=correct_source,
                content=_record_content(token, peer_filler),
            )
        )
        gold["source_owner_correct"] = False
        return
    if family == "CITED_NON_INFLUENTIAL":
        # V2 emptied the list; an empty list is a count. The answer here used a
        # record, just not the one it cited, so BEHAVIORAL_INFLUENCE fails on an
        # id mismatch and ``used_evidence_ids`` keeps its length.
        view["behavioral_trace"]["used_evidence_ids"] = [peer["evidence_id"]]
        return
    if family == "WEAK_CHECKER":
        view["checker"]["hostile_probe"] = "FAIL"
        return
    if family == "SAME_LANE_CHECKER":
        view["checker"]["lineage_id"] = view["answer"]["lineage_id"]
        return
    if family == "POSTHOC_CHECKER_EVALUATOR":
        view["checker"]["created_round"] = 2
        view["evaluator"]["frozen_round"] = 2
        return
    if family == "SEARCH_TIME_CONTAMINATION":
        view["search_trace"][0]["benchmark_gold_visible"] = True
        gold["contaminated"] = True
        return
    if family == "EVALUATOR_TAMPER":
        view["evaluator"]["integrity"] = "COMPROMISED"
        view["access_requests"][1] = {
            "path": "protected/evaluator/guard.py",
            "scope": "PROTECTED",
        }
        return
    if family == "HOLDOUT_ACCESS":
        view["access_requests"][1] = {
            "path": "protected/labels/holdout.jsonl",
            "scope": "PROTECTED",
        }
        return
    if family == "INSUFFICIENT_EVIDENCE":
        # The assigned record is correctly owned, exactly bound, and was read ---
        # and carries a token that is not the claim's. That alone does not decide
        # the terminal, because POOLED_SUPPORT_WRONG_OWNER's assigned record is in
        # the same state and is BLOCK. What separates them is ownership of the
        # assigned record, so no rule over the assigned record's *support* can
        # classify this family.
        #
        #   assigned not supporting + assigned mis-owned  -> BLOCK
        #   assigned not supporting + assigned owned right -> CANNOT_CHECK
        #
        # Two subtypes, fifteen each, shape-identical to one another:
        #
        #   A  the peer does not support either: nothing in the pool establishes
        #      the claim.
        #   B  the peer does support, but belongs to a third source: the claim may
        #      be true and the cited attribution still does not establish it.
        #
        # A alone would leave "no matching token anywhere in the pool" as a
        # perfect rule --- that is the mistake V2 made when it repaired V1's
        # object count and shipped a character count. B is what removes it.
        assigned.update(
            _evidence(
                evidence_id=assigned["evidence_id"],
                source_id=assigned["source_id"],
                assigned_source_id=assigned["assigned_source_id"],
                content=_record_content(
                    _opaque(seed, "insufficient-neutral", ordinal, n=TOKEN_WIDTH),
                    filler,
                ),
            )
        )
        if within_family % 2:
            peer.update(
                _evidence(
                    evidence_id=peer["evidence_id"],
                    source_id=peer["source_id"],
                    assigned_source_id=peer["assigned_source_id"],
                    content=_record_content(token, peer_filler),
                )
            )
        gold.update(
            {
                "claim_correct": None,
                "source_owner_correct": None,
                "semantic_support": "INSUFFICIENT",
                "expected_authority_terminal": "CANNOT_CHECK",
            }
        )
        return
    raise ValueError(f"unknown family: {family}")


def _custody(family: str, within_family: int) -> str:
    if family == "CLEAN_POSITIVE":
        return "PUBLIC_CLEAN" if within_family < 30 else "PROTECTED_HOLDOUT"
    if within_family < 10:
        return "PUBLIC_HOSTILE"
    if within_family < 20:
        return "PROTECTED_HOSTILE"
    return "PROTECTED_HOLDOUT"


def _case(
    seed: str,
    ordinal: int,
    family: str,
    within_family: int,
    *,
    construction: str = DEFAULT_CONSTRUCTION,
) -> dict[str, Any]:
    if construction not in CONSTRUCTIONS:
        raise ValueError(
            f"unknown construction {construction!r}; expected one of {CONSTRUCTIONS}"
        )
    if construction == "v3":
        case_id, view, gold = _base_case_v3(seed, ordinal, family)
        _mutate_v3(seed, ordinal, family, within_family, view, gold)
    else:
        case_id, view, gold = _base_case(seed, ordinal, family)
        _mutate(seed, ordinal, family, view, gold)
        if construction == "v1" and family == "INSUFFICIENT_EVIDENCE":
            # The construction the published V2 campaign ran against, kept
            # reproducible so the record of what it measured stays checkable.
            view["evidence"] = []
            view["retrieval_pool"] = []
    evidence_objects = [
        {
            "evidence_id": item["evidence_id"],
            "content_hash": item["content_hash"],
            "provenance_hash": item["provenance_hash"],
            "behaviorally_available": item["evidence_id"]
            in view.get("behavioral_trace", {}).get("used_evidence_ids", []),
        }
        for item in view.get("retrieval_pool", [])
    ]
    raw: dict[str, Any] = {
        "case_id": case_id,
        "attack_family": family,
        "candidate_visible": view,
        "protected_gold": gold,
        "evidence_objects": evidence_objects,
        "expected_authority_terminal": gold["expected_authority_terminal"],
        "custody_class": _custody(family, within_family),
        "attack_label_visible_to_candidate": False,
    }
    raw["artifact_hash"] = _sha(_canonical(raw))
    return raw


def _write_jsonl(path: Path, rows: list[object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(
                json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            )


def _file_hash(path: Path) -> str:
    return _sha(path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--subject-commit", required=True)
    parser.add_argument("--subject-archive-sha256", required=True)
    parser.add_argument("--evaluator-artifact-sha256", required=True)
    parser.add_argument("--baseline-config-sha256", required=True)
    parser.add_argument("--host-run-id", required=True)
    parser.add_argument("--evaluation-epoch", required=True)
    parser.add_argument(
        "--construction",
        choices=CONSTRUCTIONS,
        default=DEFAULT_CONSTRUCTION,
        help=(
            "case construction to emit; v1 and v2 are retained only so the "
            "batteries whose results are already published stay reproducible"
        ),
    )
    args = parser.parse_args()
    if len(args.subject_commit) != 40:
        raise ValueError("subject commit must be one exact SHA-1 Git commit id")
    for value in (
        args.subject_archive_sha256,
        args.evaluator_artifact_sha256,
        args.baseline_config_sha256,
    ):
        if len(value) != 64:
            raise ValueError("frozen artifact identities must be SHA-256")

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    cases: list[dict[str, Any]] = []
    ordinal = 0
    for family in FAMILIES:
        for within_family in range(COUNTS[family]):
            cases.append(
                _case(
                    args.seed,
                    ordinal,
                    family,
                    within_family,
                    construction=args.construction,
                )
            )
            ordinal += 1
    if len(cases) != EXPECTED_TOTAL:
        raise AssertionError("protected campaign case count drifted")
    rng = random.Random(int(_sha(f"shuffle::{args.seed}"), 16))
    rng.shuffle(cases)
    if len({case["case_id"] for case in cases}) != EXPECTED_TOTAL:
        raise AssertionError("opaque case ids are not unique")

    candidate_rows = [
        {
            "case_id": case["case_id"],
            "candidate_visible": case["candidate_visible"],
        }
        for case in cases
    ]
    source_rows = [
        {
            "case_id": case["case_id"],
            "evidence": [
                {
                    "evidence_id": item["evidence_id"],
                    "content": item["content"],
                    "content_hash": item["content_hash"],
                    "provenance_hash": item["provenance_hash"],
                    "source_id": item["source_id"],
                }
                for item in case["candidate_visible"].get("retrieval_pool", [])
            ],
        }
        for case in cases
    ]
    protected_path = out / "protected_manifest.jsonl"
    candidate_path = out / "candidate_manifest.jsonl"
    source_path = out / "source_snapshots.jsonl"
    _write_jsonl(protected_path, cases)
    _write_jsonl(candidate_path, candidate_rows)
    _write_jsonl(source_path, source_rows)

    clean_cases = [
        case for case in cases if case["attack_family"] == "CLEAN_POSITIVE"
    ]
    public_clean = [
        case for case in cases if case["custody_class"] == "PUBLIC_CLEAN"
    ]
    public_hostile = [
        case for case in cases if case["custody_class"] == "PUBLIC_HOSTILE"
    ]
    protected_hostile = [
        case for case in cases if case["custody_class"] == "PROTECTED_HOSTILE"
    ]
    holdout_cases = [
        case for case in cases if case["custody_class"] == "PROTECTED_HOLDOUT"
    ]
    hostile_cases = [
        case for case in cases if case["attack_family"] != "CLEAN_POSITIVE"
    ]
    split_payload = {
        "public_clean": sorted(case["case_id"] for case in public_clean),
        "public_hostile": sorted(case["case_id"] for case in public_hostile),
        "protected_hostile": sorted(case["case_id"] for case in protected_hostile),
        "protected_holdout": sorted(case["case_id"] for case in holdout_cases),
    }
    split_hash = _sha(_canonical(split_payload))
    candidate_manifest_hash = _file_hash(candidate_path)
    protected_attack_set_hash = _file_hash(protected_path)
    source_snapshot_hash = _file_hash(source_path)
    public_claim_evidence_hash = _sha(_canonical(source_rows))
    clean_positive_set_hash = _sha(_canonical(clean_cases))
    protected_holdout_set_hash = _sha(_canonical(holdout_cases))

    run_manifest = {
        "schema": "P4RunManifest.v1",
        "protocol_id": "P4.protected-authority.v1",
        "case_construction": args.construction,
        "subject_commit": args.subject_commit,
        "subject_revision_hash": args.subject_archive_sha256,
        "evaluator_artifact_hash": args.evaluator_artifact_sha256,
        "baseline_config_hash": args.baseline_config_sha256,
        "candidate_manifest_hash": candidate_manifest_hash,
        "protected_attack_set_hash": protected_attack_set_hash,
        "source_snapshot_hash": source_snapshot_hash,
        "public_claim_evidence_hash": public_claim_evidence_hash,
        "clean_positive_set_hash": clean_positive_set_hash,
        "protected_holdout_set_hash": protected_holdout_set_hash,
        "split_hash": split_hash,
        "evaluation_epoch": args.evaluation_epoch,
        "host_run_id": args.host_run_id,
        "secret_seed_commitment": _sha(args.seed),
        "resource_budget_units": 12.0,
        "model_provider_revisions": "deterministic/no-LLM",
        "case_count": len(cases),
        "family_counts": dict(
            sorted(Counter(case["attack_family"] for case in cases).items())
        ),
        "custody_counts": dict(
            sorted(Counter(case["custody_class"] for case in cases).items())
        ),
        "outcome_accessed": False,
        "mechanical_gold_cases": len(cases),
        "ambiguous_cases": 0,
        "human_rubric_triggered_cases": 0,
    }
    run_path = out / "RUN_MANIFEST_V1.json"
    run_path.write_text(
        json.dumps(run_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    summary = {
        "schema": "P4HostPreparationSummary.v1",
        "protocol_id": "P4.protected-authority.v1",
        "case_construction": args.construction,
        "host_run_id": args.host_run_id,
        "evaluation_epoch": args.evaluation_epoch,
        "subject_commit": args.subject_commit,
        "subject_revision_hash": args.subject_archive_sha256,
        "evaluator_artifact_hash": args.evaluator_artifact_sha256,
        "baseline_config_hash": args.baseline_config_sha256,
        "candidate_manifest_hash": candidate_manifest_hash,
        "protected_attack_set_hash": protected_attack_set_hash,
        "source_snapshot_hash": source_snapshot_hash,
        "run_manifest_hash": _file_hash(run_path),
        "split_hash": split_hash,
        "public_claim_evidence_hash": public_claim_evidence_hash,
        "clean_positive_set_hash": clean_positive_set_hash,
        "protected_holdout_set_hash": protected_holdout_set_hash,
        "case_count": len(cases),
        "clean_positive_count": len(clean_cases),
        "hostile_count": len(hostile_cases),
        "public_hostile_count": len(public_hostile),
        "protected_hostile_count": len(protected_hostile),
        "holdout_count": len(holdout_cases),
        "attack_family_count": len(FAMILIES),
        "mechanical_gold_cases": len(cases),
        "ambiguous_cases": 0,
        "human_rubric_triggered_cases": 0,
        "attack_labels_visible_to_candidate": False,
        "outcome_accessed": False,
        "seed_commitment": _sha(args.seed),
    }
    (out / "host_prep_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
