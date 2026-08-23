# P7 claim ledger V4

**Current science manuscript:** `manuscript/FINAL_V4.md`
**Historical V2 / V3:** retained
**Terminal:** `P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`

V4 changes the *authority* behind two of V3's rows — P7.V3.5 and P7.V3.7 — and
adds two: one for the incompleteness the mechanization found in P7's own rule,
and one for the reading of the donor stack under which the finite composition
rows are instances. The permitted claims of P7.V3.1–4 and P7.V3.6 are unchanged.

| ID | Permitted claim | Authority | Forbidden upgrade |
|---|---|---|---|
| P7.V4.5 | Heterogeneous closure-carrying transforms compose scientifically only under exact intermediate closure-contract binding or a registered equivalence bridge — for chains of any length, over any number of transformations, contracts, closure coordinates and obligations, and for every donor-native validity predicate. | MECHANIZED THEOREM (`formal/mechanized/P7_COMPOSITION_CALCULUS_MECHANIZED_2026-08-21.json`; Z3 over uninterpreted sorts) | Ordinary donor composability is invalid; or that the rule is exact rather than fail-closed. |
| P7.V4.7 | Exact support: 320 states, 25 minimal separations, 31 nonclosure countermodels, 155 full refinements, 1,055 partial failures, 25 successful compositions, 25 bridge countermodels, zero donor/ideal-product violations. | DETERMINISTIC ARTIFACT + INDEPENDENT AUDIT | Deployed-agent performance or population inference. **Additionally forbidden from V4:** reading any of these counts as independent facts. Neither `carries` nor `compose` takes a donor argument, so every count under a donor loop is repeated by it: 320 is 64 counted five times, 25 minimal separations is 5 counted five times, 155 and 1,055 are 31 and 211 counted five times, and 25 successes and 25 bridge countermodels are one of each counted once per ordered donor pair. Only the 31 nonclosure countermodels are 31 distinct facts, and the `donor_axis` block of the result artifact carries the table. The 25 successes discriminate no reading of the donor stack at all. The 25 bridge countermodels are exactly one frame condition — that no family's target contract is any family's source contract — and two readings that collapse the stack to one and to five distinct hand-offs reproduce both composition counts exactly. |
| P7.V4.8 | P7's composition rule is **sound but incomplete** against P7's own obligation semantics: matching intermediate contracts suffice for obligation totality to compose but are not necessary, the exact condition being containment of the second leg's source demands in the first leg's target demands. | MECHANIZED THEOREM (same artifact; `MATCH_IS_NOT_NECESSARY`, `CONTAINMENT_IS_THE_EXACT_CONDITION`) | That P7's rule characterises closure composition, or that refusals it issues are always correct refusals. |
| P7.V4.9 | The five registered donor families are interpretable as a transformation family in that calculus — each with its own source and target obligation contracts, so the intermediate-contract test is computed from the pair rather than supplied — and under three stated frame conditions the published composition rows are ground instances of theorems that hold for a donor stack of any size. The same theorems cover the compositions in which a leg fails to carry; the published enumeration contains none of those. | MECHANIZED THEOREM (`formal/mechanized/P7_DONOR_STACK_AS_TRANSFORMATION_FAMILY_2026-08-22.json`) | That the interpretation has been checked by anyone outside the producing lane. |

## Allowed headline

> P7 provides closure-carrying scientific navigation: mature planning/refinement,
> counterexample-guided reopening, representation migration, replanning and
> terminal-commitment mechanisms remain reusable donor transforms, while
> task-global closure is explicitly transported, selectively refined and composed
> through typed obligation bridges — with the composition and unit laws proved
> over uninterpreted sorts rather than enumerated, and the composition rule
> sound but not complete against its own obligation semantics.

## Boundary

No universal completeness, deployed-agent superiority, universal minimality of
the five closure coordinates, or inherent centralization advantage. No empirical
or pipeline claim of any kind: no naturalistic multi-stage corpus exists. No
independent formal or empirical reproduction has been arranged; the calculus, the
interpretation and their tests were written in the same lane.
