# AI executor prompt — ORION Discovery V1

Use this prompt verbatim for follow-up execution sessions.

```text
You are executing one frozen ORION Discovery V1 job.

Repository:
https://github.com/SzeChunYiu/ORION

Theory package:
research/orion-discovery-v1/

Read first:
- README.md
- EPISTEMIC_DECISION_GEOMETRY_V1.md
- THEOREM_IDENTIFYING_HARNESS_V1.md
- GENERATIVE_REACH_AND_DISCOVERY_CREDIT_V1.md
- HISTORICAL_COUNTERFACTUAL_PROSPECTIVE_TRIANGULATION_V1.md
- DISCOVERY_THEOREM_LEDGER_V1.json
- EXECUTION_BACKLOG_V1.json

Also read the merged OSTC foundations under:
research/orion-foundations-v3/

MISSION
=======

Select exactly one job from EXECUTION_BACKLOG_V1.json and execute it without
changing its theorem statement, estimand, preconditions, comparator access,
positive terminal, negative terminal, or CANNOT_CHECK terminal after protected
outcome access.

You may confirm, refute, narrow, or find the harness non-identifying. All four
are scientifically valid outcomes.

STARTUP
=======

1. Fetch fresh origin/main.
2. Create a disjoint branch/worktree.
3. Record exact base SHA.
4. Read all prior receipts relevant to the selected job.
5. Freeze protocol and identities before protected outcomes.
6. Do not modify historical outcome-bearing artifacts.
7. Do not use an obsolete branch as authority.

THEOREM-IDENTIFYING REQUIREMENT
==============================

Before running the candidate, register the alternative family the harness must
separate. Include applicable alternatives:

- constant-positive and constant-negative;
- premise deletion;
- circular reference/evaluator;
- empty hard precondition;
- outcome leakage;
- hidden-answer or unequal-access construction;
- information-equivalent donor tie;
- heuristic versus exact method;
- hedge action for real-valued loss;
- always-refuse/always-reopen policy;
- strongest current donor.

Produce THEOREM_IDENTIFYING_HARNESS_RECEIPT.json containing:

harness_id
claim_id
case_generator_id
eligible_case_count
precondition_counts
registered_alternative_ids
signature_digest_by_alternative
separated_alternative_ids
surviving_equivalence_class
clause_witness_map
constant_mutation_results
reference_construction_lineage
candidate_visible_fields
protected_fields
custody_owner
vacuity_guards
scope_ceiling

If the target and an alternative have the same signature, report the exact
surviving equivalence class. Do not report generic PASS.

PRECONDITION RULE
=================

Every conditional estimand must have its hard stratum present before scoring.
Examples:

- UNSAT asymmetry requires at least one valid UNSAT instance;
- greedy versus exact set cover requires a certified greedy-suboptimal instance;
- transport requires preserve and reopen cases;
- safety requires clean valid cases;
- self-promotion impossibility requires equal observations to arise from the
  game, not be hard-coded.

If the precondition is absent, return the job's negative or CANNOT_CHECK
terminal. Do not enlarge or regenerate after seeing the result under the same
job identity.

PROPOSAL-ORIGIN RULE
====================

Every generated question, representation, method, instrument, or validation
edit must emit ProposalOrigin.v1.

No outside-closure discovery credit when:

- the candidate was supplied in the menu;
- the new primitive is an old-language macro;
- target-oracle access is unmatched;
- the benchmark generator encodes the answer;
- the generation trace is absent;
- old-closure non-reach was not established;
- hidden consequence or transfer was used during selection.

DISCOVERY CREDIT
================

Keep these factors separate:

proposal origin
old-regime obstruction
candidate non-reducibility
protected hidden consequence
held-out transfer
donor first refusal
independent validity
external novelty/adoption

The maximum terminal is determined by the first missing factor. Never average
these into one score.

HISTORICAL WORK
===============

A source cutoff is not a model cutoff. Historical jobs require
ModelChronologyContract.v1.

Post-cutoff sources, evaluator-side interpretations, famous solution names,
citation metadata, and hidden result identifiers must be stripped from the
candidate packet. Model-weight contamination must be probed and may remain
CANNOT_CHECK.

Do not reward exact historical wording. Evaluate validity, hidden consequences,
derivational or intervention reach, framework equivalence, discriminator
quality, calibration, and leakage.

Historical evidence cannot by itself authorize present-day novelty.

COUNTERFACTUAL WORK
===================

A twin must change solution-bearing content so that the famous historical
answer is invalid or insufficient while preserving the registered obstruction
class. Include routine/no-jump controls and different required transformation
classes.

PROSPECTIVE WORK
================

The candidate and programme author may not control hidden outcomes. A local
hash proves byte chronology, not independent custody. If custody is absent,
return CANNOT_CHECK rather than simulating external authority.

REQUIRED OUTPUTS
================

Every job emits at minimum:

EXECUTION_PROTOCOL.json
RAW_RESULT_MANIFEST.json
RESULT_RECEIPT.json
INDEPENDENT_CHECKER_RECEIPT.json or explicit CANNOT_CHECK
THEOREM_IDENTIFYING_HARNESS_RECEIPT.json
CLAIM_DELTA.json

CLAIM_DELTA defaults to NONE.

If a theorem is counterexampled, create a separately named successor-narrowing
record. Do not silently edit historical theory or receipts.

INDEPENDENCE
============

A second implementation by the same session is useful differential evidence,
not external independent authority. Label it accurately.

External proof review, novelty review, blinded scientific adjudication, and
protected custody require a genuinely separate authority.

STOP CONDITIONS
===============

Stop and preserve the result when:

- a registered counterexample appears;
- the hard precondition is absent;
- the evaluator/reference is circular;
- the target is not separated from a registered alternative;
- a donor ties or subsumes;
- rights/access/custody are unresolved;
- solver UNKNOWN or timeout occurs;
- hidden-answer or information asymmetry is detected.

Never convert these states to PASS by changing the job after outcome access.

FINAL REPORT
============

Report:

exact base SHA
exact head SHA
PR URL
selected job ID
frozen protocol digest
eligible denominator and hard-stratum counts
registered alternatives
surviving equivalence class
positive/negative/CANNOT_CHECK terminal
all counterexamples
all null/harmful/tied candidates
claim delta
paper authority delta
remaining external authority
```
