from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

EXPECTED = {
    "P1": ("P1.hidden-formulation.v1", "responsibility-diagnosability-scoped-licensing"),
    "P2": ("P2.open-world-discovery.v1", "conservative-censored-route-allocation"),
    "P3": ("P3.cross-domain-atlas.v1", "typed-scientific-lens-consistency"),
    "P4": ("P4.protected-authority.v1", "protected-defeater-evidence-planning"),
    "P5": ("P5.hidden-cause-fresh-transfer.v1", "non-compensatory-staged-candidate-gate"),
}

ALLOWED_COMPARISONS = {"delta_lte", "delta_gte", "relative_delta_lte", "relative_delta_gte"}


class V2ProtocolError(ValueError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _contains_unbound(value: Any) -> bool:
    if value == "UNBOUND":
        return True
    if isinstance(value, Mapping):
        return any(_contains_unbound(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_unbound(v) for v in value)
    return False


def validate_incremental_rule(rule: Mapping[str, Any]) -> None:
    required = {"metric", "comparison", "threshold"}
    if set(rule) != required:
        raise V2ProtocolError(f"incremental rule keys must be {sorted(required)}")
    if not isinstance(rule["metric"], str) or not rule["metric"]:
        raise V2ProtocolError("incremental metric must be a non-empty string")
    if rule["comparison"] not in ALLOWED_COMPARISONS:
        raise V2ProtocolError(f"unsupported comparison: {rule['comparison']!r}")
    threshold = rule["threshold"]
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or not math.isfinite(float(threshold)):
        raise V2ProtocolError("incremental threshold must be a finite number")


def validate_protocol(protocol: Mapping[str, Any]) -> None:
    paper_id = protocol.get("paper_id")
    if paper_id not in EXPECTED:
        raise V2ProtocolError(f"unexpected paper_id: {paper_id!r}")
    expected_v1, expected_mechanism = EXPECTED[paper_id]
    if protocol.get("schema_version") != "orion.publication-protocol.v1":
        raise V2ProtocolError("V2 incremental study must reuse the publication protocol schema")
    if protocol.get("protocol_status") != "DESIGN_FROZEN":
        raise V2ProtocolError("incremental protocol must remain DESIGN_FROZEN until execution identities bind")
    if protocol.get("outcome_accessed") is not False:
        raise V2ProtocolError("V2 outcomes must not be accessed at design freeze")
    if protocol.get("incremental_over_protocol") != expected_v1:
        raise V2ProtocolError("incremental_over_protocol does not match the paper's frozen V1 protocol")
    if protocol.get("mechanism_id") != expected_mechanism:
        raise V2ProtocolError("mechanism_id does not match the merged transfer-V2 manifest")
    if protocol.get("adoption_decision") not in {"ADOPT", "ADAPT"}:
        raise V2ProtocolError("only ADOPT/ADAPT mechanisms may have an execution protocol")
    if protocol.get("v1_protocol_mutated") is not False:
        raise V2ProtocolError("V1 mutation is forbidden")
    if protocol.get("local_evidence_authority") != "LOCAL_ENGINEERING_ONLY":
        raise V2ProtocolError("local engineering must not be promoted to scientific evidence")
    if protocol.get("requires_new_execution_freeze") is not True:
        raise V2ProtocolError("new execution freeze must be required")
    if not _contains_unbound(protocol.get("execution_bindings", {})):
        raise V2ProtocolError("DESIGN_FROZEN protocol must not masquerade as fully execution-bound")
    baselines = protocol.get("baselines")
    if not isinstance(baselines, list) or not any("V1" in str(x) for x in baselines):
        raise V2ProtocolError("each V2 protocol must directly compare against the frozen V1 system")
    for key in ("task_families", "negative_controls", "ablations", "plots", "tables"):
        value = protocol.get(key)
        if not isinstance(value, list) or not value:
            raise V2ProtocolError(f"{key} must be a non-empty list")
    decision = protocol.get("incremental_decision")
    if not isinstance(decision, Mapping):
        raise V2ProtocolError("incremental_decision is required")
    validate_incremental_rule(decision.get("primary", {}))
    guards = decision.get("guards")
    if not isinstance(guards, list) or not guards:
        raise V2ProtocolError("at least one practical/safety guard is required")
    for guard in guards:
        if not isinstance(guard, Mapping):
            raise V2ProtocolError("guard must be an object")
        validate_incremental_rule(guard)
    if paper_id == "P4" and protocol.get("authority_cap") != "PLANNER_CAN_NEVER_AUTHORIZE":
        raise V2ProtocolError("P4 helper must remain structurally unable to grant authority")
    if paper_id == "P5" and protocol.get("promotion_terminal") != "RECOMMEND_HOST_PROMOTION_ONLY":
        raise V2ProtocolError("P5 candidate cannot self-promote")


def validate_protocol_set(protocols: Sequence[Mapping[str, Any]]) -> None:
    if len(protocols) != 5:
        raise V2ProtocolError("exactly five paper V2 protocols are required")
    paper_ids = [p.get("paper_id") for p in protocols]
    protocol_ids = [p.get("protocol_id") for p in protocols]
    if set(paper_ids) != set(EXPECTED):
        raise V2ProtocolError("protocol set must contain P1..P5 exactly once")
    if len(set(protocol_ids)) != len(protocol_ids):
        raise V2ProtocolError("protocol ids must be unique")
    for protocol in protocols:
        validate_protocol(protocol)


def _finite_metric(metrics: Mapping[str, Any], name: str) -> float:
    if name not in metrics:
        raise V2ProtocolError(f"missing metric: {name}")
    value = metrics[name]
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise V2ProtocolError(f"metric {name} must be finite numeric")
    return float(value)


def _evaluate_rule(rule: Mapping[str, Any], v1_metrics: Mapping[str, Any], v2_metrics: Mapping[str, Any]) -> dict[str, Any]:
    validate_incremental_rule(rule)
    metric = rule["metric"]
    v1 = _finite_metric(v1_metrics, metric)
    v2 = _finite_metric(v2_metrics, metric)
    comparison = rule["comparison"]
    threshold = float(rule["threshold"])
    delta = v2 - v1
    if comparison.startswith("relative_"):
        if v1 == 0.0:
            raise V2ProtocolError(f"relative comparison undefined for zero V1 metric: {metric}")
        observed = delta / abs(v1)
    else:
        observed = delta
    passed = observed <= threshold if comparison.endswith("_lte") else observed >= threshold
    return {"metric": metric, "comparison": comparison, "threshold": threshold, "v1": v1, "v2": v2, "observed": observed, "passed": passed}


def evaluate_incremental_decision(protocol: Mapping[str, Any], v1_metrics: Mapping[str, Any], v2_metrics: Mapping[str, Any]) -> dict[str, Any]:
    validate_protocol(protocol)
    decision = protocol["incremental_decision"]
    try:
        primary = _evaluate_rule(decision["primary"], v1_metrics, v2_metrics)
        guards = [_evaluate_rule(rule, v1_metrics, v2_metrics) for rule in decision["guards"]]
    except V2ProtocolError as exc:
        return {"paper_id": protocol["paper_id"], "protocol_id": protocol["protocol_id"], "status": "CANNOT_CHECK", "reason": str(exc)}
    status = "PASS" if primary["passed"] and all(g["passed"] for g in guards) else "FAIL"
    return {"paper_id": protocol["paper_id"], "protocol_id": protocol["protocol_id"], "status": status, "primary": primary, "guards": guards, "authority": "LOCAL_DECISION_RULE_ONLY"}


def load_protocols(protocol_dir: str | Path) -> list[dict[str, Any]]:
    path = Path(protocol_dir)
    protocols = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(path.glob("P*_V2.json"))]
    validate_protocol_set(protocols)
    return protocols


def verify_digest_registry(protocols: Sequence[Mapping[str, Any]], registry: Mapping[str, Any]) -> None:
    entries = registry.get("protocols")
    if not isinstance(entries, list):
        raise V2ProtocolError("digest registry protocols must be a list")
    actual = {p["protocol_id"]: canonical_sha256(p) for p in protocols}
    recorded = {item.get("protocol_id"): item.get("canonical_sha256") for item in entries}
    if actual != recorded:
        raise V2ProtocolError("protocol digest registry mismatch")
