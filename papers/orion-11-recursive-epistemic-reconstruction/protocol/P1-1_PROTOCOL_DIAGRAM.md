# ORION-11-1 — Protocol diagram

**Bound to:** protocol `ORION-11.hidden-formulation.v1.1`, suite PILOT `7a50a2d5…` /
TEST `21b461d8…`. Generated from the design, not from outcomes; this figure
carries no result and is publishable before the final test is run.

## What the evaluated system sees, and what it cannot

```mermaid
flowchart TB
    subgraph HOST["HOST CUSTODY — never reaches a system under test"]
        GOLD["protected_gold<br/>reframe_required · responsibility_family<br/>target_coordinates · dependencies_to_reopen<br/>root_success_rubric · dependency_depth"]
        FAM["task_family<br/>(withheld: 4 hidden-shift vs 2 control<br/>IS the answer to H2)"]
    end

    subgraph CASE["FROZEN CASE"]
        HID(["hidden cause<br/>insufficient formulation,<br/>representation, decomposition<br/>or measurement model"])
        OBS["observable trace<br/>public_prompt + observable_resources<br/>numbers, ranges, token lists,<br/>capability states, closure edges"]
        HID -.->|"manifests as,<br/>never states"| OBS
    end

    OBS ==>|"PublicView<br/>case_id · public_prompt<br/>observable_resources · budget_class"| SUT

    subgraph SUT["SYSTEM UNDER TEST — 11 systems, matched budget"]
        direction LR
        B["5 baselines<br/>static ReAct · tree search<br/>AREX-like · SCION-like · Iris-like"]
        O["full ORION"]
        A["5 ablations<br/>no W · no M · generic retry<br/>full reset · no self-audit"]
    end

    SUT ==>|"SystemTrace<br/>reframed · responsibility_family<br/>target_coordinates · reopened<br/>root_solved · abstained · resources"| SCORE

    SCORE["metrics.py<br/>the ONLY module that reads gold"]
    GOLD ==> SCORE
    FAM ==> SCORE
    SCORE --> OUT["case records → tables"]

    style HOST fill:#fde8e8,stroke:#c0392b,stroke-width:2px
    style CASE fill:#eaf2fb,stroke:#2b6cb0
    style SUT fill:#eafaf1,stroke:#1e8449
    style SCORE fill:#fef5e7,stroke:#b7791f
```

## Protected labels

Held by the host, never in a `PublicView`, enforced by the type signature
`SystemUnderTest.run(view: PublicView, *, seed: int)` rather than by discipline —
a system cannot reach gold because it is never handed an object that carries it.

| label | why it is protected |
|---|---|
| `reframe_required` | it *is* H2; a system that knows it needs no selectivity |
| `responsibility_family` | the attribution being measured |
| `target_coordinates` | the reframe target being measured |
| `dependencies_to_reopen` | the reopen set being measured |
| `task_family` | four families are hidden-shift and two are controls, so the family name restates `reframe_required` |
| `dependency_depth` | the H4 x-axis |

## Allowed interventions

A system may read the prompt and every listed resource, compute over them,
reframe, reopen prior closures, and answer or abstain. It may not read gold,
another system's trace, the case object, or any host path.

## What makes the observable trace sufficient without stating the cause

Verified rather than asserted, on the frozen suite:

| property | evidence |
|---|---|
| the cause is *derivable* from public content | independent audit: 55 of 66 SOLVABLE, 9 PARTIAL, 2 UNSOLVABLE |
| the cause is not *stated* | gold-vocabulary checker over prompt and resources |
| no single token predicts the label | `find_lexical_separators`: **0 separators from 906 tokens** |
| no surface statistic separates families | 16 surfaces × 2 statistics × 2 labellings × 2 splits, **0 Holm rejections** |
| no *interaction* of surfaces separates them | joint-space LOO 1-NN: TEST 0.062 vs 0.167 baseline, p=0.97 |
| no shape-only responder beats chance | kind-histogram 1-NN: 0.106 / 0.056 / 0.167 vs 0.167 baseline |
| the panel is not degenerate | `probe_records` CLEAN, pooled and per split |

## Declared limitations, carried in the figure rather than hidden below it

- A residual of low-level lexical cues remains at roughly 0.10 lift
  (`comma_count`, `prompt_sentences`, `digit_density`). Two exploitable rules
  were found and removed; with 48 cases and an unbounded space of text
  statistics some statistic always separates, so the floor is published rather
  than chased.
- The reopen null is the blind largest-component policy at **0.792 PILOT /
  0.823 TEST**, not the full-reset ablation at 0.719. A reopen result between
  those numbers is graph shape, not dependency-directed reasoning.
- INTERFACE and DECOMPOSITION are not mechanically separable from public text;
  the boundary rules emit both.
