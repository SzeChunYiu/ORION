# P3 manuscript ↔ claim-ledger map V1

**Date:** 2026-08-17  
**Ledger:** `CLAIM_LEDGER_V1.md`  
**Rule:** a manuscript sentence may not outrank this ledger. This file is a map, not a promotion.

| Ledger ID | Authority | Manuscript location | Match? |
|---|---|---|---|
| P3.C1 | IMPLEMENTED / LOCAL_ENGINEERING | `30-method.tex` projection/coordinate definitions | yes |
| P3.C2 | IMPLEMENTED / LOCAL_ENGINEERING | method + local-world discussion | yes |
| P3.C3 | IMPLEMENTED / LOCAL_ENGINEERING | method (invalid bridges / pivot change) | yes |
| P3.C4 | EXECUTED / EXTERNAL-PUBLIC AUTHORITY | `40-dataset.tex`, `06-results.tex` public-reference construction | yes |
| P3.C5 | CONFIRMED IN FROZEN NARROW SCOPE (confirmatory n=32, false-merge delta −0.1875) | `06-results.tex` confirmatory subsection | **yes in Results** |
| P3.C5 vs abstract | same | `00-abstract.tex` quotes the *initial* run (false-merge 0.125, delta −0.125) | **stale relative to C5** — initial numbers are allowed as the first experiment but must not be read as the confirmatory authority |
| P3.C5 vs conclusion | same | `08-conclusion.tex` repeats the initial 0.125 / −0.125 result and omits confirmatory PASS | **stale relative to C5** |
| P3.C6 | PARTIAL ONLY | `06-results.tex` covered ablations | yes (zero-effect coordinates not claimed necessary) |
| P3.C7 | CANNOT_CHECK | abstract, results status, conclusion all keep `\conststatus{}` for end-to-end raw text | yes |
| P3.C8 | CANNOT_CHECK | same | yes |
| P3.C9 | SATISFIED FOR PUBLIC-REFERENCE ROUTE | results (byte-for-byte freeze + execution-frozen confirmatory) | yes |

## Overclaim risks left in place (not rewritten here)

`07-limitations.tex` still describes the evaluation as a four-discipline, 32-sample, eight-family, double-annotated gold study. That is the *intended* expert-gold protocol, not the executed public-reference route. Additive policy: do not silently retcon limitations into a completed expert study. A later manuscript pass should either mark those paragraphs as protocol-not-executed or wait for real dual annotation.

Issue #100 Step 8 “claim ledger maps every headline claim to an artifact” is satisfied by `CLAIM_LEDGER_V1.md` plus this map. Stage-attributed extraction vs mapping vs integration error remains `CANNOT_CHECK` (no extractor run).
