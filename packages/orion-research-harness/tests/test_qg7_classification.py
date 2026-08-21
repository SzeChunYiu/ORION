import pytest

from orion_research_harness.campaign_control import (
    decide_campaign,
    manifest_digest,
    validate_manifest,
)
from orion_research_harness.campaign_protocol import CampaignState, ProtectedReference
from orion_research_harness.domains.orion_qg import QG7_CLASSIFICATION_CAMPAIGN_MANIFEST
from orion_research_harness.domains.orion_qg.qg7_classification import (
    PROTECTED_STRETCHED_N2_PATH,
    QG7_DECISION_BY_HYPOTHESIS,
    QG7_LADDER_RUNGS,
    QG7_OBSERVATION_KEYS,
    QG7_RUNG_TOKEN_PREFIX,
    derive_observations,
    rung_probe_code,
)

M = QG7_CLASSIFICATION_CAMPAIGN_MANIFEST


def _rung_token(rung: str, terminal: str, authority: str, **overrides):
    """A clean, fully-bound serialized probe token for one rung."""
    token = {
        "rung": rung,
        "receipt_path": f"research/extensions/orion-qg/QG7{rung}.json",
        "expected_schema": f"ORIONQG.QG7{rung}.v1",
        "present": True,
        "schema": f"ORIONQG.QG7{rung}.v1",
        "schema_matches": True,
        "terminal": terminal,
        "authority": authority,
        "authority_not_r6": "NOT_R6" in authority,
        "protocol": f"QG7{rung}_PROTOCOL_V1",
        "protocol_sha256": f"proto-{rung}",
        "result_digest_declared": f"digest-{rung}",
        "result_digest_rederived": f"digest-{rung}",
        "result_digest_rebinds": True,
        "gates_present": True,
        "gates_all_true": True,
        "r6_authority_false": True,
        "novelty_credit_false": True,
        "physical_advantage_false": True,
        "protected_unread": True,
        "r6s_receipt_bound": True,
        "binds": {},
    }
    token.update(overrides)
    return token


def _tokens(*, d_terminal: str | None, c_terminal: str, c_authority: str, **overrides):
    """A mutually bound ladder; ``d_terminal=None`` means QG-7d has not landed."""
    a = _rung_token(
        "A",
        "QG7_FOURTH_SUPPORT2_REGIME_FOUND",
        "ORIONQG_QG7_FOURTH_SUPPORT2_REGIME_FOUND__NOT_R6",
    )
    b = _rung_token(
        "B",
        "QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS",
        "ORIONQG_QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS__NOT_R6",
    )
    b["binds"] = {
        "qg7_receipt_bound": True,
        "qg7_authority": a["authority"],
        "qg7_protocol_sha256_recomputed": a["protocol_sha256"],
    }
    c = _rung_token("C", c_terminal, c_authority)
    c["binds"] = {
        "qg7_receipt_bound": True,
        "qg7b_receipt_bound": True,
        "qg7b_result_digest": b["result_digest_declared"],
        "qg7b_terminal": b["terminal"],
    }
    if d_terminal is None:
        d = {
            "rung": "D",
            "receipt_path": "research/extensions/orion-qg/QG7D_LAST_LINK_RESULTS.json",
            "expected_schema": "ORIONQG.QG7D.LastLink.v1",
            "present": False,
        }
    else:
        d_authority = (
            "ORIONQG_QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE__"
            "COMM_S2_PINNED_SECTOR_CLOSED_BY_JOINT_EXCHANGE_AND_MIRROR_DOMINATION__NOT_R6"
            if d_terminal == "QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE"
            else f"ORIONQG_{d_terminal}__NOT_R6"
        )
        d = _rung_token("D", d_terminal, d_authority)
        d["binds"] = {
            "qg7_receipt_bound": True,
            "qg7b_receipt_bound": True,
            "qg7c_receipt_bound": True,
            "qg7c_result_digest": c["result_digest_declared"],
            "qg7b_result_digest": b["result_digest_declared"],
        }
    tokens = {"A": a, "B": b, "C": c, "D": d}
    for rung, patch in overrides.items():
        tokens[rung].update(patch)
    return tokens


def _closed_chain(**overrides):
    return _tokens(
        d_terminal="QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE",
        c_terminal="QG7C_FOUR_CONFIGURATION_CLASSIFICATION_ALL_N_MACHINE_CHECKED",
        c_authority="ORIONQG_QG7C_FOUR_CONFIGURATION_CLASSIFICATION__NOT_R6",
        **overrides,
    )


def _open_sector_chain(*, d_terminal=None, **overrides):
    return _tokens(
        d_terminal=d_terminal,
        c_terminal="QG7C_PARTIAL__L4B_OPEN",
        c_authority=(
            "ORIONQG_QG7C_PARTIAL__L4B_COMM_S2_PINNED_SECTOR_OPEN__"
            "L4C_CLOSED_CONDITIONAL__NOT_R6"
        ),
        **overrides,
    )


def _state(observations) -> CampaignState:
    return CampaignState.create(
        campaign_id=M["campaign_id"],
        claim_id=M["claim_id"],
        phase_id="D0",
        cycle_index=1,
        manifest_digest=manifest_digest(M),
        observations=observations,
        active_hard_obligations=(),
        protected_refs=tuple(
            ProtectedReference.from_dict(item) for item in M["protected_refs"]
        ),
        authority_ceiling=M["authority_ceiling"],
    )


def _decide(tokens):
    return decide_campaign(_state(derive_observations(tokens)), M)


# ---- manifest shape --------------------------------------------------------


def test_qg7_manifest_validates() -> None:
    validate_manifest(M)
    assert M["campaign_id"] == "orion-qg:qg7-classification-ladder"
    assert set(M["phases"]) >= {
        "S0",
        "D0",
        "ACCEPT_CHAIN_RECORDED",
        "ACCEPT_PARTIAL_RECORDED",
        "REJECT_RECORDED",
    }


def test_qg7_manifest_declares_protected_stretched_n2_reference() -> None:
    refs = M["protected_refs"]
    assert len(refs) == 1
    assert refs[0]["ref_id"] == "protected-stretched-n2"
    assert refs[0]["path"] == PROTECTED_STRETCHED_N2_PATH
    assert refs[0]["released"] is False
    # No capability may release it, and none declares it readable.
    for capability in M["capabilities"].values():
        assert "release_protected_refs_on_success" not in capability
        assert PROTECTED_STRETCHED_N2_PATH not in capability.get(
            "declared_read_paths", []
        )


def test_qg7_ladder_rungs_and_probe_code_are_content_bound() -> None:
    assert [row["rung"] for row in QG7_LADDER_RUNGS] == ["A", "B", "C", "D"]
    for row in QG7_LADDER_RUNGS:
        code = rung_probe_code(row["rung"])
        assert row["receipt_path"] in code
        assert row["schema"] in code
        assert QG7_RUNG_TOKEN_PREFIX in code
        assert row["receipt_path"] in M["capabilities"]["qg7.load"]["declared_read_paths"]


# ---- observation discrimination -------------------------------------------


def test_qg7_every_decision_branch_reachable_from_distinct_observations() -> None:
    closed = derive_observations(_closed_chain())
    partial = derive_observations(_open_sector_chain())
    broken = derive_observations(
        _open_sector_chain(C={"result_digest_rebinds": False})
    )
    assert closed != partial != broken and closed != broken

    identified = {}
    for name, observations in (
        ("closed", closed),
        ("partial", partial),
        ("broken", broken),
    ):
        decision = decide_campaign(_state(observations), M)
        assert decision.responsibility["status"] == "IDENTIFIED", name
        identified[name] = QG7_DECISION_BY_HYPOTHESIS[
            decision.responsibility["identified_hypothesis_id"]
        ]
    assert identified == {
        "closed": "ACCEPT_CLASSIFICATION_CHAIN",
        "partial": "ACCEPT_PARTIAL_CHAIN",
        "broken": "REJECT_OR_CANNOT_CHECK",
    }
    assert len(set(identified.values())) == 3


def test_qg7_accepts_closed_chain_only_with_four_bound_rungs() -> None:
    decision = _decide(_closed_chain())
    assert decision.responsibility["identified_hypothesis_id"] == (
        "RESP:ACCEPT_CLASSIFICATION_CHAIN"
    )
    assert decision.selected_kind == "REVISION"
    assert decision.selected_id == "REV:ACCEPT_CHAIN"


def test_qg7_accepts_partial_chain_when_comm_s2_sector_stays_open() -> None:
    for tokens in (
        _open_sector_chain(),  # QG-7d absent
        _open_sector_chain(d_terminal="QG7D_PARTIAL__P1_RESIDUE_OPEN"),
        _open_sector_chain(d_terminal="QG7D_PARTIAL__CENSUS_RESIDUE_OPEN"),
    ):
        observations = derive_observations(tokens)
        assert observations["QG7_COMM_S2_SECTOR"] == "OPEN"
        decision = decide_campaign(_state(observations), M)
        assert decision.responsibility["identified_hypothesis_id"] == (
            "RESP:ACCEPT_PARTIAL_CHAIN"
        )
        assert decision.selected_id == "REV:ACCEPT_PARTIAL"


def test_qg7_absent_last_link_is_skipped_not_fatal() -> None:
    observations = derive_observations(_open_sector_chain())
    assert observations["QG7_RUNGS_PRESENT"] == "THREE"
    assert observations["QG7_RUNG_D_TERMINAL"] == "ABSENT"
    assert observations["QG7_LADDER_ADMISSIBLE"] == "YES"


@pytest.mark.parametrize(
    "rung,patch",
    [
        ("A", {"result_digest_rebinds": False}),
        ("B", {"gates_all_true": False}),
        ("C", {"authority_not_r6": False}),
        ("D", {"protected_unread": False}),
        ("A", {"r6_authority_false": False}),
        ("B", {"novelty_credit_false": False}),
        ("C", {"schema_matches": False}),
        ("A", {"r6s_receipt_bound": False}),
    ],
)
def test_qg7_rejects_any_broken_rung(rung, patch) -> None:
    tokens = _closed_chain(**{rung: patch})
    decision = _decide(tokens)
    assert decision.responsibility["identified_hypothesis_id"] == (
        "RESP:REJECT_OR_CANNOT_CHECK"
    )
    assert decision.selected_id == "REV:REJECT"


def test_qg7_rejects_unbound_chain_links() -> None:
    tokens = _closed_chain()
    tokens["C"]["binds"]["qg7b_result_digest"] = "not-the-qg7b-digest"
    observations = derive_observations(tokens)
    assert observations["QG7_CHAIN_BINDINGS"] == "NO"
    assert observations["QG7_LADDER_ADMISSIBLE"] == "NO"
    assert _decide(tokens).selected_id == "REV:REJECT"


def test_qg7_rejects_refuted_or_cannot_check_last_link() -> None:
    for terminal in ("QG7D_LINK_REFUTED", "QG7D_CANNOT_CHECK"):
        tokens = _open_sector_chain(d_terminal=terminal)
        observations = derive_observations(tokens)
        assert observations["QG7_RUNG_D_TERMINAL"] == "OTHER"
        assert observations["QG7_COMM_S2_SECTOR"] == "INDETERMINATE"
        assert _decide(tokens).selected_id == "REV:REJECT"


def test_qg7_rejects_sector_closed_without_the_declared_last_link() -> None:
    """A closed sector may only be read off a present, theorem-terminal QG-7d."""
    tokens = _closed_chain()
    tokens["D"]["authority"] = "ORIONQG_QG7D_ALL_N_CLASSIFICATION_THEOREM_COMPLETE__NOT_R6"
    observations = derive_observations(tokens)
    assert observations["QG7_COMM_S2_SECTOR"] == "INDETERMINATE"
    assert _decide(tokens).selected_id == "REV:REJECT"


def test_qg7_missing_core_rung_cannot_be_accepted() -> None:
    tokens = _open_sector_chain()
    tokens["C"] = {"rung": "C", "receipt_path": "x", "present": False}
    observations = derive_observations(tokens)
    assert observations["QG7_RUNGS_PRESENT"] == "FEWER"
    assert observations["QG7_LADDER_ADMISSIBLE"] == "NO"
    assert _decide(tokens).selected_id == "REV:REJECT"


def test_qg7_observation_keys_are_stable_and_complete() -> None:
    assert set(QG7_OBSERVATION_KEYS) == set(derive_observations(_closed_chain()))
    modeled = {
        key
        for row in M["phases"]["D0"]["responsibility_hypotheses"]
        for key in row["expected_observations"]
    }
    assert modeled <= set(QG7_OBSERVATION_KEYS)
    assert "QG7_LADDER_ADMISSIBLE" in modeled


# ---- authority ceiling -----------------------------------------------------


def test_qg7_manifest_cannot_self_authorize() -> None:
    ceiling = M["authority_ceiling"]
    assert "NOT_R6" in ceiling
    assert ceiling.startswith("NON_AUTHORIZING_")
    text = repr(M)
    for forbidden in (
        "'novelty_authority': True",
        "'scientific_authority': True",
        "'r6_authority': True",
        "'physical_quantum_advantage_claim': True",
        "'protected_subject_read': True",
    ):
        assert forbidden not in text
    for capability in M["capabilities"].values():
        required = {
            tuple(row["path"]): row["equals"]
            for row in capability["result_contract"].get("required_payload_values", [])
        }
        for key in ("r6_authority", "novelty_authority", "scientific_authority"):
            assert required.get((key,), False) is False


def test_qg7_decisions_grant_no_authority() -> None:
    for tokens in (_closed_chain(), _open_sector_chain()):
        unsigned = _decide(tokens).as_dict()
        for key, value in unsigned.items():
            if key.startswith("grants_"):
                assert value is False
        assert unsigned["responsibility"]["grants_revision_authority"] is False


def test_qg7_terminal_phases_carry_no_authority_grant() -> None:
    for phase_id in (
        "ACCEPT_CHAIN_RECORDED",
        "ACCEPT_PARTIAL_RECORDED",
        "REJECT_RECORDED",
    ):
        phase = M["phases"][phase_id]
        assert phase["terminal"] is True
        assert phase["active_hard_obligations"] == []
        with pytest.raises(ValueError):
            decide_campaign(
                CampaignState.create(
                    campaign_id=M["campaign_id"],
                    claim_id=M["claim_id"],
                    phase_id=phase_id,
                    cycle_index=2,
                    manifest_digest=manifest_digest(M),
                    observations={},
                    authority_ceiling=M["authority_ceiling"],
                ),
                M,
            )


def test_qg7_state_is_bound_to_this_manifest() -> None:
    state = _state(derive_observations(_open_sector_chain()))
    mutated = dict(M)
    mutated["claim_id"] = "orion-qg:some-other-claim"
    with pytest.raises(ValueError):
        decide_campaign(state, mutated)
