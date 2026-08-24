from orion.foundations.discharge import (
    DischargeRule,
    TransitionContract,
    bridge_necessity_holds,
    contracts_compose,
    least_closure,
    no_amplification_holds,
)


def test_no_amplification_and_bridge_necessity() -> None:
    local = DischargeRule(frozenset({"native", "scope"}), "verified")
    promote = DischargeRule(frozenset({"verified", "bridge"}), "claim")
    seeds = frozenset({"native", "scope"})

    assert least_closure(seeds, (local, promote)) == frozenset({"native", "scope", "verified"})
    assert no_amplification_holds(seeds, (local,), (frozenset({"verified"}),))
    assert bridge_necessity_holds(seeds, (local,), "claim", (frozenset({"verified"}),))


def test_exact_contract_composition() -> None:
    first = TransitionContract("a", "b", "sha", "scope", "epoch", "r", "auth")
    second = TransitionContract("b", "c", "sha", "scope", "epoch", "r", "auth")
    mismatch = TransitionContract("b", "c", "other", "scope", "epoch", "r", "auth")
    assert contracts_compose(first, second)
    assert not contracts_compose(first, mismatch)
