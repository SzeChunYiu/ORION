from orion_learning_machine.adapters.lean_source import parse_lean_source, tactic_family


def test_statement_and_term_continuations_are_not_actions():
    src='''theorem foo\n    (h : True) :\n    True := by\n  have h2 : True :=\n    h\n  exact h2\n'''
    th=parse_lean_source(src,'toy.lean')
    assert len(th)==1
    assert th[0].tactics == ('calculation','apply')


def test_unknown_command_is_not_forced_into_known_family():
    assert tactic_family('custom_tactic') == 'unknown'
    src='''theorem foo : True := by\n  custom_tactic\n  exact True.intro\n'''
    th=parse_lean_source(src,'toy.lean')
    assert th[0].tactics == ('apply',)
