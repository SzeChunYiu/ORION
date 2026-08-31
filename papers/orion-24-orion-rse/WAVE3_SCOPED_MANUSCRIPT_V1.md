# Fail-closed evaluation infrastructure for autonomous research software engineering

## Abstract

Evaluating frontier agents on research-software-engineering tasks requires more than a runnable harness. A valid result must bind independently sourced tasks, actual executions, neutralized evidence packets, blinded or mechanical adjudication, immutable promotion decisions, failure-inclusive denominators and resource accounting. We specify a fail-closed evaluation architecture for these requirements and report its decisive preflight boundary. None of eight required external-input artifact classes was present, so execution was never authorized. Consequently, the registered external scientific endpoints remain undetermined: no claim is made about frontier-agent performance, useful-discovery recall, false-promotion rate or the benefit of retaining negative history. The contribution is a specification and handoff contract, not a completed harness or external efficacy study. It defines role-separated custody, task and arm contracts, fail-closed receipts, blinded adjudication rules, longitudinal history states, endpoint reconstruction and hostile controls that a future implementation must satisfy. By separating readiness to measure from outcome authority, the architecture prevents interface artifacts, internal demonstrations or missing prerequisites from being promoted into empirical evidence. A historical project label describing an “executable handoff” denotes only the specification handoff, not implemented execution.

## 1. The evaluation problem

Research software engineering combines deterministic implementation work with scientific judgment, incomplete evidence and infrastructure failure. A system can pass unit tests while making an invalid scientific inference, or produce a plausible research artifact that cannot be mechanically adjudicated. External evaluation must therefore answer two different questions.

1. Did an agent execute the registered task and produce an admissible artifact under the same information, tools, budget and stopping authority as its comparators?
2. Does independent outcome authority judge that artifact useful, valid and within scope?

A public interface, schema or dry run answers neither question by itself. It demonstrates readiness to measure, not the value being measured.

## 2. Wave 3 preflight result

The external-acquisition preflight required eight artifact classes. The realized completeness count was:

| Required artifact classes | Present artifact classes | Execution status |
|---:|---:|---|
| 8 | 0 | not authorized |

The blocked preflight is retained under the project record associated with issue #1351 and the terminal `P14D_EXTERNAL_ACQUISITION_BLOCKED`. The eight-count is a file-class inventory, not a count of attempted external cases, solicitations or failed acquisitions. It is not repaired by replacing external cases with internally authored demonstrations.

Because the admissible external denominator is zero, the external endpoints `CANNOT_CHECK`. The paper does not estimate:

- useful-discovery recall;
- false-promotion or false-rejection rates;
- relative frontier-agent performance;
- cost per valid useful discovery;
- blinded-adjudication validity; or
- the causal effect of retaining negative history.

The preflight failure is a custody boundary: external evidence is a separate resource that a specification cannot manufacture from its own completeness.

## 3. Contribution and claim boundary

The finished Wave 3 contribution is a fail-closed evaluation specification. It describes the chain from task acquisition to endpoint reconstruction and makes the absence of required external inputs visible before execution.

The paper does not claim an implemented end-to-end harness or external superiority. It also does not describe AI adjudication as human expert authority, agreement as validity or repository CI as independent scientific replication.

## 4. Custody model

A valid evaluation binds seven roles.

1. **Task acquisition and freezing.** Selects tasks under prospectively frozen inclusion rules and records source, licence, privacy constraints and task-family stratum.
2. **Agent execution.** Runs each arm under matched tools, network policy, repository snapshot, resource budget and stopping authority.
3. **Packet neutralization.** Removes system identity, expected labels, internal promotion decisions and author narrative before non-mechanical adjudication.
4. **Outcome adjudication.** Applies a mechanical oracle where possible, otherwise a frozen blinded rubric with independent judgments and an abstention rule.
5. **Promotion calculation.** Reconstructs registered endpoints without deleting failed, blocked, ambiguous or abstained cases.
6. **Archival custody.** Preserves exact inputs, outputs, receipts, judgments, conflicts and negative history.
7. **Independent replay.** Recomputes the endpoint table from immutable artifacts without importing execution-controller decision logic.

No single role is allowed to rewrite the bytes controlled by another after outcome access.

## 5. Task portfolio

The architecture requires a portfolio broad enough to expose different failure modes while preserving stratum-specific reporting.

### 5.1 Deterministic software repair

Tasks have hidden tests or another mechanical oracle. These cases measure whether the agent can produce a correct patch and whether the receipt corresponds to the current execution rather than a stale artifact.

### 5.2 Scientific artifact verification

Tasks contain a mechanically checkable core, such as a content-bound result, proof receipt, data transformation or reproduction claim, together with scientific scope that must be audited.

### 5.3 Ambiguous research judgment

Tasks require blinded adjudication because no complete mechanical oracle exists. The rubric, conflict rule and abstention rule must be frozen before judgments are read.

### 5.4 Negative controls

The correct outcome is to abstain, block a promotion or preserve an adverse result. These cases test whether the system equates activity with success.

### 5.5 Infrastructure failure

Tasks deliberately exercise timeouts, unavailable dependencies, interrupted hosts or incomplete evidence. A failed execution must remain a failed execution; it cannot inherit the outcome of a prior run.

Easy deterministic cases cannot hide failure in research judgment. Every primary endpoint is reported by stratum as well as in aggregate.

## 6. Fair comparator contracts

A comparison is invalid when one arm receives less information, fewer actions, a lower budget or weaker stopping authority. The registered architecture therefore calls for matched contracts for:

- a strong direct frontier-agent baseline without ORION-RSE governance;
- an artifact- or issue-centric baseline without negative-history mechanics;
- the full ORION-RSE system;
- ORION-RSE without negative history;
- ORION-RSE without independent promotion authority; and
- a safe-abstain or random control where meaningful.

The task packet, repository snapshot, tools, evaluator access, retry policy, budget and stopping authority must be identical except for the registered intervention.

## 7. Blinded and mechanical adjudication

The authority hierarchy is:

1. deterministic or mechanical oracle;
2. blinded domain-expert adjudication;
3. blinded independent AI adjudication for residual non-mechanical questions, explicitly labelled as AI authority.

For non-mechanical primary outcomes, at least two independent judgments are preserved together with rationales, abstentions and disagreements. Agreement is reported as a property of the judging process, not as proof that the judgments are correct. A deterministic oracle cannot be overruled post hoc by selecting a more favorable subjective judge.

Packets presented to adjudicators exclude arm identity, system name, expected outcome, internal promotion decision and project narrative. A leakage audit is part of the evidence packet.

## 8. Longitudinal negative-history experiment

The architecture is designed to test whether preserving adverse history improves later research work. A decisive experiment would compare:

- full immutable history;
- no history;
- positive-only history;
- compressed summary history; and
- shuffled or non-causal history.

Agent, task family, tools, resource budget and stopping authority must remain fixed. Outcomes should include repeated-failure rate, useful-discovery recall, false promotion, false rejection and cost. History can be corrected only by an additive superseding record; silent deletion changes the experimental state.

The present paper specifies this experiment but does not report a positive or negative effect because execution never passed the external-input preflight.

## 9. Endpoint construction

A complete external run would preserve raw counts, denominators and uncertainty for:

- adjudicated useful outputs recovered;
- promoted outputs judged invalid, unsupported or unsafe;
- observable false rejection or abstention cost;
- repeated failures across ordered episodes;
- forbidden mutations and evidence deletions;
- adjudicator disagreement and abstention;
- agent and tool calls, tokens, wall time and compute;
- monetary cost where available;
- cost per valid useful discovery; and
- infrastructure-failure and `CANNOT_CHECK` rates.

Failed acquisition, execution or adjudication cases remain visible under the frozen denominator rule appropriate to each endpoint. An endpoint calculator may not silently drop a case because its absence makes the result look cleaner.

## 10. Fail-closed receipts

Every execution receipt binds at least:

- task and arm contract digest;
- repository and harness revision;
- agent/model identity and tool policy;
- start and terminal states;
- current artifact hashes;
- resource use and retry history;
- infrastructure failures;
- adjudication packet identity; and
- authority disposition.

A receipt cannot prove that a run occurred merely by being syntactically valid. Independent replay verifies the referenced current artifacts, execution occurrence and endpoint membership. Missing, stale, conflicting or malformed receipts lead to a blocked or failed terminal.

## 11. Hostile controls

The required hostile suite includes:

1. a valid-looking receipt for a task that never executed;
2. substitution of a stale successful artifact after a failed current run;
3. promotion with missing adjudication;
4. leakage of one arm label or expected outcome into a blinded packet;
5. post-hoc selection of the favorable judge after disagreement;
6. deletion of failed or blocked cases from a denominator;
7. removal of negative history before a repeated-failure episode;
8. a comparator deprived of an action available to ORION-RSE;
9. resource overrun counted as ordinary success; and
10. subjective adjudication contradicting a deterministic oracle.

Every mutation should lead to the prospectively frozen safe terminal. A list of controls is not empirical validation; it defines obligations for a future implementation.

## 12. Reproducibility and handoff

The implementation, claim ledger, manuscript materials and execution/evaluation schemas are maintained under:

`papers/orion-24-orion-rse/`

The retained preflight boundary is documented in the repository history. The wider successor handoff is indexed in the associated artifact package.

A future external execution root should contain:

- `PROTOCOL.json`;
- `TASK_ACQUISITION_MANIFEST.json`;
- `AGENT_ARM_CONTRACTS.json`;
- `CUSTODY_BINDING.json`;
- `ADJUDICATION_RUBRIC.json`;
- neutralized per-case packets;
- exact execution receipts and artifacts;
- raw adjudications and conflict receipts;
- negative-history snapshots;
- a resource ledger;
- an immutable endpoint table;
- `RESULT.json` and `AUTHORITY_DISPOSITION.json`;
- an adverse/null/`CANNOT_CHECK` ledger; and
- an independent checker and hostile tests.

Continuous integration may verify content bindings and endpoint reconstruction. It must not pretend to rerun unavailable external agents or transform interface readiness into outcome authority.

## 13. Related evaluation and reporting work

Research-engineering and scientific-reproduction benchmarks already define
realistic tasks, environments, resource budgets and graded work products.
RE-Bench compares agents and human experts on open-ended research engineering;
CORE-Bench and PaperBench evaluate computational and paper-level reproduction.
Rollout Cards treats retained rollout records, failure counts and reporting rules
as the unit of agent-evaluation reproducibility. These works own the empirical
benchmark and reporting foundations. The residual here is only a fail-closed
specification that composes task custody, matched arm contracts, neutralized
adjudication, failure-inclusive denominators and endpoint reconstruction, while
making its blocked preflight explicit. No novelty authority is claimed for any
component in isolation.

## 14. Limitations

The primary limitation is decisive: none of the eight required external-input artifact classes was present, so execution was unauthorized and the registered scientific endpoints cannot be evaluated. The eight classes are not an acquisition denominator. The specification has not established that its packet neutralization works in a live multi-provider study, that the negative-history intervention is beneficial or that its governance overhead is cost-effective. The listed schemas, calculators and hostile controls remain implementation obligations unless separately bound as executable artifacts.

These limitations prevent an efficacy conclusion. They do not erase the engineering contribution or justify substituting internal demonstrations for the missing denominator.

## 15. Scientific disposition

The exact Wave 3 terminal is:

`ORION24_EXTERNAL_ACQUISITION_BLOCKED__EXECUTABLE_HANDOFF_COMPLETE`

The present paper is an evaluation-specification and blocked-preflight paper. Future external evidence must begin under a new frozen protocol and preserve the zero-of-eight required-class record additively. A future positive result may supersede the external endpoint status, but it may not rewrite the blocked preflight as an attempted external study.

## 16. Conclusion

Reliable evaluation of autonomous research software engineering requires matched agent contracts, independent task custody, actual execution, blinded or mechanical outcome authority, failure-inclusive denominators and independent endpoint reconstruction. The proposed specification composes these requirements. Wave 3 did not pass preflight: zero of eight required external-input artifact classes was present, so no external scientific denominator was formed. The finished claim is a fail-closed evaluation specification with an honest blocked-preflight result, not executable infrastructure and not frontier-agent superiority.

## References

- H. Wijk et al. *RE-Bench: Evaluating Frontier AI R&D Capabilities of Language Model Agents Against Human Experts.* arXiv:2411.15114, 2024.
- Z. S. Siegel, S. Kapoor, N. Nadgir, B. Stroebl & A. Narayanan. *CORE-Bench: Fostering the Credibility of Published Research Through a Computational Reproducibility Agent Benchmark.* arXiv:2409.11363, 2024.
- G. Starace et al. *PaperBench: Evaluating AI's Ability to Replicate AI Research.* arXiv:2504.01848, 2025.
- C. Masters, Z. Liu & S. V. Albrecht. *Rollout Cards: A Reproducibility Standard for Agent Research.* arXiv:2605.12131, 2026.

## Data and code availability

The specification, claim records and preflight materials are available in the repository. No external case dataset supports the present paper's endpoints; the missing required artifact classes and unauthorized execution are part of the reported boundary.
