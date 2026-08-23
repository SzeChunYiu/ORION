# ORION-Q recursive paper refinement protocol

**Freeze date:** 2026-08-22  
**External method donor:** `ACADEMIC_PAPER_SKILLS_PIN.json`  
**Venue gates:** `VENUE_READINESS_PROFILES_V1.json`

## 1. Objective

Engineer each closed ORION-Q paper to the strongest **honest** publication terminal supported by its evidence, aiming first at the paper-specific stretch venue and retaining an npj-level fallback where appropriate.

The optimisation target is not acceptance probability. It is a manuscript that is:

1. scientifically correct and bounded;
2. easy for an editor to triage;
3. difficult for a skeptical reviewer to misunderstand;
4. supported by decisive evidence rather than prestige language;
5. reproducible/auditable;
6. correctly matched to the selected journal's publication objective.

A target mismatch or evidence gap may terminate a loop. Smooth prose may not convert it into readiness.

## 2. Donor workflow imported from academic-paper-skills

The pinned donor is treated as a methodology source, not scientific authority.

The refinement loop maps donor skills to independent instruments:

| Instrument | Pinned donor skill | Function |
|---|---|---|
| `ARGUMENT_ARCHITECT` | `nature-writing` | build `question -> answer -> evidence -> boundary -> meaning`, terminology ledger, section/move architecture |
| `EDITOR_TRIAGE` | `nature-reviewer` | exact-target triage, scope/priority/evaluability gate |
| `VALIDITY_REVIEWER` | `nature-reviewer` | methods/proof/data/inference and blocking technical objections |
| `POSITIONING_REVIEWER` | `nature-reviewer` + academic search | closest prior work, donor subtraction, novelty/significance under exact target |
| `REPRO_BOUNDARY_REVIEWER` | `nature-reviewer` | reproducibility, reporting, generalization and claim boundary |
| `LANGUAGE_CONSISTENCY` | `nature-polishing` | terminology, units, notation, claim-strength and whole-paper consistency after science stabilizes |
| `FIGURE_AUDITOR` | `nature-figure` | figure roles, evidence visibility, uncertainty and submission-grade display planning |
| `STATISTICS_AUDITOR` | `nature-statistics` | experimental units, effect sizes, uncertainty, multiple comparisons and statistical text where applicable |
| `DATA_AVAILABILITY_AUDITOR` | `nature-data` | code/data/source-data availability and FAIR/repository plan |
| `REFERENCE_AUDITOR` | `nature-ref-verifier` / `nature-academic-search` | bibliographic correctness and current nearest-work search |

## 3. Foundation package required before prose refinement

For every paper create/freeze:

- `QUESTION`: one exact research question;
- `ANSWER`: one dominant bounded answer;
- `EVIDENCE_CHAIN`: ordered decisive evidence/proof blocks;
- `BOUNDARY`: what the paper explicitly does not establish;
- `MEANING`: why the bounded answer matters to the target community;
- `TERMINOLOGY_LEDGER`: canonical terms, abbreviations, notation;
- `DECISION_PROOF`: one row per headline claim with evidence, alternative explanation, resolution test and target axis;
- `VENUE_CARD`: exact stretch/fallback criteria and article type.

The manuscript may have secondary contributions, but they must attach to the dominant spine rather than competing for the abstract.

## 4. Recursive round

Each round uses the **same frozen manuscript digest** for all review instruments.

### Gate A — integrity and claim/evidence

Check:

- no result or citation invented;
- no internal ORION receipt presented as external novelty authority;
- all headline claims map to evidence/proof;
- negative/contradictory evidence remains visible;
- nearest donor/competitor is represented fairly;
- Q/QG ownership boundary is preserved.

Failure is blocking.

### Gate B — editorial triage

Resolve the exact target profile and ask:

- Is this paper in scope?
- Is the actual contribution recoverable in the title/abstract/first page?
- Why does it matter under this target's criteria?
- Is the evidence class mature enough for review?
- Can the editor recover the boundary quickly?

Allowed outcomes:

- `SEND_TO_REVIEW_CASE_CLEAR`
- `SEND_TO_REVIEW_POSITIONING_RISK`
- `TECHNICAL_CASE_NOT_REVIEW_READY`
- `TARGET_FIT_OR_PRIORITY_RISK`
- `SCOPE_OR_ARTICLE_TYPE_MISMATCH`
- `INTEGRITY_OR_COMPLIANCE_BLOCKER`

### Gate C — three review lenses

Run, or approximate when isolation is unavailable, three separate reviewer passes:

1. `VALIDITY`: proof/method/data/inference;
2. `POSITIONING`: nearest work, originality and target-specific significance;
3. `REPRO_BOUNDARY`: reproduction, reporting, readability, generalization and limitations.

Each substantive concern must bind:

`claim -> visible evidence -> why insufficient -> decision consequence -> resolution test`.

Do not impose a concern quota. Do not count reviewer votes.

When separate context isolation is technically unavailable, mark `MUTUAL_BLINDNESS_NOT_GUARANTEED` rather than pretending independence.

### Gate D — editor synthesis

Classify frozen concerns as:

- `PUBLICATION_CRITERIA_BLOCKER`
- `TECHNICAL_BLOCKER`
- `MAJOR_REPAIRABLE`
- `CLAIM_RECALIBRATION`
- `CLARITY_OR_REPORTING`
- `OPTIONAL_ENRICHMENT`

A single technically decisive concern remains blocking even if other reviewers are positive.

### Gate E — minimum valid repair

Choose the least costly scientifically valid route:

1. `ADD_DECISIVE_EVIDENCE`
2. `REANALYSE_EXISTING_EVIDENCE`
3. `CORRECT_ERROR`
4. `CLARIFY_OR_RESTRUCTURE`
5. `NARROW_CLAIM`
6. `REMOVE_CLAIM`
7. `CHANGE_TARGET_OR_ARTICLE_TYPE`

Cosmetic experiments and adjective inflation are forbidden repairs.

### Gate F — specialized audits

Run only where relevant:

- statistics;
- figures and legends;
- code/data availability;
- references/DOIs;
- terminology/unit/number consistency;
- journal submission mechanics.

Science/argument repair occurs before language polishing.

### Gate G — re-review

Recompute the manuscript digest and rerun the target-relevant checks. A concern closes only as:

- `RESOLVED_BY_EVIDENCE`
- `RESOLVED_BY_ANALYSIS`
- `RESOLVED_BY_CORRECTION`
- `RESOLVED_BY_CLARIFICATION`
- `RESOLVED_BY_CLAIM_NARROWING`
- `RESOLVED_BY_CLAIM_REMOVAL`
- `RESOLVED_BY_TARGET_CHANGE`

`RESPONDED` is not a closure state.

## 5. Readiness dimensions

Score dimensions separately from 0–10 for **engineering prioritization**, never as acceptance probability:

1. `problem_and_question`
2. `contribution_clarity`
3. `claim_evidence_alignment`
4. `technical_rigor`
5. `novelty_positioning`
6. `significance_or_field_advance`
7. `generality_and_boundaries`
8. `reproducibility_and_availability`
9. `figure_data_statistics_quality`
10. `writing_and_evaluability`
11. `venue_fit`

Hard gates in the venue profile override the numeric summary.

## 6. Recursive stop rules

Stop a manuscript round when any condition holds:

- the target readiness terminal is earned;
- a decisive new scientific evidence requirement cannot be fulfilled from existing data/receipts in the current programme;
- the paper is scientifically sound but target-mismatched and the fallback target is the appropriate terminal;
- two consecutive rounds improve the internal mean by `<0.25` with no blocker closed;
- three full manuscript rounds are reached without a material evidence/claim change;
- continued edits are optional enrichment only.

At stop, record:

- current target and fallback;
- readiness dimensions;
- unresolved blockers;
- why the loop stopped;
- strongest honest submission target **now**;
- successor research that would raise the ceiling.

## 7. Q-paper-specific target policy

### Q1

Primary: `PRX_QUANTUM_STRETCH`  
Fallback: `NPJ_QUANTUM_INFORMATION`

No new Q-era experiment is required unless reviewer simulation identifies a genuine theorem/proof/importance gap. Do not dilute the sharp theorem with QG material.

### Q2

Primary: `NATURE_COMPUTATIONAL_SCIENCE_STRETCH`  
Fallback: `NPJ_ARTIFICIAL_INTELLIGENCE`

The one-programme case study can be polished to the fallback. The stretch target remains evidence-blocked until the method is validated beyond one programme with real scientific workflows/comparators.

### Q3

Primary: `NATURE_COMPUTATIONAL_SCIENCE_STRETCH`  
Fallback: `NPJ_ARTIFICIAL_INTELLIGENCE`

One V0 measurement is not sufficient for predictive/calibration claims. The current paper can be engineered as an instrument/benchmark-definition paper; the stretch target remains evidence-blocked until the registered multi-frontier series exists.

### Q4

Primary: `NATURE_MACHINE_INTELLIGENCE_STRETCH`  
Fallback: `NPJ_ARTIFICIAL_INTELLIGENCE`

The six exact-synthetic studies can support a mechanism/benchmark paper. A real-agent/general scientific-workflow claim remains blocked until real matched-information transfer evidence exists.

## 8. AI-use/accountability boundary

The academic-paper-skills donor explicitly emphasizes human accountability for scholarly judgment. ORION therefore records AI/agent use as assistive/evaluative tooling, preserves source evidence and claim ledgers, and never treats the paper-refinement controller as an author or scientific authority.

Any target-journal disclosure is prepared according to the current official policy at submission time.
