from __future__ import annotations

from orion_research_harness.epistemic_mechanics import (
    AuthorityGrant,
    ClaimStatus,
    EpistemicMechanicState,
    HardObligation,
    MechanicContract,
    MechanicTerminal,
    PreservationCertificate,
    apply_mechanic,
    certificate_aware_reopen,
    independently_equivalent_histories,
    semantically_separated,
)


def _state() -> EpistemicMechanicState:
    return EpistemicMechanicState(
        coordinate_values=(("x", "old"), ("y", "0")),
        claim_statuses=(("q_root", ClaimStatus.CERTIFIED), ("q_child", ClaimStatus.CERTIFIED)),
        dependencies=(("q_root", "q_child"),),
        evidence_ids=("e:base",),
        provenance_ids=("p:base",),
        hard_obligations=(),
        authorities=(AuthorityGrant("a:root", ("x",), "root:protected", 1),),
        protected_root_ids=("root:protected",),
        epoch=1,
        history=(),
    )


def test_root_inclusive_reopen_reopens_changed_certified_root_and_descendant():
    repaired = certificate_aware_reopen(_state(), changed_ids=("q_root",), certificates=())
    status = dict(repaired.claim_statuses)
    assert status["q_root"] is ClaimStatus.OPEN
    assert status["q_child"] is ClaimStatus.OPEN


def test_changed_root_cannot_self_preserve_with_preservation_certificate():
    cert = PreservationCertificate(
        certificate_id="k:self",
        claim_id="q_root",
        changed_ids=("q_root",),
        issuer_id="root:protected",
        scope_ids=("q_root",),
        epoch=1,
        proof_id="proof:self",
        lineage_ids=("e:base",),
    )
    repaired = certificate_aware_reopen(_state(), changed_ids=("q_root",), certificates=(cert,))
    assert dict(repaired.claim_statuses)["q_root"] is ClaimStatus.OPEN


def test_external_exact_change_certificate_can_preserve_unchanged_descendant():
    cert = PreservationCertificate(
        certificate_id="k:child",
        claim_id="q_child",
        changed_ids=("q_root",),
        issuer_id="root:protected",
        scope_ids=("q_child",),
        epoch=1,
        proof_id="proof:child-invariant",
        lineage_ids=("e:base",),
    )
    repaired = certificate_aware_reopen(_state(), changed_ids=("q_root",), certificates=(cert,))
    status = dict(repaired.claim_statuses)
    assert status["q_root"] is ClaimStatus.OPEN
    assert status["q_child"] is ClaimStatus.CERTIFIED


def test_hard_obligation_persists_until_authorized_discharge():
    emit = MechanicContract(
        mechanic_id="m:emit",
        read_ids=(),
        write_ids=("y",),
        write_values=(("y", "1"),),
        emitted_obligations=(HardObligation("o:verify", required_evidence_ids=("e:verify",)),),
    )
    first = apply_mechanic(_state(), emit)
    assert first.terminal is MechanicTerminal.APPLIED
    assert {item.obligation_id for item in first.state.hard_obligations if item.active} == {"o:verify"}

    unrelated = MechanicContract(
        mechanic_id="m:unrelated",
        read_ids=("y",),
        write_ids=("y",),
        write_values=(("y", "2"),),
    )
    second = apply_mechanic(first.state, unrelated)
    assert second.terminal is MechanicTerminal.APPLIED
    assert {item.obligation_id for item in second.state.hard_obligations if item.active} == {"o:verify"}

    # Merely naming a discharge is not enough; its required evidence is missing.
    premature = MechanicContract(
        mechanic_id="m:premature",
        read_ids=(),
        write_ids=(),
        discharge_obligation_ids=("o:verify",),
    )
    blocked = apply_mechanic(second.state, premature)
    assert blocked.terminal is MechanicTerminal.CANNOT_CHECK
    assert blocked.state == second.state

    with_evidence = second.state.with_evidence("e:verify")
    discharged = apply_mechanic(with_evidence, premature)
    assert discharged.terminal is MechanicTerminal.APPLIED
    assert not next(item for item in discharged.state.hard_obligations if item.obligation_id == "o:verify").active


def test_write_outside_declared_footprint_is_denied_without_state_mutation():
    contract = MechanicContract(
        mechanic_id="m:bad-write",
        read_ids=(),
        write_ids=("x",),
        write_values=(("y", "forbidden"),),
    )
    result = apply_mechanic(_state(), contract)
    assert result.terminal is MechanicTerminal.DENIED
    assert result.state == _state()
    assert "write footprint" in result.reason.lower()


def test_missing_hard_evidence_and_authority_fail_closed_without_mutation():
    contract = MechanicContract(
        mechanic_id="m:needs",
        read_ids=(),
        write_ids=("x",),
        write_values=(("x", "new"),),
        required_evidence_ids=("e:missing",),
        required_authority_ids=("a:missing",),
    )
    result = apply_mechanic(_state(), contract)
    assert result.terminal is MechanicTerminal.CANNOT_CHECK
    assert result.state == _state()


def test_unrooted_authority_widening_is_denied():
    contract = MechanicContract(
        mechanic_id="m:widen",
        read_ids=(),
        write_ids=(),
        authority_additions=(AuthorityGrant("a:new", ("x", "y"), "root:unprotected", 1),),
    )
    result = apply_mechanic(_state(), contract)
    assert result.terminal is MechanicTerminal.DENIED
    assert result.state == _state()
    assert "authority" in result.reason.lower()


def test_semantically_separated_mechanics_commute_current_state_but_preserve_history_order():
    left = MechanicContract(
        mechanic_id="m:left",
        read_ids=("x",),
        write_ids=("x",),
        write_values=(("x", "L"),),
    )
    right = MechanicContract(
        mechanic_id="m:right",
        read_ids=("y",),
        write_ids=("y",),
        write_values=(("y", "R"),),
    )
    assert semantically_separated(left, right) is True

    lr = apply_mechanic(apply_mechanic(_state(), left).state, right).state
    rl = apply_mechanic(apply_mechanic(_state(), right).state, left).state
    assert lr.scientific_projection() == rl.scientific_projection()
    assert lr.history != rl.history
    assert independently_equivalent_histories(lr.history, rl.history, independent_pairs=(("m:left", "m:right"),))


def test_recursive_self_call_without_rank_decrease_is_rejected():
    recursive = MechanicContract(
        mechanic_id="m:recursive",
        read_ids=(),
        write_ids=(),
        audit_rank=2,
        recursive_calls=(("m:recursive", 2),),
    )
    result = apply_mechanic(_state(), recursive)
    assert result.terminal is MechanicTerminal.DENIED
    assert "rank" in result.reason.lower() or "cycle" in result.reason.lower()
