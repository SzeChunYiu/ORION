# Second batch: fourteen more preserve/recover claims verified intact

Same method as `VERIFICATION_V1.md` — reduce each claim to its most distinctive
literal, grep under that paper's directory with a **literal path**, report the file
count. Run against `main`.

| claim | paper | files |
|---|---|---|
| four-feature result, `k*=4` on frozen `n<=3` | ORION-09 | 17 |
| R4 faithful comparator, ordered Active-VOI | ORION-11 | 12 |
| 20-case discharge checker and binding PASS | ORION-18 | 4 |
| seven gold `CANNOT_CHECK` entries | ORION-18 | 53 |
| Qwen scaling negative | ORION-19 | 37 |
| orbit-coverage gate, 0% in-orbit | ORION-19 | 7 |
| `UT3` custody receipt, zero grid cells executed | ORION-19 | 15 |
| AND/OR both minimal singleton bases | ORION-20 | 2 (`AND and OR`), 6 (`indispensable`) |
| exact law, total forced regret **5,092** | ORION-22 | 4 |
| 32 objective-gold `CANNOT_CHECK` facts | ORION-23 | 17 |
| benign re-encoding **0/6** false rejection | ORION-25 | 16 |
| compromise **d=1** false promotion 4/4 | ORION-25 | 8 |
| affected closure is the unique minimal sound set | ORION-16 | 4 |
| analytic-vs-empirical distinction for M5 | ORION-03 | 51 |

## One near-miss, caught the same way as last time

ORION-20 first returned **zero** on the pattern `singleton bas|minimal singleton`.
Rather than record an absence, the directory was re-probed: 68 files present, and
`AND and OR` matches 2, `indispensable` 6, `minimal bas` 5. The claim is intact and
the first pattern was simply wrong.

That is the second time in this verification series that a single failed pattern
would have produced a fabricated absence. **A pattern returning nothing is evidence
about the pattern until the directory has been shown to be non-empty and a
different literal has been tried.**

## Scope

Unchanged from V1. This establishes the records are in the tree and reachable,
which is what *preserve* and *recover* ask. It does not re-derive any of them.
Where a claim is adverse or `CANNOT_CHECK` — ORION-19's Qwen negative and its zero
executed UT3 cells, ORION-18's seven gold `CANNOT_CHECK` labels, ORION-23's 32
objective-gold facts, ORION-25's compromise ceiling — the record found is the
adverse one, and nothing here upgrades it.
