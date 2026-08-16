# Paper IV research object — Verified Scientific Discovery

## Candidate claim after nearest-work challenge

ORION is not novel merely because it cites sources, fact-checks claims, or performs RAG attribution.  The scoped candidate is:

> A **non-escalating scientific authority pipeline** in which retrieved/generated content is proposal-only; claims are bound to immutable source content/provenance; attribution and support are checked separately; the checking mechanism itself must survive host-owned hostile tests and lane separation; evaluator/benchmark identity is protected; and unresolved evidence/independence/contamination produces `CANNOT_CHECK` rather than authority.

## Atoms

1. atomic claim decomposition;
2. exact source/evidence identity;
3. claim-to-source attribution;
4. semantic support/contradiction;
5. cross-source conflation;
6. content/influence provenance;
7. independent checker admissibility;
8. evaluator/benchmark protection;
9. search-time/train-test contamination;
10. authority promotion and abstention.

## Nearest work and mechanisms absorbed

### ProvenanceGuard — arXiv:2606.18037
Mechanisms: atomic claim decomposition, source-specific routing, NLI/token-alignment support checking, attribution comparison, allow/block verdict, repair-and-reverify; explicitly models cross-source conflation.

**Absorb:** source-specific claim routing; conflation benchmark; repair then reverify; source attribution as an axis independent from pooled factuality.

**Residual:** source-correct factuality is still weaker than ORION's scoped scientific authority and checker/evaluator governance.

### AttributionBench — ACL Findings 2024
Mechanism: standardized benchmark for whether generated claims are supported by cited evidence; shows automatic attribution evaluation remains imperfect.

**Absorb:** attribution is itself an evaluated model/component; no verifier is trusted solely because it outputs a score.

### Multi-source attribution / Attribute-First / SUnsET
Mechanisms: multi-source evidence, local evidence spans, generate-from-attributed-evidence ordering, unstructured evidence spans.

**Absorb:** claim-local evidence selectors; multiple evidence sources per claim; attribution-first generation option where it reduces post-hoc rationalization.

### FIRE — NAACL Findings 2025
Mechanism: iterative retrieval and verification; the verifier can request more evidence rather than accepting a fixed evidence budget.

**Absorb:** verification may reopen evidence acquisition; `insufficient evidence` is an action state, not a final negative judgment.

### CLAIM-BENCH / SciClaimHunt — 2025
Mechanisms: scientific claim↔evidence extraction/validation benchmarks and scientific-domain verification data.

**Absorb:** full-paper claim/evidence comprehension must be benchmarked separately from generic fact checking.

### ProvenAI — arXiv:2606.26449
Mechanisms: separates answer correctness, citation fidelity and behavioural influence of retrieved documents using leave-one-resource-out interventions.

**Absorb:** evidence was retrieved, cited and causally influential are distinct coordinates; cited-but-non-influential evidence should be visible.

### RewardHackingAgents — arXiv:2603.11337
Mechanisms: evaluator-tampering and train/test-leakage benchmarks, fresh workspace, patch tracking, runtime file-access logging, trusted reference metric.

**Absorb:** evaluator locking; sandbox isolation; access/patch telemetry; evaluation integrity as a first-class outcome.

### Search-Time Contamination — arXiv:2606.05241
Mechanisms: benchmark metadata/question/answer leakage detection for web-searching research agents.

**Absorb:** protected evaluation must account for what the search process could retrieve; public-answer access can invalidate a result even when the final answer is correct.

## ORION mechanics already present

Current main includes host-owned evidence resolution, content fingerprints distinct from record fingerprints, evidence-bound `AnswerRecord`s, lane-separated discriminating checks, adversarial host batteries, refusal of unauthorized waivers, trace/guard binding, protected evaluator concepts, verified-solution evidence requirements and append-only failure/negative history.

## Surviving candidate deltas

- `P4.D1.AUTHORITY_LATTICE`: correctness/citation are not themselves scientific authority; authority changes only on registered coordinates under compatible evidence/check/evaluator scope.
- `P4.D2.CHECKER_MUST_BE_VERIFIED`: a candidate check is accepted only if it discriminates positive cases from author-chosen negatives **and host-generated hostile negatives**; mere non-emptiness cannot verify an answer.
- `P4.D3.CONTENT_BOUND_EVIDENCE`: source references resolve through a host-owned index and bind exact content/provenance fingerprints; reference strings cannot launder authority.
- `P4.D4.INDEPENDENCE_AS_DATA`: author/answer/check/evaluator/process/evidence lineages are represented and compared rather than accepted as booleans.
- `P4.D5.FAIL_CLOSED_AUTHORITY`: missing evidence, unresolved attribution, evaluator compromise or contamination returns `CANNOT_CHECK/BLOCK`, not a soft confidence score that can be averaged into success.

## Falsifiers / benchmarks

### Authority laundering battery
- correct claim citing wrong source;
- same evidence ID with substituted content;
- same content under different source identities;
- verifier that returns true on any non-empty field;
- verifier trained/authored in the same lane as the answer;
- answer cites evidence it did not behaviorally use;
- benchmark answer retrieved during search;
- candidate modifies evaluator/metric code;
- candidate reads held-out labels.

### Baselines
- citation-presence checking;
- pooled-evidence NLI;
- ProvenanceGuard-style source-aware verifier;
- attribution + iterative retrieval verifier;
- ORION without hostile checker battery;
- full ORION authority pipeline.

### Metrics
- claim correctness;
- source attribution accuracy;
- support/contradiction F1;
- cross-source conflation detection;
- evidence-substitution detection;
- evaluator-tamper/leakage detection;
- false authority-promotion rate;
- correct `CANNOT_CHECK` rate;
- cost/latency.

## Paper claim boundary

Paper IV must not claim:
- first citation-aware LLM;
- first claim verification system;
- first provenance verifier;
- first evaluator-tampering benchmark.

It may test whether **content-bound provenance + independently admissible checks + protected evaluation + typed non-escalation** yields materially lower false scientific-authority promotion than attribution/factuality systems alone.
