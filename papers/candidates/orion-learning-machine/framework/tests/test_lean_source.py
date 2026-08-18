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


def test_intervening_top_level_definition_cannot_leak_into_prior_proof():
    src='''theorem first : True := by
  exact True.intro

def unrelated : Nat := by
  exact 1

theorem second : True := by
  simp
'''
    th=parse_lean_source(src,'boundary.lean')
    assert [item.theorem_name for item in th]==['first','second']
    assert th[0].tactics==('apply',)
    assert th[1].tactics==('simplify',)
    assert all('unrelated' not in line for line in th[0].raw_lines)


def test_instance_namespace_and_end_boundaries_fail_closed():
    src='''namespace N
theorem first : True := by
  exact True.intro
instance : Inhabited Nat where
  default := 0
end N

theorem second : True := by
  exact True.intro
end
'''
    th=parse_lean_source(src,'commands.lean')
    assert [item.theorem_name for item in th]==['first','second']
    assert th[0].raw_lines==('theorem first : True := by','  exact True.intro')
    assert th[1].raw_lines==('theorem second : True := by','  exact True.intro')
