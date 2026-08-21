from orion_learning_machine.adapters.lean_source import tactic_action

def test_tactic_action_keeps_lower_level_distinctions():
    assert tactic_action('  exact h')=='exact'
    assert tactic_action('  apply foo')=='apply'
    assert tactic_action('    foo h') is None
