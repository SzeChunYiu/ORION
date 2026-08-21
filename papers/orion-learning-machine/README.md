# ORION learning machine — shared reproduction lane

**This is not a paper.** It has no publication identity, no claim ledger and no
paper number, and it is deliberately absent from `PAPER_DIRECTORIES` in
`src/orion/programme/superiority_terminals.py`. It is the shared **code,
experiments and committed results** that two paper directories cite.

Until now it carried no README at all, which is why opening it next to a row of
`paper-NN-*` directories was confusing. That is what this file fixes.

## What it holds

| Path | Contents |
|---|---|
| `framework/` | the shared implementation (22 files) |
| `experiments/` | the experiment drivers (13 files) |
| `results/` | committed results the papers cite (5 files) |
| `REPRODUCE.md`, `VERIFY_LOCAL_CLOSURE*.sh`, `*_MANIFEST_SHA256.txt` | the reproduction route and its digests |

**Authority:** `LOCAL_REPRODUCIBLE_CORE_ONLY`, as `REPRODUCE.md` states. Identity,
deterministic outputs and local hostile gates are in scope. External novelty,
theorem-statement faithfulness, scientific authority and journal acceptance are
not.

## Which papers it serves — read this part carefully

Its own `REPRODUCE.md` names them:

> **Papers:** `../paper-xx-executable-research-core/` and
> `../paper-xx-content-bound-math-evaluation/`

Those are the two **retired predecessor** identities, not the active P9 and P10.
The live identities are `paper-09-structured-epistemic-learning/` (#662) and
`paper-10-structured-problem-solving/` (#663), recorded in
`../PAPER_ALIASES.md`.

So this lane is the shared evidence base of the *predecessors*, retained because
the current papers still stand on it. That is the single most confusing thing in
the `papers/` tree, and it is not a mistake — it is why both predecessor
directories are kept rather than deleted. See `../PAPER_ALIASES.md` for the
succession, and `research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json`
for how they are recorded: predecessors that license a bounded claim and discharge
no `P<n>-U` terminal.

## Why it is not renamed or moved into a paper directory

Thirteen tracked files reference this path, including two CI workflows
(`p9-p10-publication-closure.yml`, `p10-publication-overlay-v2.yml`), three
benchmark scripts under `paper-xx-content-bound-math-evaluation/`, a live test
(`tests/unit/candidates/test_p9_p10_learning_machine.py`), and the manifest
digests in this directory bind file paths.

Splitting it into the two paper directories would also duplicate one shared
evidence base into two copies that can drift. Both papers cite the *same*
experiments; one lane is the correct shape. What was missing was a file saying so.
