"""Independent replay for P9 S3 domain rotations.

Deliberately does not import s3_access, s3_experiment, or s3_rotation_experiment.
It independently parses the canonical D1 typed serialization, reconstructs only
value-independent equality/unknownness relations, and re-runs the frozen dense
classical model grid on the three rotation datasets.
"""
from __future__ import annotations

from collections import defaultdict
import json

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from orion.study.p9.d1 import COMPARISON_COORDINATES, D1Domain, D1View
from orion.study.p9.s3_rotation import DOMAIN_ORDER, generate_rotation_dataset


def parse_relation_features(sequence: list[str]) -> dict[str, object]:
    left_unknown=set(); right_unknown=set()
    grouped=defaultdict(list)
    for raw in map(str,sequence):
        if raw == "root.schema=P9.D1Typed.v1":
            continue
        if ":LEN=" in raw:
            path,_=raw.split(":LEN=",1)
        elif "=" in raw:
            path,_=raw.split("=",1)
        else:
            raise ValueError(raw)
        for side in ("left","right"):
            prefix=f"root.{side}."
            if not path.startswith(prefix):
                continue
            rest=path[len(prefix):]
            if rest=="unknown_coordinates[]" and "=" in raw:
                _,value=raw.split("=",1)
                (left_unknown if side=="left" else right_unknown).add(value)
                break
            coord=next((c for c in COMPARISON_COORDINATES if rest==c or rest.startswith(c+"[")),None)
            if coord is not None:
                grouped[(side,coord)].append("root.side."+raw[len(prefix):])
            break
    out={}
    for coord in COMPARISON_COORDINATES:
        l=tuple(grouped[("left",coord)]); r=tuple(grouped[("right",coord)])
        if not l or not r:
            raise ValueError(f"missing coordinate {coord}")
        unknown=coord in left_unknown or coord in right_unknown
        out[f"{coord}:unknown"]=unknown
        out[f"{coord}:equal"]=(not unknown) and l==r
    return out


def exact_from_features(features: dict[str,object]) -> str:
    if any(bool(features[f"{c}:unknown"]) for c in COMPARISON_COORDINATES):
        return "UNRESOLVED"
    if any(not bool(features[f"{c}:equal"]) for c in COMPARISON_COORDINATES):
        return "OBSTRUCTION"
    return "ALIGNED"


def seq(row):
    payload=row.model_payload(D1View.TYPED_SERIALIZED)
    value=payload["sequence"]
    assert isinstance(value,list)
    return list(map(str,value))


def specs():
    return [
        ("logistic-C0.1",0,lambda:LogisticRegression(C=.1,max_iter=2000,random_state=2711,solver="lbfgs")),
        ("logistic-C1",1,lambda:LogisticRegression(C=1,max_iter=2000,random_state=2711,solver="lbfgs")),
        ("logistic-C10",2,lambda:LogisticRegression(C=10,max_iter=2000,random_state=2711,solver="lbfgs")),
        ("tree-depth3",10,lambda:DecisionTreeClassifier(max_depth=3,min_samples_leaf=2,random_state=2712)),
        ("tree-depth6",11,lambda:DecisionTreeClassifier(max_depth=6,min_samples_leaf=2,random_state=2712)),
        ("rf-depth6",20,lambda:RandomForestClassifier(n_estimators=200,max_depth=6,min_samples_leaf=2,random_state=2713,n_jobs=1)),
        ("rf-none",21,lambda:RandomForestClassifier(n_estimators=300,max_depth=None,min_samples_leaf=2,random_state=2713,n_jobs=1)),
    ]


def fit_model(name_factory, rows):
    _,_,factory=name_factory
    model=Pipeline([("vectorizer",DictVectorizer(sparse=False)),("model",factory())])
    model.fit([parse_relation_features(seq(r)) for r in rows],[r.label.value for r in rows])
    return model


def verify():
    rotations={}
    for holdout in DOMAIN_ORDER:
        ds=generate_rotation_dataset(holdout)
        exact=[exact_from_features(parse_relation_features(seq(r))) for r in ds.test]
        exact_acc=accuracy_score([r.label.value for r in ds.test],exact)
        dev=[]
        for sp in specs():
            m=fit_model(sp,ds.train)
            pred=m.predict([parse_relation_features(seq(r)) for r in ds.dev])
            dev.append((float(accuracy_score([r.label.value for r in ds.dev],pred)),sp[1],sp[0],sp))
        selected=sorted(dev,key=lambda x:(-x[0],x[1],x[2]))[0][3]
        m=fit_model(selected,ds.train)
        pred=list(map(str,m.predict([parse_relation_features(seq(r)) for r in ds.test])))
        labels=[r.label.value for r in ds.test]
        acc=float(accuracy_score(labels,pred))
        double=[p==y for p,y,r in zip(pred,labels,ds.test,strict=True) if len(r.mutation_coordinates)==2]
        unresolved=[p==y for p,y,r in zip(pred,labels,ds.test,strict=True) if r.label.value=="UNRESOLVED"]
        rotations[holdout.value]={"selected":selected[0],"F1_accuracy":acc,"F1_double":sum(double)/len(double),"F1_unresolved":sum(unresolved)/len(unresolved),"F2_accuracy":float(exact_acc),"manifest":ds.manifest_digest}
    checks={
        "all_F1_one":all(v["F1_accuracy"]==1.0 for v in rotations.values()),
        "all_F1_double_one":all(v["F1_double"]==1.0 for v in rotations.values()),
        "all_F1_unresolved_one":all(v["F1_unresolved"]==1.0 for v in rotations.values()),
        "all_F2_one":all(v["F2_accuracy"]==1.0 for v in rotations.values()),
        "all_select_logistic_C0_1":all(v["selected"]=="logistic-C0.1" for v in rotations.values()),
        "workflow_manifest_matches":rotations["transactional_workflows"]["manifest"]=="sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c",
    }
    return {"schema":"P9.S3DomainRotationIndependentVerification.v1","rotations":rotations,"checks":checks,"ok":all(checks.values()),"terminal":"BOUNDED_VERIFIED" if all(checks.values()) else "DISAGREEMENT_BLOCKS_PROMOTION"}

if __name__=="__main__":
    print(json.dumps(verify(),sort_keys=True))
