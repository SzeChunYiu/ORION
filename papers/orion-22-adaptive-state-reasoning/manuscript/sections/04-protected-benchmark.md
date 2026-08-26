# Protected matched-budget benchmark

## Resource regimes

Each protected item has one hidden requirement:

- `EASY = (0,0)`;
- `ACCESS = (2,0)`;
- `REASON = (0,2)`;
- `BOTH = (1,1)`.

Every policy receives total budget `B=2`. Success is exact: allocated state and reasoning resources must meet both requirements. No arm receives extra budget and unused resource is not retrospectively reassigned.

## Held-out families

The protected split contains **16 held-out families × 512 items**. Family regime proportions vary, while a uniform mixture component prevents degenerate single-regime families. Signal noise `sigma_f` ranges from `0.30` to `0.80` across families.

All adaptive arms receive the same pre-outcome signals

`s_c = c_req + Normal(0,sigma_f)`  
`s_r = r_req + Normal(0,sigma_f)`.

These signals contain no protected success outcome, verifier result or post-allocation feedback.

## Frozen policies

- `FIXED_11`: always `(1,1)`.
- `ADAPTIVE_STATE_ONLY`: choose `(2,0)` if `s_c>=1`, else `(0,0)`.
- `ADAPTIVE_REASON_ONLY`: choose `(0,2)` if `s_r>=1`, else `(0,0)`.
- `JOINT_FROZEN`: choose the feasible allocation in `{(0,0),(1,1),(2,0),(0,2)}` nearest to `(s_c,s_r)` under squared Euclidean distance, with frozen tie order.
- `ORACLE_JOINT`: exact hindsight requirement, diagnostic only.

No policy is tuned on protected family outcomes.