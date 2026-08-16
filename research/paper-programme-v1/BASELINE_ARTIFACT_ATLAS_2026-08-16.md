# Publication baseline artifact atlas — 2026-08-16

This ledger distinguishes **nearest-work papers** from **runnable/public implementation artifacts**. A paper can be scientifically mandatory as a comparison even when no faithful public implementation is available; conversely, pinning a repository commit does not make it an execution baseline until the exact configuration, dependencies, model/provider/tool identities and resource budget are frozen in the publication run manifest.

The pins below are reference points for reproducibility and implementation study. They are not evidence that ORION has run or beaten these systems.

| Paper | Baseline / asset | Frozen public reference | Artifact role | Execution status |
|---|---|---|---|---|
| P1 | SciAgentArena | `HelloWorldLTY/SciAgentArena@9865bb0c261bd9a59ef23576805b268b458b59d2` | realistic scientific-agent task/evaluation substrate | reference pinned; final ORION-compatible task/config binding UNBOUND |
| P1 | AREX | paper/specification | recursive audit + targeted follow-up baseline | protocol reimplementation required unless a faithful runnable release is identified before execution freeze |
| P1 | SCION scientific workflow | paper/specification | dependency-aware staged research execution baseline | protocol reimplementation required unless a faithful runnable release is identified; do not confuse with unrelated repositories named `scion` |
| P1 | Iris | paper/specification | revisable information-state / epistemic-action baseline | protocol reimplementation required unless a faithful runnable release is identified |
| P2 | AutoResearchBench code/evaluator | `CherYou/AutoResearchBench@a46c9bfb8968786f73f0a6a5b365b5384cd0f96d` | Deep/Wide benchmark inference/evaluation reference | code pinned; released benchmark bundle must still be separately content-hashed at execution freeze |
| P2 | AutoResearchBench released data repo | `Lk123/AutoResearchBench` | obfuscated released benchmark bundle | repository/license identified; exact downloaded/decrypted bundle content hash UNBOUND |
| P2 | SAGE benchmark | `HughieHu/Sage@bc62257a13d81ae233ecbd508037614746d2776b` | scientific retrieval benchmark with short-form exact-match and open-ended weighted-recall tasks | public benchmark revision pinned; exact local dataset/split hash and evaluation config UNBOUND |
| P2 | MetaSyn | `THUIR/MetaSyn@51b95b7061e1faf241c205eb7f8e5c2bccff4848` | systematic-review/meta-analysis retrieval, screening and synthesis benchmark/baselines | public code/data/config reference pinned; exact chosen corpus/split/config hashes UNBOUND |
| P2 | AgentSLR | `OxRML/AgentSLR@3111fcf456c6fbcba768dfdce2bd2934d8cb5cef` | protocol-driven systematic-literature-review agent baseline | runnable public harness reference pinned; exact task/resource/model config UNBOUND |
| P3 | MUSE | `cohentsofia/MUSE@f7a40317db46145d0c90b221311d8324db5da1b9` | source-grounded cross-domain scientific problem/solution/rationale representation | public reference pinned; P3 gold source sample and evaluation config remain independent/UNBOUND |
| P4 | ProvenanceGuard / attribution / auditability systems | paper/specification unless an exact runnable release is separately registered | source-aware verification / auditability baselines | implementation/config discovery remains part of execution freeze; do not substitute a weak homemade baseline if a faithful release becomes available |
| P5 | Darwin Gödel Machine | `jennyzzt/dgm@a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2` | self-code modification + archive + empirical validation baseline | public implementation pinned; exact subject/task/model/sandbox/resource config UNBOUND |
| P5 | PAST-Bench | `Gen-Verse/PAST-Bench@f8223517ae7491e776b69793d9f11e9d074ab42e` | experience-on/off / pathway-sensitive transfer evaluation reference | public reference pinned; exact P5 mapping/split/config UNBOUND |
| P5 | ADAS / ADIAS / SAGE-MHFA / CausalFlow | paper/specification or future exact release | automated agent design, issue-centric improvement, failure attribution and counterfactual repair baselines | runnable release/config must be registered if used; otherwise implement a protocol-matched baseline and declare the fidelity limitation |

## Baseline-admissibility rule

Before `EXECUTION_FROZEN`, each headline baseline receives one of:

- `UPSTREAM_PINNED`: exact public repository/artifact revision plus exact execution config is frozen;
- `PROTOCOL_REIMPLEMENTED`: the paper/specification is implemented locally from a frozen written protocol because upstream runnable code is unavailable; fidelity differences are documented before outcomes;
- `NOT_EXECUTABLE_WITH_JUSTIFICATION`: a scientifically relevant nearest-work comparison cannot be executed under a fair/legal/reproducible setup, so the paper provides mechanism-level comparison but does not pretend to have empirical head-to-head evidence.

A missing upstream release is never a reason to compare only against weak straw men. If the nearest work cannot be run, the limitation and the strongest feasible protocol-matched replacement must be explicit.

## What is still required at execution freeze

A reference pin is only the first layer. The run manifest must additionally bind:

- exact baseline configuration/prompt/controller hash;
- dependency/environment identity;
- model/provider/tool/search backend versions;
- data and split content hashes;
- seeds and resource limits;
- evaluator/metric hash;
- any adaptation layer needed to place the baseline on the same task interface.

If a public upstream repository changes after this ledger, the final run remains bound to its exact registered commit rather than silently following `main`.
