# Minimum Safe License Basis as Least-Privilege Agent Permission Synthesis R10

Date: 2026-08-26

Status: application specification for the R9 Minimum Safe License Basis theorem. Access-control/role-mining/set-cover literature is donor-owned; this note defines the exact transfer target and falsifiable experiment.

## 1. Operational mapping

Consider an agent or multi-agent workflow with a finite set of candidate permission/license coordinates `Lambda`.

A coordinate may represent, for example:

- an MCP/OAuth scope;
- permission to invoke one tool or tool class;
- permission to read a data source;
- permission to perform an external/write action;
- a tenant/jurisdiction/origin-specific capability;
- a reviewed approval class.

For each coordinate `lambda`, the typed policy graph determines a closure `Reach(lambda)` of operational claims that the coordinate can support under the declared positive rules/caps.

Freeze:

- required operational claims `Q_req` needed for a workflow;
- forbidden claims `Q_forbid` that this agent instance must not be able to authorize;
- candidate coordinate cost `w(lambda)` representing privilege, user friction, administrative cost, or another declared metric.

A coordinate is unsafe if `Reach(lambda)` intersects `Q_forbid`.

The **Minimum Safe License Basis** problem chooses a minimum-cost subset of the remaining coordinates whose closure union covers all claims in `Q_req`.

Strong license noninterference is essential: each coordinate's typed closure is computed independently, so selecting coordinates does not silently erase their identity and rerun an untyped union policy.

## 2. Exact theorem transfer

After computing typed closures and discarding unsafe coordinates, the optimization is weighted set cover on

`Cover(lambda)=Reach(lambda) intersect Q_req`.

Therefore:

1. exact minimum safe permission synthesis is NP-complete in general under the restrictions already proved for Minimum Safe License Basis;
2. for `m=|Q_req|`, bitmask dynamic programming gives an exact `O(|Lambda| 2^m)` post-closure algorithm;
3. classical greedy/weighted-set-cover approximation guarantees apply to the reduced coverage instance, with the approximation theorem credited to donor literature;
4. infeasibility is certified when no safe coordinate family covers every required claim.

The application-specific scientific question is whether typed closure filtering materially changes the permissions selected in real agent/tool workflows.

## 3. Why this is timely

Current agent platforms and MCP authorization specifications expose increasingly explicit permission surfaces. The 2025-11-25 MCP authorization specification emphasizes scope selection and least privilege; the 2026-07-28 specification adds further authorization hardening. Managed-agent platforms expose tool permission policies and role/app restrictions. These systems motivate a concrete synthesis problem: what is the smallest permission basis that supports a declared workflow without enabling forbidden actions?

The ORION contribution is not OAuth or MCP authorization itself. It is the typed proof-ownership layer used to compute what each candidate permission actually licenses downstream before solving the minimum safe basis.

## 4. Experiment A — MCP/tool least privilege

Freeze a public or internally reviewable MCP/tool catalogue with:

- tools/actions;
- authorization scopes or permission classes;
- preconditions and downstream capability rules;
- at least 50 workflow tasks grouped by role/persona;
- a predefined destructive/sensitive action set.

For each workflow:

1. derive `Q_req` from the task plan independently of the optimizer;
2. define `Q_forbid` from security policy before outcome review;
3. compute typed per-coordinate closures;
4. solve the exact minimum safe basis where tractable and a registered approximation otherwise;
5. execute the workflow in a sandbox using only the selected basis;
6. run adversarial attempts to reach forbidden claims.

Compare:

- all available permissions;
- per-tool naive minimum permissions without downstream closure;
- static role bundle;
- typed minimum safe basis;
- oracle/manual security-review bundle.

Metrics:

- number/weight of granted permissions;
- required-task completion rate;
- forbidden-action reachability;
- false denial;
- policy closure/evaluation time;
- optimizer time;
- reviewer agreement on `Q_req/Q_forbid`;
- gap between naive per-tool and typed downstream privilege.

A top-tier positive discriminator is a workflow where a seemingly minimal raw scope set still derives a forbidden downstream authority, while typed closure filtering selects a different safe basis without reducing legitimate task success.

## 5. Experiment B — multi-agent delegation

Candidate coordinates are delegation authorities between agents/tools. Required claims are the calls needed to complete a workflow; forbidden claims include cross-agent destructive or external effects.

The experiment asks whether minimum safe basis synthesis can remove unnecessary delegation edges while preserving task completion and preventing cross-agent privilege escalation.

Hostile cases:

- two individually harmless permission coordinates whose untyped union creates a forbidden hybrid proof;
- stale/retracted approval;
- origin mismatch;
- unsupported delegation cycle;
- an essential permission that makes the safe basis infeasible because it also reaches a forbidden claim.

The last case is important: the method must report `INFEASIBLE` rather than hide a policy-design conflict.

## 6. Integration with AuthorityGuard

The application has two stages:

1. **offline/administrative synthesis:** compute a minimum safe permission basis for a declared workflow portfolio;
2. **runtime authorization:** use typed fixed-point proof trees and merge checks to decide whether a particular action is currently licensed under the granted basis and current evidence/retractions.

The first minimizes attack surface. The second prevents runtime provenance/authority splicing.

## 7. Manuscript claim boundary

Potential evidence-backed claim:

> Typed downstream closure turns least-privilege agent configuration into an exact safe-basis optimization problem; on reviewed workflows it can remove permissions or scopes that look harmless locally but authorize forbidden actions after composition.

Not inferred:

- legal/compliance correctness;
- security against vulnerabilities outside the policy model;
- universal optimality of MCP/OAuth scope design;
- a claim that set cover or role mining is new.

## 8. Current external anchors

- Model Context Protocol authorization specifications, especially scope selection, token audience binding, and 2026 authorization hardening.
- AWS Prescriptive Guidance for agentic AI governance: identity, tool invocation permissions, agent-to-agent permissions, lineage and audit.
- OpenAI 2026 Codex safety guidance: controlled boundaries, approvals, and agent-native telemetry.
- Current agent-security provenance work (ProvenanceGuard, AuthGraph, Agent-Sentry, AttriGuard) provides the surrounding threat model but does not replace the typed safe-basis optimization.

A submission-grade prior-art audit must include access-control policy minimization, role mining, permission-set compression, set-cover-based authorization optimization, and policy-language synthesis before novelty language is frozen.
