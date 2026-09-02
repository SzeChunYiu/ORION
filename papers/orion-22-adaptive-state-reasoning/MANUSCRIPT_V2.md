# Adaptive State–Reasoning Co-Design under Matched Total Compute — V2

V2 is V1 with two redundant passages resolved and no change to any result,
number, protocol or authority binding. The introduction closed with two
paragraphs stating the same two points -- that P12A's causal superiority
interpretation is withheld, and that P12B is the stronger contract -- and
section 9 stated its motivation twice, repeating one bolded clause verbatim.
Both were leftovers from earlier edits. Each is now stated once, keeping the
fuller of the two wordings and the information only the shorter one carried.


> **Historical integrated review snapshot — noncanonical.** The editable publication source is `manuscript/sections/*.md`, the rendered paper is `manuscript/main.pdf`, and the sole current claim authority is `P12_ACTIVE_CLAIM_AUTHORITY_V5.json`
> (V5 preserves every V4 leaf, terminal, status and binding byte-for-byte and
> adds only the stop/go campaign leaf; V4 and V3 are retained as historical
> authorities). This snapshot preserves earlier review history and must not be used as the current submission source.

**ORION-22 · issue #665 · resource-accounting owner #664**  
**Evidence freeze:** 2026-08-21  
**Submission status:** `P12_SIGNAL_COMPLEMENTARITY_AUTHORITY_SUPPORTED`; controlled equal-action world

**Authority at the time of this snapshot** (historical; superseded by
`P12_ACTIVE_CLAIM_AUTHORITY_V5.json`): `P12_ACTIVE_CLAIM_AUTHORITY_V3.json`. It retains P12A's
comparison failure and activates only the prospectively frozen P12B equal-action
signal-complementarity result after locked-environment V1.1 revalidation.
**Submission status:** `P12A_SUPERIORITY_AUTHORITY_WITHHELD`; capability-matched P12B required

**Current authority:** `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`. The
historical P12A result and replay remain unchanged execution records. They do not
authorize signal-count superiority because the losing arms were also denied
allocations the winner could emit.

## Abstract

Test-time scaling is usually treated as a one-dimensional problem. State
construction creates a second place to spend inference resource, motivating a
two-axis allocation formulation. We report an exactly reproducible controlled
run over 16 held-out generated families. Its joint arm scores 0.8582 versus
0.4631 and 0.4528 for the named one-axis arms. A later hostile audit shows that
this is not a valid signal-count contrast: the joint arm can emit four
allocations while each losing arm can emit only two, and both baseline ceilings
are below the winner's achieved score. When action capability is matched, the
gain is +0.0408, the worst-family gain is +0.0020, and the frozen positive gate
is not met. The historical bytes remain; active superiority authority is
withheld. A prospectively frozen P12B then gives all three arms the same four
actions and scores exact allocation. Across 32 independent family RNG blocks,
the two-signal arm gains 0.253906 over the stronger one-signal arm (stratified
family-block 95% bootstrap interval 0.251221 to 0.256653); every family and every
fixed noise stratum passes. The result is controlled and does not authorize
naturalistic or external-system superiority.
withheld. P12A therefore motivates the resource-location hypothesis and defines
the corrected comparator contract, while a prospectively frozen P12B must test
it.

## 1. Introduction

Test-time computation has become an explicit design variable in modern reasoning systems. Systems allocate more tokens, samples, search nodes, verifier calls or iterative refinement to difficult instances. Recent work develops bandit, constrained-policy and learned adaptive allocation strategies, reinforcing a general lesson: uniform inference budgets waste computation when item difficulty is heterogeneous.

But difficulty itself has more than one source. Some tasks are difficult because the relevant structure is poorly exposed in the current representation. Others are difficult because substantial search or reasoning remains even after the right structure is visible. If a system spends all marginal budget on reasoning in an access-limited task, it reasons harder over the wrong state. If it spends all marginal budget on state construction in a reasoning-limited task, it repeatedly reorganizes information that was already accessible.

ORION-22 asks a stronger resource question:

> **Under one matched total budget, when should a system spend computation changing state, when should it spend computation reasoning over state, and can a prospective policy learn or exploit the difference?**

The system is modeled as

`raw/current state -> optional state construction -> downstream reasoning/search -> verified outcome`.

The paper makes four contributions.

1. **Two-axis inference formulation.** State construction and downstream reasoning are symmetric budgeted actions rather than free preprocessing plus paid reasoning.
2. **A strict comparator contract.** The joint policy must beat both adaptive-state-only and adaptive-reasoning-only policies at identical total resources, not merely a fixed baseline.
3. **Comparator-capability adjudication.** The protected run is retained beside
   the later finding that signal count and permitted allocations varied together.
4. **Equal-action successor.** P12B holds the four actions and budget fixed,
   varies only visible signals, and reports family-block uncertainty.

P12A's result is intentionally controlled and exactly reproducible, but its
causal superiority interpretation is withheld. Its purpose is to define the
stronger P12B contract: equal budget, equal actions, then a change in visible
signals.

## 2. Donor boundary and novelty

### 2.1 Adaptive test-time compute is prior-owned

Recent systems allocate inference compute dynamically based on predicted difficulty, value or resource constraints. Bandit formulations, constrained policy optimization, adaptive demonstration/generation strategies and “when to think” policies already own the primitive that different examples deserve different reasoning budgets. ORION-22 therefore does not claim adaptive inference allocation itself.

### 2.2 Dynamic state construction is also prior-owned

Retrieval, compression, context selection, query-conditioned memory and structured-state construction already adapt what a model sees. ORION-21 additionally supplies controlled evidence that construction can change accessibility. ORION-22 does not claim dynamic state selection as a new primitive.

### 2.3 Residual after subtraction

The live residual is the **competition between those actions under one resource boundary**:

> State construction and downstream reasoning are two places to spend test-time computation. A valid joint-allocation result must hold total resource fixed and strictly improve over policies allowed to adapt either axis alone.

In the current donor set, adaptive-compute methods optimize downstream reasoning/sampling/search or generation control; they do not make costed state construction and downstream reasoning symmetric decision variables under the same matched envelope and then require superiority over both one-axis adaptive controls.

## 3. Formal problem

For item `i`, let:

- `R_i` be current/raw state;
- `c_i` be resource spent constructing/restructuring state;
- `r_i` be downstream reasoning/search resource;
- `B_i` be the total envelope;
- `z_i` be information available before the protected outcome;
- `Y_i(c_i,r_i)` be verified success or quality.

The policy chooses `(c_i,r_i)` using `z_i`, subject to the common accounting contract. In the controlled benchmark the budget is scalar and exact: `c_i+r_i<=B`. In a real system the resource is a vector and comparison is Pareto-based unless a cost scalarization is frozen before protected outcomes.

### Policy classes

- `FIXED_STATE_FIXED_COMPUTE`: fixed allocation across items.
- `ADAPTIVE_STATE_ONLY`: may change state budget but not reasoning budget.
- `ADAPTIVE_REASON_ONLY`: may change reasoning budget but not state budget.
- `JOINT_STATE_REASONING`: may choose both under the same total envelope.
- `ORACLE_JOINT`: hindsight ceiling used only diagnostically.

Define

`joint_gain(B) = Q_joint(B) - max(Q_state_only(B), Q_reason_only(B))`.

A positive ORION-22 result requires `joint_gain>0` under the frozen comparison, not merely superiority to a fixed policy.

## 4. Why joint allocation can be strictly valuable

Consider a one-unit world containing two prospectively distinguishable regimes. In the access-limited regime success requires spending the unit on state construction; in the reasoning-limited regime success requires spending it on reasoning. A state-only adaptive policy cannot solve the latter and a reasoning-only adaptive policy cannot solve the former. A joint policy that sees the regime signal can spend the same unit at the valuable locus.

This existence argument is elementary and is not the empirical contribution. Its purpose is to identify the condition ORION-22 must test: **heterogeneity in the location of marginal computation value**.

## 5. Protected matched-budget benchmark

### 5.1 Resource regimes

Each protected item has one hidden requirement:

- `EASY = (0,0)`;
- `ACCESS = (2,0)`;
- `REASON = (0,2)`;
- `BOTH = (1,1)`.

Every policy receives total budget `B=2`. Success is exact: allocated state and reasoning resources must meet both requirements. No arm receives extra budget and unused resource is not retrospectively reassigned.

### 5.2 Held-out families

The protected split contains **16 held-out families × 512 items**. Family regime proportions vary, while a uniform mixture component prevents degenerate single-regime families. Signal noise `sigma_f` ranges from `0.30` to `0.80` across families.

All adaptive arms receive the same pre-outcome signals

`s_c = c_req + Normal(0,sigma_f)`  
`s_r = r_req + Normal(0,sigma_f)`.

These signals contain no protected success outcome, verifier result or post-allocation feedback.

### 5.3 Frozen policies

- `FIXED_11`: always `(1,1)`.
- `ADAPTIVE_STATE_ONLY`: choose `(2,0)` if `s_c>=1`, else `(0,0)`.
- `ADAPTIVE_REASON_ONLY`: choose `(0,2)` if `s_r>=1`, else `(0,0)`.
- `JOINT_FROZEN`: choose the feasible allocation in `{(0,0),(1,1),(2,0),(0,2)}` nearest to `(s_c,s_r)` under squared Euclidean distance, with frozen tie order.
- `ORACLE_JOINT`: exact hindsight requirement, diagnostic only.

No policy is tuned on protected family outcomes.

## 6. Results

The historical P12A protected terminal is
`P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED`; its historical superiority authority is
withheld under `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`. Current authority
at the time of this snapshot came from the historical, since-superseded
`P12_ACTIVE_CLAIM_AUTHORITY_V3.json`; the current authority is `P12_ACTIVE_CLAIM_AUTHORITY_V5.json`.
The historical protected terminal is
`P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED`. Current authority is
`P12A_SUPERIORITY_AUTHORITY_WITHHELD` under
`P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`.

| policy | mean verified success |
|---|---:|
| `JOINT_FROZEN` | **0.858154** |
| `FIXED_11` | 0.515503 |
| `ADAPTIVE_STATE_ONLY` | 0.463135 |
| `ADAPTIVE_REASON_ONLY` | 0.452759 |

The joint policy improves over the better one-axis adaptive policy by

**mean `+0.334717`**, family-block 95% bootstrap CI **`[0.286008, 0.382693]`**.

The **worst held-out family gain is `+0.158203`**. Joint versus fixed `(1,1)` gain is **`+0.342651`** on average. Every allocation respects the two-unit budget, the oracle ceiling holds in every family, and two fresh executions produce the identical SHA-256

`0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947`.

### 6.1 Comparator capability, not only budget

Both one-axis policies use pre-outcome signals, but each may emit only two
allocations while `JOINT_FROZEN` may emit four. Their perfect-signal ceilings,
0.475464 and 0.463623, are below the winner's achieved 0.858154. The historical
contrast therefore does not isolate the value of a second signal.

### 6.2 Regime interpretation

The large gain arises primarily because the restricted action sets cannot serve
opposite-axis and jointly limited regimes at any signal value. With identical
four-action sets, mean gain is 0.040771, the family-block interval is
[0.031006, 0.050659], and worst-family gain is 0.001953. The original gate then
returns `P12A_JOINT_ALLOCATION_SUPERIORITY_GATE_NOT_MET`.

### 6.3 Prospectively frozen P12B

P12B changes the estimand rather than a P12A threshold. Every arm may emit
exactly `(0,0)`, `(2,0)`, `(0,2)` or `(1,1)` under budget two. The endpoint is
exact required-allocation accuracy. The independent unit is one family RNG
block (`n=32`); 1,024 episodes within a family are technical observations.

Mean two-signal gain over the stronger one-signal arm is **0.253906**. The
stratified family-block 95% bootstrap interval is **[0.251221, 0.256653]**,
minimum family gain is **0.196289**, and fixed-stratum mean gains range from
0.213379 to 0.291138. All frozen gates and the byte-identical replay gate pass.
An append-only V1.1 revalidation reproduces these values under the repository
lock's CPython 3.12.13 and NumPy 2.5.2 environment; the original receipt remains
unchanged.
Terminal: `P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_SUPPORTED`.

## 7. Resource-accounting contract for real systems

The scalar controlled budget is intentionally clean. Real systems require vector receipts including:

- compiler/retrieval/preprocessing model and operations;
- state tokens/bytes and memory traffic;
- downstream generated tokens/recurrent steps;
- search nodes and verifier calls;
- tool calls and external latency;
- cache/recovery cost;
- model identity/capacity;
- end-to-end latency and reproducible energy where available.

A joint policy cannot “win” by shortening the downstream trace while hiding expensive retrieval or compilation upstream. Likewise a reasoning-only baseline cannot receive a larger model or search cap. If resource vectors are incomparable, the result should be a quality–resource Pareto frontier rather than a post-hoc weighted score.

## 8. Statistical analysis

The protected unit is the held-out family RNG block. P12A uses 16 family blocks.
P12B uses 32 independent family blocks, eight in each fixed noise stratum.
P12B's primary deterministic 20,000-resample bootstrap samples families within
each stratum, preserving the registered mixture; an unstratified family-block
interval is reported only as sensitivity.

The analysis does not pool items as if 8,192 individual trials were independent domains. Hyperparameters are frozen before protected evaluation. The worst-family gain is reported to prevent a favorable mean from hiding a family-level failure.

## 9. Relation to current adaptive-compute literature

Strategic test-time-compute allocation treats inference budget as a learnable or bandit decision across examples. Constrained policy approaches optimize accuracy under average compute. Adaptive in-context demonstration and generation methods jointly alter conditioning and generation effort. Recent “when to think” work likewise emphasizes selective reasoning to reduce unnecessary inference.

These results strengthen, rather than weaken, ORION-22's motivation: **adaptive
inference is crowded; the novel discriminator must be where the resource can be
spent.** ORION-22 supplies a budget portfolio containing state construction and
reasoning as distinct actions, but P12A does not establish strict superiority
over the named one-axis policies: their shipped action sets cap their attainable
scores below the joint arm's achieved score.
`P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json` therefore withholds superiority
authority pending a capability-matched P12B. P12B in turn establishes a bounded
signal-complementarity result once the actions are matched; it does not establish
real-system resource-locus superiority.

## 10. Limitations and real-system promotion gate

1. The protected benchmark is a controlled resource world, not an LLM, prover or production agent.
2. The pre-outcome signals are constructed measurements of resource need. Real signal quality may be substantially worse.
3. Scalar units are commensurate by construction. Real compiler work, tokens, verifier calls and latency are heterogeneous.
4. The joint policy is a simple frozen nearest-allocation rule; the paper does not claim it is optimal.
5. A real-system result must include strong compute-only and state-only adaptive baselines, not merely fixed context and fixed reasoning; P12B remains a constructed allocation world.
6. A broad superiority claim requires at least one held-out real LLM/procedural domain or verifier-backed search domain under matched end-to-end resource receipts.
7. If real tasks overwhelmingly favor one resource locus, a simpler one-axis policy may be preferable; ORION-22 predicts this as a regime condition rather than denying it.

## 11. Discussion

ORION-22 reframes test-time scaling as a **portfolio of computations**. “Think longer” is not the only adaptive action available to an intelligent system. It may be cheaper to parse, retrieve, compile, restructure or recover state so that less downstream search is required. Conversely, when state already exposes the relevant structure, additional preprocessing is wasteful and reasoning should receive the marginal budget.

P12A demonstrates the construction but not the key discriminator because equal
budget did not imply equal action capability. P12B repairs that controlled
estimand and finds a positive two-signal effect across the registered panel.
The protected benchmark demonstrates the construction but does not establish the
key causal discriminator. Equal total budget was real; equal action capability
was not. Family-level uncertainty cannot repair that estimand defect.

This leaves a concrete systems hypothesis: **test-time scaling curves may be
two-dimensional, but action capability must be held fixed across signal
ablations and all work must share one receipt.**

## 12. Conclusion

Adaptive inference may need to decide not only **how much** computation to spend
but **where** to spend it. ORION-22 supplies the formulation and an exact correction
to its first empirical discriminator, and a positive prospectively frozen
equal-action successor. The next scientific step is matched real end-to-end
validation; P12B's constructed world does not substitute for it.
to its first empirical discriminator. The next scientific step is a
prospectively frozen, capability-matched P12B; real end-to-end validation follows
only after that controlled contrast is sound.

## References

- Zuo, B. & Zhu, Y. *Strategic Scaling of Test-Time Compute: A Bandit Learning Approach.* ICLR 2026.
- Zuo, B., Zhou, D. & Zhu, Y. *Adaptive Test-Time Compute Allocation with Evolving In-Context Demonstrations.* Findings of ACL 2026, 35156–35173. DOI: 10.18653/v1/2026.findings-acl.1754.
- Zhai, Z., Li, B., Xiao, B., Li, M. & Wang, X. *Adaptive Test-Time Compute Allocation for Reasoning LLMs via Constrained Policy Optimization.* arXiv:2604.14853, 2026.
- *Learning When to Think: Adaptive Reasoning for Test-Time Compute Allocation.* arXiv:2608.20256, 2026.
- ORION-21 provides the controlled state-construction basis consumed by this paper; it does not transfer scientific authority to ORION-22.
