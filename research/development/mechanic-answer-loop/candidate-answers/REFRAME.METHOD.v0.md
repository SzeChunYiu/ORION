# Candidate answer — REFRAME.METHOD.v0

**Target dimensions:** TRANSITION_MODEL, AUTHORITY_SECURITY, INVARIANTS, STATE, VERIFICATION.
**Incumbent evidence:** RAKL `publication/papers/paper-03-method-evolution-mechanics/sections/04_experience_to_method_architecture.tex` (§Saturation and the invention gate; §Unified substrate and Self-Orion) and `sections/05_governed_upgrade_protocol.tex` @ `bd4ce50f` (entire section).

## Proposed step-specific contract

**Preconditions — the invention gate (fail-closed creativity).** A method/operator challenger may be proposed only after a bounded audit supports all of: (1) relevant knowledge/operator/path axes flat under the registered search window; (2) residual stable across independent routes; (3) ordinary causes excluded (missing source detail, wrong context, unavailable tool, implementation failure, verification debt); (4) cross-domain transfer routes searched or bounded; (5) explicit evidence of a representation or method-basis gap. A system that invents whenever it is confused is failing retrieval, not being creative.

**State — four events that must never collapse:**

```text
code exists ≠ code is deployed ≠ improvement is supported ≠ method is the governed incumbent
```

**Transition model — challenger lifecycle DAG (not a destructive sequence).**

```text
OBSERVED_PATHOLOGY -> UPGRADE_HYPOTHESIS -> PREREGISTERED -> CHALLENGER_IMPLEMENTED
 -> DEVELOPMENT_VALIDATED -> FRESH_ASSURANCE_PENDING
 -> {ASSURED | REJECTED | META_OVERFIT | CANNOT_CHECK}
 -> GOVERNANCE_APPROVED -> PROMOTED -> ACTIVE_PROMOTION_ATTESTED -> MONITORED
```

Rejected/superseded variants remain negative history; the previous incumbent remains a rollback target. Preregistration packet (frozen before outcomes): parent method identity, source episode/diagnosis ids, change class, alternative diagnoses, mechanism, affected contracts, predicted meta-QoIs with material-effect thresholds, negative controls, hostile near-misses, fresh-assurance reserve, resource contract, rollback plan. A result predating its packet is retrospective calibration only.

**Change classes.** A: implementation (regression + invariants, no capability claim). B: workflow/method (matched parent/challenger tests + fresh transfer + hostile near-misses + protected fresh assurance). C: constitutional (what may mint authority, evaluator independence, promotion rights) — never auto-promoted; human-visible amendment review.

**Authority/security — anti-self-certification.** Seven separated roles (observer, proposer, challenger engineer, development evaluator, fresh-assurance evaluator, governance authority, post-promotion attestor); same-session labels create no independence. Incumbent proposition (with proof): if the challenger cannot modify the protected evaluator/packet/thresholds/credentials and promotion requires a content-bound external certificate, the challenger's own output cannot establish its promotion. Known incumbent gap to avoid: a promotion API accepting a caller-provided `governance_approved` boolean is declaration-bound, not content-bound — ORION must bind attestation to exact candidate + assurance verdict + constitution epoch + approving process.

**Invariants.** Evaluator frozen within an evaluation epoch; evaluator evolution is a separately governed parent mutation at epoch boundaries. Operator overrides are modeled explicitly (`OPERATOR_OVERRIDE` with deviation, blockers, rollback) and create zero evolution-evidence credit — deployed-before-assured stays method-provisional. Development evaluation exposed to the optimizer is no longer blind; fresh assurance consumes an exposure budget.

## Known-answer / hostile test candidates

1. Challenger with passing development metrics but no fresh-assurance packet → cannot leave `DEVELOPMENT_VALIDATED`.
2. Hostile: challenger output sets its own `governance_approved` → promotion refused (content-bound attestation missing).
3. Hostile: repeated failures with no invention-gate audit → `REFRAME.METHOD` refuses to propose a new operator; emits the missing-gate residual instead.

## Not licensed

That the full seven-role separation is operable by the current multi-agent development setup is itself an empirical open coordinate — worth an explicit readiness check before Phase 3 (Governed Self-ORION).
