# P10-U GPT-R1 academic-paper-skills and framework audit

Date: 2026-08-20
Issue: #663
Subject base: `main@d36c6d81611ee510e4864fb9b8790dcb86d9b760`
Manuscript: `papers/candidates/paper-10-structured-problem-solving/successor/P10_U_MANUSCRIPT.tex`

## Scope

This audit applies the relevant `academic-paper-skills` discipline to the P10-U maximum-claim manuscript:

- venue-agnostic primary/current literature search and donor saturation;
- load-bearing reference verification;
- three independent reviewer lenses (validity/methods, prior-work/ownership, reproducibility/generalization);
- statistical/design audit with independent task/family as the default unit;
- whole-manuscript claim/evidence/boundary consistency sweep.

The target remains the largest one:

`VERIFIED_PROBLEM_SOLVING_AND_METHOD_SPACE_EXPANSION_SUPERIORITY`.

The audit is not allowed to create a positive result that has not been run.

## Literature and donor saturation

### Direct problem-solving / theorem-proving donors

P10 must grant the comparator the strongest available theorem-proving and proof-repair mechanics, including:

- proof-state conditioned search and retrieval;
- lifelong proof-learning / library growth;
- proof repair and MCP/tool-mediated theorem-proving agents;
- failure-triggered learned interventions in Lean automation;
- exact verifier feedback and deterministic tactic search;
- premise retrieval, tactic generation, dependency-aware search, macro/library mining.

Current examples include LAMP (arXiv:2606.28841) and learned interventions in Lean 4 `grind` (arXiv:2607.22972). The latter is particularly important because it demonstrates a failure-triggered learned intervention that is constructed not to destroy proofs already solved by stock `grind`. Therefore failure-triggered adaptation is donor-owned and cannot be claimed as P10 novelty.

### Algorithm/method discovery donors

AlphaEvolve (arXiv:2506.13131) and later evolutionary coding systems establish strong evaluator-guided algorithm/method search over executable programs. CodeEvolve (arXiv:2510.14150) adds an open evolutionary coding baseline. These systems own generic evolutionary program/method search and algorithm improvement.

Therefore a P10 method-space claim cannot mean merely:

- mutation of code;
- discovery of a better program under an evaluator;
- mining a macro/library item;
- evolutionary search over an already-expressive program language;
- a tactic abbreviation that expands to already-registered tactic composition.

### Strongest donor-complete comparator

The P10 donor product receives, under the same information/resource model where runnable:

1. native proof state;
2. dependency/premise retrieval;
3. best-first/tree/heuristic search;
4. deterministic tactic search;
5. proof repair;
6. failure-triggered learned intervention;
7. tactic/macro/library mining;
8. program synthesis;
9. evolutionary code/method search;
10. P9 representation/accessibility improvements;
11. additional search/compute controls;
12. exact verifier feedback.

The residual is not generic search or generic method generation. The residual is **correctly distinguishing search/access failure from registered-method inadequacy, then expanding a frozen method language only when an independently checkable obstruction justifies it**.

## Reference-verifier findings

Verified load-bearing identifiers for the successor bibliography:

- AlphaEvolve: arXiv:2506.13131.
- CodeEvolve: arXiv:2510.14150.
- LAMP: arXiv:2606.28841.
- Learned Interventions in Lean 4 grind: arXiv:2607.22972.

No conference/journal venue is asserted when only the arXiv record was verified.

## Reviewer 1 — validity / methods

### Major concern V1: timeout is not an obstruction certificate

A bounded search failure can arise from search order, representation, implementation, environment, missing library access, heuristic error, or insufficient budget. P10 must not infer method-basis inadequacy from timeout, low solve rate, or failed proof search.

**Resolution test:** method-space expansion is inaccessible until a prospectively frozen obstruction protocol excludes lower-level responsibilities under the same access/resource model.

### Major concern V2: method expansion needs a closure definition

A proposed edit is not outside the old method space unless the pre-freeze basis and closure operation are explicit. A new name for an old composition is not expansion.

**Resolution test:** bind method basis, composition/closure rules, semantic model, resource/access model and an independent `outside_closure` witness before calling an edit an expansion.

### Major concern V3: representation change must not be mislabeled invention

P9 owns representation accessibility. If a better interface makes an old method succeed, the result is a representation/access repair, not method-space expansion.

**Resolution test:** run representation-repair and search-more first-right-of-refusal arms; P10 expansion is credited only if the obstruction persists after their prospectively permitted fixes.

## Reviewer 2 — prior work / ownership

### Major concern O1: evolutionary discovery is direct prior art

AlphaEvolve/CodeEvolve make evaluator-guided executable method/algorithm evolution a strong donor. A P10 claim that ORION can "invent methods" without stronger discrimination would be overbroad.

**Resolution test:** donor-complete evolutionary/program-synthesis baselines receive the same evaluator, budget and search language. ORION must either expand beyond their frozen language/closure or show a higher-order obstruction-and-language-selection advantage.

### Major concern O2: theorem-prover gains require current prover pressure

LAMP and learned Lean interventions make proof repair, proof-state interaction and failure-triggered learned tactics donor mechanisms.

**Resolution test:** the manuscript explicitly donor-subtracts these mechanics and evaluates verified solve/search value, not tactic-prediction accuracy alone.

### Ownership conclusion

The unowned scientific object is not "structured reasoning" or "learning from proof failure." It is the combined relation:

`bounded obstruction -> responsibility diagnosis -> method-language opening -> semantics-preserving outside-closure edit -> held-out verified reach expansion -> low false invention`.

## Reviewer 3 — reproducibility / generalization

### Major concern R1: formal-engine readiness is not a Lean result

`src/orion/benchmarks/formal_engine.py` checks the ORION registered mechanic surface and explicitly distinguishes structural contracts from independent formal closure. It is not a native Lean theorem-proving engine and cannot support P10 empirical claims.

**Resolution test:** keep formal-engine readiness as framework consistency only. Native Lean results must come from separately frozen execution, currently the active #618 lane.

### Major concern R2: #618 runtime results remain pending authority

#618 has implemented exact native-Lean execution and cross-revision extraction, but its own contract says no positive native-state claim exists until frozen analyzers pass. P10-U must retain this boundary.

### Major concern R3: expansion must transfer

A method edit that solves only its originating target may be memorization, target leakage or an overfit macro.

**Resolution test:** freeze held-out tasks/families before edit generation; require independent re-execution plus a low false-expansion rate on known-method controls.

## Statistics / experimental-unit audit

- Primary unit for solve-rate inference: protected task/theorem, not repeated samples from one theorem.
- Method-expansion unit: independently frozen obstruction family/task, with repeats treated as technical repeats.
- Report paired task-level effects where systems solve the same tasks.
- Keep solve rate, verifier calls, branching/depth, invalid actions, repair success, false expansion and cost separate.
- A mean gain cannot compensate a catastrophic semantic violation or false method-space claim.
- Freeze multiplicity treatment for confirmatory H1-H6 comparisons before protected outcomes.
- Cross-revision or cross-domain claims require whole-block holdouts, not random remints of the same template.

## Framework consistency map

| P10-U object | Current ORION substrate | Status |
|---|---|---|
| `SEARCH` / bounded search | canonical `SEARCH.v1` and registered search mechanics | implemented substrate |
| method responsibility protected from local reframe | `formal_engine.py` proof check `PO-METHOD-CHANGE-IS-PROTECTED` | implemented guard |
| ambiguous responsibility blocks broad revision | `formal_engine.py`; responsibility gates | implemented guard |
| proposal != adoption | Self-ORION change/revision gates | implemented guard |
| native Lean proof-state execution | active #618 research implementation | candidate/runtime research, not main authority |
| cross-revision Lean transfer | active #618 | prospective/pending result |
| method-basis obstruction certificate | no canonical registry object | prospective |
| outside-closure method-language edit | no canonical registry object | prospective |
| general method-space expansion superiority | no empirical authority | prospective claim |

Verdict: `CONSISTENT_AS_PROSPECTIVE_EXTENSION`.

The existing framework already enforces the key safety direction: method change is protected and cannot be licensed by ordinary local reframing. What is missing is the scientific obstruction/closure object and protected evidence for method-language expansion.

## Negative-result recovery doctrine

Historical P9/P10 and ORION-Q negatives are immutable. They are converted into one of:

1. representation/accessibility repair (P9/AAGD);
2. search/compute failure;
3. implementation/environment/verifier failure;
4. action-abstraction/library failure;
5. genuine frozen-method closure obstruction;
6. donor domination;
7. non-identifiable/CANNOT_CHECK.

Only class 5 opens the P10 method-language expansion gate.

## Academic decision

The manuscript is reviewable as a **prospective maximum-claim protocol** after donor correction and OCME addition. It is not yet an empirical superiority paper.

The first paper-completion object is therefore:

`Obstruction-Certified Method-Language Expansion (OCME)`

which converts negative proof/search outcomes into either a lower-level repair or a justified method-language jump without weakening the headline target.
