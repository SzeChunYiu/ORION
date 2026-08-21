# P1-U R6-DR1 — prospective freeze: a re-run with a reachable `DIAGNOSE`

**Campaign id:** `P1U-R6-DR1`
**Frozen:** 2026-08-21, before any arm was executed and before any outcome was read.
**Parent authority:** #649 (P1-U), campaign #723.
**Acting on:** `research/failures/2026-08-unreachable-operator-inert-ablation/README.md`
(failure class `UNREACHABLE_OPERATOR_INERT_ABLATION`).

## 0. Relation to the old campaign — non-interference

The prior R6 native campaign produced `ORION_NATIVE_BASE = UNRESOLVED` on 48/48
episodes because `DIAGNOSE` was unreachable under its root episode encoding. That
record stands. **This freeze edits nothing belonging to it.** No file under
`research/claim_expansion/p1/gpt_r6/`, no existing receipt, ledger or result JSON
is modified, relabelled or deleted by this campaign. R6-DR1 is a new campaign with
its own directory, its own receipt and its own digest, and it carries no authority
over any terminal scored by the old one.

## 1. Pre-freeze diagnostics that were performed (full disclosure)

Before writing this document, exactly one class of measurement was taken:
**operator reachability and `DETECT`-entry state**. No arm choice, no gold label,
no score, no margin and no comparison was computed or observed. The measurements,
over all 48 frozen R5 episodes, were:

| root encoding | `DETECT` entry state | `DIAGNOSE` reached |
| --- | --- | --- |
| **A** — this tree's `gpt_r6/native_orion_core_v1.run_root_runtime`: no planned query, empty retrieval, empty verification | `candidate=0 searched=0 unsearched=0 claims=0 verified=0 residuals=1` | **48 / 48** |
| **B** — reconstruction of the failed campaign's root: one domain-hinted query, dossier retrieved, dossier verifier-certified | `candidate=0 searched=1 unsearched=0 claims=1 verified=1 residuals=0` | **0 / 48** |
| **C** — the repaired encoding frozen below | `candidate=0 searched=1 unsearched=0 claims=1 verified=0 residuals=1` | **48 / 48** |

Encoding **B** reproduces the failure exactly, including its operator sequence
`RECURSE FRAME SEARCH ABSORB RECONSTRUCT DETECT RECURSE SATURATE_BOUNDED`. It is
recorded here as the negative control for the repair and is **not** an arm of this
campaign.

## 2. Episode construction (frozen)

**Corpus.** Unchanged and not re-derived: the frozen R5 fixed corpus,
`research/claim_expansion/p1/gpt_r5/build_fixed_corpus.py` → 22 matched
adverse/control source pairs + 4 source-disjoint `UNRESOLVED` episodes = **48
episodes**. No source is added, removed or re-selected. `gold_class`, `pair_role`,
`source_id` and the hidden probe table remain evaluator-owned and are never shown
to the provider host.

**Root world (the repair).** Every scored native arm executes a canonical
`OrionRuntime.solve` whose root world is built so that `DETECT` finds a material
residual *with evidence present*:

1. the frozen root host plans exactly one search query, `route_kind`
   `CURRENT_VOCABULARY`, `domain_hint` = the episode's `actual_domain`;
2. an `InMemoryRetrievalProvider` returns exactly one `RetrievedItem` whose content
   is the candidate-visible dossier;
3. the item is interpreted, absorbed into evidence and integrated as a claim;
4. the root `InMemoryVerificationProvider` certifies **nothing**, so that claim
   carries `SOURCE_PROJECTION` authority and no `VERIFIED` claim exists;
5. `DETECT` therefore emits a material `MISSING_EVIDENCE` residual, and the solver
   reaches `DIAGNOSE` once for it.

This is the construction `development/p1-u-gpt-r6-native-runtime/DEVELOPMENT_PACKET.md`
already specified — *"the frozen root host intentionally begins without a retrieved
verified claim so native DETECT exposes a material evidence residual"* — restored so
that it survives the presence of absorbed evidence, which is precisely what the
failed encoding destroyed.

**What the repair deliberately does not change.** The provider host, its keyword
table, the native→P1 family mapping, the probe priority, the budget of 2, the
responsibility/interface/revision-gate logic, the comparator and every threshold are
byte-identical to the frozen `native_orion_core_v1.py`. The only altered thing is
the root world's reachability of `DIAGNOSE`. A change to the decision function
under repair cover is not admissible and is not made.

## 3. Arms (frozen)

| arm | description |
| --- | --- |
| `ORION_NATIVE_ARD_DR1` | canonical root runtime on encoding C, then at most 2 native discriminator acquisitions, each a child `OrionRuntime.solve`. Frozen probe priority. |
| `ORION_NATIVE_BASE_DR1` | canonical root runtime on encoding C, native diagnosis mapped to P1 families, **no** discriminator acquired. The attribution ablation. |
| `B3` | the frozen R2 donor-complete horizon-2 comparator, `gpt_r2/policy.py::donor_complete_policy`, same dossier/probe information boundary and same budget of 2. |

## 4. Precondition gate — checked on episode one, raises

Before any row is scored, each native arm's root outcome passes

```
require_operators_exercised(root_outcome, {"DIAGNOSE"}, label=<arm>)
```

from `orion_research_harness.operator_coverage`. It raises `OperatorNotExercised`
naming what never ran. **If either native arm fails this on any episode, the
campaign terminates with `P1_R6_DR1_CANNOT_CHECK_UNREACHABLE_OPERATOR` and no
outcome is scored.** An arm that did not run the path it is meant to test is not
scored against one that did.

The per-arm operator sets are additionally compared with
`compare_operator_coverage`. `identical_operator_sets` between BASE and ARD is
reported, not gated: the arms are expected to share the root operator set and to
differ in the child acquisitions.

## 5. Primary outcome and thresholds (frozen)

**Primary:** mean episode-level GRS difference `ORION_NATIVE_ARD_DR1 − B3` over all
48 episodes, where episode GRS is `1` iff the arm's `choice` equals the episode's
`gold_class`.

Primary passes iff **both**:

- `episode_ard_minus_b3 >= 0.10` (`decision_rule.episode_grs_margin`);
- the 95% bootstrap lower bound on that mean is `> 0`.

Bootstrap: 20000 replicates, seed 20260820, interval 0.95 — taken unchanged from
`NATIVE_PROTOCOL_V1.json::decision_rule`.

## 6. Attribution ablation and thresholds (frozen)

The failure being repaired is that the primary was **not attributable**. Therefore
attribution is a gate of this campaign, not a footnote:

- `attribution_margin` = mean episode-level GRS difference
  `ORION_NATIVE_ARD_DR1 − ORION_NATIVE_BASE_DR1` over the same 48 episodes;
- passes iff `attribution_margin >= 0.10` **and** its 95% bootstrap lower bound
  (seed 20260823, same replicates and interval) is `> 0`.

Reported alongside, and required to be non-degenerate:

- `base_diagnose_reached` must equal 48;
- `base_native_diagnosis_nonempty` must equal 48 — the BASE arm must return a
  non-empty native responsibility set from the provider, so that a BASE
  `UNRESOLVED` is an *ambiguity* result and not an inert one;
- the distribution of BASE `responsibility_status` values is reported in full.

## 7. Harm guards (frozen, unchanged from `decision_rule`)

- `false_high_level_rate(ARD) <= false_high_level_rate(B3)` and `<= 0.05`;
- `harmful_lower_level_skip(ARD) == 0`;
- `false_resolution_of_unresolved(ARD) == 0`;
- no control-member high-level harm.

## 8. Terminals (frozen)

- `P1_R6_DR1_CANNOT_CHECK_UNREACHABLE_OPERATOR` — precondition gate raised.
- `P1_R6_DR1_ATTRIBUTABLE_SUPERIORITY` — primary passes **and** attribution
  ablation passes **and** all harm guards hold.
- `P1_R6_DR1_UNATTRIBUTED_MARGIN` — primary passes but the attribution ablation
  does not. Explicitly **not** a superiority result: this is the outcome shape the
  old campaign wrongly reported as one.
- `P1_R6_DR1_NOT_SUPPORTED` — primary does not pass.

No terminal of this campaign promotes any claim, edits `src/orion/registry.py`, or
grants adoption/promotion/merge authority. Every native row must report
`grants_*_authority == false`.

## 9. What a null result means here

If `ORION_NATIVE_ARD_DR1` shows no gain over B3, or shows a gain that the ablation
cannot attribute to the ARD mechanism, that is a **real negative** of this campaign
and is reported as one. The repair being made is to reachability of `DIAGNOSE`, and
a repair that makes a mechanism runnable is not a prediction that the mechanism
works. Nothing in sections 2–8 is revisited after an outcome is read; if the design
turns out to be wrong, the successor campaign says so under its own freeze.

## 10. Receipt

One receipt, `P1_R6_DR1_RECEIPT_V1.json`, schema `P1U.NativeOrionDR1Result.v1`,
carrying its own `campaign_id`, the digest of this freeze document, every per-arm
row, the operator-coverage report for every native root run, and a
`orion.transfer.v2.canonical.content_digest` over the whole payload.
