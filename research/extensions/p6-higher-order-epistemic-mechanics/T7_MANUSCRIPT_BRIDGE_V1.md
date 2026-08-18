# Higher-order epistemic mechanics T7 — control-composition manuscript bridge

**Status:** additive successor theory only. This file does not alter the frozen P6 V2.1 peer-review paper and does not create a new scientific result.

## 1. From isolated mechanics to a control relation

T1–T6 separately formalize claim-relative revision locality, responsibility, interface adequacy, computation allocation, validity containment, and social-evidence dependence. T7 asks a narrower question: **given already-bound reports from those mechanics, what class of next step may Self-ORION recommend without laundering any of the component signals into scientific authority?**

The executable object is `SelfOrionEpistemicControlDecision.v1` in `src/orion/self_orion/epistemic_control.py`.

It is intentionally a read-only composition layer. It cannot execute a tool, mutate an epistemic coordinate, adopt a candidate revision, promote a claim, merge code, or close a global research task.

## 2. Bounded precedence relation

For a declared claim `C`, let

- `R_C` be the T2/T3 revision-gate report;
- `G_C` be the T4 computation-selection report;
- `V_C` be an optional T5 containment report;
- `S_C` be a set of optional T6 social-independence reports.

T7 defines a deterministic next-step map

```text
Control_C(R_C, G_C, V_C, S_C) -> D_C
```

with the following bounded precedence:

1. **Hard computation obligations first.** If a protected verification or other registered hard computation obligation remains active, it is non-compensatory. An already-selectable revision cannot bypass it.
2. **Required independent social evidence next.** If a caller has registered independent corroboration as a hard condition, correlated, unresolved, unreliable, or absent reports do not satisfy it.
3. **Validity containment next.** A blocked context yields `CONTAINED`; an unresolved context stays `UNRESOLVED`. Containment restricts use and does not establish truth.
4. **Already-selectable bounded revision next.** A unique revision candidate beats optional positive-value computation. Multiple minimal revisions remain `REVISION_AMBIGUOUS`.
5. **Optional computation only when revision is not yet selectable.** Positive-net diagnostic/retrieval/planning work may be recommended to gather discriminating evidence.
6. **Residual fail-closed terminals.** `LOCAL_COMPUTATION_STOP` means only that no registered local optional computation has positive bounded value. It never grants global task closure or scientific impossibility.

This relation is not claimed to be universally optimal. It is the smallest deterministic composition needed to expose authority-laundering and precedence countermodels.

## 3. Why optional computation does not always come first

A naive metareasoning controller might continue to retrieve, plan, or invoke an LLM whenever the expected value is positive. T7 deliberately rejects that as a universal rule. If a bounded revision is already uniquely admissible and no hard obligation or validity/social condition blocks it, optional extra computation cannot indefinitely defer the candidate merely because its scalar value estimate is large.

Conversely, a hard verification obligation outranks the revision even when the verification action has negative scalar net value. This preserves the programme's non-compensatory authority semantics.

## 4. Local stopping is not scientific closure

The T4 terminal `LOCAL_COMPUTATION_STOP` is especially dangerous if interpreted too broadly. T7 preserves the distinction:

```text
no positive value among registered local computation actions
!=
no useful experiment exists
!=
claim is false
!=
research task is complete.
```

Accordingly every T7 receipt fixes `grants_global_task_stop_authority = false`.

## 5. Frozen composition countermodels

`T7_COUNTERMODELS_V1.json` binds ten deterministic cases:

1. mandatory verification preempts an already-selectable revision;
2. an already-selectable bounded revision preempts optional high-value computation;
3. unresolved responsibility can route to an optional discriminator;
4. invalid validity context produces containment;
5. unresolved validity context fails closed;
6. correlated reports fail a registered independent-evidence requirement;
7. bounded-independent reports allow the revision path to continue;
8. multiple minimal revisions remain ambiguous;
9. local computation stop does not become global task stop;
10. no admissible computation plus no admissible revision yields a bounded no-action terminal.

The deterministic summary terminal is `T7_CONTROL_COMPOSITION_GREEN` only when all ten outcomes replay exactly and every authority flag remains false.

## 6. What T7 establishes

A green T7 finite panel establishes only that the implementation has the declared precedence and non-authority behavior on the frozen cases. It does not establish:

- that this precedence is optimal in open-ended science;
- that the expected-value estimates are calibrated;
- that registered social provenance captures all dependence;
- that validity envelopes are complete;
- that responsibility diagnoses are correct;
- that using T7 improves Self-ORION development outcomes;
- novelty over rational metareasoning, safe control, belief revision, workflow/effect systems, or multi-agent epistemic frameworks.

Those require nearest-work adjudication and the prospective T8/#455 experiment.

## 7. Paper consequences

### P5 / Self-ORION
T7 supplies the executable V3 control substrate for the future cause-confusable experiment. It may be described as an implemented governance contract, not as evidence for H1–H4. The historical 21/24 attribution result and its three errors remain unchanged.

### P6
P6 successor theory can study whether the precedence relation admits a smaller algebraic characterization and whether composition preserves non-authority and locality. The frozen P6 V2.1 submission remains untouched.

### P3
The scoped P3 public-reference paper is now merged and peer-review ready on the bounded P3.C5/P3.C9 track. T7 does not modify that package. Future P3 successor work could provide reconstruction/preservation witnesses for representation-level revisions.

### P4/P8
T7 consumes their authority boundary conceptually: recommendation and admissibility remain upstream of protected host disposition. It does not replace their verification/authority semantics.

### P1/P2/P7/P9/P10
Only successor research may consume T7. Current ready/frozen submission claims are not broadened by this bridge, and learned proposal/ranking systems never gain formal authority from the control decision.

## 8. Next tranche

T8 should prospectively freeze and implement the empirical discriminator under #455. It must compare revision-level control against strong parents, include evidence permutation/no-feedback controls, preserve negative/null outcomes, and keep the experiment/result authority outside the T7 controller.
