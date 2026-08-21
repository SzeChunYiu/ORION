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

## P6–P10 candidate succession

The sections above cover the five flagship identities. Candidate papers P6–P10 live
under `candidates/` and are not flagship identities, but two of their numbers are
carried by more than one directory, so the succession is recorded here.

| Stable ID | Active directory | Retired directory | Disposition |
|---|---|---|---|
| ORION-P9 | `candidates/paper-09-structured-epistemic-learning/` | `candidates/paper-09-executable-research-core/` | retained |
| ORION-P10 | `candidates/paper-10-structured-problem-solving/` | `candidates/paper-10-content-bound-math-evaluation/` | retained |

**Retained, not removed.** The P1–P5 redirects above were deleted because they
"contained no independent manuscript content". That test fails here: both retired
directories hold results that live tests and other papers cite, and
`paper-10-content-bound-math-evaluation/` is the predecessor evidence P10's own
successor issue (#663) rests on. Deleting either would remove evidence and red the
suite.

P6, P7 and P8 each have exactly one directory and need no alias.

The machine-readable registry is `PAPER_DIRECTORIES` in
`src/orion/programme/superiority_terminals.py`. `HC-SUP-STALE-PAPER-IDENTITY` fails
on any paper-numbered directory that is neither a registered active identity nor a
recorded predecessor, so a third directory cannot appear under a number without
someone recording which one carries the identity.

## Older RAKL numbering

RAKL used multiple publication-numbering generations before ORION. A bare historical label such as “Paper III” is therefore not a stable identity across repositories or dates.

When resolving migrated material:

1. prefer the manuscript/topic title;
2. then use its immutable RAKL source path/commit;
3. map it through `legacy-rakl-map.md` and `provenance/rakl/PAPER_SALVAGE_LEDGER.md`;
4. never infer current ORION identity from the historical number alone.
