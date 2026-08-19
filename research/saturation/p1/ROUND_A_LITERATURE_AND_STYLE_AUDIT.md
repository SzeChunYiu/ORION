# P1 saturation — Round A literature and style audit

Date: 2026-08-19  
ORION base: `e5504065dcf1f71b371a611b5d5ad8db7f4a8ce0`  
Nature-skills subject: `Yuan1z0825/nature-skills@96e41d3348748796c239cf5cb85bd947e5b02d38`

Workflows applied conceptually from `nature-academic-search`, `nature-literature-pipeline`, `nature-reader`, `nature-paper-card`, `nature-writing`, `nature-reviewer`, and `nature-shared` consistency/main-text contracts.

This is Round A, not literature saturation. Source state is recorded as `FULL_TEXT/HTML`, `ABSTRACT`, or `VENUE_GUIDE`.

## 1. Fresh candidate set

| Work | Source state | Role for P1 | Round-A disposition |
|---|---|---|---|
| Who&When Pro, arXiv:2607.09996 | FULL_TEXT/HTML | large-scale decisive failure attribution | ADOPT attribution as prior art; no high-level epistemic mutation authority |
| HarnessFix, arXiv:2606.06324 | FULL_TEXT/HTML | diagnosis of responsible harness evidence/layer + scoped repair operators | ADOPT generic diagnosis-to-scoped-repair; tighten P1.D2 residual |
| Dependency-Guided Rollback Repair, arXiv:2608.10502 | ABSTRACT | typed dependency graph, invalidation, trusted-support preservation, selective replay | ADOPT rollback/preservation as prior art; add explicit citation/table row |
| EviGraph, arXiv:2608.04738 | ABSTRACT + existing prior body check | typed evidence graph and downstream regeneration | ADOPT scoped downstream regeneration; metadata correction needed |
| AgentRewind, arXiv:2608.14380 | ABSTRACT | aligned checkpoint rewind/resume | DEFER as state recovery, not epistemic mutation authority; metadata correction needed |
| ScienceFlow, arXiv:2608.14354 | ABSTRACT | recoverable executable state + evidence-aware re-anchoring | DEFER for P1.D2; metadata correction needed |
| AI scientists produce results without reasoning scientifically, arXiv:2604.18805 | ABSTRACT | negative pressure: workflow success can coexist with weak evidence revision | CLAIM_BOUNDARY/MOTIVATION, not novelty evidence |
| Reformulation Techniques for Automated Planning, arXiv:2301.10079 / KER 38 e9 | FULL_TEXT/HTML metadata + abstract | historical reformulation parent discipline | ADAPT historical terminology/mechanism boundary; metadata correction needed |
| Towards end-to-end automation of AI research, Nature 2026 | FULL_TEXT/HTML | modern end-to-end AI-scientist exemplar | BACKGROUND/CONTRAST; does not establish P1 residual |
| An agentic artificially intelligent X-ray scientist, NMI 2026 | FULL_TEXT/HTML | strong comparable scientific-agent writing/evidence architecture | STYLE exemplar, especially broad opening + explicit non-novel architecture boundary + real/virtual evidence ladder |
| Towards agentic science for advancing scientific discovery, NMI 2025 | FULL_TEXT/HTML | broad audience field framing and limitations | STYLE/BACKGROUND exemplar |
| A Kripke-Lewis semantics for belief update and revision, AIJ 2025 | ABSTRACT | current formal belief-revision literature | FORMAL_PRECEDENT pressure against loose AGM language |
| Introduction to open-world AI, AIJ 2025 | ABSTRACT | novelty/assumption-violation/open-world framing | BACKGROUND/CONTRAST for P1/P2 boundary |

## 2. Material scientific findings

### F1 — generic diagnosis-to-repair is no longer a safe residual phrase

HarnessFix explicitly compiles traces/harness artifacts, attributes failures to responsible steps and harness artifacts, consolidates flaw records, maps those diagnoses to scoped repair operators, and validates patches with regression awareness. Therefore P1 must not say that all close attribution work stops at a descriptive label. The surviving distinction is narrower:

> a diagnosis of **epistemic responsibility type** participates in an authority rule that can permit or forbid a *high-level formulation/search-universe mutation* after ordinary lower-level repairs have been challenged.

This is a wording/ownership correction, not a new experiment.

### F2 — dependency rollback is fully prior art and should be cited normally

The 2026 dependency-guided rollback paper explicitly traces downstream dependencies, preserves independently supported benign state, deactivates unsupported memory state, and selectively replays affected computation. P1 already grants this mechanism to parents in the successor design, but the manuscript currently mentions it without a normal bibliography citation/table row. That is a citation completeness defect.

### F3 — current failure-attribution benchmark metadata drifted

Who&When Pro's primary record is titled **Who&When Pro: Can LLMs Really Attribute Failures in AI Agents?** and lists Jiale Liu as first author. The current P1 BibTeX entry uses a different first author/title. This is a concrete `nature-ref-verifier` failure.

### F4 — reformulation and belief revision must be presented as precedents, not as derivations

The planning review treats reformulation as transformation of planning representations; current belief-revision literature remains a rich formal field. P1's K/W/M engineering split is not derived by Parnas, and its K update code is not automatically an AGM revision operator merely because it aims for minimal change. The prose should say `inspired by`, `borrows`, or explicitly prove the required postulates.

### F5 — current scientific-agent evidence supports P1's motivation but not its generality

The 2026 critique of AI scientists reports that outcome success can coexist with weak evidence use and limited refutation-driven revision. This supports the importance of epistemic-process evaluation. It does **not** show P1's protected mutation rule works outside the frozen mechanical world family.

## 3. First style atlas — NMI / AIJ / TMLR

### NMI empirical Article pattern observed

From the 2026 X-ray-scientist Article:

1. Abstract starts with a field-scale operational bottleneck, not the system name.
2. The contribution sentence arrives early (`Here we demonstrate...`).
3. Evidence proceeds virtual development -> controlled benchmarking -> real deployment -> unexpected-condition adaptation.
4. The introduction is citation-dense and broad, but narrows to a concrete facility/task bottleneck.
5. Crucially, the paper explicitly says it is **not presenting new learning mechanisms or agentic architectures** before stating what it does contribute.
6. Results subheadings are question/evidence oriented, and the real-world validation is given a separate stage.
7. Limitations are admitted near the evidence, for example metric imperfections and non-repeated real beamline trials.

P1 lesson: if NMI is attempted, lead with the scientific governance problem, not `ORION Paper I`; make the donor subtraction sentence explicit; make the mechanical-world limitation obvious before the reader infers general AI-scientist superiority.

### AIJ pattern / official expectation

AIJ explicitly welcomes reasoning, knowledge representation, planning/action, uncertainty and agent work. Its guidance says mature papers should include all relevant proofs and/or experimental data, a thorough connection to literature, and convincing motivation/implications. P1 therefore needs more than a compressed ML-style benchmark story if sent to AIJ: the epistemic-level distinction and relation to belief revision, diagnosis, planning reformulation, truth maintenance and dependency repair must be explained as an AI problem.

### TMLR pattern / official expectation

TMLR's central criterion is whether claims are supported by accurate, convincing and clear evidence. Novelty/significance are not themselves required; reducing claims is an accepted way to close a claim-evidence gap. P1's bounded mechanical result is naturally compatible with this standard if the audience-interest case is clear. TMLR would be less tolerant of portfolio/programme prose that obscures the exact testable claim.

## 4. Manuscript architecture diagnosis

### Strengths

- unusually explicit negative-history preservation;
- strong donor subtraction rather than novelty-by-omission;
- powered primary + disjoint replication + independent verifier;
- clean negative controls make the mechanism non-vacuous;
- ablations identify load-bearing certificate components;
- limitations already deny model-general/open-ended superiority.

### Rejection risks / edits

1. `ORION Paper I` branding makes the title look like a programme installment instead of a standalone scientific question.
2. Foundations currently make Parnas/AGM relationships sound stronger/formal than demonstrated.
3. Related work is scientifically rich but too close to a ledger dump in places; after saturation, the main text should synthesize mechanism families and move the full donor ledger to supplement/repository.
4. The residual-claim paragraph should mention that modern repair work can be diagnosis-conditioned, then state the **authority-level** distinction precisely.
5. The abstract is evidence-rich but long and numerically dense for NMI; a journal-neutral core abstract plus a 150-word NMI overlay should be created later.
6. Protocol-amendment chronology is important for integrity but should not interrupt the primary Results evidence chain unless required to explain validity.

## 5. Round-A literature stop state

`MATERIAL_CHANGE = YES`, but only to **citation/ownership wording**, not to the supported experimental terminal.

Changes required before Round B:

- correct confirmed reference metadata;
- cite dependency-guided rollback normally;
- add HarnessFix as a close donor and narrow the residual wording;
- bound Parnas/AGM language;
- begin standalone title / venue-overlay work.

A second fresh search round is required after these edits. Two consecutive no-material-change rounds have not yet been achieved.