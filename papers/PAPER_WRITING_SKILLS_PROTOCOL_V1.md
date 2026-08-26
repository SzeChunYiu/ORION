# PAPER WRITING SKILLS PROTOCOL V1 (operator mandate, 2026-08-26)

> **MANDATORY for every AI session writing or rewriting any manuscript in this repo.**
> Operator directive, verbatim intent: *"when you write the papers, you must use this
> package skills to help you write the papers … including rewriting existing papers
> and new papers, it must use this."*

## 1. Scope — what counts as "writing a paper"

This protocol applies to **every change that produces or restructures manuscript
content**, in *any* lane (`shadow/*`, `claude/*`, `codex/*`, takeover branches):

- New manuscripts: P1–P18 and successors, the Q/QG series, the theory lanes
  (A+B, C, D, NQ, NP and their post-rename targets), `papers/candidates/*`.
- **Rewrites, refactors, restructures, and polishing of existing manuscripts**
  — a section edit, abstract rewrite, related-work rebuild, figure remake,
  citation pass, or top-tier promotion pass is "writing a paper" under this rule.
- Manuscript-adjacent artifacts bound to a submission: figures, tables,
  data-availability statements, reviewer response letters, cover letters.

Out of scope: research ledgers, receipts, freeze-package JSON, wiki pages — the
evidence layer, which keeps its own contracts.

## 2. The package and how to invoke it

The designated package is the **`nature-*` skills family**, vendored in-repo at
**`papers/skills/nature/`** (provenance and refresh procedure:
`papers/skills/nature/PROVENANCE.md`, pinned at source rev `93bb0f9`).

- **Claude Code sessions (Skill tool available):** invoke the matching skill by
  name (`nature-writing`, `nature-polishing`, …) **before** drafting or editing
  manuscript text, and follow its instructions for the whole artifact.
- **Sessions without a Skill tool (codex, ChatGPT lanes, LUNARC batch jobs):**
  `Read` the vendored `papers/skills/nature/<skill>/SKILL.md` (+ its
  `references/` when the SKILL.md points there, and `papers/skills/nature/_shared/`
  when referenced) and follow it **as written protocol** — same requirement,
  different transport.

A session that cannot load the package must not silently proceed with its own
style; it stops and says so (that is a cannot-check, not a pass).

## 3. Lifecycle → skill map

| Manuscript work | Skill(s) to apply |
|---|---|
| Plan/argue/draft a paper or section from claims, results, notes | `nature-writing`, `nature-proposal-writer` |
| Restructure an existing draft; argument-before-sections rebuilds | `nature-writing` (restructure mode), `nature-proposal-writer` (revise/hybrid) |
| Polish prose to publication English; LaTeX layout/typesetting fixes | `nature-polishing` |
| Figures and multi-panel plots for manuscripts | `nature-figure` |
| Insert/verify citations; literature search; systematic pipelines | `nature-citation`, `nature-academic-search`, `nature-literature-pipeline` |
| Data availability statements and repository plans | `nature-data` |
| Internal referee simulation before submission | `nature-reviewer` |
| Point-by-point response letters | `nature-response` |
| Reading/absorbing prior work while positioning the paper | `nature-reader` (comprehension aid; not a manuscript output) |

Apply every skill whose row matches the work actually being done — e.g. a
top-tier promotion pass touches drafting + polishing + figures + citations and
must run all four, not just one.

## 4. Compliance record

Every PR that adds or modifies manuscript content (`papers/**/*.tex`,
manuscript `papers/**/*.md`, figure sources, response letters) must carry one
line in its body:

```
skills-applied: nature-writing, nature-polishing, ...
```

listing the skills actually applied (or `skills-applied: NONE — <reason>` when the
change is purely mechanical, e.g. a path move). Reviewers treat a missing line as
a process defect, same class as a skipped development packet.

## 5. Authority boundaries (non-negotiable)

The skills package governs **craft** — structure, argumentation, prose, figures,
citation hygiene. It never governs **truth**:

- Claims stay bounded by the freeze control plane
  (`research/orion-v1-freeze/`) and the result-claim ledgers
  (`papers/P1_P15_RESULT_BOUND_CLAIM_LEDGER_V1.json` and successors). No skill,
  prompt, or polishing pattern authorizes a claim stronger than the ledgered
  evidence; `paper_authority_delta = NONE` discipline holds.
- Manuscript authorization itself stays gated by
  `research/orion-v1-freeze/V1_PAPER_CANDIDATE_GATE_V1.json`
  (`BLOCKED_NO_MANUSCRIPT_AUTHORIZED` until its prerequisites are earned).
  This protocol governs how authorized writing happens, not whether it may.

## 6. Relation to earlier docs

This protocol supersedes any conflicting style guidance in older paper-programme
documents (they remain binding on *substance*: gates, evidence, venues). When an
older doc and a skill disagree on craft, the skill wins; when they disagree on
what may be claimed, the freeze package wins.
