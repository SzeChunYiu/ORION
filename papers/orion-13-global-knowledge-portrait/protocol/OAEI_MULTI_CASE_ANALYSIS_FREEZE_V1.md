# OAEI_MULTI_CASE_ANALYSIS_FREEZE_V1 — pre-execution analysis contract

- **Canonical artifact:** `OAEI_MULTI_CASE_ANALYSIS_FREEZE_V1.json` (same directory). JSON is authoritative.
- **Frozen (UTC):** 2026-08-24T10:20:24Z — `FROZEN_BEFORE_ANY_OAEI_SCORING`, `outcome_accessed: false`,
  `execution_status: CANNOT_CHECK__NO_OAEI_EXECUTION_IN_REPOSITORY`.
- **Issue:** SzeChunYiu/ORION#1086 (ORION-13 boxes 2, 3, 4, 5; box 1 is carried by the licence manifest).
- **Licence manifest binding:** `../gold/OAEI_TRACK_LICENSE_MANIFEST_V1.json`. No reference alignment,
  dataset payload or matcher output was opened before this freeze; MELT has not been executed here.

## What this freezes

| Element | Frozen rule |
|---|---|
| Gold | Official RDF reference alignments only; a suite whose gold cannot be lawfully obtained is dropped as CANNOT_CHECK, never substituted with a self-built gold |
| Scoring | MELT, REQUIRED; not executed in this repository at freeze time |
| Case composition | bench23 MUST be paired with ≥1 natural ontology-pair track; bench23 alone is insufficient (single seed ontology) |
| Arms | ORION full policy (candidate) + LogMap + AML; unavailable arms stay CANNOT_CHECK — no weak-proxy substitution |
| Inference unit | Ontology pair or track — never the correspondence row; paired bootstrap over that unit |
| Pass gate | 100% valid standard alignment output AND (macro-F1 ≥0.03 with lower CI >0 OR precision noninferior within 0.01 plus recall gain ≥0.05 with lower CI >0) AND zero increase in logical incoherence |

## Comparator evidence bound

LogMap and AML participation in OAEI 2025 Conference is recorded from the results page
(`https://oaei.ontologymatching.org/2025/results/conference/index.html`, fetched 2026-08-24T10:20:24Z,
page sha256 `802f5fb3…92d3`; LogMap reported at F1 0.61 on that track). This is public-participation
evidence only — **neither tool has been executed in this repository**, their exact versions are not
bound, and both arms remain `CANNOT_CHECK__NOT_EXECUTED_IN_REPOSITORY`.

## Boundaries

1. This is an analysis contract, not a result: no alignment scoring has been performed.
2. Post-hoc changes to arms, gates, statistical units or the gold rule after the first scoring artifact
   exist are protocol violations requiring a new versioned freeze.
3. Execution may start only after the licence manifest preconditions hold: bench23 SHA-256 computed at
   download time, and a natural-pair track licence unblocked (or a lawful alternative verified).
4. Incomplete reference alignments never make absent entity pairs true negatives; absence is
   UNDETERMINED absent an authoritative exhaustive-reference statement, which zero audited suites supply.
