# Bibliography depth is a live submission gate

Measured by counting `^@` entries across every `.bib` under each `manuscript/` (recursive). No paper uses embedded `\bibitem`, so the `.bib` files are the whole bibliography.

| paper | entries | note |
|---|---|---|
| ORION-22, -23, -24 | **2** | |
| ORION-21 | **3** | |
| ORION-10 | **3** | Quantum |
| ORION-05, -06, -07, -20 | **4** | ORION-07 targets TMLR |
| ORION-09 | 5 | |
| ORION-08 | 9 | TMLR |
| ORION-18 | 13 | |
| ORION-25 | 13 | |
| ORION-17 | 14 | |
| ORION-19 | 16 | |
| ORION-14 | 24 | TMLR |
| ORION-15 | 30 | |
| ORION-13 | 33 | |
| ORION-12 | 48 | |
| ORION-11 | 51 | |

## Why this matters

A theory paper submitted to a top-tier venue with **two to four references** has effectively no related-work positioning. That is a desk-rejection trigger on its own, independent of the quality of the result: a reviewer cannot tell what is new if the paper does not say what came before.

The gap is not marginal. ORION-11 carries 51 references and ORION-22 carries 2 — a 25x spread across papers in the same programme, aimed at comparable venues.

## What this does not say

This counts references; it does not judge them. A paper can carry 40 references and still position itself badly. The claim here is narrower and safer: **2–4 references cannot be enough** for a top-tier theory venue, whatever those references are.

## Two probes that lied, recorded so they are not trusted again

1. **`refs-in-bib = 0` for all 22 papers.** A shell glob `"$d/manuscript"/*.bib` failed inside a loop, returning zero everywhere. A control read of one file directly showed 24 entries. Twenty-two identical zeros is a broken probe, not a finding.

2. **"ORION-08 renders no References section."** The probe required a line matching exactly `References`. TMLR's style formats that heading differently, so a paper whose text demonstrably ends `[9] Kazuki Nakayashiki...` was reported as having none.

A third measure — counting `[N] Author` patterns in extracted PDF text — returns 0 for author-year styles, so it silently reports TMLR papers as reference-free. It disagreed with the `.bib` count for ORION-05 (12 vs 4) and was discarded rather than averaged in.

## Next

Bibliography expansion is literature work, not packaging: each paper needs its nearest prior work identified, read and positioned against. It cannot be regex'd, and it is the largest remaining gate for the papers whose front matter is now clean.
