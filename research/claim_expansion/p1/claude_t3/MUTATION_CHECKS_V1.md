# P1-U-T3 mutation checks — every repair has a test that goes red when it is reverted

Method: apply one mutation to `research/claim_expansion/p1/gpt_r6/evaluate_native.py` in place,
run `tests/unit/p1/test_p1_u_t3_repaired_guards.py`, record which tests fail, restore the
pristine file, and confirm the restored file is byte-identical and the suite is green again.
Both the pristine and the restored runs were green (`M0`, `M8`), and the restored file was
verified byte-identical to the pre-mutation copy after each pass.

| id | mutation applied | tests that go red |
| --- | --- | --- |
| M1 | file each member back under `pair["adverse_class"]` (the original line 338) | `test_class_strata_are_filed_under_each_members_own_gold_class`, `test_a_comparator_that_only_wins_on_controls_now_fails_the_class_guard` |
| M2 | keep the member-level stratum but drop it from the `class_noninferiority` conjunction | `test_a_comparator_that_only_wins_on_controls_now_fails_the_class_guard` |
| M3 | rename `domain_zero_loss` back to `domain_noninferiority` and delete the verdict-equivalence assertion | `test_domain_margin_is_restated_as_the_zero_loss_rule_it_actually_is` |
| M4 | restore the fail-open shape: coerce a missing/None/non-sequence payload record to `[]` instead of `CANNOT_CHECK` | `test_leakage_audit_fails_closed_on_absent_empty_and_malformed_records` |
| M5 | drop pair role from the forbidden token set (id category, `pair_role` literal, role-assignment regex) | `test_pair_role_is_a_forbidden_token`, `test_the_repaired_leakage_guard_finds_the_leak_it_was_named_for` |
| M6 | give `LeakageVerdict.__bool__` an ordinary two-valued meaning instead of raising | `test_leakage_verdict_refuses_a_two_valued_reading` |
| M7 | drop `payload_sink`, so a leakage finding can only ever be seen as a digest | `test_payloads_can_be_re_audited_from_the_sink_with_a_corrected_token_set` |

## Note on M2 — the first version of this test did not catch it

The initial conjunction test asserted only that
`checks["class_noninferiority"] == pair_level and member_level`. On the real corpus both
conjuncts are `True`, so `pair_level and member_level == pair_level`, and deleting the second
conjunct changed nothing observable. The mutation harness caught the hole, not a reading of
the test.

The replacement builds the case the broken guard structurally could not see: a comparator that
is **always right on the 22 matched controls and always wrong everywhere else**. Under it,
every pair-level class mean is `>= 0` (`P_b3 = 0` for every pair, because B3 still misses the
adverse member, so the pair statistic sees nothing), while the control gold class loses 14 of
22 episodes and its member-level mean is `-0.636`. Pair-level verdict `True`, member-level
verdict `False`, repaired check `False`. The substitute comparator is confined to that one
test; it touches no result, artifact or real B3 code path.

## Reproduce

```
PYTHONPATH=src python -m pytest tests/unit/p1/test_p1_u_t3_repaired_guards.py -q
```

The mutation harness itself is scratch tooling and is not committed; each mutation above is a
one- or two-line edit at the anchor named in the corresponding test's docstring.
