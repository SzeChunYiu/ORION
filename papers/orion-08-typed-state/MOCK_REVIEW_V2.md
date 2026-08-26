# ORION-04 mock peer review V2

**Subject:** `MANUSCRIPT_V2.md`  
**Review mode:** three mutually blind reports frozen before synthesis  
**Purpose:** scientific closure only; this is internal adversarial review, not external peer review or acceptance authority.

---

# Reviewer 1 — Mechanism / decision-theory review

## Summary assessment

The manuscript has a coherent paper-level thesis that was not visible in the six-study V1 framing: typed/scoped state matters when the downstream responsibility requires distinctions flattened by a matched-information control. The two donor-absorption negatives materially increase credibility.

## Major concern R1.1 — “same information” needs one formal statement

**Evidence-backed finding.** The manuscript repeatedly says non-oracle arms receive the same serialized facts but vary in representation/consumption. That is central to causal interpretation, yet the main text does not define a common information-parity condition formally enough for a skeptical reader to audit across six different worlds.

**Required repair.** Add a short Methods definition:

`information parity := identical world realization + identical candidate-visible primitive facts + identical resource budget; permitted difference = registered state typing/scoping/decision rule only.`

Then state, per study, which field/rule differs. A compact table is sufficient.

**Severity:** ORION-11 / blocking for a mechanism paper.

## Major concern R1.2 — separate “typed state” from “known correct rule”

**Evidence-backed finding.** Several worlds supply a type/scope rule that is correct by construction. The current Limitations section acknowledges this but the Results occasionally read as though the experiment establishes that the type system itself is scientifically correct.

**Required repair.** Add one sentence at the start of the synthesis: these studies test the **value of exposing a registered distinction**, not the ability to infer that distinction or prove it correct in natural data.

**Severity:** ORION-11 but text-only.

## Minor concern R1.3 — N4-C terminology

Avoid saying the method “identifies higher-value verification” without the frozen scalarized objective qualifier. Keep “higher-value under the registered objective/budget.”

## Decision

**Minor-to-moderate revision.** No new experiment required.

---

# Reviewer 2 — Novelty / related-work review

## Summary assessment

The current title and central claim are substantially more defensible than the earlier “six first-right-of-refusal studies” title. The paper correctly gives VOI, stale memory, provenance and active learning away. The remaining novelty claim should be framed as a **cross-responsibility mechanism synthesis**, not a new primitive.

## Major concern R2.1 — recent stale-memory/context-governance work must enter the main Related Work, not only limitations

**Evidence-backed finding.** 2026 work now directly addresses implicit stale memory and governed versioned context. Broad statements such as “most systems carry this state untyped” are no longer safe without qualification.

**Required repair.** Replace broad prevalence language with a narrower tension: individual systems often represent some dimensions (time, provenance, confidence), but the paper asks whether different downstream responsibilities require **different explicit scope/type distinctions** under matched information. Include the current donor cluster (STALE, stale-dependency repair, ContextNest) as direct nearest work.

**Severity:** ORION-11 / publication-positioning blocker.

## Major concern R2.2 — “responsibility” is close to ORION-23 terminology

**Evidence-backed finding.** Elsewhere in ORION, ORION-23 explicitly develops responsibility-carrying state. ORION-04 risks internal novelty overlap if it presents responsibility-scoped authority as its own theoretical invention.

**Required repair.** ORION-04 should state that “downstream responsibility” is an organizing variable for these exact-synthetic experiments, while any general theory/certificate of responsibility-scoped sufficiency belongs to ORION-23. ORION-04 owns the quantum/research-interface mechanism-isolation evidence.

**Severity:** ORION-11 internal-overlap blocker.

## Minor concern R2.3 — title

“Typed and Scoped Partial-Knowledge State for Research Decisions” is accurate but broad. Consider a subtitle or abstract opening that says “six exact-synthetic mechanism-isolation studies” to preempt deployment/generalization readings.

## Decision

**Revision required; novelty survives after narrowing.** No new experiment required.

---

# Reviewer 3 — Reproducibility / statistics / generalization review

## Summary assessment

The manuscript is unusually explicit about synthetic scope and deterministic replay. The main remaining risk is readers interpreting large episode counts and exact rates as statistical generalization rather than properties of constructed worlds.

## Major concern R3.1 — mark descriptive versus inferential numbers consistently

**Evidence-backed finding.** N1-C has a valid registered bootstrap interval. Most N4 result numbers are deterministic/frozen-world aggregates. The manuscript correctly says this in Limitations but should label it earlier.

**Required repair.** In the shared Methods, add a reporting rule: unless a protocol explicitly defines an inferential unit/interval, N4 rates and means are descriptive summaries over frozen generated episodes, not estimates of a natural population parameter.

**Severity:** ORION-11 text/reporting blocker.

## Major concern R3.2 — claim-to-artifact map should be visible to reviewers

**Evidence-backed finding.** The repository has excellent result/protocol structure, but `MANUSCRIPT_V2.md` cites fewer exact paths than V1. A reviewer should not need to reverse-engineer the claim ledger.

**Required repair.** Add a compact Reproducibility table or appendix mapping N4-A..F3/N1-C/N2-F5B to protocol, result receipt, runner and replay ledger. The main prose can remain readable.

**Severity:** ORION-11 package/reproducibility blocker.

## Minor concern R3.3 — exact 1.000/0.000 transport result

Keep the construction denominator (200 hostile/200 honest) adjacent to the rate every time it appears in abstract/table so the number cannot be mistaken for an asymptotic/security guarantee.

## Decision

**Minor revision.** No new data required.

---

# Editor synthesis — post-review only

## Common ground

All three reviewers agree that:

1. the paper now has one coherent contribution rather than six disconnected ones;
2. the science can be submitted on the current exact-synthetic evidence cut;
3. no reviewer requests a new experiment;
4. the blocking risks are **claim architecture and auditability**, not missing outcomes.

## Non-overlapping blocking repairs

### E1 — formalize information parity
Owner: Methods.  
Repair: one definition + one per-study parity table.  
Source: R1.1.

### E2 — state rule-learning boundary
Owner: Introduction/Synthesis/Limitations.  
Repair: explicitly distinguish “value of an exposed type/scope distinction” from learning/validating that distinction in natural data.  
Source: R1.2.

### E3 — current donor subtraction
Owner: Introduction/Related Work.  
Repair: STALE / stale-dependency repair / ContextNest as direct donors; delete any claim that agents broadly carry state untyped.  
Source: R2.1.

### E4 — ORION-23 internal ownership boundary
Owner: Introduction/Related Work/Discussion.  
Repair: ORION-04 uses downstream responsibility as experimental organization; ORION-23 owns a general responsibility-carrying-state/sufficiency-authority theory.  
Source: R2.2.

### E5 — descriptive/inferential label discipline
Owner: Shared Methods + Results captions/tables.  
Repair: default N4 summaries descriptive; identify N1-C bootstrap interval as a separately registered inferential analysis.  
Source: R3.1.

### E6 — reviewer-visible artifact map
Owner: Reproducibility/Supplement.  
Repair: protocol/result/runner/replay table for all eight families.  
Source: R3.2.

## Minimum-sufficient repair decision

**No new scientific experiment.** Perform one manuscript revision round containing E1–E6, then re-run the three review lenses. If no new central blocker appears, move to citation/reference verification, figure build, polish and target-journal packaging.

## Current editorial disposition

`REVISION_REQUIRED__SCIENTIFIC_OBJECT_SURVIVES__NO_NEW_EXPERIMENT_REQUESTED`