# P17 Substrate Check Receipt V1

Status: **SUBSTRATE GREEN / SCIENTIFIC EFFICACY UNCHECKED**  
Date: 2026-08-20

Protocol: `P17_RESPONSIBILITY_CARRYING_STATE_PROTOCOL_V1.md`  
Implementation: `responsibility_carried_state_v1.py`  
Check: `check_p17_responsibility_carried_state_v1.py`

Terminal:

`P17_RESPONSIBILITY_CARRYING_STATE_SUBSTRATE_GREEN`

Finite hostile cases:

- supported responsibility + exact bound/context -> `USE_COMPILED`;
- approximate witness -> `CANNOT_CHECK`;
- unregistered higher-rung responsibility -> `CANNOT_CHECK`;
- registered reopen-trigger revision change with recoverable raw state -> `REOPEN_REQUIRED`;
- required-same semantic change -> `CANNOT_CHECK`;
- requested resource-bound mismatch -> `CANNOT_CHECK`;
- attempted evaluator/authority identity collapse -> rejected.

The substrate is explicitly non-authorizing and grants neither scientific nor novelty authority. Its research value remains prospective until an external evaluation compares responsibility-carrying state against unqualified compression/confidence-only/always-raw controls under matched task and resource budgets.
