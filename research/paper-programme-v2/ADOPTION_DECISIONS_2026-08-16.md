# V2 Adoption Decisions — 2026-08-16

Source implementation: PR #149, merge `a452b41c7f326f9d0d3424567c2ef408c6a54e8e`.

The decision standard is intentionally hostile: a useful implementation is not automatically a publishable novelty. Each mechanism is admitted only if its incremental scientific question survives nearest-work contraction and can be falsified prospectively against the frozen V1 system.

| Paper | Decision | Incremental mechanism | Claim boundary |
|---|---|---|---|
| P1 | **ADOPT** | responsibility diagnosability + active discriminator + scoped epistemic licensing | active diagnosis itself is prior art |
| P2 | **ADAPT** | conservative censored route allocation composed with P2 route/task semantics | conservative/safe bandits are prior art |
| P3 | **ADOPT** | typed scientific round-trip + cycle consistency routed to GLUE/OBSTRUCTION/CANNOT_CHECK | lenses/cycle consistency/transportability/obstruction are not standalone novelty |
| P4 | **ADAPT** | protected defeater-directed evidence acquisition | helper only; never an authority source |
| P5 | **ADOPT** | non-compensatory STATIC→REPLAY→FRESH→PROTECTED gate + retained negative history + host-only recommendation | anytime-valid acceptance is prior art |

## Why no `REJECT`

All five mechanics passed the local hostile implementation gate in PR #149, and each exposes a falsifiable incremental question that is materially distinct from merely adding software complexity. That is sufficient for a **prospective study**, not for paper adoption.

## Why no V1 mutation

V1 protocols are historical scientific objects. A V2 result cannot erase or rewrite them. The direct V1-vs-V2 comparator in every protocol is mandatory: extra complexity must earn value over the frozen incumbent rather than being credited because it was added later.

## Paper-level decision rule

A V2 mechanism may enter the corresponding abstract/conclusion only if:

1. the new protocol was prospectively execution-frozen;
2. the primary incremental margin passes;
3. every safety/non-inferiority guard passes;
4. mechanism ablations identify the claimed incremental component;
5. nearest-work is rerun before execution freeze and within 14 days of submission.

Otherwise keep V2 as infrastructure, negative evidence, or future work.
