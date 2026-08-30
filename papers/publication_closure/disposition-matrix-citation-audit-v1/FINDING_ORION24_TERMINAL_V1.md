# The disposition matrix cites a terminal ORION-24 does not record

`PUBLICATION_DISPOSITION_MATRIX_V1.md` is the document that drives filing order,
so a terminal it attributes to a paper should be one that paper records. For
ORION-24 it is not.

## What was checked

Issue #1701's ORION-24 list contains a verification box:

> Verify current control-plane terminal `CONTROL_PLANE_VERIFIED__EMPIRICAL_CAMPAIGN_NOT_RUN` where applicable.

Searching `main` for that string returns **one** file:

```
papers/PUBLICATION_DISPOSITION_MATRIX_V1.md
```

The matrix itself, and nowhere else in the repository. Not in ORION-24, not in any
other paper, and not on any remote branch carrying ORION-24.

The absence is checked rather than inferred from an empty result. ORION-24 has
127 files on `main` and a control pattern matches 76 of them, so the search
reaches the paper; and the branch sweep covers every `origin/*` ref, not just the
default one.

## What ORION-24 actually records

Its own terminals are a different family entirely:

| terminal | occurrences |
|---|---|
| `P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED` | 7 |
| `P14D_EXTERNAL_ACQUISITION_BLOCKED` | 6 |
| `P14E_SPECIFICATION_SEPARATED_SUPERIORITY_SUPPORTED` | 3 |
| `P14E_SPECIFICATION_SEPARATED_SUPERIORITY_GATE_NOT_MET` | 2 |
| `P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED` | 2 |
| `P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET` | 2 |

The matrix's own evidence column for row 24 points at
`PEER_REVIEW_READINESS.md` and its
`READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-CONFORMANCE_RESULT`, which
does exist. So the row cites a real artifact and then describes the gap using a
terminal string that artifact never uses.

## Why this is worth recording rather than fixing here

The substance may well be right: ORION-24's empirical campaign has not run, and
`P14D_EXTERNAL_ACQUISITION_BLOCKED` says something compatible. The defect is that
the matrix names a terminal as though quoting the paper, and a reader checking the
claim against the paper finds nothing. That is the same failure the
`ORION-P4`/`ORION-P3`/`ORION-P11` double prefixes had: an identifier asserted
against a subject that does not carry it.

The box cannot be ticked. "Verify current control-plane terminal ... where
applicable" has been executed and the answer is that no such terminal is recorded,
which is a verification result and not a verification.

Choosing the right repair -- adding the terminal to ORION-24, or rewriting the
matrix row to quote a terminal the paper does use -- is a decision about what
ORION-24's control-plane status actually is. That belongs to whoever owns the
paper's claim surface, not to an audit.
