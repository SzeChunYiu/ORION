# P7 submission saturation closure

Date: 2026-08-19  
Normative paper: V2 / AIJ submission object.

## One-sentence contribution

> P7 formalizes when open-world scientific navigation may stop locally, when task completion remains undecidable because admissible completions disagree, and how evidence/closure obligations must be transported or reopened across representation/objective changes.

## Literature round B — abstraction/refinement, world models, replanning

Fresh primary-source pressure:

- 2025 situation-calculus temporally lifted abstractions prove preservation/refinement of strategies and temporally extended goals across high/low-level models. P7 therefore claims no novelty for representation transport or sound abstraction.
- 2025 sound-and-complete generalized-planning abstraction methods and 2024/2026 planning-abstraction work further establish abstraction/refinement as mature planning machinery.
- CEGAR planning literature iteratively refines abstractions when abstract plans fail, and current Cartesian-abstraction work studies both correctness and efficiency.
- WorldEvolver (arXiv:2606.30639) revises world-model context at deployment time and selectively uses predictions; representation/world-model revision is therefore donor territory.
- *Ask the World Before Acting* (arXiv:2606.31422) explicitly treats environment probing as a scarce calibration action for structured beliefs; evidence acquisition before action is donor territory.
- 2026 numeric pattern-database work documents that abstraction can be expensive/uninformative, complementing the already mandatory P7 negative literature that abstraction can make search worse without the right refinement guarantees.

None of these results equates a soundly transported plan/representation with preservation of **scientific closure obligations**, nor do they make route-local exhaustion imply task-global completeness under unknown/censored routes.

Round B terminal: `NO_MATERIAL_CLAIM_CHANGE`.

## Literature round C — search control, exploration and harmful reframing

An independent query family across heuristic search, real-time abstraction refinement, online replanning, exploration and dynamic domain-model refinement returned the same ownership boundary:

- search/planning algorithms already own graph expansion, subgoaling, replanning and abstraction refinement;
- world-model systems own test-time model update and predictive planning;
- exploration methods own novelty-seeking and uncertainty-guided exploration;
- negative planning evidence shows abstraction/reframing is not monotonically helpful and can trade information for cost badly.

The P7 residual remains the scientific **stop/transport authority** layer: local route stop, global task stop, `CONTINUE`, and `CANNOT_CHECK` are distinct; evidence transport is weaker than closure transport; incomplete ambiguous transport reopens or abstains.

Round C terminal: `NO_MATERIAL_CLAIM_CHANGE`.

Two consecutive no-material-change rounds close current literature saturation. Reopen if a formalism proves the same obligation/closure-transport and open/censored stopping laws under equivalent assumptions.

## Historical/nearest-work source audit

The mandatory #400 correction is retained:

- Knoblock-style ordered-monotonic abstraction is a verified preservation precedent;
- planning abstraction without appropriate refinement guarantees can worsen search, including exponentially in the cited negative line;
- P7 may consume a proven planning preservation map as one component of a scientific transport witness but does not own the planning theorem.

The manuscript must never revert to `abstraction helps` as a monotonic story.

## Theorem/residual map

| P7 object | Parent pressure | Residual / boundary |
|---|---|---|
| extension-ambiguity stopping impossibility | open-world reasoning / incomplete-information planning | only under explicit admissible-completion ambiguity; no converse without richness |
| route stop vs task stop | P2/internal + search stopping | local stop never certifies task completion without coverage/obligation discharge |
| representation refinement | planning abstraction/refinement | no representation-change novelty; fixed latent/raw information used only to show strict expressivity possibility |
| harmful coarsening/reframe | negative abstraction literature | mandatory negative control; no monotonic benefit claim |
| evidence vs closure transport | schemas/lenses/planning maps | preserving evidence identity does not preserve changed scientific objective/obligation closure |
| complete transport | planning/schema preservation | donor preservation facts instantiate witness coordinates; P7 adds scientific closure obligations |
| incomplete ambiguous transport | open-world epistemic uncertainty | reopen or `CANNOT_CHECK`; no forced failure if ambiguity is not established |
| orientation obligation | Initial Exploration Problem | donor-owned orientation; P7 only types its role in closure-safe navigation |

## Blind review round 1

### R1 planning/search novelty reviewer
Attack: P7 is ordinary planning abstraction plus stopping.
Resolution: generic search, abstraction, POMDP/world-model revision, route stopping and orientation are explicitly donor-owned. The paper's residual is closure/obligation transport and fail-closed task stopping across representation/objective change.
Verdict: no unresolved major/blocking concern.

### R2 formal theorem reviewer
Attack: V1's `no closure certificate => ambiguity` and representation strictness could be false.
Resolution: V2 already repairs both: extension ambiguity requires an explicit richness premise; strictness holds fixed latent state/actions/goals/raw sensing and varies only the representation map. Incomplete transport alone yields `CANNOT_CHECK` unless target ambiguity is proved.
Verdict: no unresolved major/blocking concern.

### R3 benchmark/reproducibility reviewer
Attack: eight contract cases do not establish deployed-agent superiority.
Resolution: correct; they are exact-ground-truth contract cases, including hidden branch, censored coverage, deceptive route diversity, dead-end revisit, beneficial and harmful reframe, and non-retrieval experiment-design transfer. The paper claims formal/contract semantics, not live-agent superiority.
Verdict: no unresolved major/blocking concern.

## Blind review round 2

- **Ideal planning-stack attack:** a donor-complete planner with explicit obligation certificates could match P7. Accepted; superiority is not claimed. P7's formal object remains useful only if its closure laws add a scientific distinction not already encoded by the donor stack.
- **Always-reframe attack:** fails the harmful/unnecessary-reframe control and is inconsistent with Proposition 3.1.
- **Never-stop attack:** avoids false closure but fails clean task-stop/contract cases; blanket refusal is not a valid navigation policy.
- **No-certification attack:** P7 does not infer task incompleteness merely from absence of a certificate unless extension-richness/ambiguity supports that conclusion.

Second round: no new unresolved major/blocking concern.

## Venue/style closure

Primary: **Artificial Intelligence (AIJ)**. Fallback: **JAIR**.

Presentation invariants:

1. explain route-stop/task-stop distinction before formal notation;
2. place harmful-reframe and unknown/censored examples early;
3. theorem statements expose ambiguity/richness/fixed-information assumptions explicitly;
4. donor planning/schema preservation results are inputs to transport witnesses, not P7 inventions;
5. eight exact contract cases are formal-support examples, not empirical benchmark superiority;
6. keep method-space successor #437/#449 outside current submission.

No fallback requires a stronger empirical claim; if a venue demands deployed-agent superiority, that is new science, not a formatting overlay.

## Citation/formal/reproduction audit

- current package cites donor-complete planning/representation/world-model families;
- #400's verified/negative abstraction boundary is mandatory;
- current exact V2 checker distinguishes `ROUTE_STOP`, `TASK_STOP`, `CONTINUE`, `CANNOT_CHECK` and tests transport/refinement countermodels;
- frozen eight-case contract manifest and deterministic checks are retained;
- candidate package has content binding and audited AIJ PDF gate;
- no inferential statistics are invented for exact contract outcomes.

## Whole-paper invariant

Forbidden drift:

- representation change -> P7 novelty;
- reframe -> monotonic benefit;
- route exhaustion -> task completion;
- evidence preservation -> closure preservation;
- missing proof -> semantic failure without target ambiguity;
- budget exhaustion -> scientific completeness;
- P7 MethodChart successor -> frozen P7 evidence.

Terminal: `P7_SATURATION_CONVERGED__NO_MANUSCRIPT_CLAIM_CHANGE_REQUIRED`.
