# ORION-04 information-parity and artifact map V2

**Purpose:** close ORION-04 mock-review items E1/E2/E5/E6 and expose the evidence chain without inflating the scientific claim.

## 1. Information-parity definition

For ORION-04, a comparison satisfies **information parity** when:

1. candidate and comparator operate on the same frozen world realization;
2. they receive the same candidate-visible primitive facts and protected outcome boundary;
3. they operate under the same registered resource/budget envelope where the protocol calls for matched resources;
4. the only load-bearing difference is the registered representation/type/scope field or the decision rule that consumes the same facts;
5. oracle arms, when present, are diagnostic ceilings and are never treated as matched competitors.

Information parity does **not** mean two methods have identical internal computation. It means the paper does not award the typed method extra ground-truth facts while claiming a representation effect.

## 2. What is supplied versus learned

The six primary studies generally **supply** the relevant type/scope distinction through the frozen world definition. They test whether exposing and using that distinction changes the downstream decision.

They do not generally establish:

- that a natural research agent can infer the correct type/scope from raw text or logs;
- that the supplied type system is universally scientifically correct;
- that the same distinction is prevalent in deployed scientific workflows.

This boundary must appear in the Introduction, shared Methods, Synthesis and Limitations.

## 3. Per-study parity table

| Study | Same primitive facts supplied to non-oracle arms | Registered difference | Matched resource rule | Hostile validity condition | Result authority |
|---|---|---|---|---|---|
| N4-A unknown feasibility | graph, known edge outcomes, edge types, costs, declared type-conditional generator rates | `ORION_TYPED_VOI` uses type-conditioned priors; isolation arm uses uniform prior inside identical VOI machinery | same probe/commit problem | blind optimism must be punished | exact-synthetic bounded |
| N4-B stale receipts | receipt history, context-coordinate changes, same edge/world state | receipt scope determines which coordinate changes reopen the failure; unscoped control reacts to any change | same round/action structure | always/unscoped reopen must fail in `REOPEN_WASTEFUL` | exact-synthetic bounded |
| N4-C interval Pareto | same interval-valued edges, scalarization weight, verification budget | targeting uses decision/dominance participation versus random or endpoint policies | identical `B=4` verification budget | ambiguity/non-degeneracy gate must hold | exact-synthetic bounded |
| N4-D chain transport | identical serialized hop chain, labels, tier data, hashes/receipts | full-chain composition versus label/summary/last-hop checks | same chain input | deep splices must evade weaker local checks while honest-chain FPR remains acceptable | exact-synthetic bounded; non-cryptographic |
| N4-E active experiments | same unknown facts, entropy, costs, stopping rule | probe score is decision-coupled versus pure information gain/other selectors | same probe/stopping framework | max-entropy decoys must attract pure IG | exact-synthetic bounded |
| N4-F3 remint transport | same representation edit, receipt state, invalidation facts/costs | typed invalidation decides carry/remint versus naive carry or matched re-derive | registered matched remint/rederive budget | `REMINT_UNNECESSARY` must produce no spurious typed advantage | exact-synthetic bounded |
| N1-C donor boundary | same typed failure facts | candidate scoped state versus unscoped ablation; ideal VOI donor gets same typed facts | registered verifier budget | donor exact tie is admissible | bounded state-value positive; policy novelty absorbed |
| N2-F5B donor boundary | same frozen world/predictor inputs per registered comparison | candidate predictor versus model-selection donor | protocol matched | original-world donor tie is admissible | original residual absorbed; misspecified-world edge only |

## 4. Descriptive versus inferential reporting

Default rule:

> Unless a protocol explicitly defines an inferential unit and uncertainty procedure, N4 means/rates are **descriptive properties of frozen generated episodes**, not estimates of a natural-population parameter.

Specific notes:

- N4-A..F3: report exact frozen denominators, means/rates and protocol seed; do not create new p-values/CIs post hoc merely because episode counts are large.
- N4-D: always report `200 laundering / 200 honest` adjacent to recall/FPR `1.000/0.000` in the abstract/table/caption.
- N1-C: the registered paired bootstrap interval `[0.0248, 0.02955]` may be reported as the protocol's bounded uncertainty result; do not generalize its inferential unit to the N4 worlds.
- Exact ties such as N4-F3 `REMINT_UNNECESSARY = 11.809659685355605` remain exact first-right-of-refusal evidence and should not be rounded into a near-tie claim.

## 5. Reviewer-visible artifact map

| Family | Protocol | Result receipt | Runner / implementation | Replay / authority anchor | Manuscript role |
|---|---|---|---|---|---|
| N4-A | `development/orion-q-nlane-closure/N4_A_UNKNOWN_VOI_PROTOCOL.md` | `research/extensions/orion-q/nlanes/N4_A_UNKNOWN_VOI_RESULTS.json` | N4-A runner under `research/extensions/orion-q/nlanes/` | `development/orion-q-nlane-closure/REPLAY_VERIFICATION_LEDGER.md` | typed prior/probing |
| N4-B | `.../N4_B_STALE_RECEIPT_REOPENING_PROTOCOL.md` | `.../N4_B_STALE_RECEIPT_REOPENING_RESULTS.json` | N4-B runner | replay ledger | scope/reopening |
| N4-C | `.../N4_C_INTERVAL_PARETO_PROTOCOL.md` | `.../N4_C_INTERVAL_PARETO_RESULTS.json` | N4-C runner | replay ledger; disclosed pre-outcome tie-break code repair in closure assessment | verification targeting |
| N4-D | `.../N4_D_LAUNDERING_DETECTION_PROTOCOL.md` | `.../N4_D_LAUNDERING_DETECTION_RESULTS.json` | N4-D runner | replay ledger | chain transport |
| N4-E | `.../N4_E_ACTIVE_EXPERIMENTS_PROTOCOL.md` | `.../N4_E_ACTIVE_EXPERIMENTS_RESULTS.json` | N4-E runner | replay ledger | decision-coupled probing |
| N4-F3 | `.../N4_F3_REMINT_TRANSPORT_PROTOCOL.md` | `.../N4_F3_REMINT_TRANSPORT_RESULTS.json` | N4-F3 runner | claim ledger records fresh double replay during manuscript preparation | remint/transport |
| N1-C | `development/orion-q-nlane-closure/N1_C_PROTOCOL.md` | `research/extensions/orion-q/nlanes/N1_C_COSTLY_VERIFICATION_RESULTS.json` | N1-C runner | replay ledger | donor-absorption/state-value boundary |
| N2-F5B | `development/orion-q-nlane-closure/N2_F5B_DONOR_COMPARISON_PROTOCOL.md` | `research/extensions/orion-q/nlanes/N2_F5B_DONOR_COMPARISON_RESULTS.json` | N2-F5B runner | replay ledger / closure assessment | donor absorption + misspecification edge |

Path ellipses in this reviewer guide are shorthand only; the final submission manifest must contain the exact repository-relative strings and content digests.

## 6. ORION-23 internal ownership boundary

ORION-04 uses **downstream responsibility** as an organizing variable for mechanism-isolation experiments: probe, reopen, verify, transport, select experiment, remint/reuse.

ORION-04 does **not** claim a general theory that a state certificate should name its supported downstream responsibility. The general responsibility-scoped sufficiency/authority theory and responsibility-carrying-state object are owned by ORION-23. ORION-04's contribution is bounded exact-synthetic evidence that different downstream decisions can require different typed/scope distinctions.

Recommended ORION-04 wording:

> We use “responsibility” descriptively for the decision consuming state. General responsibility-carrying-state authority is developed separately in ORION-23 and is not claimed here.

## 7. Required manuscript insertions before second review

1. Shared Methods: information-parity definition.
2. Introduction/Synthesis: supplied-rule versus learned-rule boundary.
3. Results/captions: descriptive/inferential reporting rule and exact denominators.
4. Related Work/Discussion: ORION-23 internal ownership sentence.
5. Reproducibility: exact artifact map generated from the final publication cut.