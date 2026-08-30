# Internal version labels in rendered headings

Seven papers print internal version labels in headings that a reader sees. Found by extracting text from the rendered PDFs, not by reading source — the source looked finished.

## Repaired

| paper | was | now |
|---|---|---|
| ORION-17 | `Replacement abstract for V4` | `Abstract` |
| ORION-17 | `18. The composition calculus (replaces the informal V3.5)` | `The composition calculus` |
| ORION-18 | `Replacement abstract for V3` | `Abstract` |

## Not repaired — renumbering hazard

`Theorem V4.1`–`V4.6` (ORION-17) and `Theorem V3.1`–`V3.10` (ORION-18) are **cross-referenced in prose**: 20 and 27 mentions respectively. They cannot be edited as headings alone.

The obvious mapping — `V4.1` → `Theorem 1` — is wrong. **Both papers already carry a second, independent numbering**: ORION-17 has plain `Theorem 1`–`8` (six mentions of `Theorem 1` alone) and `Corollary 1.1`; ORION-18 similarly. Collapsing the V-set onto plain integers collides with it, and silently renumbering theorems in a theory paper is a content error, not a typographic one.

Resolving this needs a decision about which sequence is canonical and whether the two sets are genuinely distinct results or duplicate statements of the same ones. That is a reading task per paper, not a substitution.

## Remaining, unexamined

`ORION-07` (`V0 agreement` — possibly a legitimate technical term, not a version), `ORION-11` (`Owner/custody execution packets V11--V13`), `ORION-12` (`Post-V2 active-comparator audit`, `V6 outcome-unopened source`, `V7 hash-frozen`), `ORION-13` (`Cross-construct V3 development`, `Outcome-blind V4 audit`, `V5 direct-certificate semantics`), `ORION-15` (`24/24 V2 attribution result`, `Pre-registered V4 revival`).

Several of these name a *study stage* rather than a document version — `Post-V2 active-comparator audit` may be a real experimental phase. Each needs reading before rewriting; a blanket `V\d` strip would corrupt genuine methodology names.
