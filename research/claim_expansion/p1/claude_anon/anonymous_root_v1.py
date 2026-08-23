#!/usr/bin/env python3
"""Role-free episode identifiers for the P1-U R6 re-run.

Protocol: ``FREEZE_2026-08-21_ROLE_FREE_IDENTIFIERS_V1.md`` beside this file,
written before any anonymised identifier existed.

The defect this closes is measured, not suspected. The repaired leakage audit in
``research/claim_expansion/p1/claude_t3/`` reports 96 of 96 episode-arms failing,
because episode identifiers are ``R5-<QUERY>-A``/``-C``/``-U`` and those strings
reach the candidate-visible payload through eight separate surfaces. For the 22
control episodes the ``-C`` suffix is a perfect gold predictor.

This is a **wrapper**. ``native_orion_core_v1.py`` and ``repaired_root_v1.py``
are imported and not modified, and no committed receipt is touched; the
identified run stands as the record of what it produced. Only the strings that
cross the provider boundary change.

Two things this module refuses to do, both of which would make it useless:

* It does not anonymise the ledger. Anonymity is a property of the *boundary*,
  not of the record --- every scored row stays traceable to its real episode, so
  a result cannot become unauditable in the name of being unleaky.
* It does not accept a handle scheme that merely re-encodes the role. A hash
  that still sorts by role is the same defect with more steps, so
  :func:`handle_is_role_free` fits a classifier on every prefix of the handle and
  requires informedness ``0.0`` at each length before any arm is scored.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any

#: Frozen in the protocol document. Fixing it here is what stops the mapping
#: from being re-drawn after an outcome is seen.
SALT = "p1-r6-role-free-2026-08-21"
HANDLE_HEX_LENGTH = 12

#: Substrings that must not survive into a handle. The first three are the pair
#: roles; ``R5-`` is the corpus prefix that makes a pair id reconstructable.
FORBIDDEN_SUBSTRINGS = ("-A", "-C", "-U", "R5-")

#: Permutation null for the role-recovery precondition. Frozen in V4 of the
#: protocol so the noise floor is measured rather than assumed to be zero.
PERMUTATION_REPS = 1000
PERMUTATION_SEED = 20260821
NULL_PERCENTILE = 0.99


def episode_handle(episode_id: str, *, salt: str = SALT) -> str:
    """An opaque, stable, role-free handle for one episode."""

    digest = hashlib.sha256(f"{salt}\x00{episode_id}".encode()).hexdigest()
    return f"ep-{digest[:HANDLE_HEX_LENGTH]}"


def _informedness(labels: Sequence[str], cues: Sequence[str]) -> float:
    """Majority-vote informedness of a cue for a label set, max over labels.

    The same statistic the P4 identifiability register uses: fit the majority
    label per cue value, then score TPR + TNR - 1. Zero means the cue separates
    nothing.
    """

    from collections import Counter, defaultdict

    by_cue: dict[str, list[str]] = defaultdict(list)
    for label, cue in zip(labels, cues, strict=True):
        by_cue[cue].append(label)
    majority = {cue: Counter(items).most_common(1)[0][0] for cue, items in by_cue.items()}
    predicted = [majority[cue] for cue in cues]

    best = 0.0
    for target in set(labels):
        tp = sum(1 for a, p in zip(labels, predicted, strict=True) if a == target and p == target)
        fn = sum(1 for a, p in zip(labels, predicted, strict=True) if a == target and p != target)
        fp = sum(1 for a, p in zip(labels, predicted, strict=True) if a != target and p == target)
        tn = sum(1 for a, p in zip(labels, predicted, strict=True) if a != target and p != target)
        if (tp + fn) == 0 or (fp + tn) == 0:
            continue
        best = max(best, tp / (tp + fn) + tn / (fp + tn) - 1.0)
    return best


def _held_out_informedness(
    labels: Sequence[str], cues: Sequence[str], fit_index: Sequence[int], score_index: Sequence[int]
) -> float:
    """Fit the majority vote on one split, score it on the other.

    Fitting and scoring on the same rows is the whole defect this replaces. With
    48 episodes and near-unique cue values, a majority vote reproduces its own
    training labels exactly, so *any* injective cue --- including one carrying no
    information --- scores 1.0. See ``FREEZE_..._V2.md``.

    A cue value never seen during fitting predicts nothing, which is the correct
    behaviour: an unseen identifier is exactly the situation a candidate is in.
    """

    from collections import Counter, defaultdict

    by_cue: dict[str, list[str]] = defaultdict(list)
    for index in fit_index:
        by_cue[cues[index]].append(labels[index])
    majority = {cue: Counter(items).most_common(1)[0][0] for cue, items in by_cue.items()}

    actual = [labels[index] for index in score_index]
    predicted = [majority.get(cues[index]) for index in score_index]

    best = 0.0
    for target in set(actual):
        tp = sum(1 for a, p in zip(actual, predicted, strict=True) if a == target and p == target)
        fn = sum(1 for a, p in zip(actual, predicted, strict=True) if a == target and p != target)
        fp = sum(1 for a, p in zip(actual, predicted, strict=True) if a != target and p == target)
        tn = sum(1 for a, p in zip(actual, predicted, strict=True) if a != target and p != target)
        if (tp + fn) == 0 or (fp + tn) == 0:
            continue
        best = max(best, tp / (tp + fn) + tn / (fp + tn) - 1.0)
    return best


def handle_is_role_free(episode_ids: Sequence[str], roles: Sequence[str]) -> dict[str, Any]:
    """Freeze V2 precondition 2: the handle must not *generalise* to the role.

    Held out, because the question is whether someone who has not already seen
    the mapping could predict the role from a handle -- and that is a
    generalisation question. See ``FREEZE_..._V2.md`` for why the first version
    of this check, which fitted and scored on the same rows, reported 1.0 for a
    cryptographic hash.
    """

    handles = [episode_handle(item) for item in episode_ids]
    findings: list[str] = []

    if len(set(handles)) != len(handles):
        findings.append("handles are not distinct; two episodes would be indistinguishable")
    for handle in handles:
        for forbidden in FORBIDDEN_SUBSTRINGS:
            if forbidden in handle:
                findings.append(f"handle {handle} contains the forbidden substring {forbidden!r}")

    # Stratified by role, then alternating within each role. V2 alternated over
    # the whole sorted list, which put adverse on one side and control on the
    # other -- episode ids are R5-<QUERY>-A and R5-<QUERY>-C, so pair members
    # sort adjacent and a global alternation is nearly anti-correlated with the
    # thing being tested. See FREEZE_..._V3.md.
    from collections import defaultdict

    by_role: dict[str, list[int]] = defaultdict(list)
    for index in sorted(range(len(episode_ids)), key=lambda item: episode_ids[item]):
        by_role[roles[index]].append(index)
    fit_index = [index for group in by_role.values() for index in group[0::2]]
    score_index = [index for group in by_role.values() for index in group[1::2]]
    fit_roles = {roles[index] for index in fit_index}
    score_roles = {roles[index] for index in score_index}
    all_roles = set(roles)
    if fit_roles != all_roles or score_roles != all_roles:
        findings.append(
            "the held-out split does not carry every role on both sides "
            f"(fit={sorted(fit_roles)}, score={sorted(score_roles)}); a split that "
            "omits a role cannot detect that role being predicted"
        )

    import random
    import statistics

    by_prefix: dict[int, dict[str, float]] = {}
    label_list = list(roles)
    for length in range(1, HANDLE_HEX_LENGTH + 1):
        # "ep-" is constant, so the informative part starts after it.
        cues = [handle[3 : 3 + length] for handle in handles]
        observed = _held_out_informedness(label_list, cues, fit_index, score_index)

        # Permuting the labels destroys any real association while preserving the
        # cue distribution, the split and the class balance, so this is the
        # distribution of the statistic under "the handle carries nothing". The
        # alternative -- a fixed ceiling of 0.0 -- is unattainable at the coarsest
        # prefix for any handle scheme, which makes it a broken test rather than a
        # strict one. See FREEZE_..._V4.md.
        rng = random.Random(PERMUTATION_SEED + length)
        null: list[float] = []
        for _ in range(PERMUTATION_REPS):
            shuffled = label_list[:]
            rng.shuffle(shuffled)
            null.append(_held_out_informedness(shuffled, cues, fit_index, score_index))
        null.sort()
        cutoff = null[min(len(null) - 1, int(NULL_PERCENTILE * len(null)))]
        p_value = sum(1 for value in null if value >= observed) / len(null)

        by_prefix[length] = {
            "observed": observed,
            "null_p99": cutoff,
            "null_mean": statistics.fmean(null),
            "p_value": p_value,
        }
        if observed > cutoff:
            findings.append(
                f"a {length}-character handle prefix predicts the pair role on held-out "
                f"episodes at informedness {observed}, above the permutation null's "
                f"99th percentile of {cutoff} (p={p_value})"
            )

    return {
        "handles": handles,
        "distinct": len(set(handles)) == len(handles),
        "fit_episodes": len(fit_index),
        "scored_episodes": len(score_index),
        "permutation_reps": PERMUTATION_REPS,
        "by_prefix_length": by_prefix,
        "worst_observed": max(item["observed"] for item in by_prefix.values()),
        "findings": findings,
        "passed": not findings,
    }


class TraceableLedger:
    """Wraps the coverage ledger so it records real episode ids, not handles.

    ``build_repaired_root`` records whatever episode id it is handed, and it is
    handed a handle. Without this the ledger would be anonymised too, which is
    the opposite of the point: the boundary is what needs to be role-free, and a
    record nobody can trace back is not an improvement over one that leaks.
    """

    def __init__(self, inner: Any, mapping: Mapping[str, str]) -> None:
        self._inner = inner
        self._by_handle = dict(mapping)

    def record(self, *, arm: str, episode_id: str, report: Mapping[str, Any]) -> None:
        real = self._by_handle.get(str(episode_id), str(episode_id))
        self._inner.record(arm=arm, episode_id=real, report=report)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


def build_anonymous_root(
    core: Any,
    repaired: Any,
    *,
    arm: str,
    ledger: Any | None = None,
    mapping_out: dict[str, str] | None = None,
) -> Any:
    """``run_root_runtime`` with every candidate-visible id replaced by a handle.

    The substitution happens at the single point where the episode id enters the
    repaired root, so all eight surfaces the freeze enumerates are covered by
    construction rather than one edit at a time. That matters: the audit found
    three token categories, and a repair that covers two of them is not a repair.
    """

    handles: dict[str, str] = {}
    wrapped_ledger = TraceableLedger(ledger, handles) if ledger is not None else None
    inner = repaired.build_repaired_root(core, arm=arm, ledger=wrapped_ledger)

    def run_root_runtime(*, episode_id: str, dossier: str, domain: str) -> Any:
        handle = episode_handle(episode_id)
        handles[handle] = str(episode_id)
        if mapping_out is not None:
            mapping_out[str(episode_id)] = handle
        return inner(episode_id=handle, dossier=dossier, domain=domain)

    return run_root_runtime


def wrap_root_runtime(inner: Any, *, mapping_out: dict[str, str] | None = None) -> Any:
    """Substitute an opaque handle for the episode id at the single entry point.

    ``native_orion_core_v1`` resolves ``run_root_runtime`` as a module global at
    call time, so replacing the module attribute reaches every caller --- both
    ``run_native_ard`` and ``run_native_base`` --- without editing the frozen
    core. One substitution point covers all eight surfaces the freeze
    enumerates, because every one of them is built downstream from this argument.

    That single-point property is the reason to do it here rather than at each
    surface: the audit found three token categories, and they are three
    substrings of one identifier. Patching them one at a time would leave
    whichever surface nobody thought of.
    """

    def run_root_runtime(*, episode_id: str, dossier: str, domain: str) -> Any:
        handle = episode_handle(episode_id)
        if mapping_out is not None:
            mapping_out[str(episode_id)] = handle
        return inner(episode_id=handle, dossier=dossier, domain=domain)

    return run_root_runtime


def wrap_arm(inner: Any, *, mapping_out: dict[str, str] | None = None) -> Any:
    """Substitute the handle in the episode itself, before an arm sees it.

    Patching ``run_root_runtime`` alone anonymises the root and leaves the probe
    path untouched: ``run_native_ard`` passes the episode's real ``id`` to the
    probe host separately, so ``p1-r6-probe:R5-SEARCH-P1-A:...`` still carries
    the role. Measured, not guessed --- patching only the root took the audit
    from 96 failing episode-arms to 48.

    The episode's ``id`` is the single upstream source both paths read, so
    substituting it once covers every candidate-visible surface downstream. The
    evaluator keeps the real episode dict for its own bookkeeping, which is what
    lets the leakage audit still know which token to look for.
    """

    def call(episode: Mapping[str, Any], **kwargs: Any) -> Any:
        real = str(episode["id"])
        handle = episode_handle(real)
        if mapping_out is not None:
            mapping_out[real] = handle
        anonymised = dict(episode)
        anonymised["id"] = handle
        return inner(anonymised, **kwargs)

    return call
