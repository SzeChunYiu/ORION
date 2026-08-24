# Development packet — issue #1086 portfolio disposition

## Atomic question

Can the eight editorial/consolidation decisions at the top of issue #1086 be
made explicit and machine-checkable without changing any paper's scientific
authority?

## Scope

This change adds one portfolio-disposition record and structural tests. It does
not fetch benchmark outcomes, edit a manuscript claim, change an experiment,
or satisfy an external/protected-custody gate.

## Acceptance criteria

1. Decisions D1–D8 occur exactly once.
2. P1–P4 have four distinct named external evidence partitions.
3. P6–P8, P13–P14 and P15–Q3 consolidation dispositions are explicit.
4. P9 and P12 remain conditional; P10 remains an execution programme.
5. The record states that its scientific-authority delta is `NONE`.
6. Public data, AI execution, local hashes and same-owner CI are explicitly
   forbidden as substitutes for independent adjudication or protected
   confirmation.

## Verification

Run:

```bash
python -m pytest -q tests/unit/publication/test_issue_1086_portfolio_disposition.py
```

The issue boxes may be checked only for the eight portfolio decisions. No
shared-infrastructure or paper-level experimental box is closed by this packet.
