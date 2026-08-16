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

## Older RAKL numbering

RAKL used multiple publication-numbering generations before ORION. A bare historical label such as “Paper III” is therefore not a stable identity across repositories or dates.

When resolving migrated material:

1. prefer the manuscript/topic title;
2. then use its immutable RAKL source path/commit;
3. map it through `legacy-rakl-map.md` and `provenance/rakl/PAPER_SALVAGE_LEDGER.md`;
4. never infer current ORION identity from the historical number alone.

## Non-flagship technical material

`shadow-mechanics-v1/` is a technical companion/research substrate for mechanic-cell and failure-learning details. It is not assigned an ORION-P1..P5 number and must not be counted as a sixth flagship paper.
