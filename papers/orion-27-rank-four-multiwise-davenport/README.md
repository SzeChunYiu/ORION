# ORION-27 — Generalized Davenport constants of `C_p^r` above rank three

Manuscript: `MANUSCRIPT_V1.md`. Claim ledger: `CLAIM_LEDGER.md`.
Evidence packet: `research/experiments/davenport-c7-frontier/`.

**Companion to ORION-26.** ORION-26 (*The pointed polynomial method for generalized Davenport
constants of `C_p^3`*) is a rank-three paper: its method is a pointed Chevalley–Warning identity
and its results are `D_2(C_p^3)`, `D_3(C_7^3)` and `D_4(C_5^3)`. ORION-27 is a different method
in a different regime — a positional recoding, an exact packing criterion for one algebraic
family, and the rank-four-and-above consequences. The two papers share no theorem, and the only
result of one that the other uses is Olson's classical value of `D(C_p^r)`, which both take as
external.

## skills-applied

`academic-writing` (canonical router, `manifest.yaml` v1.20.0) + the **FORMAL task bundle**
it routes to — `formal-spine-preservation`, `atomic-claim-verification`, and the theory/proof
archetype of `paper-archetype-atlas` — together with the always-loaded
`ai-session-execution-kernel`, `ai-session-context-routing` and `ethics`.

Source: the upstream **`SzeChunYiu/academic-paper-skills`** repository at rev **`b457de8`**
(latest at time of writing), cloned and read as written protocol; the skills are not installed
in this session. Resolution axes: `paper_type = theory/proof`, `section = full manuscript`,
`language = en`, `target venue = unresolved`.

**Target venue is deliberately unresolved.** The venue-decision contract requires an exact
`venue × article type × stage × effective date` tuple before target rules may be treated as
binding, and none has been chosen. No venue-specific budget, structure or house style has been
applied, and none should be inferred from the manuscript's shape.

## Divergence from the vendored protocol, flagged not resolved

`papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md` mandates the **vendored** package at
`papers/skills/nature/`, pinned at source rev `93bb0f9` (2026-07-03). Upstream is now at
`b457de8`: journal-agnostic, archetype-aware, with `academic-writing` as canonical entry point
rather than `nature-writing`, and with a session-execution kernel and context router that the
vendored pin predates entirely. This paper used upstream at the operator's direction, as
ORION-26 did.

Refreshing the vendored pin — or re-pointing the protocol at upstream — remains a **separate,
unmade change**. The protocol is an operator mandate and that decision is not made here.

## One deliberate departure from ORION-26's surface conventions

The upstream skill's artifact-leakage rule is explicit: manuscript prose must not carry
filenames, paths, helper names, branches, commits, CI jobs or CLI commands, and project URLs
resolve to **one** authoritative availability location. ORION-26 V1 predates that rule being
applied and names checker files in its verification table. ORION-27 names none: its verification
table describes *what is checked and against which control*, and availability is a single
sentence. The per-claim mapping from result to checker lives in `CLAIM_LEDGER.md`, which is a
project artifact and not manuscript-facing.

## Status

**Draft.** Not submittable. Two pre-submission gates are open and neither can be closed from the
authoring host:

1. **Prior art.** One reference (Marchan–Ordaz–Santos–Schmid, arXiv:1407.1966) has been read in
   full and its overlap with this work established as empty. The rest are unread: every
   scholarly host is refused by this environment's egress policy. In particular the novelty of
   Theorem C, Theorem W and Theorem Y is **unchecked**, as is whether `D_2(C_3^4)` or
   `D_2(C_3^5)` already appears in the literature. The manuscript says so in §11 and makes no
   priority claim.
2. **Independent mathematical review.** None of the proofs has been read by a mathematician.
