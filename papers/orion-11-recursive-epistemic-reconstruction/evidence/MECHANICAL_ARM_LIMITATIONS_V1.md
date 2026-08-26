# Mechanical arm — what 62/66 does and does not establish

**Bound to:** PILOT `7a50a2d5…`, TEST `21b461d8…`.
**Result being qualified:** the LLM-free reduction layer attributes the correct
top-ranked responsibility on 62 of 66 cases, with 0 of 22 negative controls
topped by a formulation responsibility.

This document exists because the headline number is softer than it reads, and
every limitation below was raised by the lane that produced the result rather
than found by review.

## 1. Half the score rests on rules that fire once

Measured directly on the frozen suite:

| | count |
|---|---|
| distinct rules that ever rank first | 40 |
| rules that top **exactly one** case | 32 |
| cases carried by a one-case rule | **32 / 66** |
| cases covered by rules that top 3+ cases | **26 / 66** |

Only four relations carry three or more cases:

| relation | cases |
|---|---|
| `required_input_absent_but_obtainable` | 10 |
| `framing_remedy_tried_and_failed` | 8 |
| `counterfactual_restores_baseline` | 5 |
| `equal_weight_aggregation_over_skewed_units` | 3 |

**What this means.** A rule that fires on exactly one case is not distinguishable,
from inside this suite, from a case-specific recognizer. The defensible claim is
therefore *not* "a general mechanical procedure attributes responsibility on 94%
of cases". It is: **four general relations cover 26 cases; the remaining
attributions rest on narrower rules whose generality is untested.** Only a fresh
set of cases the rules were not written against can separate the two, and no such
set exists yet.

Removing the five rules the author judged phrase-anchored
(`claimed_optimum_beaten_by_ad_hoc_change`, `rule_input_supplied_by_interested_party`,
`policy_needs_comparison_data_cannot_support`, `distinct_encodings_never_merge`,
`operation_not_invariant`) costs 62 → 57.

## 2. Four attributions may be agreement-by-construction

The independent solvability audit rates **c017 UNSOLVABLE** and records that
reaching its cause requires gold vocabulary. The reducer's
`analysis_drops_stated_subset` nonetheless tops it correctly. The underlying
relation — kept plus dropped equals the whole, and the dropped part is stated to
differ systematically — is computed soundly from public content. Mapping that
relation to SEARCH rather than to another family is a design decision made by the
rule author, not something the case forces.

The same caveat applies to **c105, c110, c118**, where the audit's independent
reader placed a different family before consulting gold.

## 3. One correct answer rests on a false premise

`operation_not_invariant` fires on c014's `symmetry-check.md`, which asserts that
plain averaging is not complement-invariant. It is, by linearity. The rule
therefore reaches the graded answer through a claim in the case that is
arithmetically false. Recorded rather than tuned around: the fire is "correct"
only in the sense that it matches gold.

Four sibling arithmetic defects (c013, c139, c142, c143) were confirmed and
repaired. c014 was examined and **not** changed — its stated numbers check out
and no fault was found, so the disagreement is about the prose claim rather than
the arithmetic.

## 4. Two boundaries relations genuinely cannot reach

- **INTERFACE versus DECOMPOSITION is not mechanically separable** from the
  public text. The boundary rules emit both together; INTERFACE-first is
  arbitrary and costs exactly the 3 in-set cases (c018, c103, c147). The more
  specific DECOMPOSITION finding remains in the returned set. Rule strengths were
  deliberately *not* re-tuned to recover these, since tuning a strength to match
  gold on three cases is fitting, not detection.
- **c016 is detected but deliberately unattributed.** The disagreement is found
  and returned with no responsibility, because the rater-marginal spread does not
  determine whether the fault is the unit of account or a missing model. The
  independent audit also rates it UNSOLVABLE. An unattributed detection is the
  honest output and is scored as such, not as a miss.

## 5. What is genuinely established

Stated plainly, because the negative framing above should not obscure it:

- The earlier conclusion — that the mechanical arm is **structurally**
  non-viable, since any channel rich enough for a detector is rich enough for a
  blind responder — is **false**, and false at suite scale rather than on one
  case. It was refuted first arithmetically on c109 and then by an independent
  audit rating 55 of 66 cases SOLVABLE from public content alone.
- The detector reads **relations between computed quantities**, not vocabulary.
  Replacing every resource path stem and closure slug with an opaque id costs
  **0 of 62**. Two prompts differing only by the template sentence reduce
  identically. The template tokens are refused from the lexicon by rule.
- **0 of 22 negative controls** is topped by a formulation responsibility, which
  is the quantity H2 depends on.
- Degeneracy is CLEAN pooled, pilot and test with the reducer's own structure as
  features, and the strongest shape-only blind responder scores 0.106 / 0.056 /
  0.167 against a 0.167 majority baseline — at or below chance everywhere.

## 6. The test that would settle §1

Write 20 fresh cases against the four generalising relations **without consulting
the rule set**, and score the existing rules on them unchanged. If the four
relations hold and the singleton rules stay silent, §1 resolves in favour of
generality. If the singletons were recognizers, they will stay silent there too
and the score will fall to roughly the 26-case core. Either outcome is
publishable; running it is the only way to know which.
