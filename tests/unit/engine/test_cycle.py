import pytest

from orion.engine.cycle import (
    CycleOperator,
    Responsibility,
    Transition,
    revision_allowed,
)


def test_search_cannot_mint_authority():
    transition = Transition(
        operator=CycleOperator.SEARCH,
        input_epoch=0,
        output_epoch=1,
        authority_increase=True,
        scientific_authority_certificate_ids=("certificate:fake",),
    )
    with pytest.raises(ValueError, match="cannot directly increase"):
        transition.validate()


def test_authority_increase_requires_certificate():
    transition = Transition(
        operator=CycleOperator.ABSORB,
        input_epoch=1,
        output_epoch=2,
        authority_increase=True,
    )
    with pytest.raises(ValueError, match="requires certificate"):
        transition.validate()


def test_reframe_blocked_under_ambiguous_responsibility():
    assert not revision_allowed((Responsibility.SEARCH, Responsibility.METHOD))
    assert revision_allowed((Responsibility.SEARCH,))
