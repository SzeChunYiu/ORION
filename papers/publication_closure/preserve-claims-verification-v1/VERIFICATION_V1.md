# The "preserve" claims across ORION-01…25 are intact on `main`

#1701 carries a family of boxes of the form *preserve <named result>* and
*recover <named packet>*. They are verification tasks: the question is whether the
named record still exists in the tree and still says what it said. Checked
directly against `main`.

## Method, and the control that caught a broken harness

Each claim was reduced to its most distinctive literal — a terminal string, a
figure, a named constant — and grepped under that paper's directory. Counts are
files matched.

The first two attempts returned `NOT_FOUND` for **every** claim, including one I
had already seen in eleven files minutes earlier. The cause was the shell: zsh does
not glob-expand a pattern held in a variable, so `grep` received a literal
`papers/orion-19-*` that matches nothing. **A positive control — a literal known to
be present — is what exposed it.** Without one, this document would have reported
fifteen fabricated absences. The counts below come from the third attempt, run with
literal paths and the control passing at 11 files.

## Results

| claim | paper | files |
|---|---|---|
| `CANNOT_CHECK_MOVE_COMPLETENESS` | ORION-01 | 22 |
| `kappa_R6M` local obstruction theorem | ORION-05 | 19 |
| TREC-COVID **+175.7%** reads | ORION-12 | 8 |
| corpus does **not** test necessity of other coordinates | ORION-13 | 43 |
| V4 fresh transfer **0.889** | ORION-15 | 2 |
| GLM-5.3 blinded harvest **22/24** | ORION-15 | 2 |
| #1692 **5/5** prospective density | ORION-17 | 5 |
| `UT3` custody record | ORION-19 | 15 |
| `P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3` | ORION-19 | 11 |
| `P11D` sparse-decoder negative | ORION-21 | 36 |
| `P11G_ARM_PLACEMENT` adjudication | ORION-21 | 10 |
| 31-repo / 14-org external campaign | ORION-23 | 8 |
| **6/6** registered corruptions | ORION-25 | 11 |

Every one is present. None is contradicted by another record found in the same
search.

## What this establishes and what it does not

It establishes that these results are **still in the tree and reachable**, which is
what "preserve" asks. It does not re-derive any of them, and it does not re-verify
the numbers inside the artifacts against a fresh run — several of those runs are
LUNARC campaigns or model-panel harvests that cannot be reproduced from a grep.

Where a claim has an adverse or `CANNOT_CHECK` character — ORION-12's failed recall
gate, ORION-13's necessity limit, ORION-19's zero executed UT3 grid cells,
ORION-21's `P11D` negative, ORION-25's compromise ceiling — the record found is the
adverse one. Nothing here upgrades any of them.
