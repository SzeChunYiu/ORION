#!/usr/bin/env python3
"""P9: relational vs invertible serialization over four held-out domains.

Protocol, following P9's own held-out-domain definition (a domain sharing zero
value atoms with train, as in the D1 v1.2 protected split):

* four domains, each held out in turn, trained on the other three;
* 128 instances per held-out domain, all three labels present;
* two serializations of the *same* typed payload -- relational and invertible;
* four arms -- linear, tree, graph-kernel, exact oracle.

Two guards the numbers depend on:

``round_trip``
    Every instance's invertible token stream is parsed back and compared to
    the typed payload. If that fails anywhere the run aborts, because the
    relational/invertible contrast is only about *accessibility* when both
    encodings provably carry the same information.

``collision_floor``
    Instance pairs sharing a feature vector but not a label. Every such pair
    forces an error on any learner reading those features, so the floor is an
    exact lower bound on that arm's error, computed rather than estimated.

The oracle takes no serialization column. It reads the method structure, so
filling a relational or invertible cell for it would credit an encoding with a
score the encoding did not supply.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.feature_extraction import DictVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402

from orion.study.p9.d1 import (  # noqa: E402
    D1Domain,
    D1Split,
    D1View,
    SurfaceRemintScope,
    _split_instances,
    classify_methods,
)
from orion.study.p9.d1_experiment import D1FeatureFamily, features  # noqa: E402
from orion.study.p9.serialization_arms import (  # noqa: E402
    ORACLE_SERIALIZATION_NA,
    comparison_graph,
    parse_serialized,
    round_trip_typed,
    wl_histogram,
)

SEED = "p9-serialization-four-domain-v1"
PER_BASE_PAIR = int(__import__("os").environ.get("P9_PER_BASE_PAIR", "32"))  # 32 x 4 variants = 128 instances per domain
SERIALIZATIONS = {
    "relational": D1FeatureFamily.TYPED_RELATIONAL,
    "invertible": D1FeatureFamily.TYPED_SERIALIZED_BAG,
}


def instances(domain: D1Domain, split: D1Split):
    return _split_instances(
        seed=SEED,
        split=split,
        domains=(domain,),
        instances_per_base_pair=PER_BASE_PAIR,
        include_double=True,
        surface_remint_scope=SurfaceRemintScope.PER_INSTANCE,
    )


def graph_kernel_features(inst, serialization: str) -> dict[str, float]:
    """WL features over the method-comparison graph.

    Under ``relational`` the graph is built from the typed payload directly.
    Under ``invertible`` it is built from the payload *recovered by parsing the
    token stream*, so the arm demonstrates the recovery instead of quietly
    reusing the structure it is supposed to have decoded.
    """
    if serialization == "relational":
        payload = inst.model_payload(D1View.TYPED)
    else:
        payload = parse_serialized(inst.model_payload(D1View.TYPED_SERIALIZED)["sequence"])
    labels, edges = comparison_graph(payload)
    return wl_histogram(labels, edges)


def feature_dict(inst, serialization: str) -> dict:
    if serialization == "relational":
        return features(inst, D1FeatureFamily.TYPED_RELATIONAL)
    return features(inst, D1FeatureFamily.TYPED_SERIALIZED_BAG)


def collision_floor(rows: list[tuple[dict, str]]) -> dict:
    """Exact error floor: groups sharing a feature vector but not a label."""
    groups: dict[str, list[str]] = defaultdict(list)
    for feats, label in rows:
        key = json.dumps({k: str(v) for k, v in sorted(feats.items())}, sort_keys=True)
        groups[key].append(label)
    forced = 0
    ambiguous_groups = 0
    for labels in groups.values():
        counts = Counter(labels)
        if len(counts) > 1:
            ambiguous_groups += 1
            forced += len(labels) - counts.most_common(1)[0][1]
    return {
        "distinct_feature_vectors": len(groups),
        "ambiguous_groups": ambiguous_groups,
        "forced_errors": forced,
        "error_floor": round(forced / max(len(rows), 1), 6),
    }


def fit_score(train_rows, test_rows, learner: str) -> dict:
    Xtr = [f for f, _ in train_rows]
    ytr = [l for _, l in train_rows]
    Xte = [f for f, _ in test_rows]
    yte = [l for _, l in test_rows]
    if learner == "linear":
        model = LogisticRegression(max_iter=4000, random_state=0)
    elif learner == "tree":
        model = RandomForestClassifier(n_estimators=300, random_state=0)
    else:  # graph_kernel reuses the linear decision rule over WL features
        model = LogisticRegression(max_iter=4000, random_state=0)
    pipe = Pipeline([("vec", DictVectorizer(sparse=True)), ("model", model)])
    pipe.fit(Xtr, ytr)
    pred = list(pipe.predict(Xte))
    acc = sum(int(a == b) for a, b in zip(pred, yte)) / len(yte)
    return {
        "accuracy": round(acc, 6),
        "macro_f1": round(float(f1_score(yte, pred, average="macro", zero_division=0)), 6),
        "n_test": len(yte),
        "predicted_label_support": dict(Counter(pred)),
    }


def main() -> int:
    domains = list(D1Domain)
    # ---- guard 1: invertibility, checked on every instance actually used ----
    rt_ok = rt_bad = 0
    for d in domains:
        for split in (D1Split.TRAIN, D1Split.TEST):
            for inst in instances(d, split):
                typed = inst.model_payload(D1View.TYPED)
                toks = inst.model_payload(D1View.TYPED_SERIALIZED)["sequence"]
                if round_trip_typed(typed, toks):
                    rt_ok += 1
                else:
                    rt_bad += 1
    if rt_bad:
        print(f"ABORT: {rt_bad} instances failed the invertibility round trip")
        return 3

    results: dict = {
        "schema": "P9.SerializationFourDomain.v1",
        "seed": SEED,
        "protocol": {
            "held_out_domains": [d.value for d in domains],
            "instances_per_domain": PER_BASE_PAIR * 4,
            "train": "the other three domains",
            "held_out_definition": "zero shared value atoms with train (P9 D1 protected-split rule)",
        },
        "invertibility_guard": {
            "instances_checked": rt_ok + rt_bad,
            "round_trip_ok": rt_ok,
            "round_trip_failed": rt_bad,
            "meaning": "both serializations provably carry the same information",
        },
        "per_domain": {},
    }

    for held_out in domains:
        train_domains = [d for d in domains if d is not held_out]
        test_inst = instances(held_out, D1Split.TEST)
        train_inst = [i for d in train_domains for i in instances(d, D1Split.TRAIN)]
        block: dict = {
            "train_domains": [d.value for d in train_domains],
            "n_train": len(train_inst),
            "n_test": len(test_inst),
            "test_label_support": dict(Counter(i.label.value for i in test_inst)),
            "arms": {},
        }

        # ---- trivial null: predict the training majority label ----
        # Without this a table of 1.0s cannot be read. If the null already
        # scores high the held-out domain is not discriminating anything and
        # no arm above it has been shown to work.
        maj = Counter(i.label.value for i in train_inst).most_common(1)[0][0]
        gold_null = [i.label.value for i in test_inst]
        block["arms"]["majority_class_null"] = {
            "predicted_label": maj,
            "accuracy": round(sum(int(g == maj) for g in gold_null) / len(gold_null), 6),
            "macro_f1": round(
                float(f1_score(gold_null, [maj] * len(gold_null), average="macro", zero_division=0)), 6
            ),
            "note": "a learner that does not beat this has not been shown to read anything",
        }

        # ---- oracle: serialization-independent by construction ----
        oracle_pred = [classify_methods(i.left, i.right).value for i in test_inst]
        gold = [i.label.value for i in test_inst]
        block["arms"]["exact_oracle"] = {
            "relational": ORACLE_SERIALIZATION_NA,
            "invertible": ORACLE_SERIALIZATION_NA,
            "structure_read_directly": {
                "accuracy": round(sum(int(a == b) for a, b in zip(oracle_pred, gold)) / len(gold), 6),
                "n_test": len(gold),
            },
            "note": "attainable ceiling, not a competitor: the gold labels are this predicate",
        }

        for serialization, family in SERIALIZATIONS.items():
            tr = [(feature_dict(i, serialization), i.label.value) for i in train_inst]
            te = [(feature_dict(i, serialization), i.label.value) for i in test_inst]
            floor = collision_floor(te)
            arm_block = {"collision_floor_on_held_out": floor, "learners": {}}
            for learner in ("linear", "tree"):
                arm_block["learners"][learner] = fit_score(tr, te, learner)
            # graph-kernel arm reads the structure through WL, same information
            gtr = [(graph_kernel_features(i, serialization), i.label.value) for i in train_inst]
            gte = [(graph_kernel_features(i, serialization), i.label.value) for i in test_inst]
            arm_block["learners"]["graph_kernel"] = fit_score(gtr, gte, "graph_kernel")
            arm_block["learners"]["graph_kernel"]["note"] = (
                "WL over the method-comparison graph. Under the invertible "
                "serialization the graph is rebuilt by parsing the token "
                "stream, so any match with the relational column is a "
                "demonstrated recovery, not a shared code path"
            )
            block["arms"][serialization] = arm_block

        results["per_domain"][held_out.value] = block
        print(f"[done] held-out {held_out.value}")

    out = Path(__file__).resolve().parent / "P9_SERIALIZATION_FOUR_DOMAIN_V1.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
