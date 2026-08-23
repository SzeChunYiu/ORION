# ORION-Q Research Harness V1 — development / execution protocol

Date: 2026-08-20
Parent: #679
Programme: #633
Branch: `shadow/orion-q-max-r0`
Status: FROZEN BEFORE HARNESS IMPLEMENTATION / FIRST HARNESS-DRIVEN R6 CYCLE
Authority ceiling: development + non-authorizing research-control only. The harness cannot self-authorize scientific validity, novelty, R6, merge, or programme closure.

## Development question

Can ORION-Q stop relying on an operator to manually stitch together one-off research scripts and instead run a persistent, resumable, proof-carrying research loop in which the same harness both attacks the live quantum research problem and records/repairs its own control failures?

Target loop:

`ResearchState -> native ORION diagnosis -> computation/revision selection -> registered capability execution -> evidence admission -> failure/reopen update -> next ResearchState -> protected promotion gate`

The harness is infrastructure for the MAX programme, not a new scientific result by itself.

## Atomic development fibres

H1. **State:** define one canonical cycle state carrying visible scientific evidence, hard obligations, responsibility hypotheses, interface checks, revision mechanics, computation actions, capability registry identity, protected/unopened references, authority ceiling, and history.

H2. **Native control:** build responsibility / interface / revision / computation receipts by importing the existing production `orion.transfer.v2` and `orion.self_orion` modules. No duplicate decision policy is permitted.

H3. **Capability execution:** select only a registered capability whose id is exactly the action/revision emitted by native control; run it in an isolated subprocess; bind executable hash, arguments, exit status, stdout hash and parsed receipt.

H4. **Evidence admission:** update state only through frozen extraction rules from a successful capability receipt. Raw stdout, candidate prose, and self-declared authority are not evidence.

H5. **Custody:** protected/fresh subject files remain inaccessible until a frozen gate marks them releasable. A capability cannot open a protected reference merely because it knows a path.

H6. **Failure learning:** execution, measurement, donor, interface, method-language, verification and novelty failures remain typed/scoped. A failed capability updates history and may reopen only registered coordinates.

H7. **Resume/replay:** every cycle writes canonical state/decision/execution/transition receipts; rerunning from the same state + registry must reproduce the same native decision.

H8. **Self-improvement:** a harness defect is itself recorded as a research failure with responsibility `HARNESS_*`; repairing the harness must preserve the original scientific state and cannot retroactively change a protected gate.

H9. **Authority:** no candidate, capability, harness transition, or native controller decision may set R6. Promotion remains a separate protected evaluator over frozen evidence.

H10. **Live proof:** the first integrated workload is the current ORION-Q MAX R6 chain, beginning from the already-frozen blinded N0 state and using existing donor-closure, interface-envelope, N1/N2, and candidate-blind P10 capabilities.

## Incumbent mechanics absorbed

The harness must consume rather than duplicate:

- `orion.transfer.v2.epistemic_responsibility` for claim-relative competing responsibility hypotheses;
- `orion.transfer.v2.interface_adequacy` for fail-closed interface checks;
- `orion.transfer.v2.higher_order_epistemic_mechanics` for typed non-authorizing revision mechanics and minimality;
- `orion.transfer.v2.epistemic_computation` for hard-obligation precedence and bounded computation value;
- `orion.self_orion.revision_gate` for responsibility-bound revision nomination;
- `orion.self_orion.epistemic_control` for composition of revision/computation receipts;
- `orion.programme.cycle_protocol` for the nine-step protected research-cycle semantics;
- existing ORION-Q frozen states/protocols/results as workload-specific evidence, not framework logic.

## Bounded saturation assessment

Enough of the control substrate is already merged to implement a bounded harness now: typed responsibility, interface adequacy, revision minimality, computation allocation, control composition, cycle receipt shapes, and failure epistemology already exist. The missing object is orchestration/custody/replay across those modules for a real MAX research campaign.

This is not universal research automation saturation. The harness deliberately excludes generic LLM prompting, arbitrary web browsing, generic lab automation, and universal scientific ontology from V1.

## Challenge to the saturation basis

The harness could be unnecessary or wrongly scoped if:

1. `SelfOrionDevelopmentDriver` already owns full live execution rather than only scheduling an empirical frontier;
2. `orion.programme` already contains a complete executable protected cycle runner hidden under a different vocabulary;
3. the live quantum campaign needs domain semantics that cannot be expressed by a generic capability/evidence adapter;
4. subprocess capability isolation is too weak for protected custody;
5. a research harness that can mutate its own registry creates an ungovernable self-modification path.

Search/review of current modules shows existing drivers/controllers are explicitly non-authorizing and/or do not execute a full scientific cycle; V1 therefore fills an orchestration gap while retaining their authority boundaries.

## Why prior work could have missed the right harness object

- orchestration may appear under programme execution, campaign engine, experiment runner, agent tool router, workflow DAG, or laboratory automation rather than `research harness`;
- Self-ORION modules intentionally separate recommendation from execution, so no single file advertises itself as the complete loop;
- previous ORION-Q development accreted one-off scripts because each scientific freeze was locally correct even though the global execution architecture remained manual;
- CI workflows looked like an execution layer but do not own epistemic state transitions.

## Frozen implementation hypothesis

Implement a research-only package `research/extensions/orion-q/harness/` with five information-hiding responsibilities:

1. `model.py` — canonical immutable state/registry/receipt schemas and SHA-256 sealing;
2. `native_control.py` — adapter from manifest/state into production ORION responsibility/interface/revision/computation/control modules, with no policy copy;
3. `capabilities.py` — strict subprocess executor + result-token parser + frozen evidence extraction;
4. `engine.py` — one-cycle and bounded multi-cycle transition engine; no scientific authority;
5. `io.py` — canonical JSON state/receipt persistence and replay verification.

Add a workload manifest for the current R6 campaign and a CLI `run_orion_q_research_harness.py`.

The engine may execute only capabilities registered before the cycle. It may not invent shell commands from model text or candidate output.

## First live R6 capability graph

Registered actions/revisions initially include:

- `COMPUTE:DONOR_CLOSURE_PACKET` -> existing optimistic general-m TARE donor-closure harness;
- `REV:CHANGE_INTERFACE` -> existing optimistic FOQCS interface-envelope harness;
- `REV:GROW_METHOD_LANGUAGE` -> existing candidate-blind P10 frame optimizer;
- verification/replay steps may be registered after their protocol is frozen.

The harness begins from the existing N0 evidence and drives until it reaches a frozen stop condition, missing capability, protected-boundary requirement, or non-authorizing terminal.

## RED / hostile tests frozen before implementation

1. state digest changes if any scientific evidence or authority field changes;
2. duplicate hypothesis/mechanic/action/capability ids are rejected;
3. missing required native-control discriminator keeps responsibility unresolved;
4. hard computation obligation beats an otherwise selectable revision;
5. a control-selected id absent from the registry yields `CAPABILITY_UNREGISTERED`, not an invented command;
6. registry command path must stay inside the repository and use an allowlisted interpreter;
7. capability nonzero exit cannot admit evidence;
8. missing/duplicate result token cannot admit evidence;
9. evidence extractor may read only declared receipt paths;
10. candidate-emitted `r6_authority=true` is ignored/rejected;
11. protected reference with `released=false` cannot appear in capability arguments or declared readable inputs;
12. cycle transition cannot alter success gates/protocol ids;
13. replay from same state/manifest yields the same decision digest;
14. P9/no-P10 shadow registry cannot execute `REV:GROW_METHOD_LANGUAGE`;
15. a harness defect may create a typed failure receipt but cannot change the scientific outcome bytes that exposed it;
16. no harness receipt grants scientific/novelty/merge/global-stop authority;
17. bounded loop stops rather than spinning when the next state is unchanged;
18. current R6 N0 state must select donor closure through production ORION modules;
19. post-donor N1 state must select interface change through production ORION modules;
20. post-interface N2 state must select method-language growth only after atomic donor/interface hypotheses are individually defeated.

## Reopen triggers

Reopen the harness design if:

- a production ORION module already owns an implemented responsibility and the harness duplicates it;
- capability execution can mutate protected state outside declared transition rules;
- evidence admission cannot bind source/result hashes;
- a live R6 failure cannot be represented without quantum-specific engine logic;
- the harness needs to edit its own policy code during a scientific cycle;
- a hostile test shows candidate output can influence promotion authority;
- a second domain cannot use the same engine with only manifest/adapter changes.

## First harness terminal

`ORION_Q_RESEARCH_HARNESS_V1_OPERATIONAL`

Allowed only if hostile unit tests pass and the harness reproduces at least N0 -> donor closure -> N1 -> interface closure -> N2 control semantics from the frozen R6 campaign without reading the stretched-N2 protected subject.

This terminal is infrastructure only. It does not imply R6.
