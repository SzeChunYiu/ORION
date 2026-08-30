# ORION-01 independent proof checker V1 — theory-A Lemma 3

Discharges the #1701 box "Run an implementation-independent proof checker from
theorem statements, not production code."

## What was checked

`theory-A-MANUSCRIPT_V2.md` §6 defines the local `b`-way Restore functional

```
F_b(a_1,...,a_b) = 1                    if all letters are the same nonidentity Pauli
                 = #{i : a_i != I}       otherwise
```

**Lemma 3.** Replacing one argument of `F_b` increases its value by at most
`b-1`, and the bound is attained.

## Independence

`check_lemma3_independent_v1.py` imports **nothing** from `src/orion`. `F_b` is
re-implemented directly from the sentence above, and the lemma is then checked
by exhaustive enumeration. If the production implementation of `F_b` and the
manuscript's definition disagree, this checker follows the manuscript — which is
the point of the box, and the only configuration in which the check can falsify
the paper rather than the code.

## Result: verified, both halves

| b | tuples | max increase | bound `b-1` | at most | attained |
|---|---|---|---|---|---|
| 2 | 16 | 1 | 1 | yes | yes |
| 3 | 64 | 2 | 2 | yes | yes |
| 4 | 256 | 3 | 3 | yes | yes |
| 5 | 1,024 | 4 | 4 | yes | yes |
| 6 | 4,096 | 5 | 5 | yes | yes |
| 7 | 16,384 | 6 | 6 | yes | yes |
| 8 | 65,536 | 7 | 7 | yes | yes |

**87,376 tuples, every single-argument replacement, zero violations.** Both
clauses hold: the inequality is never exceeded, and equality is realised at
every `b`.

## Mechanism, not just the number

The extremal witness is the same at every `b`: `XX...X`, replace position 0 by
`Y`, taking `F_b` from **1 to b**. The all-same-nonidentity tuple is the unique
place where `F_b` takes the value 1, so it is the unique launching point for a
maximal jump, and any replacement that breaks the "all same" condition while
keeping every letter nonidentity realises the full `b-1`. The lemma is tight for
exactly one structural reason, and the checker exhibits it rather than asserting
it.

## Mutation control

A checker that always reports "verified" is worthless. `F_b` was mutated to drop
the all-same-nonidentity special case (leaving only the nonidentity count).
Under that mutation a single replacement can change the value by at most 1, so
the `b-1 = 3` bound at `b=4` is **not** attained — and the checker reports max
increase 1, detecting the mutation. The check is therefore sensitive to the very
clause that makes the lemma non-trivial.

## Scope

- Lemma 3 only. Theorems 1-4 and the surrounding grammar are not checked here.
- Exhaustive for `b <= 8`; `b > 8` follows by the structural argument above but
  is not enumerated.
- Verifies the manuscript's *stated* lemma. It does not verify that the
  production code implements the same `F_b`; a divergence there would be a
  separate finding.
- `scientific_authority_delta: NONE` — this confirms an existing lemma and
  creates no new claim.

**Terminal:** `LEMMA3_EXHAUSTIVELY_VERIFIED_b2_b8__MUTATION_CONTROL_PASSED`
