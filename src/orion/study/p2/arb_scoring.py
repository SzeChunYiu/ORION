"""Official AutoResearchBench Wide scorer, vendored verbatim.

===========================================================================
VENDORED CODE - APACHE LICENSE 2.0
===========================================================================
The five functions in the VENDORED BLOCK below are copied **verbatim** from:

    Repository : CherYou/AutoResearchBench
    Commit     : a46c9bfb8968786f73f0a6a5b365b5384cd0f96d
    File       : evaluate/evaluate_wide_search.py
    File sha256: fee4b8f821cdd6a0f36a37eae3e9d0b86745c31372ff010658afa21b55460dc2
    Licence    : Apache License, Version 2.0
    Licence URL: https://www.apache.org/licenses/LICENSE-2.0

The upstream repository tarball at that commit is hashed in
``papers/orion-12-open-world-scientific-discovery/evidence/access/fetched_artifact_hashes.json``
(``CherYou/AutoResearchBench@a46c9bfb tarball`` ->
``0729109bae4115d9bea60d1213a953b647af6d4cdd0cfbe133dd4151b304021f``); the
per-file hash above was taken from ``evaluate/evaluate_wide_search.py`` inside it.

Copyright and licence remain with the upstream authors. This file is a
redistribution of a portion of that work in unmodified form, as permitted by
the Apache-2.0 licence, for the purpose of scoring ORION against the *official*
metric rather than a reimplementation of it.

===========================================================================
WHY VERBATIM, AND WHAT WE DELIBERATELY DID NOT FIX
===========================================================================
Fidelity to the official evaluator is the entire point of this module. A
"better" IoU would produce numbers that cannot be compared to published
AutoResearchBench results, which is precisely the comparison Paper II needs.
So the vendored block is not linted, not modernised, and not corrected.

Two upstream properties were found while vendoring. Both are **preserved**:

U1. ``compute_iou_recall``'s ``iou = intersection / union if union else 0.0``
    has an unreachable ``else`` branch. ``union`` is zero only when both sets
    are empty, and that case already returned ``(1.0, 1.0, 1.0)`` above. The
    dead branch is kept exactly as written.

U2. ``max_iou_at_k_sampling`` draws from the **global** ``random`` module, so
    it is not deterministic unless the caller seeds ``random`` first. Verified
    empirically: with ``iou_list=[0.1, 0.5, 0.9]`` and ``k=1``, seed 1 gives
    0.5080 and seed 2 gives 0.5064. Note also that ``k=1`` averages 1000 single
    draws, which estimates the *mean* IoU, not any maximum; the function is
    only deterministic when ``k == len(iou_list)`` (then it returns the true
    max) or when ``k > len(iou_list)`` (then it returns 0.0).

    Consequence for Paper II: ``avg_iou`` is the deterministic aggregate and is
    the one bound as ``wide_official_iou``. ``avg_max_iou_at_k`` is reported
    descriptively under an explicitly recorded seed. See
    ``protocol/ARB_WIDE_PROTOCOL_V1.md``.

===========================================================================
DEVIATIONS FROM UPSTREAM (there are three, all in module scope, none in a
function body)
===========================================================================
D1. Upstream reads ``JINA_API_KEY`` from the environment / a ``.env`` file. Here
    it is pinned to ``""``. With no key configured, upstream's own behaviour is
    identical: ``os.environ.get("JINA_API_KEY", "")`` returns ``""`` and the
    Jina branch of ``get_gt_arxiv_ids`` is not taken. Every Wide record in the
    pinned bundle carries a non-empty ``arxiv_id`` list, so the branch is
    unreachable on this data regardless.

D2. Upstream's ``search_arxiv_id_by_title`` performs a network call to
    ``s.jina.ai``. It is **not** vendored. The name is bound to a stub that
    raises ``JinaLookupDisabled``. This changes behaviour only inside the
    branch D1 makes unreachable, and it converts a would-be silent network
    call into a loud failure if that branch is ever reached.

D3. Upstream's module-scope ``load_env_file(ENV_PATH)`` side effect and its
    ``requests`` import are omitted, since D1/D2 remove the only consumers.

Nothing inside a vendored function body is altered.
"""

from __future__ import annotations

import logging
import random
import re
from typing import Any, Dict, List, Sequence, Set, Tuple  # noqa: UP035 - vendored style

__all__ = [
    "JINA_API_KEY",
    "JinaLookupDisabled",
    "compute_iou_recall",
    "get_gt_arxiv_ids",
    "get_predicted_arxiv_ids",
    "max_iou_at_k_sampling",
    "normalize_arxiv_id",
    "score_wide_task",
    "UPSTREAM_COMMIT",
    "UPSTREAM_FILE",
    "UPSTREAM_FILE_SHA256",
    "UPSTREAM_REPO",
    "evaluator_hash",
]

UPSTREAM_REPO = "CherYou/AutoResearchBench"
UPSTREAM_COMMIT = "a46c9bfb8968786f73f0a6a5b365b5384cd0f96d"
UPSTREAM_FILE = "evaluate/evaluate_wide_search.py"
UPSTREAM_FILE_SHA256 = (
    "fee4b8f821cdd6a0f36a37eae3e9d0b86745c31372ff010658afa21b55460dc2"
)

LOGGER = logging.getLogger(__name__)

# D1: pinned empty. Upstream sources this from the environment.
JINA_API_KEY = ""


class JinaLookupDisabled(RuntimeError):
    """Raised if the vendored Jina fallback is reached. It should not be."""


def search_arxiv_id_by_title(title: str, max_retries: int = 3) -> str | None:
    """D2: stub for upstream's network title lookup. Never silently returns."""

    raise JinaLookupDisabled(
        "the vendored AutoResearchBench scorer does not perform Jina title "
        "lookups; every Wide record in the pinned bundle carries arxiv_id "
        f"directly (asked for {title[:60]!r}, max_retries={max_retries})"
    )


# ==========================================================================
# BEGIN VENDORED BLOCK - verbatim from CherYou/AutoResearchBench@a46c9bfb,
# evaluate/evaluate_wide_search.py. Do not reformat, do not "improve".
# ==========================================================================


def max_iou_at_k_sampling(iou_list: Sequence[float], k: int, sample_times: int = 1000) -> float:
    if len(iou_list) < k or k <= 0:
        return 0.0

    total_max = 0.0
    for _ in range(sample_times):
        total_max += max(random.sample(list(iou_list), k))
    return round(total_max / sample_times, 4)


def normalize_arxiv_id(arxiv_id: str) -> str:
    if not arxiv_id:
        return ""
    cleaned = re.sub(r"(?i)arxiv:", "", arxiv_id).strip()
    match = re.search(r"(\d{4}\.\d{4,5})", cleaned)
    return match.group(1) if match else cleaned.strip()


def get_gt_arxiv_ids(input_data: Dict[str, Any], use_jina: bool = True) -> Set[str]:
    raw_ids = input_data.get("arxiv_id", [])
    if raw_ids:
        normalized = {normalize_arxiv_id(str(raw_id)) for raw_id in raw_ids if raw_id}
        normalized.discard("")
        if normalized:
            return normalized

    if use_jina and JINA_API_KEY:
        answers = input_data.get("answer", [])
        found_ids: Set[str] = set()
        LOGGER.info("GT arxiv_id missing. Trying Jina lookup for %s answer titles.", len(answers))
        for title in answers:
            arxiv_id = search_arxiv_id_by_title(title)
            if arxiv_id:
                found_ids.add(arxiv_id)
        return found_ids

    return set()


def get_predicted_arxiv_ids(final_candidates: Sequence[Dict[str, Any]]) -> Set[str]:
    predicted: Set[str] = set()
    for candidate in final_candidates or []:
        normalized_id = normalize_arxiv_id(str(candidate.get("arxiv_id", "")))
        if normalized_id:
            predicted.add(normalized_id)
    return predicted


def compute_iou_recall(gt_ids: Set[str], pred_ids: Set[str]) -> Tuple[float, float, float]:
    if not gt_ids and not pred_ids:
        return 1.0, 1.0, 1.0

    intersection = len(gt_ids & pred_ids)
    union = len(gt_ids | pred_ids)
    iou = intersection / union if union else 0.0
    recall = intersection / len(gt_ids) if gt_ids else 0.0
    precision = intersection / len(pred_ids) if pred_ids else 0.0
    return iou, recall, precision


# ==========================================================================
# END VENDORED BLOCK
# ==========================================================================


def evaluator_hash() -> str:
    """Stable identity of the scorer used, for result-record binding B13.

    Names the upstream file this module vendors rather than hashing this file.
    Hashing this file would change whenever a comment here is edited, which
    would falsely signal that the *metric* changed. What B13 needs to pin is
    which official evaluator produced the number.
    """

    return UPSTREAM_FILE_SHA256


def score_wide_task(
    gold_arxiv_ids: Sequence[str],
    predicted_arxiv_ids: Sequence[str],
) -> Tuple[float, float, float]:
    """Score one Wide task through the vendored official path, unmodified.

    Both argument lists are pushed through ``normalize_arxiv_id`` by exactly the
    upstream entry points -- gold through ``get_gt_arxiv_ids`` and predictions
    through ``get_predicted_arxiv_ids`` -- so no normalisation happens outside
    vendored code. This wrapper only adapts the *shape* of the call; it never
    touches the arithmetic.
    """

    gold = get_gt_arxiv_ids({"arxiv_id": list(gold_arxiv_ids)}, use_jina=False)
    candidates: List[Dict[str, Any]] = [
        {"arxiv_id": item} for item in predicted_arxiv_ids
    ]
    predicted = get_predicted_arxiv_ids(candidates)
    return compute_iou_recall(gold, predicted)
