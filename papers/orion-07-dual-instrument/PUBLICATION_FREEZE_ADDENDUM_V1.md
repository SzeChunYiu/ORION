# ORION-07 publication-freeze addendum V1

**Freeze date:** 2026-08-31  
**Status:** `CURRENT_EARNED_CEILING_FROZEN__AGGREGATE_RELIABILITY_SUCCESSOR_ONLY`

This addendum is part of the frozen ORION-07 paper-content packet. It records the
ceiling the paper's own checkers already assert, and grants no authority beyond them.

## Earned scientific ceiling

The submission terminal is `READY_TO_SUBMIT_SECOND_TIER`, target venue TMLR. TMLR
was the assigned route and is the correct one: its acceptance criterion is whether
claims are supported by convincing evidence, which is exactly the axis this paper
can meet.

The recorded terminal is
`Q3_PROSPECTIVE_CASE_SERIES_COMPLETE__N3_VALID__AGREEMENT_NOT_VALIDATION_COUNTEREXAMPLE_OBSERVED__NO_RELIABILITY_GENERALIZATION`.

**The central result is negative, and it is the point of the paper.** Three
prospectively frozen frontier questions were scored — V0, R1/QG-19 and R2/QG-20.
In all three the two instruments, a tool-capable LLM host diagnosis and a typed
deterministic non-LLM controller, agreed on the primary diagnosis and move. On R2
they were **jointly wrong**. The series therefore supports the methodological
separation *agreement is not correctness* on at least one prospectively scored
unit, which is a stronger and more useful finding than concordance would have been.

The evidence gate that previously blocked standalone submission is now closed **on
its own terms, by running the work rather than by relaxing the requirement**. The
earlier readiness record listed standalone evidence sufficiency as blocked because
only the V0 instance existed against a prospectively frozen requirement for
additional frontier-question instances.
`Q3_REPLACEMENT_PROSPECTIVE_PROTOCOL_V2.md` states the content-readiness condition:
both replacements validly frozen, both independent outcomes existing, both scored
and mapped, both results replaying, the harness defects explicitly disposed, and the
original contaminated slots still visible. `check_q3_completion.py` returns `PASS`,
and `check_q3_result_bindings.py` confirms both replacement results are sha-bound.

## Frozen boundary

This paper states its own limit in code, and the limit is sharp. Its checkers report
`AGGREGATE_RELIABILITY_AUTHORITY=FALSE` and
`SCIENTIFIC_AUTHORITY=NOT_GRANTED_BY_CHECKER`, with
`scientific_authority_delta = NONE_FOR_MANUSCRIPT_CLAIMS`.

That means the instrument is demonstrated on a small, prospectively frozen case
series, and **no aggregate reliability claim is licensed**. Passing the completion
gate is not the same as earning reliability authority, and this freeze does not
convert one into the other. The contaminated original slots remain visible rather
than being retired, so a reader can see what was replaced and why.

A larger prospective series against at least twenty currently unresolved public
items, selected before their outcomes exist, is successor work. It must not
retroactively promote the present bounded case series.

## Frozen content surface

The content packet consists of the canonical manuscript designated in
`submission/CANONICAL_SOURCE_DECISION.md`, the Q3 prospective protocol and its
replacement result bindings, `check_q3_completion.py` and
`check_q3_result_bindings.py`, the submission directory, and this addendum. The
ORION-07 claim is about deferred-outcome measurement of live research decisions; it
does not own the reliability of the systems it measures.
