# P9 closure matrix V1

Purpose: make `finish Paper 9` a set of evidence-bound terminals, not a prose milestone. Every P9-relevant issue closes only after the evidence named here exists. A speculative branch may close as **narrowed/deferred/not load-bearing** when the final supported paper scope no longer requires it; it must not be mislabeled `SUPPORTED`.

## Already terminal

| Issue | Terminal | Evidence |
|---|---|---|
| #469 donor saturation | `P9_NEURAL_DONOR_SATURATION_REACHED` | merged PR #520, rounds 7–8 no material change, novelty preflight, reopen triggers |

## Result-bearing gates

| Issue | Closing evidence | Allowed terminal(s) |
|---|---|---|
| #486 M1 | official exact-head M1 JSON + review-clean CI + archived receipt | `M1_SIMPLE_MODELS_SUFFICIENT_FOR_CURRENT_EXACT_WORLDS`, `M1_NONLINEAR_RELATIONAL_RESIDUAL`, `M1_GLOBAL_COMPOSITION_RESIDUAL`, `M1_HISTORY_OR_BINDING_RESIDUAL`, `M1_SAMPLE_EFFICIENCY_RESIDUAL`, `M1_LEAKAGE_OR_EVALUATOR_FAILURE`, `CANNOT_CHECK` |
| #478 A5 | official payload-only A5 result + independent replay | `EXPLICIT_INFERENCE_SUFFICIENT` for D0 transport, narrower/fail, or `CANNOT_CHECK` |
| #475 A2 | official M1 + A2/A4 payload-only result; any surviving mechanic-learning residual explicitly identified | bounded simple/explicit operator sufficient, residual routed, or `CANNOT_CHECK` |
| #477 A4 | official M1 + A2/A4 payload-only result; no false claim beyond admitted D0 history | bounded failure-history explicit inference sufficient, residual routed, or `CANNOT_CHECK` |
| #479 A6 | D0 exact corpus + D1 exact whole-domain dataset + contamination audit; natural-paper gold not fabricated | `EXACT_TRACE_DATA_ONLY`, `NARROW_COORDINATE_SET_ONLY`, `NATURAL_STRUCTURE_GOLD_SUPPORTED` only if actually built, or `CANNOT_CHECK` |

## Representation / computation atoms

| Issue | Closure rule |
|---|---|
| #474 A1 Representation | Close after M1/A5/D1 decide whether any typed-graph/sheaf/higher-order architecture is load-bearing. If simple typed coordinate comparison + explicit inference exhausts the bounded claim, terminal is `TYPED_EXPLICIT_STRUCTURE_SUFFICIENT_FOR_BOUNDED_SCOPE`; richer branches become not load-bearing, not experimentally refuted in general. |
| #476 A3 Latent | If no final P9 residual requires recurrent/anonymous latent computation after M1/A5/D1, close `NOT_LOAD_BEARING_FOR_FINAL_P9_SCOPE`; preserve Coconut/recurrent donor analysis for P10. Do not claim anonymous latent sufficiency without a direct test. |
| #484 A9 Binding | If final P9 benchmark contains no variable-role binding task, close `DEFERRED_TO_P10_OR_SUCCESSOR_NOT_LOAD_BEARING`; preserve NPS/Transformer-binding donor analysis. If final claim requires binding, reopen with the exact A9 benchmark before manuscript freeze. |
| #485 A10 Causal | If final P9 claim is observational/exact structural transfer only, close `DEFERRED_CAUSAL_MECHANISM_RESEARCH_NOT_LOAD_BEARING`; preserve MWM/causal donor analysis. No causal result may be implied. |

## Scale / learning-law atoms

| Issue | Closure rule |
|---|---|
| #480 A7 Scale | Use exact information ceilings + M1 preregistered train-size curves/resource accounting. If final paper makes no asymptotic scaling claim, terminal is `BOUNDED_SAMPLE_RESOURCE_ANALYSIS_ONLY`; do not require billion-scale GraphBFF reproduction merely to close a bounded paper. |
| #482 A8 Learning law | If M1 classical/simple + explicit inference exhausts the final bounded residual, close `ADVANCED_TRAINING_NOT_LOAD_BEARING_FOR_FINAL_P9`; preserve curriculum/RL/meta-learning donor map for successor/P10. If a learned residual survives, issue remains open until the strongest native training recipe is pressure-tested. |

## Parent programme issues

### #425 Structural learning

Close only after:
1. exact data authority terminal from #479;
2. M1 diagnostic terminal;
3. D1 whole-domain/combinatorial transfer terminal;
4. final representation/computation scope from #474/#478;
5. result-independent donor saturation #469;
6. final claim ledger distinguishes learned result from explicit inference and deterministic ceilings;
7. final manuscript/technical-note disposition is known.

Allowed final states:
- `P9_BOUNDED_STRUCTURAL_LEARNING_SUPPORTED`;
- `P9_STRUCTURAL_REPRESENTATION_ONLY_NARROWED`;
- `P9_NO_INCREMENTAL_LEARNING_RESIDUAL`;
- `CANNOT_CHECK`.

### #426 Protocol refoundation

Close when the **actual final paper scope**, not the old aspirational neural scope, has:
- versioned structure/data schemas;
- frozen protocols and preserved amendments;
- immutable split/manifests;
- baseline registry;
- threat/leakage model;
- exact claim/nonclaim ledger;
- P10 exclusion manifest;
- final result identities.

Allowed terminal: `P9_FINAL_BOUNDED_PROTOCOL_FROZEN` or `NO_STANDALONE_PROTOCOL_RESIDUAL`.

### #428 Model/execution

Close after the escalation ladder terminates honestly:
- if simple models + exact inference are sufficient, terminal is `P9_NEURAL_ESCALATION_NOT_JUSTIFIED`;
- if a real residual survives and a neural donor-complete branch is run, use its supported/narrowed/refuted terminal;
- no neural code is required merely to satisfy the issue title.

### #391 Paper parent

Final closing sequence:
1. all P9-specific child issues reach honest terminals;
2. merged immutable result archives and completion receipts;
3. #283 P9 independent verification receipt (`VERIFIED`/`BOUNDED_VERIFIED`/`INVALIDATED`/`CANNOT_CHECK`);
4. #287 current novelty disposition;
5. manuscript decision:
   - standalone peer-review package, or
   - technical benchmark note, or
   - merge/no-standalone disposition;
6. references/results/claims reconciled;
7. reproduction audit and final PDF if standalone;
8. parent issue body replaced with the exact final scope and all historical aspirational claims explicitly retired.

Possible final terminals:
- `P9_PEER_REVIEW_READY_BOUNDED`;
- `P9_TECHNICAL_BENCHMARK_NOTE_ONLY`;
- `MERGE_P9_INTO_PROGRAMME`;
- `NO_STANDALONE_RESIDUAL`;
- `INVALIDATED`;
- `CANNOT_CHECK`.

## Programme-wide issues not to close from P9

- #283 independent verification is programme-wide: P9 adds a verification receipt/comment; do **not** close the global issue unless all papers are done.
- #287 novelty authority is programme-wide: P9 adds its novelty disposition; do **not** close globally.
- #318/#454 donor/mechanism assimilation are shared programme services; P9 may add receipts/comments but does not close them unless their own global terminals are satisfied.

## Final scope discipline

Closing an unused research branch as `NOT_LOAD_BEARING` or `DEFERRED` is a completed scientific decision, not abandonment. The final P9 manuscript is prohibited from implying experimental support for deferred latent, binding, causal, advanced-training, or natural-science claims.
