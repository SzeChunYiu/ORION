# Protocol: ORION13.MATCHED_POLARITY_NECESSITY.v2

**Frozen 2026-09-03, before any case was built, any arm was re-run, any
separator subset was enumerated, or any outcome was observed.** Nothing below
may be revised in response to a result. If a result contradicts a prediction
recorded here, the prediction is reported as wrong and the construction stays
as written.

- **Study id:** `ORION13.MATCHED_POLARITY_NECESSITY.v2`
- **Protocol id:** `P3.matched-polarity-necessity-extension.v2`
- **Lane type:** REGISTERED_CONSTRUCTION_PLUS_FROZEN_DATA_ANALYSIS
- **Paper:** ORION-13 (coordinate-governed scientific mapping)
- **Base revision:** the `origin/main` commit this protocol is registered on
  (recorded in `RESULT.json.base_revision`)
- **Driver:** `research/extensions/p1-p3-structure/matched_polarity_necessity_v2.py`
  (registration commit contains the protocol and the driver only; no results)
- **Artifacts dir (results commit):** `research/p3-matched-polarity-necessity-v2/`
- **New atlas id:** `matched-polarity-necessity-v2` (n = 80)

## 1. The residual this study closes

Three committed records name this exact rung:

1. **v1 atlas audit** (`research/p3-coordinate-necessity-v1/AUDIT_AFTER_coordinate-necessity-v1.json`,
   n = 56): `remove_referent` FAIL (treated 56/56, changed 0) and
   `remove_construct` FAIL (treated 43/56, changed 0). Both are *populated but
   never contrastive within a case* — real negatives on that corpus.
2. **Theory packet §7** (`papers/orion-13-global-knowledge-portrait/theory/minimal-semantic-separator-v1/CLAIM_DISPOSITION.md`):
   > "A coordinate-necessity study needs opposite-verdict cases in the families
   > that currently contribute none — `different_name_same_referent` and
   > `valid_invalid_representation_mapping` with non-`COMPATIBLE` gold — plus
   > `DISTINCT_REFERENT`, `DISTINCT_CONSTRUCT` and `DISTINCT_MEASUREMENT`
   > verdicts. The case schema already admits all of these; the frozen corpus
   > never instantiates them."
3. **Publication disposition matrix** (`papers/PUBLICATION_DISPOSITION_MATRIX_V1.md`,
   ORION-13 row): the successor must carry "matched-polarity opposite-verdict
   pairs so polarity alone cannot solve the task". The separator result on the
   frozen gold is k\* = 1 with unique reduct `{polarity}` — the verdict is
   perfectly confounded with polarity agreement. Every added case in this study
   holds `polarity = POSITIVE` on **both** sides, so no added case can be
   separated from any other by polarity: matched-polarity by construction.

## 2. Relationship to the v1 freeze's explicit prohibition

The v1 freeze (`research/p3-coordinate-necessity-v1/FREEZE_2026-08-21.md` §1)
forbade *that repair* from adding cases on which `referent_ids` or
`construct_ids` differ, on the grounds that flipping those two arms inside the
measurement/temporal vacuity repair "would be constructing the outcome". That
prohibition is scope-bound to the v1 repair and remains true of it. This study
is the separately-named successor rung (theory §7), with its own freeze, and it
honours the boundary the v1 freeze drew:

- The v1 atlas, both frozen public-reference atlases, and every committed P3
  result are copied through unchanged; their FAILs stand as the record for
  those corpora.
- The claim is scoped exactly as v1 scoped its own: the added cases establish
  that the coordinates are **load-bearing in the comparison rule** on
  constructed matched-polarity pairs. They establish nothing about how often
  such pairs occur in public corpora (EXTERNAL_VALIDITY), and no accuracy,
  false-merge or superiority number over this atlas is evidence about ORION's
  competence (ACCURACY_CAVEAT).
- The headline registered question is not the arm flip. It is the
  de-confounding question (RQ2): on the extended corpus, is `{polarity}` still
  a merge-sufficient separator? The arm repair (RQ1) is the same corpus read a
  second way.

## 3. Frozen construction

Mirror of the v1 build discipline (`src/orion/study/p3_coordinate_necessity_build.py`),
with the stratum coordinates changed and the registries re-sourced. All
machinery is imported, never copied: `_decimal_digest`, `shape_invariants`,
`write_jsonl`, `DISCIPLINES`, `SLOTS_PER_STRATUM = 12`, `DIFFER_SLOTS = 4`,
`measurement_dimensions()`, `observation_epochs()` from the v1 builder;
`compare_meaning` via `evaluate_case`; `ablated_relation` from the analysis
module; `audit_atlas`, `audit_atlas_identifiability`; the separator checker at
`papers/orion-13-global-knowledge-portrait/theory/minimal-semantic-separator-v1/independent_checker/separator.py`
via `importlib`.

| field | value |
| --- | --- |
| strata | `referent` (12 slots), `construct` (12 slots) |
| slots 0–3 of each stratum | differ on the stratum's coordinate |
| slots 4–11 of each stratum | agree on every coordinate |
| family (referent stratum) | `different_name_same_referent` |
| family (construct stratum) | `valid_invalid_representation_mapping` |
| predicate | `reports_quantity` (referent stratum), `reports_observed_state` (construct stratum); equal across the pair on every added case |
| polarity / modality | `POSITIVE` / `POSITIVE` and `ASSERTED` / `ASSERTED` on **every** side of **every** added case (the anti-confound) |
| measurement / temporal | equal across the pair on every added case, arity 1, drawn from the v1 frozen tables (`measurement_dimensions()`, `observation_epochs()`) |
| referent / construct arity | 1 on both sides of every added case |
| registries | the distinct `referent_ids` / `construct_ids` values attested in the 32 non-synthetic rows of `research/p3-coordinate-necessity-v1/cases.jsonl`, sorted; recorded verbatim in the standard document with the parent file's sha256 |
| differ-slot rule | slot s < 4: left = `registry[(2s) % n]`, right = `registry[(2s+1) % n]` (asserted distinct); slot s >= 4: both sides `registry[s % n]`; values wrapped `registry:referent:` / `registry:construct:` |
| gold rule | referent differ → `DISTINCT_REFERENT`; else construct differ → `DISTINCT_CONSTRUCT`; else `COMPATIBLE` — stated before any run; the full system must agree on every added case (receipt) |
| case ids | `matched-synth-` + 16-digit decimal digest of (protocol id, stratum, slot, all ten coordinate values) — constant length, hyphen count and alphabetic prefix |
| provenance | one source record per case: dataset `ORION-P3-MatchedPolarityStandard`, revision = sha256 of the standard document bytes, `CC0-1.0` |
| authority | `DERIVED_FROM_ALLOWED`, rule `identity:frozen-registry-distinctness`, inputs = the four coordinate values |

Shape invariants (`shape_invariants` from the v1 builder) must be constant
across the 24 added cases; any varying invariant is a blocker. The corpus is
frozen (cases.jsonl written, hashed) **before** any arm, guard, identifiability
probe or separator subset is evaluated on it.

**Composition of the new atlas:** the 56 rows of
`research/p3-coordinate-necessity-v1/cases.jsonl` (themselves the untouched
v1.1-confirmatory parent plus the v1 synthetic 24) copied through unchanged,
plus these 24, sorted by `case_id`, n = 80.

## 4. Registered questions

**RQ1 (arms).** On the n = 80 atlas, do `remove_referent` and
`remove_construct` become `PASS / COORDINATE_LOAD_BEARING` with exactly 4
decisions changed each? Predictions: `remove_referent` treated 80/80 changed 4;
`remove_construct` treated 67/80 changed 4; the other four arms stay
qualitatively as in v1 (`remove_measurement` 4, `remove_temporal_context` 4,
`remove_modality_polarity_attribution_discourse` 6,
`force_compatibility_without_obstruction` 14 + 8 = 22). Overall audit outcome
predicted `CANNOT_CHECK` (not FAIL): both standing guard `CANNOT_CHECK`s — the
false-split comparator that has no separating branch, and the absent
`UNRESOLVED` gold denominator — persist and are out of scope here exactly as in
v1. The `P3.FALSE_SCIENTIFIC_MERGE` guard must remain `PASS` (0 false merges on
38 opportunities).

**RQ2 (separator de-confounding).** Composed corpora, both frozen before any
subset is enumerated:

- Derivation corpus D = `public-reference-v1` (32) + the v1 synthetic 24
  (extracted by `coordinate-synth-` id prefix) + the v2 added 24 (n = 80).
- Challenge corpus C = `public-reference-v1.1-confirmatory` (32) + the same 48
  synthetic rows (n = 80).

Discipline, inherited from the frozen checker: exhaustive enumeration over all
2^k coordinate subsets on **D only**; every derivation reduct re-evaluated on
C; structure-free permutation null on D (20000 trials, seed 20260828, the
checker's own constants and RNG). The challenge corpus is never consulted while
choosing subsets. The encoding is the checker's agreement-bit encoding
(`[L_j == R_j]`), fixed before any subset was evaluated; no alternative was
tried. **Shared case ids between D and C are 48 by construction (the synthetic
contrast is deliberately present in both); the held-out part of C is its 32
parent rows, and the transfer claim is scoped to those.** Questions: is
`{polarity}` merge-sufficient on D? on C? What are k\*, the reducts, the core?
Predictions: `{polarity}` insufficient on both (construction-guaranteed: 16
added COMPATIBLE cases and 8 added opposite-verdict cases all carry polarity
bit 1); no singleton sufficient on either corpus (pigeonhole: 6 verdict classes
share 2 patterns under one bit); k\* = 5 on D with unique reduct
`{polarity, measurement_ids, temporal_context_ids, referent_ids,
construct_ids}` — this prediction is **derived from the committed
coordinate-opportunity measurement** (no case in either parent has two sides
differing on referent or construct) and is *wrong* if any parent COMPATIBLE
case carries a zero bit on any of those five coordinates; every derivation
reduct sufficient on C; the null rate small.

**RQ3 (anti-shortcut and guards).** Does the shipped atlas pass the
identifiability audit under its primary split? `audit_atlas_identifiability`
on the n = 80 atlas: in-sample overall must be `PASS` (the v1 precedent: the
56-case atlas passed in-sample). The hash-parity split and the added-24-only
audit are recorded descriptively, not gated — v1 shipped with a parity failure
and an added-only quartile tie-break reported as limitations. Construction
property making the family-token shortcut dead by design: after this
extension `different_name_same_referent` carries COMPATIBLE (21) **and**
DISTINCT_REFERENT (4); `valid_invalid_representation_mapping` carries
COMPATIBLE (14) **and** DISTINCT_CONSTRUCT (4).

## 5. Hard gates (executed, not logged)

- **G1 parent integrity.** sha256 of
  `research/p3-coordinate-necessity-v1/cases.jsonl` equals
  `271ef70de685ab49a74b322dc6382f488e5f2cd9b1f82a946cf79e838ebb695c`; the
  derivation gold equals
  `35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8` and the
  challenge gold equals
  `13a76c68c149c2552f3543babeca6e1ad5afe23c45ea9c0dc365c1445cf2782b`; all 56
  parent ids present unchanged in the 80-row atlas.
- **G2 added-case correctness.** Full system correct on all 24 added cases;
  for each of the 8 differ cases, emptying its coordinate changes the answer
  (dependence receipts, checked with the analysis module's own
  `ablated_relation`).
- **G3 arm repair.** `remove_referent` and `remove_construct` both
  `PASS / COORDINATE_LOAD_BEARING` with `decisions_changed == 4`.
- **G4 separator.** Full coordinate set sufficient on D; `{polarity}` NOT
  sufficient on D and NOT sufficient on C; no singleton subset sufficient on
  D; every derivation reduct reported with its challenge-set outcome.
- **G5 identifiability.** In-sample overall `PASS` on the n = 80 atlas.
- **G6 guards.** `P3.FALSE_SCIENTIFIC_MERGE` guard `PASS` on the n = 80 atlas.
- **G7 shape invariants.** No varying invariant across the 24 added cases.
- **G8 import gate.** The driver's own imports (ast-parsed) are within the
  frozen whitelist; no numeric/instrument library, no RNG import in this file.

## 6. Terminals (frozen at registration; first match wins)

1. `MPN2_CONSISTENCY_FAILURE` — a hard assert fired; exit 3.
2. `MPN2_CONSTRUCTION_CUE` — G5 fails: the repair shipped a shortcut cue.
3. `MPN2_ARM_REPAIR_FAILED` — G3 fails: the construction did not make the
   coordinates load-bearing (a real negative, with the v1 FAILs standing).
4. `MPN2_POLARITY_STILL_SUFFICIENT` — G4's `{polarity}`/singleton clauses
   fail: the anti-confound reasoning is falsified.
5. `MPN2_HELDOUT_SEPARATOR_FAILS` — some derivation reduct collides on C.
6. `MPN2_ARMS_MEASURED_AND_POLARITY_DETHRONED` — all gates pass.

Every non-positive terminal ships with one-stage failure attribution and a
named revival lever.

## 7. Authority boundary

A favourable outcome would license, and only license: stating that the
referent and construct coordinates are load-bearing in the comparison rule on
this constructed corpus; stating that the verdict on the extended corpus is no
longer confounded with polarity agreement (`{polarity}` is not a separator);
reporting the new k\*, reducts and null rate as exact facts about these frozen
bytes; and closing the theory-§7 named rung. It would not license: any
external-validity or frequency claim about public corpora; any accuracy,
false-merge or superiority claim over the added cases; touching the standing
v1 FAILs as records of their corpora; any claim that the six coordinates are
necessary in general; novelty over donor rough-set/discernibility theory
(`novelty_authority = false`); any physical or quantum-advantage claim
(`physical_quantum_advantage_claim = false`). The external anti-confound
corpus (GO / Uberon / EFO) named in the disposition matrix remains the next
open residual and is untouched by this study.
