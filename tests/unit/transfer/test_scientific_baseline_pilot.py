from orion.transfer.scientific.baseline_pilot import (
    Representation,
    evaluate_representation,
    frozen_stage0_episodes,
    run_matched_baselines,
)


def test_stage0_has_four_domains_and_all_pair_kinds() -> None:
    episodes = frozen_stage0_episodes()
    assert len(episodes) == 16
    assert len({episode.source_family for episode in episodes}) == 4
    assert {episode.pair_kind for episode in episodes} == {"positive", "near_miss", "negative", "partial"}


def test_all_requested_representation_baselines_execute() -> None:
    outcomes = run_matched_baselines()
    assert {outcome.representation for outcome in outcomes} == set(Representation)
    assert all(outcome.n == 16 for outcome in outcomes)


def test_mechanic_contract_rejects_negative_transfer_controls() -> None:
    outcome = evaluate_representation(Representation.MECHANIC_CONTRACT)
    assert outcome.harmful_transfer == 0
    assert outcome.accuracy == 1.0


def test_surface_or_unstructured_representations_are_not_silently_perfect() -> None:
    for rep in (
        Representation.RAW_TRAJECTORY,
        Representation.SUMMARY,
        Representation.NL_INSIGHT,
        Representation.SKILL,
        Representation.SOURCE_CODE,
    ):
        outcome = evaluate_representation(rep)
        assert outcome.accuracy < 1.0


def test_nl_insight_and_skill_show_near_miss_negative_transfer() -> None:
    assert evaluate_representation(Representation.NL_INSIGHT).harmful_transfer > 0
    assert evaluate_representation(Representation.SKILL).harmful_transfer > 0


def test_oracle_is_analysis_ceiling_not_claimed_mechanism() -> None:
    oracle = evaluate_representation(Representation.ORACLE)
    mechanic = evaluate_representation(Representation.MECHANIC_CONTRACT)
    assert oracle.accuracy == 1.0
    assert mechanic.accuracy <= oracle.accuracy
