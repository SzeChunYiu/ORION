from __future__ import annotations

from copy import deepcopy

from orion.study.p9.applications.sre_projection import (
    SRECase,
    SRENode,
    SREObservableEvidence,
    SRERelation,
    SREView,
    extract_itbench_alerts,
    extract_itbench_evaluator_truth,
)


def _mixed_groundtruth() -> dict[str, object]:
    return {
        "alerts": [
            {
                "group_id": "payment-service-1",
                "id": "HighRequestErrorRate",
                "metadata": {
                    "description": "Payment failing due to feature flag",
                },
            },
            {
                "group_id": "checkout-service-1",
                "id": "HighRequestErrorRate",
                "metadata": {
                    "description": "Checkout affected by payment failure",
                },
            },
        ],
        "fault": [
            {
                "category": "Configuration Setting",
                "condition": "paymentFailure feature flag set",
                "entity": {"kind": "ConfigMap", "name": "flagd-config"},
            }
        ],
        "groups": [
            {
                "id": "flagd-config",
                "kind": "ConfigMap",
                "name": "flagd-config",
                "root_cause": True,
            },
            {"id": "payment-service-1", "kind": "Service"},
            {"id": "checkout-service-1", "kind": "Service"},
        ],
        "propagations": [
            {
                "source": "flagd-config",
                "target": "payment-service-1",
                "condition": "feature flag causes payment service to fail",
            },
            {
                "source": "payment-service-1",
                "target": "checkout-service-1",
                "condition": "checkout cannot charge payment",
            },
        ],
        "recommended_actions": [
            {"solution": {"actions": ["Disable paymentFailure flag"]}}
        ],
    }


def _observable(alerts) -> SREObservableEvidence:
    return SREObservableEvidence(
        alerts=alerts,
        nodes=(
            SRENode("flagd-config", "CONFIGMAP"),
            SRENode("payment-service-1", "SERVICE"),
            SRENode("checkout-service-1", "SERVICE"),
        ),
        relations=(
            SRERelation("flagd-config", "payment-service-1", "REFERENCES_CONFIG"),
            SRERelation("payment-service-1", "checkout-service-1", "CALLS"),
        ),
    )


def test_alert_projection_ignores_causal_descriptions_faults_and_actions():
    raw = _mixed_groundtruth()
    alerts = extract_itbench_alerts(raw)
    assert [(row.source_id, row.alert_id) for row in alerts] == [
        ("payment-service-1", "HighRequestErrorRate"),
        ("checkout-service-1", "HighRequestErrorRate"),
    ]

    hostile = deepcopy(raw)
    hostile["alerts"][0]["metadata"]["description"] = "ROOT CAUSE IS flagd-config"
    hostile["fault"] = [{"secret": "different answer"}]
    hostile["recommended_actions"] = [{"solution": "oracle"}]
    hostile["propagations"] = [{"source": "x", "target": "y"}]
    hostile["groups"][0]["root_cause"] = False
    hostile["groups"][1]["root_cause"] = True

    assert extract_itbench_alerts(hostile) == alerts


def test_evaluator_truth_is_separate_and_changes_without_model_payload_change():
    raw = _mixed_groundtruth()
    alerts = extract_itbench_alerts(raw)
    first = SRECase(
        case_id="scenario-7",
        observable=_observable(alerts),
        evaluator=extract_itbench_evaluator_truth(raw),
    )
    first_payload = first.model_payload(view=SREView.TYPED_EVIDENCE, remint_seed="heldout")
    assert first.evaluator.root_cause_ids == ("flagd-config",)

    hostile = deepcopy(raw)
    hostile["groups"][0]["root_cause"] = False
    hostile["groups"][1]["root_cause"] = True
    hostile["propagations"] = [
        {"source": "payment-service-1", "target": "checkout-service-1"}
    ]
    second = SRECase(
        case_id="scenario-7",
        observable=_observable(extract_itbench_alerts(hostile)),
        evaluator=extract_itbench_evaluator_truth(hostile),
    )
    assert second.evaluator.root_cause_ids == ("payment-service-1",)
    assert second.model_payload(view=SREView.TYPED_EVIDENCE, remint_seed="heldout") == first_payload


def test_view_ladder_adds_structure_without_revealing_raw_entity_names():
    raw = _mixed_groundtruth()
    case = SRECase(
        case_id="scenario-7",
        observable=_observable(extract_itbench_alerts(raw)),
        evaluator=extract_itbench_evaluator_truth(raw),
    )

    surface = case.model_payload(view=SREView.SURFACE, remint_seed="protected")
    topology = case.model_payload(view=SREView.TOPOLOGY, remint_seed="protected")
    typed = case.model_payload(view=SREView.TYPED_EVIDENCE, remint_seed="protected")

    assert set(surface) == {"alerts"}
    assert set(topology) == {"alerts", "topology"}
    assert set(typed) == {"alerts", "topology", "typed_nodes", "typed_relations"}

    rendered = repr(typed)
    for forbidden in (
        "flagd-config",
        "payment-service-1",
        "checkout-service-1",
        "paymentFailure",
        "root_cause",
        "recommended_actions",
    ):
        assert forbidden not in rendered
    assert "REFERENCES_CONFIG" in rendered
    assert "CALLS" in rendered


def test_topology_and_typed_views_receive_same_edges_but_only_typed_get_semantics():
    raw = _mixed_groundtruth()
    evidence = _observable(extract_itbench_alerts(raw))
    topology = evidence.model_payload(view=SREView.TOPOLOGY, remint_seed="s")
    typed = evidence.model_payload(view=SREView.TYPED_EVIDENCE, remint_seed="s")

    assert topology["topology"] == typed["topology"]
    assert "typed_relations" not in topology
    assert {row[2] for row in typed["typed_relations"]} == {"CALLS", "REFERENCES_CONFIG"}


def test_reminting_changes_surface_identity_but_preserves_structural_equalities():
    raw = _mixed_groundtruth()
    evidence = _observable(extract_itbench_alerts(raw))
    first = evidence.model_payload(view=SREView.TYPED_EVIDENCE, remint_seed="a")
    second = evidence.model_payload(view=SREView.TYPED_EVIDENCE, remint_seed="b")
    assert first != second
    assert len(first["topology"]) == len(second["topology"])
    assert [row[2] for row in first["typed_relations"]] == [
        row[2] for row in second["typed_relations"]
    ]


def test_target_observability_is_explicit_not_silently_assumed():
    raw = _mixed_groundtruth()
    truth = extract_itbench_evaluator_truth(raw)
    alerts = extract_itbench_alerts(raw)

    visible = SRECase("visible", _observable(alerts), truth)
    assert visible.target_observable() is True

    missing_root = SRECase(
        "missing-root",
        SREObservableEvidence(
            alerts=alerts,
            nodes=(
                SRENode("payment-service-1", "SERVICE"),
                SRENode("checkout-service-1", "SERVICE"),
            ),
            relations=(
                SRERelation("payment-service-1", "checkout-service-1", "CALLS"),
            ),
        ),
        truth,
    )
    assert missing_root.target_observable() is False
