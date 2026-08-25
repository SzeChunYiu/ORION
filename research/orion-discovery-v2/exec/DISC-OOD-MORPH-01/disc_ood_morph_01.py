"""DISC-OOD-MORPH-01 driver — open-morphology recovery vs fixed-basis false certainty.

Gate: the generator does not encode the missing move in labels, metadata, or
evaluator hints.

worlds.py and basis_solver.py were authored by the first agent on this job;
the solver was written BEFORE any world existed and its coverage predicate is
derived only from the spec text. This driver adds the leakage probe and the
four required receipts.

The leakage probe is adversarial to this job's own hypothesis. It sees exactly
what the solver sees -- the move text, nothing else -- and tries to predict
out-of-basis membership. If a trivial probe beats its chance baseline, the
corpus leaks and "recovery" is reading the answer key, so the terminal becomes
FIXED_BASIS_FALSE_CERTAINTY_OR_GENERATOR_LEAKAGE rather than a success.
"""
from __future__ import annotations

import json
import random
import re
from collections import Counter
from pathlib import Path

import worlds as W
from basis_solver import BasisSolver

HERE = Path(__file__).resolve().parent
THRESHOLD = 1


def corpus():
    rows = []
    for space, sit, prob, move in W.IN_BASIS:
        rows.append({"stratum": "IN_BASIS", "true_space": space, "move": move,
                     "situation": sit, "problem": prob})
    for item in W.OUT_CLEAN:
        space, sit, prob, move = item
        rows.append({"stratum": "OUT_CLEAN", "true_space": None, "move": move,
                     "situation": sit, "problem": prob})
    for item in W.OUT_BORDERLINE:
        space, sit, prob, move = item
        rows.append({"stratum": "OUT_BORDERLINE", "true_space": None, "move": move,
                     "situation": sit, "problem": prob})
    return rows


def leakage_probe(rows, seed=20260825, folds=5):
    """Trivial lexical probe, move text only, predicting out-of-basis membership.

    Deliberately weak: unigram log-odds with add-one smoothing. A weak probe
    beating chance is stronger evidence of leakage than a strong one, because a
    strong probe might be detecting genuine semantics rather than a tell.
    """
    rng = random.Random(seed)
    data = [(r["move"], r["stratum"] != "IN_BASIS") for r in rows]
    rng.shuffle(data)
    n = len(data)
    majority = max(Counter(y for _, y in data).values()) / n

    def toks(t):
        return set(re.findall(r"[a-z]{3,}", t.lower()))

    correct = 0
    for f in range(folds):
        test = [d for i, d in enumerate(data) if i % folds == f]
        train = [d for i, d in enumerate(data) if i % folds != f]
        pos = Counter(); neg = Counter()
        for t, y in train:
            (pos if y else neg).update(toks(t))
        np_, nn = sum(1 for _, y in train if y), sum(1 for _, y in train if not y)
        for t, y in test:
            s = 0.0
            for w in toks(t):
                s += ((pos[w] + 1) / (np_ + 2)) - ((neg[w] + 1) / (nn + 2))
            if (s > 0) == y:
                correct += 1
    acc = correct / n
    return {"probe": "unigram log-odds, add-one smoothing, move text only",
            "folds": folds, "accuracy": round(acc, 4),
            "chance_baseline_majority_class": round(majority, 4),
            "beats_chance": acc > majority,
            "margin_over_chance": round(acc - majority, 4),
            "reading": ("a trivial probe seeing only the solver's input should not "
                        "beat majority-class guessing; if it does, out-of-basis "
                        "membership is readable from the text itself")}


def main() -> int:
    rows = corpus()
    solver = BasisSolver(threshold=THRESHOLD)

    for r in rows:
        r["abstaining"] = solver.classify(r["move"])
        r["forced"] = solver.classify_forced(r["move"])

    out = [r for r in rows if r["stratum"] != "IN_BASIS"]
    inb = [r for r in rows if r["stratum"] == "IN_BASIS"]

    recovered = [r for r in out if r["abstaining"]["decision"] == "OPEN_MOVE_CLASS_REQUIRED"]
    false_certain = [r for r in out if r["abstaining"]["decision"] == "IN_BASIS"]
    # in-basis worlds must NOT be abstained on, or "recovery" is just abstaining always
    in_basis_answered = [r for r in inb if r["abstaining"]["decision"] == "IN_BASIS"]
    in_basis_correct = [r for r in in_basis_answered
                        if r["abstaining"]["space"] == r["true_space"]]

    leak = leakage_probe(rows)

    # non-vacuity: an always-abstain solver would "recover" 100% and answer 0 in-basis
    always_abstain_would_recover = len(out)
    discriminates = len(in_basis_answered) > 0 and len(recovered) > 0

    if leak["beats_chance"]:
        terminal = "FIXED_BASIS_FALSE_CERTAINTY_OR_GENERATOR_LEAKAGE"
        reason = "generator leakage: a trivial probe predicts out-of-basis membership above chance"
    elif not discriminates:
        terminal = "FIXED_BASIS_FALSE_CERTAINTY_OR_GENERATOR_LEAKAGE"
        reason = "solver does not discriminate: it abstains on everything or answers everything"
    elif false_certain:
        terminal = "OPEN_MORPHOLOGY_RECOVERY_SUPPORTED"
        reason = (f"recovery on {len(recovered)}/{len(out)} out-of-basis worlds; "
                  f"{len(false_certain)} false-certainty cases recorded, not hidden")
    else:
        terminal = "OPEN_MORPHOLOGY_RECOVERY_SUPPORTED"
        reason = f"recovery on all {len(out)} out-of-basis worlds"

    (HERE / "OPEN_MOVE_CLASS_GENERATOR.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.open-move-class-generator.v1",
        "job_id": "DISC-OOD-MORPH-01",
        "strata": dict(Counter(r["stratum"] for r in rows)),
        "authoring_order": ("basis_solver.py written FIRST from spec section 3 alone; "
                            "worlds.py authored afterwards without consulting the parsed "
                            "coverage-term lists. Independence is procedural, not perfect, "
                            "and the leakage probe is the empirical control for it."),
        "adversarial_design": ("out-of-basis move text deliberately uses registered-basis "
                               "vocabulary where natural. Scrubbing basis words from "
                               "out-of-basis moves would manufacture recovery by vocabulary "
                               "absence rather than by morphology."),
        "worlds": [{k: r[k] for k in ("stratum", "true_space", "situation", "problem", "move")}
                   for r in rows],
    }, indent=2) + "\n")

    (HERE / "GENERATOR_LEAKAGE_CHECKER.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.generator-leakage-checker.v1",
        "job_id": "DISC-OOD-MORPH-01", "result": leak,
        "why_a_weak_probe": ("a weak probe beating chance is stronger evidence of a tell "
                             "than a strong probe beating chance, because a strong probe "
                             "may be reading genuine semantics"),
    }, indent=2) + "\n")

    (HERE / "REGISTERED_BASIS_FAILURES.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.registered-basis-failures.v1",
        "job_id": "DISC-OOD-MORPH-01",
        "out_of_basis_total": len(out),
        "recovered_open_move_class": len(recovered),
        "false_certainty": len(false_certain),
        "false_certainty_cases": [
            {"stratum": r["stratum"], "move": r["move"][:160],
             "asserted_space": r["abstaining"]["space"], "score": r["abstaining"]["score"]}
            for r in false_certain],
        "forced_mode_note": ("classify_forced shows what the basis returns when it may not "
                             "say 'I cannot'. Every out-of-basis world receives an in-basis "
                             "label under forcing, which is the false certainty a fixed "
                             "taxonomy produces when abstention is unavailable."),
        "forced_mode_labels": dict(Counter(r["forced"].get("space") for r in out)),
    }, indent=2) + "\n")

    (HERE / "SUCCESSOR_MOVE_OR_CANNOT_CHECK_RECEIPTS.json").write_text(json.dumps({
        "schema": "orion.discovery-v2.successor-move-receipts.v1",
        "job_id": "DISC-OOD-MORPH-01",
        "terminal": terminal, "reason": reason,
        "in_basis_total": len(inb),
        "in_basis_answered": len(in_basis_answered),
        "in_basis_space_correct": len(in_basis_correct),
        "non_vacuity": {
            "always_abstain_would_recover": always_abstain_would_recover,
            "solver_answers_in_basis_worlds": len(in_basis_answered),
            "discriminates": discriminates,
            "note": ("an always-abstain solver would score perfect recovery and is the "
                     "degenerate control; answering in-basis worlds is what shows the "
                     "abstention is selective rather than constant"),
        },
        "cannot_check": [
            {"subclaim": "COUNTERFACTUAL_REALISM",
             "reason": ("these worlds are synthetic. That the registered basis fails on them "
                        "does not establish that real discovery episodes contain moves "
                        "outside the six spaces; it establishes that the basis can fail and "
                        "can report failing.")}],
    }, indent=2) + "\n")

    print(json.dumps({"terminal": terminal, "reason": reason,
                      "strata": dict(Counter(r["stratum"] for r in rows)),
                      "recovered": len(recovered), "false_certainty": len(false_certain),
                      "in_basis_answered": f"{len(in_basis_answered)}/{len(inb)}",
                      "in_basis_correct": len(in_basis_correct),
                      "leak": {k: leak[k] for k in ("accuracy", "chance_baseline_majority_class",
                                                    "beats_chance")}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
