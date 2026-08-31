# Formal problem and why joint allocation can be strictly valuable

For item `i`, let:

- `R_i` be current/raw state;
- `c_i` be resource spent constructing/restructuring state;
- `r_i` be downstream reasoning/search resource;
- `B_i` be the total envelope;
- `z_i` be information available before the protected outcome;
- `Y_i(c_i,r_i)` be verified success or quality.

The policy chooses `(c_i,r_i)` using `z_i`, subject to the common accounting contract. In the controlled benchmark the budget is scalar and exact: `c_i+r_i<=B`. In a real system the resource is a vector and comparison is Pareto-based unless a cost scalarization is frozen before protected outcomes.

## Policy classes

- `FIXED_STATE_FIXED_COMPUTE`: fixed allocation across items.
- `ADAPTIVE_STATE_ONLY`: may change state budget but not reasoning budget.
- `ADAPTIVE_REASON_ONLY`: may change reasoning budget but not state budget.
- `JOINT_STATE_REASONING`: may choose both under the same total envelope.
- `ORACLE_JOINT`: hindsight ceiling used only diagnostically.

Define

`joint_gain(B) = Q_joint(B) - max(Q_state_only(B), Q_reason_only(B))`.

A positive ORION-22 result requires `joint_gain>0` under the frozen comparison, not merely superiority to a fixed policy.

Consider a one-unit world containing two prospectively distinguishable regimes. In the access-limited regime success requires spending the unit on state construction; in the reasoning-limited regime success requires spending it on reasoning. A state-only adaptive policy cannot solve the latter and a reasoning-only adaptive policy cannot solve the former. A joint policy that sees the regime signal can spend the same unit at the valuable locus.

This existence argument is elementary and is not the empirical contribution. Its purpose is to identify the condition ORION-22 must test: **heterogeneity in the location of marginal computation value**.