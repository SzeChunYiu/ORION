# Editor synthesis after frozen Wave-1 review

Date: 2026-08-28  
Status: simulated editor synthesis, not external peer review or a journal decision  
Article archetype: theory/proof paper with bounded computational corroboration  
Targets assessed in the frozen round: *PRX Quantum* and *Quantum*

## Review inputs and independence

The synthesis begins only after the three initial reviewer reports and the independent atomic-coverage pass were frozen. Reviewer 1 assessed validity, methods, data, and inference. Reviewer 2 assessed contribution, nearest work, significance, and target fit. Reviewer 3 assessed reproducibility, reporting, clarity, boundaries, and readership. The atomic-coverage checker reconstructed its own content inventory from the same immutable blind packet. No frozen report was edited after comparison.

Frozen inputs:

- `ROUND1_REVIEWER_1_VALIDITY_2026-08-28.md`;
- `ROUND1_REVIEWER_2_CONTRIBUTION_2026-08-28.md`;
- `ROUND1_REVIEWER_3_REPRODUCIBILITY_FROZEN_2026-08-28.md`, SHA-256 `c34d56ee213fc342b2dad3b73076f7f0404b1ad9aadec1ad4904697bb241668d`;
- `ROUND1_INDEPENDENT_ATOMIC_COVERAGE_FROZEN_2026-08-28.md`, SHA-256 `5da87a47fe625e3e8fa98bcfd672f74fba13177f37531a58744ccab35fe6c897`.

## What external review changed relative to triage

The review did not refute the central theorem. It did identify that the initial manuscript stated the admitted grammar and normalized objective too informally to make the theorem self-contained. It also showed that the initial anonymous archive supported only two executable checks while presenting broader exact-comparison and runtime claims as reproducible. Those are substantive reporting and artifact defects, not requests for more favorable experimental results.

Reviewer 2 identified a different terminal issue. Even if the technical and reporting defects are repaired, the fixed six-target grammar, nonphysical objective, absence of a same-problem asymptotic improvement, and adverse runtime panel do not establish the significance burden for *PRX Quantum* or *Quantum*. That is a target-fit problem rather than a hidden request for cosmetic experiments.

## Consensus strengths

1. No reviewer or independent coverage pass found a counterexample to the correction-exchange lemma, zero-sum-subset lemma, support-reduction theorem, exact `5<6` obstruction, ordered-pair count, or constructive `O(n^9)` upper bound within the declared model.
2. The paper keeps the distinction between representation and implementation performance explicit.
3. The adverse result is retained. The final record contains 120 attempts, 108 completions, and 12 timeouts, including six three-qubit and six full-subject support-two timeouts.
4. Claims of hardware, fault-tolerant-resource, energy, memory, runtime, universal-compiler, broad-novelty, and journal authority are excluded.

## Decision-relevant concern synthesis

| Concern family | Editor class | Must address | Minimum sufficient route | Post-revision disposition |
|---|---|---:|---|---|
| `O5-R1-MAJ-01`, `R3-OR5-001`, `ACG-OR5-001` | technical blocker | yes | Formalize all variables, admissibility, syndrome equations, branch/central semantics, normalized objective, and feasible families | repaired in the current manuscript; original R1 and R3 owners must recheck |
| `O5-R1-MAJ-02`, `R3-OR5-002`, exact-comparison part of `ACG-OR5-002` | claim recalibration | yes | Release a separate referee or remove unsupported separate-referee and broad finite-conformance claims | resolved by claim removal and narrowing; owner recheck required |
| `O5-R1-MAJ-03`, `R3-OR5-003`, runtime part of `ACG-OR5-002` and `ACG-OR5-003` | major repairable | yes | Release the pre-measurement specification, all 120 sanitized rows, environment fields, and deterministic aggregation, while stating that the original unrestricted measurement stack is absent | repaired for deterministic row audit, not for a new timing campaign; R1 and R3 recheck required |
| `O5-R1-MIN-01` | clarity and proof reporting | yes | State branch-swap, central-multiplier, and minimum-shared-operator reductions | repaired in Methods and sharpness text |
| `O5-R1-MIN-02` | claim alignment | yes | Promote the stronger transformation statement to the theorem or weaken the abstract | repaired by the cost-nonincreasing transformation theorem |
| `OR05-R2-M01`, `OR05-R2-m01`, `OR05-R2-m02` | major repairable | yes | Provide a source-anchored inherited/specialized/new crosswalk and compare nearest scientific objects and guarantees | repaired without priority language |
| `OR05-R2-M02` | publication-criteria blocker | yes for named targets | Demonstrate a broader consequence or generalization, or change to a focused specialist target | unresolved for *PRX Quantum* and *Quantum*; resolved only by an author-selected target change or new science |
| `OR05-R2-M03`, `OR05-R2-m04` | claim recalibration | yes | Define input length and comparator status; if no improvement is established, present only constructive exact solvability | repaired by claim narrowing; no algorithmic-advancement claim remains |
| `OR05-R2-m03`, `R3-OR5-006`, `ACG-OR5-004` | literature reporting and external-authority boundary | yes | Date and bound the search, expose query families and nearest-object comparison, retain no absence or priority claim | repaired in manuscript prose, the public literature crosswalk, and the source-entailment audit; external novelty authority remains absent |
| `R3-OR5-004`, `ACG-OR5-005` | reviewer-surface blocker | yes | Rebuild from neutral public names, remove digests and private lineage, scan names and payloads recursively, and embed anonymity-safe PDF metadata | repaired in the current source and builder; R3 recheck required |
| `R3-OR5-005` | explanation and readership | yes | Make the scientific object reconstructable from the formal specification and walk through the sharpness cost | repaired in Methods and Results; R3 recheck required |
| `R3-OR5-007` | surface and metadata | yes | Embed the exact title and anonymity-safe author value; recheck every page | repaired; final byte and page audit required after render |
| `R3-OR5-008`, human-attestation rows `AC-A09` to `AC-A11` | human-only filing gate | yes before filing | Reconcile authorship and obtain human approval for declarations, contribution, conflicts, funding, affiliation, and AI disclosure | outside blind technical closure; retained in `submission/HUMAN_METADATA_REQUIRED.md` |
| `ACG-OR5-006` | build and custody | yes | Document engine and command, rebuild twice, compare bytes, inspect every page, and bind final private hashes | repair to be completed by the final deterministic build and package manifest |

## Where reviewer emphasis genuinely differs

Reviewer 1 and Reviewer 3 treat the paper as technically recoverable by specification, artifact reconstruction, and claim narrowing. Reviewer 2 agrees that the theorem may be sound but finds the remaining contribution too narrow for either named target. These positions are compatible. Technical closure does not create target significance.

## Simulated decision posture

`scientifically_sound_but_target_mismatch`

The current central theorem can be made technically and reproducibly reviewable at its fixed-model boundary. The evidence does not establish the broader theoretical consequence, same-problem complexity advance, or practical resource benefit needed to defend *PRX Quantum* or *Quantum*. No filing to either target is authorized by this closeout. A focused formal or theory venue is plausible only after the author selects the target and its exact current venue contract is checked.

## Decision engineering map

| Priority | Risk | Best closure route | Minimum sufficient change | Residual risk |
|---|---|---|---|---|
| 1 | Grammar/objective ambiguity | correct and formalize | Complete equations and feasible-set definition | original reviewer recheck pending |
| 2 | Aggregate-only evidence | release and narrow | Public 120-row audit plus removal of unsupported separate-referee claims | original measurement stack absent and disclosed |
| 3 | Reviewer-surface leakage | reconstruct artifact | Neutral archive with recursive zero-hit scan | reviewer recheck pending |
| 4 | External novelty uncertainty | bound and subtract | Dated search and nearest-object crosswalk with no priority inference | external novelty authority absent |
| 5 | Named-target significance mismatch | change target or add real science | Author-selected specialist target, or genuinely broader theorem/resource consequence | no target chosen |

### Do not waste effort on

- cosmetic favorable experiments that do not discriminate a scientific alternative;
- hiding or rerunning away the 12 timeouts;
- inflating the fixed objective into a physical resource model;
- calling a constructive upper bound a state-of-the-art improvement without a same-problem comparator;
- treating simulated reviewer agreement as external validation.

## Risk and unsupported-claim boundary

No claim of broad novelty, priority, target significance, production value, external replication, real journal acceptance, or submission authorization is supported. The final technical package still requires targeted re-review by the original R1 and R3 concern owners. Human declarations and an exact specialist target remain outside this simulated editor closure.
