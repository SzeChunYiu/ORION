# P3 V22 scientific report: comparator-arm disposition and the analysis-unit rule

## What this increment is

Two frozen rules and the checkers that enforce them. **No campaign was executed, no
new result was created, and no reference alignment was opened.** Both artifacts
carry `results_exist: false`, `campaign_executed: false`, `outcome_accessed: false`.

It addresses exactly two boxes of issue #1086's P3 section and deliberately leaves
the other two open.

## Box 1 — "Compare against LogMap and AML, or mark unavailable arms CANNOT_CHECK"

**AML: SCORED.** AML 3.2 ran in matching mode and was scored against the frozen
reference on the OAEI 2004 test-103 case. Receipts: `AML_ALIGNMENT_V16.rdf`
(`994c74c3…`, 15,151 bytes), `RESULT_V16.json` (`8045631b…`), and the common-universe
scoring in `COMMON_PAIR_METRICS_V21.json` (`99c2b561…`).

**LogMap: CANNOT_CHECK** — and the disposition is careful about *which* claim it makes.
LogMap runs. V11 reconstructed its exact 90/90 manifest classpath, 25,337,399 bytes,
and the child exited 0. The true statement is narrower than "unavailable": no LogMap
**matching-mode** alignment over the scored case has been admitted through the frozen
V21 identity interface. Four blocking conditions, each bound to a receipt by hash:

| id | blocker |
|---|---|
| LM-B1 | matching mode exercised only on a synthetic smoke universe (`urn:orion:p3:v6:smoke:*`), preflight-only authority, rows never compared to gold, and its declared output `logmap2_mappings.rdf` is recorded by digest but not retained in the tree |
| LM-B2 | the retained output on the real case is a **repair** of another system's mappings, not LogMap's own alignment, so it cannot be scored as an independent arm |
| LM-B3 | **16 of 16** retained rows wrap their IRIs in `Optional.of(…)`, which the frozen V21 decoder rejects — and stripping it after reference access is exactly the post-outcome normalization V11 forbade its successor from performing |
| LM-B4 | no reproducible runtime pin for the official MELT LogMap wrapper; its POM resolves `master-SNAPSHOT` on `openjdk:8-jre-alpine`, which is provenance, not a runtime |

LM-B3 is the strongest of the four, because it is a real interface defect measured
first-hand rather than an absence. The disposition also carries five promotion
conditions: what would have to be frozen for LogMap to become a scored arm.

The absence claim is stated with its search scope named — every non-JAR path matching
`logmap` on `origin/main` was inspected, plus the patterns `logmap_mappings`,
`logmap_anchors`, `logmap_overestimation` and `logmap2_mappings` across the whole tree.
Matching-mode outputs retained: **0**.

## Box 2 — "Bootstrap/aggregate by ontology pair or track, not correspondence row"

V21 stated this discipline and obeyed it: the analysis unit was one case, and it
declined to report a population estimand, confidence interval or p value over pair
cells. V22's next discriminator re-froze it as a prohibited promotion. Neither
mechanized it, so nothing prevented a later report from quietly resampling rows.

`ANALYSIS_UNIT_RULE_V22.json` closes the unit taxonomy — admissible:
`ontology_pair`, `track`, `case`; inadmissible: `correspondence_row`, `pair_cell`,
`mapping`, `seed`, `episode`, `generated_row`. `orion.study.p3.analysis_unit_guard`
enforces it and fails closed, with **CANNOT_CHECK as an exit code distinct from PASS**
(a report it cannot parse exits 5; it never falls through to 0).

The rule that matters: one pair with 91 correspondences is `n=1`, not `n=91`.
Correspondences inside a pair share the seed ontology, the label vocabulary, the
reference construction and the matcher's threshold — inflating `n` there manufactures
significance the case count cannot support.

## Checker validation

Both checkers were validated against **real data with adversarial mutation**, not
fixtures, because a checker that has only ever seen fixtures passes while whole
classes of defect go unseen.

The committed disposition passes on the real tree (exit 0, 2 arms, every cited digest
re-verified against the actual file). Ten mutations of that same real document were
each caught with the right code: tampered SCORED digest → 3, missing evidence path → 3,
tampered blocking digest → 3, CANNOT_CHECK without promotion conditions → 4, without
blocking conditions → 4, `is unavailable` overclaim → 5, unknown disposition → 2,
CANNOT_CHECK also claiming scored → 2, garbage document → 6.

The no-alarm case is asserted as deliberately as the alarms: the honest V21 stance
(unit `case`, one case, no interval) passes, and quoting an overclaim inside
`explicitly_not_claimed` in order to disclaim it passes — scanning that field would
punish honesty.

Focused tests: **67 passed** in `tests/unit/p3/` (47 new, 20 pre-existing), ~0.3 s.
The `Optional.of(…)` 16/16 measurement is re-derived from the cited artifact by a test
rather than trusted as a recorded number.

## What this does NOT close

- **"Use official RDF reference alignments and MELT scoring."** The official RDF
  reference *is* used (`REFERENCE_FROZEN_V21.rdf`, `0afb0f2c…`), but scoring is done by
  the house evaluator `common_pair_evaluator_v21.py`, not MELT. **Box remains open.**
- **"Add at least one natural ontology-pair track."** The only scored case is OAEI 2004
  test-103, itself a generated benchmark track — the same objection the box raises
  against bench23. **Box remains open**, and needs a natural pair.

Both are named as out of scope inside the disposition itself, and a test asserts they
are, so this file cannot later be read as covering the whole P3 section.

## Claim boundary

This increment creates rules and enforcement. It establishes no mapping correctness,
no performance, no coverage, no superiority and no transport. The V21 boundary stands
unchanged: one public case, descriptive only, no population estimand.
