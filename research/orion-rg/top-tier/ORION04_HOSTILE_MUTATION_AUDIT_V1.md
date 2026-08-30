# ORION-04 hostile mutation audit

`HANDOFF.md` claims the packet carries "hostile missing-branch, source-byte,
result-byte, removed-zero-detection controls" that "fail as required". Claims that
a checker rejects things are worth exactly as much as running them, so all four
were run against a copy of the committed packet, with an unmutated control.

## Results

| case | injected | `check_result` | `check_static` | `check_full_cover` |
|---|---|---|---|---|
| **control** | nothing | 0 `ACCEPT_ORION04_C0_31_D4_30` | 0 `STATIC_COVER_ACCEPT` | 0 `FULL_COVER_ACCEPT` |
| missing-branch | drop 1 of the 78 branches | **1 REJECT** | 0 accept | 0 accept |
| source-byte | append a comment to `engine_high_u128.c` | **1 REJECT** | 0 accept | 0 accept |
| result-byte | corrupt one run's `stdout_sha256` | **1 REJECT** | 0 accept | 0 accept |
| removed-zero | flip `all_solutions_zero` to `false` | **1 REJECT** | 0 accept | 0 accept |
| survivor | `branches[0].solutions` `0 → 1` | **1 REJECT** | 0 accept | 0 accept |

All five hostile cases are rejected and the control is accepted. The claim holds.

## Two things the table says that the claim does not

**`check_result` catches source edits.** Appending a comment to an engine's C
source is rejected, because `RESULT.json` records a `source_sha256` per engine and
the checker verifies it. The source-byte control is not a separate mechanism; it
is the result checker refusing a result whose declared sources no longer exist.

**The two cover checkers are not redundant confirmation.** They accept every one
of these mutations, correctly: they verify the branch cover's structure, which no
mutation touched. Only `check_result` is sensitive to results, sources or
branch counts. "All three checkers pass" is therefore **not** three independent
opinions on the theorem — it is one opinion on the result and two on the cover, and
a reviewer who reads it as triple redundancy would be overcounting the evidence by
two.

## Scope

This audits the packet's *checkers*, not the theorem. It shows the checkers detect
the five corruptions tried, and it does not show they detect every corruption. The
packet's own authority fields are unchanged: `finite_theorem_authority: true`,
`novelty_authority: false`, `external_independent_replay_complete: false`.
