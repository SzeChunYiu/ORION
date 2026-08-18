# T4–T6 successor manuscript bridge — computation, containment, social evidence

**Status:** additive successor theory/framework material. It does not alter the frozen P6 V2.1 peer-review package and does not create a paper-level scientific terminal.

## Computation is an epistemic action, not hidden implementation effort

`EpistemicComputationAction.v1` makes a bounded internal/inquiry action explicit through a claim identity, caller-declared action kind, expected decision value, declared cost, hard applicability requirements, obligations it can discharge, and required authority domains.

The selection rule deliberately separates **scheduling value** from **scientific authority**. When a hard obligation is active, eligible actions capable of discharging that obligation take precedence over optional actions even if their scalar net value is lower or negative. This captures cases such as protected verification that remains mandatory despite being expensive. Without active hard obligations, positive net value may choose a computation action; equal maxima remain plural; if every eligible optional action has non-positive net value, local computation stops.

This is a finite one-step metareasoning contract, not a claim of optimal computation allocation. Sequential information gathering, risk-sensitive value, deadlines and learned calibration remain open.

## Containment is not model repair

`EpistemicValidityEnvelope.v1` assigns caller-declared contexts one of `SUPPORTED / INVALID / UNRESOLVED` for a bound subject and claim. A successor envelope may point to its parent's digest; the parent is not overwritten.

`EpistemicContainmentReport.v1` maps a requested context to:

- `IN_SCOPE` when the registered context is supported;
- `BLOCKED` when the registered context is invalid;
- `UNRESOLVED` when the context is unresolved or not registered.

The report hard-codes:

```text
establishes_model_correctness = false
grants_scientific_authority = false
rewrites_model = false
```

Thus uncertainty can restrict the admissible action/claim region without forcing model-class expansion, representation change or method invention. The current discrete context model is only a bounded countermodel substrate; continuous or probabilistic validity regions may supersede it.

## Different agents do not imply independent evidence

`SocialEvidenceRecord.v1` binds agent/report/claim identity, direct observations, upstream sources and a bounded truthfulness state. The independence report distinguishes:

- `INDEPENDENT` — disjoint registered direct observations and upstream provenance with satisfied truthfulness evidence;
- `CORRELATED` — shared direct observation, shared upstream source or repeated agent identity;
- `UNRESOLVED` — missing provenance basis or unresolved truthfulness;
- `UNRELIABLE` — violated truthfulness requirement.

`INDEPENDENT` is deliberately bounded to the registered provenance graph; it is not a global proof of epistemic independence. In particular, different model/process identifiers do not by themselves increase independent evidence weight.

## Hidden contribution remains a scientific uncertainty

`SocialContribution.v1` records registered contributors as `OBSERVED / ABSENT / UNRESOLVED`. The bounded credit report returns:

- `EXCLUSIVE_SUPPORTED` only when exactly one registered contributor is observed and every other registered contributor is absent;
- `SHARED` when multiple contributors are observed;
- `UNRESOLVED` when any plausible registered contribution remains unresolved;
- `NONE_OBSERVED` when no registered contributor is observed.

This protects failure-learning and verification analyses from silently attributing success to the visible candidate when a hidden collaborator or intervention may have mattered. It is not publication authorship authority or a complete causal-inference procedure.

## Countermodel surface

`T4_T6_COUNTERMODELS_V1.json` binds sixteen finite cases:

1. mandatory protected verification before high-value optional compute;
2. uncovered hard obligation blocks optional substitution;
3. unresolved only route to a hard obligation stays unresolved;
4. equal positive-net actions remain multiple optima;
5. non-positive optional compute stops locally;
6–9. supported/invalid/unresolved/unregistered containment contexts;
10–13. correlated/independent/unresolved/unreliable social evidence;
14–16. unresolved/shared/bounded-exclusive contribution credit.

The frozen formal terminal is `T4_T6_FORMAL_COUNTERMODELS_GREEN`. It grants neither scientific authority nor Self-ORION adoption.

## Relationship to T1–T3

The current successor sequence is now:

```text
T2 responsibility state
-> T3 interface adequacy
-> T4 computation/inquiry choice
-> T5 validity containment where relevant
-> T1 minimal revision candidate
-> later replay/fresh/protected authority
```

T6 social evidence can contribute evidence to responsibility, interface, verification or contribution state only after provenance/reliability checks. **This composition is not yet wired as one autonomous runtime controller.** That is the T7 task and must preserve all fail-closed boundaries.

## Paper consequences

### P1/P2/P3/P7
Future successor studies may map retrieval/diagnostic/search/wait/representation actions into T4 or containment contexts, but current positive/ready paper claims are unchanged.

### P4/P8
Protected verification/authority can create hard computation obligations; positive expected utility cannot waive them. Social independence or containment never substitutes for P4/P8 authority.

### P5
The working paper may state that the formal substrate exists. It may not claim improved computation efficiency, safer containment, better multi-agent verification, lower harmful transfer or Self-ORION V3 benefit until prospective experiments execute.

### P6
#463 owns the successor mathematical correspondence. Rational metareasoning, safe-control validity regions, social learning and mechanism-design ingredients remain donor-owned unless a narrower cross-coordinate residual survives #287.

### P9/P10 successors
Learned models may estimate compute values, validity regions, social dependence or contributor likelihoods. Their scores cannot self-authorize the formal terminal, scientific truth, novelty or adoption.

## Next obligations

- T7 executable composition with hostile cycles/authority attacks;
- richer parent-formalism pressure for rational metareasoning and validity regions;
- social-evidence causal/provenance graph pressure beyond shared-ID overlap;
- prospective #455 test with matched compute budgets and strong M-open/world-model/objective-evolution parents;
- independent #283 verification of any future positive.
