# PAPER WRITING SKILLS PROTOCOL V1 (operator mandate, 2026-08-26)

> **MANDATORY for every AI session writing or rewriting any manuscript in this repo.**
> Operator directive, verbatim intent: *"when you write the papers, you must use this
> package skills to help you write the papers … including rewriting existing papers
> and new papers, it must use this."*

## 1. Scope — what counts as "writing a paper"

This protocol applies to **every change that produces or restructures manuscript
content**, in *any* lane (`shadow/*`, `claude/*`, `codex/*`, takeover branches):

- New manuscripts: ORION-11–P18 and successors, the Q/QG series, the theory lanes
  (A+B, C, D, ORION-04, NP and their post-rename targets), `papers/candidates/*`.
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
| Statistical reporting, uncertainty, estimands and inferential-unit audit | `nature-statistics` (installed skill; use the vendored closure checklist when the package is unavailable) |
| Reference-identity and metadata verification | `nature-ref-verifier` (installed skill) together with `nature-citation` |
| Publication closure, venue/anonymity routing, package binding and repository mirroring | `nature-publication-closure` |
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

## 7. House style (binding for all manuscript work)

Absorbed 2026-08-27 from `papers/HOUSE_STYLE_TODO.md` (agreed 2026-08-21; the
parked TODO retires into `papers/archive/2026-08-pre-unification/`). These are
craft rules and bind every new or rewritten manuscript exactly like the skills:

1. **Standalone contributions.** Papers 1–14 (ORION-11…24) must not presuppose
   that the composed system exists. Each paper is a mechanism, its theory, and
   its experiment. The system is assembled and named only in Paper 15
   (ORION-25). A paper needing a sibling result **cites it** like any other
   reference — no internal cross-references to sibling papers or a shared
   programme.
2. **Mechanism as subject.** Remove the system name from the body; claims are
   about the mechanism ("routes count as independent only when independence is
   earned"). Name the implementation once, in Methods or Availability, as the
   artifact under test.
3. **No machine tokens in prose.** `CANNOT_CHECK`, `TIER_B_committed`,
   `P2_WIDE_EXTERNAL_CANNOT_CHECK` and similar are internal vocabulary. State
   the three-valued outcome idea once, in plain English, in Methods; in prose
   say "remains undetermined".
4. **No repository paths or artifact filenames in the narrative** — they belong
   in Data Availability.
5. **No defensive scaffolding sections.** "Problem and claim boundary" is an
   Introduction; "Nearest work" is Related Work that positions the contribution
   among neighbours. The claim boundary stays — stated once, in prose, in
   Limitations.
6. **No tables of open-literature checks.** Discuss the neighbouring work and
   cite it.
7. **Internal identifiers out of prose.** An experiment id gets one
   reader-holdable name ("the exact-contract battery").

## 8. Publication-closure authority

Publication closure is a separate, fail-closed craft and custody step. Apply
`papers/skills/nature/nature-publication-closure/SKILL.md` whenever work claims
that a manuscript or submission package is current, complete, ready to file, or
mirrored. A prose readiness note cannot supply that authority. The closure
record must bind the active claim authority, reader-facing source, rendered PDF,
venue/article type, audience-specific identity rule, package inventory, and any
mirror receipt. Contradictory visible terminals must be explicitly historical or
name the current superseding record.

Scope order: ORION-12 first, reviewed, then the same treatment per paper as each
is finished. All R2 rewrite waves apply this section from their first draft.
