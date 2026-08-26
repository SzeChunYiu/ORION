# Paper D R11 — source-bound `agentgateway` authorization merge as a real SAFE control

## Why this result matters

Paper D was deliberately built to distinguish **unsafe provenance erasure** from legitimate modular composition. A credible provenance calculus must therefore return both kinds of answers. The synthetic OAuth/JWT/DPoP corpus gives hostile positive examples where coordinate erasure creates authority that no source coordinate owns. This note supplies the complementary real-system control: a current open-source agent gateway whose HTTP/MCP authorization merge is explicitly designed to preserve lower-precedence denies and mandatory requirements.

The result is a **SAFE theorem for one exact merge path**, not a security certification of `agentgateway` as a whole.

## Frozen external source

Repository: `agentgateway/agentgateway`

Commit: `e136c7458b0fe0f51378dd31ffd60ab2b6939fc2`

Load-bearing source blobs:

- `controller/api/v1alpha1/agentgateway/agentgateway_policy_types.go`: `e6274b96aa7e1a2d9d0bdf5c735f34951998ee88`;
- `controller/pkg/agentgateway/policyselection/selector.go`: `7ad08169d525baee6a62e074e334b9f3119213b6`;
- `controller/pkg/agentgateway/plugins/traffic_plugin.go`: `8dac971919257e025155a80c5da22fcd065c6b21`;
- `crates/agentgateway/src/store/policy.rs`: `10f2f00d0e3bd4fb0b38e069d177e547c45425b9`;
- `crates/agentgateway/src/store/binds.rs`: `203227d5d19ee29848821d72b06a373908ddb3bf`;
- `crates/agentgateway/src/http/authorization.rs`: `30e65076749448cb7b35d47ccf4303add7e6fec8`;
- `crates/agentgateway/src/mcp/rbac.rs`: `f6c19bdf0fdd889fbf04332a22305a8a568bd86b`.

The source establishes five facts used here:

1. the Kubernetes API rejects at least one mixed authentication combination inside a single policy (`traffic.jwtAuthentication` together with `backend.mcp.authentication`);
2. target selection is precedence-aware rather than a blind union of every candidate policy;
3. traffic fields are merged from less-specific to more-specific attachment points, with `inheritance=Override` able to lock a field against later replacement;
4. backend HTTP authorization and MCP authorization are **composed**, rather than overwritten, specifically so a broader deny is not erased; and
5. HTTP and MCP authorization share the same `RuleSets` Boolean semantics.

The upstream MCP regression test explicitly checks that a higher-precedence allow does not erase a base deny.

## Exact Boolean semantics

For authorization origin `i` and request `x`, define:

- `D_i(x)`: at least one DENY expression in origin `i` evaluates true;
- `R_i(x)`: every REQUIRE expression in origin `i` evaluates true;
- `H_i`: origin `i` contains at least one ALLOW expression;
- `A_i(x)`: at least one ALLOW expression in origin `i` evaluates true.

By construction `A_i(x)` implies `H_i`.

The source-level `RuleSets::validate` semantics are

`Accept_i(x) = not D_i(x) and R_i(x) and (not H_i or A_i(x))`.

`RuleSets::merge` concatenates the constituent rule sets, so the merged semantics are

`Accept_merge(x) =`

`[for all i: not D_i(x)]`

`and [for all i: R_i(x)]`

`and [(for all i: not H_i) or (there exists i: A_i(x))]`.

This formulation exactly reflects the source ordering: any deny wins; every require must hold; if at least one allowlist exists then at least one allow must match; a pure denylist defaults to allow after its denials are checked.

## Theorem 1 — mandatory-constraint preservation

If the merged authorization accepts `x`, then every origin's deny expressions are false and every origin's require expressions are satisfied.

### Proof

Immediate from the first two conjuncts of `Accept_merge`. No higher-precedence allow can launder a lower-precedence deny or failed require. ∎

This is the semantic property targeted by the upstream MCP regression test.

## Theorem 2 — origin-witness preservation

If the merged authorization accepts `x`, then at least one constituent authorization origin accepts `x` by itself.

Equivalently,

`Accept_merge subseteq union_i Accept_i`.

### Proof

If no origin has ALLOW rules, then all `H_i` are false. By Theorem 1 every origin has no triggered deny and all requires satisfied, so every origin accepts.

Otherwise the merged acceptance condition requires `A_j(x)` for some origin `j`. Theorem 1 gives `not D_j(x)` and `R_j(x)`, while `A_j(x)` supplies the final allowlist condition. Thus origin `j` accepts independently. ∎

### Consequence for Paper D

For this exact same-field merge operator there is **no hybrid-splicing authorization witness** of the Paper-D form “merged origin set authorizes but no selected origin independently authorizes.” The coordinate-erasure false-positive discriminator must therefore return SAFE on this path.

## Theorem 3 — the merge is not intersection semantics

Origin-witness preservation does **not** mean every constituent origin approves every merged request.

Two origins may contain disjoint allowlists. A request matching origin A's allowlist but not origin B's can be accepted by the merged policy, provided no deny or require fails. Thus

`Accept_merge` need not be a subset of `intersection_i Accept_i`.

This distinction matters operationally. `agentgateway` intentionally gives allow rules union semantics while making deny/require constraints cumulative. Paper D must not misclassify that declared policy algebra as evidence splicing merely because another origin would deny under its own unmatched allowlist.

## Theorem 4 — semantic algebra

At the level of request acceptance, repeated `RuleSets::merge` is associative and commutative. It is also idempotent with respect to acceptance semantics, although the source representation can contain duplicate rules after a self-merge.

### Proof

The merged decision depends only on set-union truth aggregates:

- whether any deny predicate is true;
- whether every require predicate is true;
- whether any allow rule exists; and
- whether any allow predicate is true.

These Boolean aggregations are associative, commutative and duplicate-insensitive. ∎

This yields a useful implementation invariant: source merge order can affect representation/order diagnostics but not the final authorization truth value for the frozen rule language.

## MCP corollary

`McpAuthorizationSet::merge` delegates directly to the same `RuleSets::merge`, so Theorems 1–4 apply unchanged to MCP tool/prompt/resource/task authorization after the CEL execution context is fixed.

The source contains a regression test in which a base `deny_all` MCP authorization is merged with a higher-precedence `allow true`; the merged result remains denied. This is a real positive control for the theorem's mandatory-constraint preservation claim.

## Bridge boundary: what this theorem does *not* certify

`agentgateway` also composes different policy fields: JWT authentication, authorization, backend authentication, MCP authorization, transformations, routing and other policies can originate at different attachment points. Some such cross-field composition is intentionally modular—for example, an authorization rule may consume claims produced by an authentication layer.

Paper D therefore requires a declared **bridge license** when information produced by one semantic field/origin is consumed by another. Theorems 1–4 certify only the same-field `RuleSets` merge. They do not prove that every cross-field composition in `agentgateway` is provenance-safe, nor do they assert a vulnerability in any cross-field path.

This is an important refinement of the paper's model: “no authority without one originating document” is too strict for deliberately modular systems. The correct invariant is “no authority without either a witnessing origin under the field algebra or an explicitly licensed cross-origin bridge.”

## Executable finite corroboration

The companion verifier exhausts abstract origin summaries through eight origins. Each origin is one of five request-relative states:

1. triggered DENY;
2. failed REQUIRE;
3. mandatory constraints satisfied, no ALLOW list;
4. mandatory constraints satisfied, ALLOW list present but unmatched;
5. mandatory constraints satisfied, ALLOW list present and matched.

It checks:

- exact equivalence between direct rule-summary evaluation and the closed-form merged formula;
- mandatory-constraint preservation;
- origin-witness preservation;
- semantic associativity/commutativity/idempotence;
- a non-intersection hostile control; and
- the higher-precedence-allow/base-deny control mirrored from the upstream MCP test.

The all-instance theorem is analytic; finite enumeration is implementation corroboration only.

## Scientific value

The source-bound SAFE result strengthens Paper D in three ways.

First, it shows the typed method has specificity: it does not label every multi-origin authorization system unsafe. Second, it gives a real design pattern that prevents one important class of provenance laundering—cumulative denies and requirements plus witness-preserving allow union. Third, it exposes the next research boundary sharply: same-field merge is safe here, while cross-field modular bridges require explicit ownership semantics rather than blanket origin isolation.

That is a stronger systems story than claiming a generic evidence-merging vulnerability.

## Authority ceiling

This note establishes a theorem about the exact source-bound `RuleSets` algebra and a real null control. It does not establish:

- security of the whole `agentgateway` project;
- correctness of every controller/runtime translation path;
- absence of implementation bugs;
- safety of arbitrary CEL expressions beyond their returned Booleans;
- safety of all cross-field policy bridges;
- deployed prevalence; or
- journal acceptance.
