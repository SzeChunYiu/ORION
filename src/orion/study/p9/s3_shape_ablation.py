"""Post-result S3 diagnostic: relation-only versus extra shape/length features."""
from __future__ import annotations

from typing import Callable, Sequence

from . import s3_runtime as _runtime  # dense execution transport
from .d1 import D1Instance, D1View
from .d1_experiment import _estimator, _metrics, _typed_relational_features, model_specs
from .s3_access import serialized_generic_binding_features
from .s3_rotation import DOMAIN_ORDER, generate_rotation_dataset

FeatureFn = Callable[[D1Instance], dict[str, object]]


def _sequence(row: D1Instance) -> list[str]:
    payload = row.model_payload(D1View.TYPED_SERIALIZED)
    seq = payload["sequence"]
    assert isinstance(seq, list)
    return list(map(str, seq))


def f1_relation_only(row: D1Instance) -> dict[str, object]:
    return serialized_generic_binding_features(_sequence(row))


def f3_relation_only(row: D1Instance) -> dict[str, object]:
    full = _typed_relational_features(row)
    return {k: v for k, v in full.items() if k.endswith(":equal") or k.endswith(":unknown")}


def _serialized_lengths(sequence: list[str]) -> dict[str, object]:
    out: dict[str, object] = {}
    for token in sequence:
        if ":LEN=" not in token:
            continue
        path, raw = token.split(":LEN=", 1)
        for side in ("left", "right"):
            prefix = f"root.{side}."
            if not path.startswith(prefix):
                continue
            coord = path[len(prefix):]
            if coord in {"preconditions","invariants","effects","failure_modes","dependencies"}:
                out[f"{coord}:{side}_length"] = int(raw)
    return out


def f1_plus_lengths(row: D1Instance) -> dict[str, object]:
    out = f1_relation_only(row)
    out.update(_serialized_lengths(_sequence(row)))
    return out


def f3_full(row: D1Instance) -> dict[str, object]:
    return _typed_relational_features(row)


def _fit_select(train: Sequence[D1Instance], dev: Sequence[D1Instance], feature_fn: FeatureFn):
    rows=[]
    fitted={}
    for spec in model_specs():
        model=_estimator(spec)
        model.fit([feature_fn(r) for r in train],[r.label.value for r in train])
        pred=tuple(map(str,model.predict([feature_fn(r) for r in dev])))
        met=_metrics(dev,pred)
        rows.append((spec,met))
        fitted[spec.config_id]=model
    spec,_=sorted(rows,key=lambda x:(-float(x[1]["accuracy"]),x[0].complexity_rank,x[0].config_id))[0]
    model=_estimator(spec)
    model.fit([feature_fn(r) for r in train],[r.label.value for r in train])
    return spec,model


def _eval(dataset, feature_fn: FeatureFn):
    spec,model=_fit_select(dataset.train,dataset.dev,feature_fn)
    pred=tuple(map(str,model.predict([feature_fn(r) for r in dataset.test])))
    return {"selected":spec.config_id,"test":_metrics(dataset.test,pred)}


def run_shape_ablation() -> dict[str, object]:
    rotations={}
    for holdout in DOMAIN_ORDER:
        ds=generate_rotation_dataset(holdout)
        rotations[holdout.value]={
            "A0_F1_relation_only_serialized":_eval(ds,f1_relation_only),
            "A1_F3_full":_eval(ds,f3_full),
            "A2_F3_relation_only":_eval(ds,f3_relation_only),
            "A3_F1_plus_lengths":_eval(ds,f1_plus_lengths),
        }
    graph=rotations["graph_algorithms"]
    a0=float(graph["A0_F1_relation_only_serialized"]["test"]["accuracy"])
    a1=float(graph["A1_F3_full"]["test"]["accuracy"])
    a2=float(graph["A2_F3_relation_only"]["test"]["accuracy"])
    a3=float(graph["A3_F1_plus_lengths"]["test"]["accuracy"])
    pattern=a2>=.99 and a3<=a1+.01 and a3<.99 and a0>=.999999
    terminal="EXTRA_SHAPE_FEATURES_CAUSE_GRAPH_SHORTCUT" if pattern else "F3_GRAPH_FAILURE_NOT_LENGTH_ATTRIBUTABLE"
    return {"schema":"P9.S3ShapeAblationResult.v1","rotations":rotations,"terminal":terminal,"authority":"POST_RESULT_DIAGNOSTIC_ONLY"}

__all__=["run_shape_ablation","f1_relation_only","f3_relation_only","f1_plus_lengths","f3_full"]
