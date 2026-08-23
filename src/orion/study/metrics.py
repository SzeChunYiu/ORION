"""All evaluation metrics for ORION Paper 3 (P3.cross-domain-atlas.v1).

Each metric function accepts a list of (gold, predicted) annotation pairs plus
a case_family classifier and returns a dict of metric_name -> float.

All metrics are deterministic: no randomness, no side effects.
"""
from __future__ import annotations

from collections import Counter
from typing import Sequence

# ── type aliases ──────────────────────────────────────────────────────────────

# A gold annotation carries all coordinates from ANNOTATION_SCHEMA_V1.json
Annotation = dict[str, object]

# A predicted integration carries the same structure (possibly with UNRESOLVED)
Prediction = dict[str, object]


# ── core rate helpers ──────────────────────────────────────────────────────────

def _is_safe_integration(gold: Annotation, pred: Prediction) -> bool | None:
    """True if pred correctly integrates or obstructs per gold.  None if abstained."""
    gv = str(gold.get("integration_verdict", ""))
    pv = str(pred.get("integration_verdict", ""))
    if pv == "UNRESOLVED":
        return None  # abstention
    # GLUE_ALLOWED is correct when gold says GLUE_ALLOWED
    # OBSTRUCTION/PLURAL_VIEW is correct when gold says OBSTRUCTION/PLURAL_VIEW
    return pv == gv


def _is_false_merge(gold: Annotation, pred: Prediction) -> bool | None:
    """Pred says GLUE but gold says OBSTRUCTION/PLURAL_VIEW."""
    pv = str(pred.get("integration_verdict", ""))
    gv = str(gold.get("integration_verdict", ""))
    if pv == "UNRESOLVED":
        return None
    return bool(pv == "GLUE_ALLOWED" and gv in ("OBSTRUCTION", "PLURAL_VIEW"))


def _is_false_split(gold: Annotation, pred: Prediction) -> bool | None:
    """Pred says OBSTRUCTION/PLURAL_VIEW but gold says GLUE_ALLOWED."""
    pv = str(pred.get("integration_verdict", ""))
    gv = str(gold.get("integration_verdict", ""))
    if pv == "UNRESOLVED":
        return None
    return bool(pv in ("OBSTRUCTION", "PLURAL_VIEW") and gv == "GLUE_ALLOWED")


def _is_false_contradiction(gold: Annotation, pred: Prediction) -> bool | None:
    """Pred says CONTRADICTION but gold says NO_CONTRADICTION or CONTEXT_DEPENDENT."""
    pc = str(pred.get("contradiction_verdict", ""))
    gc = str(gold.get("contradiction_verdict", ""))
    if pc == "UNRESOLVED":
        return None
    return bool(pc == "CONTRADICTION" and gc != "CONTRADICTION")


def _is_missed_contradiction(gold: Annotation, pred: Prediction) -> bool | None:
    """Gold says CONTRADICTION but pred says NO_CONTRADICTION or CONTEXT_DEPENDENT."""
    pc = str(pred.get("contradiction_verdict", ""))
    gc = str(gold.get("contradiction_verdict", ""))
    if pc == "UNRESOLVED":
        return None
    return bool(gc == "CONTRADICTION" and pc != "CONTRADICTION")


def _mapping_is_correct(gold: Annotation, pred: Prediction) -> bool | None:
    """Prediction's mapping_relation matches gold exactly."""
    gm = str(gold.get("mapping_relation", ""))
    pm = str(pred.get("mapping_relation", ""))
    if pm == "UNRESOLVED":
        return None
    return pm == gm


def _obstruction_correct(gold: Annotation, pred: Prediction) -> bool | None:
    """Prediction identified obstruction/plural where gold expects it."""
    gv = str(gold.get("integration_verdict", ""))
    pv = str(pred.get("integration_verdict", ""))
    if pv == "UNRESOLVED":
        return None
    if gv in ("OBSTRUCTION", "PLURAL_VIEW"):
        return pv in ("OBSTRUCTION", "PLURAL_VIEW")
    return None  # not an obstruction case


def _source_recoverable(gold: Annotation, pred: Prediction) -> bool | None:
    """Does the predicted portrait expose enough lineage to recover sources?

    The gold lists recoverability_target coordinates.  The prediction must
    include all of them in its output (checks broken out per coordinate).
    """
    g_targets = gold.get("recoverability_target", [])
    if not isinstance(g_targets, list):
        g_targets = []
    if not g_targets:
        return None  # no recoverability requirement
    # Check that predicted output has all required fields
    p_output = pred.get("recoverability_target", [])
    if not isinstance(p_output, list):
        return False
    return all(str(t) in [str(x) for x in p_output] for t in g_targets)


def _preservation_condition_accurate(gold: Annotation, pred: Prediction) -> bool | None:
    """Prediction's preservation conditions match gold's."""
    g_conds = gold.get("preservation_conditions", [])
    p_conds = pred.get("preservation_conditions", [])
    if not isinstance(g_conds, list) or not isinstance(p_conds, list):
        return None
    if not g_conds and not p_conds:
        return True
    return set(str(c) for c in g_conds) == set(str(c) for c in p_conds)


def _measurement_equivalence_accurate(gold: Annotation, pred: Prediction) -> bool | None:
    """Prediction's measurement_relation matches gold."""
    gm = str(gold.get("measurement_relation", ""))
    pm = str(pred.get("measurement_relation", ""))
    if pm == "UNRESOLVED":
        return None
    return pm == gm


# ── headline metrics ──────────────────────────────────────────────────────────

#: What a rate is when nothing was measured.
#:
#: Every rate below divides by the number of non-abstained cases, and that
#: number can be zero. Returning ``0.0`` there is not a neutral choice: for a
#: *harm* rate zero is the best attainable score, so a metric that measured
#: nothing reported a perfect result, and a threshold check on it passed. This
#: is the ``VACUOUS_GUARD_ZERO_DENOMINATOR`` shape
#: (``research/failures/2026-08-vacuous-guard-zero-denominator/``), and it was
#: found here after the same shape turned up in a P3 guard that had never once
#: had an opportunity to fire.
#:
#: ``nan`` rather than ``None``: every comparison against ``nan`` is ``False``,
#: so ``rate >= margin`` and ``rate <= threshold`` both fail, and the metric
#: fails closed wherever it is read. ``None`` would be worse than the bug --- a
#: caller writing ``not rate`` sees ``not None`` as ``True`` and reports clean.
#: The companion ``*_n`` field carries the denominator either way, so a caller
#: that wants to distinguish "measured, and it was zero" from "not measured" can.
NO_CASES = float("nan")


def false_merge_rate(gold: Sequence[Annotation],
                     preds: Sequence[Prediction]) -> dict[str, float]:
    """False merge rate = (false merges) / (non-abstained cases)."""
    false_merges = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        v = _is_false_merge(g, p)
        if v is not None:
            total += 1
            if v:
                false_merges += 1
    return {"false_merge_rate": false_merges / total if total else NO_CASES,
            "false_merge_n": float(total)}


def false_contradiction_rate(gold: Sequence[Annotation],
                             preds: Sequence[Prediction]) -> dict[str, float]:
    false_contra = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        v = _is_false_contradiction(g, p)
        if v is not None:
            total += 1
            if v:
                false_contra += 1
    return {"false_contradiction_rate": false_contra / total if total else NO_CASES,
            "false_contradiction_n": float(total)}


def missed_contradiction_rate(gold: Sequence[Annotation],
                              preds: Sequence[Prediction]) -> dict[str, float]:
    missed = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        v = _is_missed_contradiction(g, p)
        if v is not None:
            total += 1
            if v:
                missed += 1
    return {"missed_contradiction_rate": missed / total if total else NO_CASES,
            "missed_contradiction_n": float(total)}


def false_split_rate(gold: Sequence[Annotation],
                     preds: Sequence[Prediction]) -> dict[str, float]:
    false_splits = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        v = _is_false_split(g, p)
        if v is not None:
            total += 1
            if v:
                false_splits += 1
    return {"false_split_rate": false_splits / total if total else NO_CASES,
            "false_split_n": float(total)}


def valid_integration_rate(gold: Sequence[Annotation],
                           preds: Sequence[Prediction]) -> dict[str, float]:
    """Rate at which safe integration is correctly identified (non-abstained)."""
    correct = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        v = _is_safe_integration(g, p)
        if v is not None:
            total += 1
            if v:
                correct += 1
    return {"valid_integration_rate": correct / total if total else NO_CASES,
            "valid_integration_n": float(total)}


def false_integration_rate_with_valid_integration_guard(
    gold: Sequence[Annotation], preds: Sequence[Prediction],
) -> dict[str, float]:
    """Primary composite metric: false merge rate + valid integration guard."""
    fm = false_merge_rate(gold, preds)
    vi = valid_integration_rate(gold, preds)
    result: dict[str, float] = {}
    result.update(fm)
    result.update(vi)
    return result


# ── mapping metrics ───────────────────────────────────────────────────────────

def mapping_precision_recall_f1(gold: Sequence[Annotation],
                                preds: Sequence[Prediction]) -> dict[str, float]:
    """Precision, recall, F1 for mapping_relation, by type and macro."""
    mapping_types = ["IDENTITY", "EQUIVALENCE", "CONDITIONAL_TRANSFORM",
                     "SUBSUMPTION", "ASSOCIATION_ONLY", "NO_LICENSED_MAPPING"]
    correct = Counter()
    predicted = Counter()
    actual = Counter()
    for g, p in zip(gold, preds, strict=True):
        gm = str(g.get("mapping_relation", ""))
        pm = str(p.get("mapping_relation", ""))
        if pm == "UNRESOLVED" or gm == "UNRESOLVED":
            continue
        predicted[pm] += 1
        actual[gm] += 1
        if pm == gm:
            correct[pm] += 1
    result: dict[str, float] = {}
    macro_p, macro_r, macro_f1 = 0.0, 0.0, 0.0
    count = 0
    for mt in mapping_types:
        p = predicted.get(mt, 0)
        a = actual.get(mt, 0)
        c = correct.get(mt, 0)
        prec = c / p if p else 0.0
        rec = c / a if a else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        result[f"mapping_precision_{mt}"] = prec
        result[f"mapping_recall_{mt}"] = rec
        result[f"mapping_f1_{mt}"] = f1
        # Macro is averaged over types with support in gold OR predictions.
        # Absent types (no gold, no predicted) would drag the macro toward 0
        # and make it impossible to reach 1.0 on a run where only a subset of
        # mapping types legitimately occurs.
        if p or a:
            macro_p += prec
            macro_r += rec
            macro_f1 += f1
            count += 1
    if count:
        result["mapping_precision_macro"] = macro_p / count
        result["mapping_recall_macro"] = macro_r / count
        result["mapping_f1_macro"] = macro_f1 / count
    return result


# ── measurement equivalence ───────────────────────────────────────────────────

def measurement_equivalence_accuracy(
    gold: Sequence[Annotation], preds: Sequence[Prediction],
) -> dict[str, float]:
    correct = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        v = _measurement_equivalence_accurate(g, p)
        if v is not None:
            total += 1
            if v:
                correct += 1
    return {"measurement_equivalence_accuracy": correct / total if total else NO_CASES,
            "measurement_equivalence_n": float(total)}


# ── obstruction metrics ───────────────────────────────────────────────────────

def obstruction_precision_recall(gold: Sequence[Annotation],
                                 preds: Sequence[Prediction]) -> dict[str, float]:
    true_pos = 0
    false_pos = 0
    false_neg = 0
    for g, p in zip(gold, preds, strict=True):
        gv = str(g.get("integration_verdict", ""))
        pv = str(p.get("integration_verdict", ""))
        if pv == "UNRESOLVED":
            continue
        is_gold_obstruction = gv in ("OBSTRUCTION", "PLURAL_VIEW")
        is_pred_obstruction = pv in ("OBSTRUCTION", "PLURAL_VIEW")
        if is_pred_obstruction and is_gold_obstruction:
            true_pos += 1
        elif is_pred_obstruction and not is_gold_obstruction:
            false_pos += 1
        elif not is_pred_obstruction and is_gold_obstruction:
            false_neg += 1
    prec = true_pos / (true_pos + false_pos) if (true_pos + false_pos) else 0.0
    rec = true_pos / (true_pos + false_neg) if (true_pos + false_neg) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"obstruction_precision": prec,
            "obstruction_recall": rec,
            "obstruction_f1": f1,
            "obstruction_true_pos": float(true_pos),
            "obstruction_false_pos": float(false_pos),
            "obstruction_false_neg": float(false_neg)}


# ── source recoverability ─────────────────────────────────────────────────────

def source_recoverability_rate(gold: Sequence[Annotation],
                               preds: Sequence[Prediction]) -> dict[str, float]:
    recoverable = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        v = _source_recoverable(g, p)
        if v is not None:
            total += 1
            if v:
                recoverable += 1
    return {"source_recoverability_rate": recoverable / total if total else NO_CASES,
            "source_recoverability_n": float(total)}


# ── preservation condition accuracy ───────────────────────────────────────────

def preservation_condition_accuracy(
    gold: Sequence[Annotation], preds: Sequence[Prediction],
) -> dict[str, float]:
    correct = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        v = _preservation_condition_accurate(g, p)
        if v is not None:
            total += 1
            if v:
                correct += 1
    return {"preservation_condition_accuracy": correct / total if total else NO_CASES,
            "preservation_condition_n": float(total)}


# ── literature bridge validity ─────────────────────────────────────────────────

def literature_bridge_validity_precision_recall(
    gold: Sequence[Annotation], preds: Sequence[Prediction],
) -> dict[str, float]:
    true_pos = 0
    false_pos = 0
    false_neg = 0
    for g, p in zip(gold, preds, strict=True):
        cf = str(g.get("case_family", ""))
        if "bridge" not in cf.lower() and "bridge" not in str(g.get("task_family", "")):
            continue
        gv = str(g.get("mapping_relation", ""))
        pv = str(p.get("mapping_relation", ""))
        if pv == "UNRESOLVED":
            continue
        is_good = gv in ("IDENTITY", "EQUIVALENCE", "CONDITIONAL_TRANSFORM")
        is_pred_good = pv in ("IDENTITY", "EQUIVALENCE", "CONDITIONAL_TRANSFORM")
        if is_pred_good and is_good:
            true_pos += 1
        elif is_pred_good and not is_good:
            false_pos += 1
        elif not is_pred_good and is_good:
            false_neg += 1
    prec = true_pos / (true_pos + false_pos) if (true_pos + false_pos) else 0.0
    rec = true_pos / (true_pos + false_neg) if (true_pos + false_neg) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"literature_bridge_precision": prec,
            "literature_bridge_recall": rec,
            "literature_bridge_f1": f1}


# ── downstream answer accuracy ────────────────────────────────────────────────

def downstream_answer_accuracy(gold: Sequence[Annotation],
                               preds: Sequence[Prediction]) -> dict[str, float]:
    """Accuracy of downstream scientific answers using the reconstructed portrait.

    This requires a separate evaluation where answers are rated correct/incorrect.
    """
    correct = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        gd = g.get("downstream_correct", None)
        pd = p.get("downstream_correct", None)
        if gd is None or pd is None:
            continue
        correct += int(bool(gd) == bool(pd))
        total += 1
    return {"downstream_answer_accuracy": correct / total if total else NO_CASES,
            "downstream_answer_n": float(total)}


# ── abstention calibration ────────────────────────────────────────────────────

def unresolved_abstention_calibration(
    gold: Sequence[Annotation], preds: Sequence[Prediction],
) -> dict[str, float]:
    """Calibration of UNRESOLVED rate: does the system abstain on the right cases?"""
    unresolved = 0
    truly_unresolved = 0
    total = 0
    for g, p in zip(gold, preds, strict=True):
        pv = str(p.get("integration_verdict", ""))
        gv = str(g.get("integration_verdict", ""))
        total += 1
        if pv == "UNRESOLVED":
            unresolved += 1
            if gv == "UNRESOLVED":
                truly_unresolved += 1
    unresolved_rate = unresolved / total if total else NO_CASES
    calibration = truly_unresolved / unresolved if unresolved else 0.0
    return {"unresolved_rate": unresolved_rate,
            "unresolved_calibration": calibration,
            "unresolved_total": float(total)}


# ── annotation agreement ──────────────────────────────────────────────────────

def annotation_agreement_by_coordinate(
    annotator_a: Sequence[Annotation],
    annotator_b: Sequence[Annotation],
) -> dict[str, float]:
    """Per-coordinate agreement between two independent annotators."""
    coordinates = [
        "referent_relation", "construct_relation", "measurement_relation",
        "context_relation", "polarity_relation", "modality_relation",
        "attribution_relation", "discourse_relation", "mapping_relation",
        "contradiction_verdict", "integration_verdict",
    ]
    result: dict[str, float] = {}
    for coord in coordinates:
        agree = 0
        total = 0
        for a, b in zip(annotator_a, annotator_b, strict=True):
            va = str(a.get(coord, ""))
            vb = str(b.get(coord, ""))
            if va == "UNRESOLVED" or vb == "UNRESOLVED":
                continue
            total += 1
            if va == vb:
                agree += 1
        result[f"agreement_{coord}"] = agree / total if total else NO_CASES
    return result


# ── cost / latency ────────────────────────────────────────────────────────────

def cost_metrics(results: Sequence[dict[str, object]]) -> dict[str, float]:
    """Aggregate cost/latency from result records."""
    wall = [float(r.get("cost", {}).get("wallclock_seconds", 0)) for r in results]
    tokens = [float(r.get("cost", {}).get("model_tokens", 0)) for r in results]
    storage = [float(r.get("cost", {}).get("storage_overhead", 0)) for r in results]
    return {
        "wallclock_seconds_total": sum(wall),
        "wallclock_seconds_mean": sum(wall) / len(wall) if wall else 0.0,
        "model_tokens_total": sum(tokens),
        "model_tokens_mean": sum(tokens) / len(tokens) if tokens else 0.0,
        "storage_overhead_total": sum(storage),
        "storage_overhead_mean": sum(storage) / len(storage) if storage else 0.0,
    }


# ── all metrics ───────────────────────────────────────────────────────────────

ALL_METRIC_FUNCTIONS: dict[str, callable] = {
    "false_integration_rate_with_valid_integration_guard":
        false_integration_rate_with_valid_integration_guard,
    "false_merge_rate": false_merge_rate,
    "false_split_rate": false_split_rate,
    "false_contradiction_rate": false_contradiction_rate,
    "missed_contradiction_rate": missed_contradiction_rate,
    "valid_integration_rate": valid_integration_rate,
    "mapping_precision_recall_f1": mapping_precision_recall_f1,
    "measurement_equivalence_accuracy": measurement_equivalence_accuracy,
    "obstruction_precision_recall": obstruction_precision_recall,
    "source_recoverability_rate": source_recoverability_rate,
    "preservation_condition_accuracy": preservation_condition_accuracy,
    "literature_bridge_validity_precision_recall":
        literature_bridge_validity_precision_recall,
    "downstream_answer_accuracy": downstream_answer_accuracy,
    "unresolved_abstention_calibration": unresolved_abstention_calibration,
    "annotation_agreement_by_coordinate": annotation_agreement_by_coordinate,
    "cost_metrics": cost_metrics,
}


def compute_all_metrics(gold: Sequence[Annotation],
                        preds: Sequence[Prediction]) -> dict[str, float]:
    """Compute all P3 metrics and return a flat dict."""
    result: dict[str, float] = {}
    for name, fn in ALL_METRIC_FUNCTIONS.items():
        try:
            output = fn(gold, preds)
            result.update(output)
        except Exception:
            result[f"{name}_error"] = -1.0
    return result