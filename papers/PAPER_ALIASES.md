# ORION paper aliases and retired numbering

This ledger is the single place for historical ORION paper-directory aliases. The active manuscript tree contains only the five canonical numbered paper directories listed in `README.md`.

## Canonical identities

| Stable ID | Canonical title | Active directory |
|---|---|---|
| ORION-P1 | Recursive Epistemic Reconstruction | `paper-01-recursive-epistemic-reconstruction/` |
| ORION-P2 | Open-World Scientific Knowledge Discovery | `paper-02-open-world-scientific-discovery/` |
| ORION-P3 | Global Knowledge Portrait | `paper-03-global-knowledge-portrait/` |
| ORION-P4 | Verified Scientific Discovery | `paper-04-verified-scientific-discovery/` |
| ORION-P5 | Self-ORION | `paper-05-self-orion/` |

## Removed redirect directories

These paths were transitional redirects created during the five-paper reindexing. They contained no independent manuscript content and are now removed from the working tree.

| Retired path | Historical meaning | Canonical destination |
|---|---|---|
| `paper-02-global-knowledge-portrait/` | Global Knowledge Portrait before insertion of the clean-generation discovery paper | `paper-03-global-knowledge-portrait/` |
| `paper-03-verified-discovery/` | Verified Discovery before the five-paper reindex | `paper-04-verified-scientific-discovery/` |
| `paper-04-self-orion/` | Self-ORION before the five-paper reindex | `paper-05-self-orion/` |

The deleted redirect READMEs remain recoverable from Git history. No scientific content is lost by removing them.

## Dissolved paper-like technical path

The former `shadow-mechanics-v1/` directory was never assigned ORION-P1..P5 but its title and manuscript layout made it look like a sixth paper. It is now dissolved rather than numbered:

- mechanic-cell representation and recursive self-audit -> **ORION-P1**;
- failure-to-method learning, challenger governance, protected self-development -> **ORION-P5**;
- discovery/stopping interfaces -> **ORION-P2**;
- verification/authority interfaces -> **ORION-P4**;
- the original Shadow README, manuscript, claim ledger, and evidence packets -> `research/technical-companions/mechanics-of-mechanics-v1/archive/`.

The archive preserves the original bytes and chronology but is not a publication identity.

## P6–P15 identity — one directory per paper

Every paper carries exactly one directory. P6, P7 and P8 always did; P9 and P10 no
longer sit beside a second `paper-NN-*` directory.

### The two that used to

They were never second versions of P9 and P10. They were a **benchmark package**
and a **benchmark corpus** that happened to wear paper numbers, and both had
already been routed elsewhere by a dated decision:

| Directory | Was | Its own terminal |
|---|---|---|
| `paper-xx-executable-research-core/` | P9 | `MERGED INTO P8/PROGRAMME`, no standalone manuscript |
| `paper-xx-content-bound-math-evaluation/` | P10 | `TECHNICAL_NOTE_MERGED_INTO_P4_P8_PROGRAMME`, 2026-08-18 |

The `paper-xx-` prefix vacates the number while keeping the record that each was a
paper candidate. Neither directory was deleted: both hold results that live tests
and other papers cite.

**Neither could be renumbered into P11–P14.** Not because those numbers are taken,
but because both are already absorbed — into P8 and P4/P8 respectively — and
re-absorbing them would contradict a recorded terminal while moving them away from
the papers that own their subjects. `content-bound-math-evaluation` is not even
dormant: its `FOLLOW_UPS.md` carries active reopen triggers, and trigger 5 routes
any surviving positive through P4 and P8.

### Correcting an earlier framing in this file

An earlier revision described these pairs as *active identity* and *retired
predecessor*. That was the wrong lens and is withdrawn. For P9 it was simply false:
the live manuscript does not cite `executable-research-core` at all, so there is no
lineage between them.

What actually distinguishes the directories under `papers/` is **layer**, not
lineage:

- the **manuscript** — the publication identity, one per paper;
- the **benchmark** — corpus, results, technical notes, now `paper-xx-` prefixed
  where it once carried a number;
- the **shared lane** — `orion-learning-machine/`, the framework and experiments
  both benchmark packages run on, which is not a paper and now says so in its own
  README.

### P15

`paper-15-orion-research-harness/` is opened ahead of an issue, as a systems paper
introducing the ORION research harness and the ORION-Q dual harness. The P-series
already contains non-claim papers — #669 writes P14 as a methods/evaluation-contract
paper — so a systems paper is in-series rather than an exception. A programme issue
assigning this subject a different number would override that.

## P11–P14, and why absorption retires a number rather than renumbering a paper

`#670` assigns four further identities — P11 State as Computation, P12 Adaptive
State–Reasoning Co-Design, P13 Responsibility-Carrying State, P14 ORION-RSE — whose
directories arrive with PR #715 as `papers/paper-11-state-as-computation/`,
`paper-12-adaptive-state-reasoning/`, `paper-13-responsibility-carrying-state/` and
`paper-14-orion-rse/`. One directory per number; no aliases needed.

The same issue fixes the rule for absorption:

> Research decomposition is fine-grained; publication synthesis is coarse-grained.
> A research atom does not automatically receive a paper number.

Three research tracks were absorbed under that rule. Each **lost its standalone paper
numbering** and became a child track; each issue stays open as a falsifiable research
track:

| Issue | Track | Absorbed into |
|---|---|---|
| #664 | accessibility work and representation–computation accounting | P11 |
| #667 | state optionality: compile, cache, recover or materialize | P11 |
| #668 | responsibility-carrying state interface and certified reuse | P13 |

**Nothing in P1–P10 was absorbed or renumbered.** `#670` states plainly that
"P1-U–P8-U remain #649–#656", and P9 and P10 keep their own successor issues #662 and
#663.

### Why a general renumber is not the way to resolve identity confusion

Recorded here because the question recurs, and because the answer is not a matter of
taste. As of 2026-08-21 the working tree contains:

- **1,399** files mentioning a paper identity;
- **374** files carrying a frozen `P<n>_…` terminal string;
- **55** CI workflows keyed to a paper number;
- **10** open pull requests from other lanes.

The decisive item is the second. Terminal strings such as
`P9_BOUNDED_STRUCTURAL_LEARNING_SUPPORTED` and
`P1_WIDER_ARCHITECTURE_CLAIM_SUPPORTED__BOUNDED_EXACT_HETEROGENEOUS_CONTRACTS__A3_CANNOT_CHECK`
are frozen scientific identifiers embedded in evidence artifacts and receipts. A
renumber leaves exactly two options, and both are bad: leave the terminals stale, so
the number inside a terminal no longer names its paper; or rewrite frozen evidence,
which the repository's immutability rules forbid.

That is also the lesson this file already carries from the P1–P5 reindex: *never infer
current ORION identity from the historical number alone.* The cost of the last
renumber is why that sentence exists.

So identity confusion is resolved by **making identity explicit**, not by moving
numbers. The machine-readable registry is `PAPER_DIRECTORIES`,
`FUTURE_PAPER_DIRECTORIES` and `RETIRED_PAPER_NUMBERING` in
`src/orion/programme/superiority_terminals.py`, and `HC-SUP-STALE-PAPER-IDENTITY`
fails on any paper-numbered directory that is neither a registered identity nor a
recorded predecessor.

## Older RAKL numbering

RAKL used multiple publication-numbering generations before ORION. A bare historical label such as “Paper III” is therefore not a stable identity across repositories or dates.

When resolving migrated material:

1. prefer the manuscript/topic title;
2. then use its immutable RAKL source path/commit;
3. map it through `legacy-rakl-map.md` and `provenance/rakl/PAPER_SALVAGE_LEDGER.md`;
4. never infer current ORION identity from the historical number alone.
