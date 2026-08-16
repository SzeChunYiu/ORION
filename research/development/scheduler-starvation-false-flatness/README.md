# The driver stops "flat" while attainable verified closures remain

**Observed:** 2026-08-16, sandboxed CLI runs on main (post-#51), Claude lane.

## Measurement

Fresh state, `--rakl-transfer`, `--rounds 24`, both evidence roots registered:

```
run 1:  1298 -> 1295   verified_closures 3   stop: a_priori_frame_flat (4 rounds)
reruns: 1295 -> 1295   verified_closures 0   stop: a_priori_frame_flat (x3)
```

Meanwhile the transfer inventory demonstrably supports far more: #48/#49/#51 verified 3 + 103 + 152 closures through direct grading. The driver plateaus at 1295 with ≥250 verified-closable answers unconsumed.

## Mechanism (from the run ledger, not conjecture)

Across every round, `selected_question_ids` contained **only** VERIFICATION (133) and FAILURE (27) questions. The fixed breadth-first priority order feeds the 16-slot selection window from the top dimensions; with ~59 cells each still open in VERIFICATION and FAILURE, lower-priority dimensions — HANDOFF and DEPENDENCIES, exactly where the transfer source's verified-closable answers live — are never selected, so the source is never asked for them. Growth is flat for `flat_rounds_to_stop` rounds, and the run stops `a_priori_frame_flat`.

## Failure class

`FALSE_FLATNESS_BY_STARVATION` — a stop condition reports saturation while a registered route (the answer source) is demonstrably not exhausted for open questions. This is the incumbent SEARCH.ROUTE_STOP / SATURATE lesson in kernel form: nearby-selection flatness is not coverage, and a route-level stop must never be rounded up to frame-level flatness while unqueried route–question pairs remain.

## Bounded repair candidates (in governance order)

1. **Stop-condition guard (smaller, correctness-of-contract):** before declaring `a_priori_frame_flat`, mechanically check whether any registered source offers answers targeting open questions *outside* the selected window; if yes, the honest stop reason is `SELECTION_WINDOW_EXHAUSTED` (a route-level stop), not frame flatness. No selection-policy change; the bounded-saturation contract already requires route-coverage audit before flatness.
2. **Scheduler rotation (Class-B challenger):** starved-dimension rotation or answerability-aware selection. Per `development/MECHANICS_PROGRAM.md`, the V0 fixed policy is deliberate and any replacement must demonstrate better root-relevant progress under frozen evaluation before promotion — this path needs a development packet and matched parent/challenger runs, not a hot patch.

## Falsifier for this finding

Run the same fresh-state CLI configuration with a selection limit large enough to cover all open dimensions (or with repair 1 in place): if closures still plateau at 3, the starvation attribution is wrong and the blocker is elsewhere in the source/gate path.

Not repaired here: the measuring lane is not the scheduler's owning wave, and repair 2 is constitutionally gated.
