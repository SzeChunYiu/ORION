# ORION-14 protected battery V3 — prospective freeze

**Written 2026-08-21, before the construction was repaired and before any panel
outcome on the repaired construction was observed.**

This document exists because the change it authorises can make a null result
positive. `research/failures/2026-08-label-recoverable-from-construction-cue/`
records that ORION-14's H3 has never been measured: under V1 the `CANNOT_CHECK` family
was separable by `len(evidence) == 0`, and under the V2 repair it is separable by
`len(evidence[0]["content"])`. Repairing the construction gives H3 headroom for
the first time. A repair chosen after seeing which construction makes H3 come out
well is not a measurement, so the protocol is fixed here, in advance, and the
order of operations below is binding.

## 0. Order of operations (binding)

1. This document.
2. Repair the construction. Iterating the construction against the
   **identifiability register** (§3) is the register's purpose and is permitted.
3. Run the full register and record every probe's informedness (§3, §4).
4. Only once the register clears at the declared ceiling: run the frozen panel,
   once.
5. Report whatever came out. **If H3 is still null with the cue gone, that is a
   real negative and is reported as one.**

Iterating the construction against a *panel* outcome is forbidden. If the panel
run fails for a mechanical reason (missing input, crash, harness misinvocation)
the fix is to the invocation, never to the construction.

No committed V2 artefact is edited. `PUBLICATION_METRICS_V2.json` and everything
else under `papers/orion-14-verified-scientific-discovery/evidence/protected_v2/`
stands as the record of what the cued battery produced. V3 is a new battery with
its own identity and its own outputs.

## 1. Identity

| field | value |
| --- | --- |
| construction id | `v3` |
| generator | `papers/orion-14-verified-scientific-discovery/host/generate_protected_cases.py --construction v3` |
| shape | 420 cases, 13 families, gold terminals `{BLOCK: 330, PROMOTE: 60, CANNOT_CHECK: 30}` — unchanged from V1/V2 |
| custody split | unchanged: FIT = 150 `PUBLIC_*`, EVAL = 270 `PROTECTED_*`, of which 20 are `CANNOT_CHECK` |
| audit seed | `v3-audit-20260821` |
| seed-invariance seeds | `v3-audit-alt-a`, `v3-audit-alt-b` |
| panel seed | `p4-v3-panel-20260821` |
| panel | frozen and unmodified: `host/run_baselines_v2.py` (10 comparators) + `host/run_candidate.py` (ORION) |
| statistics | frozen and unmodified: `host/evaluate_campaign_v2.py` |

The seeds are named here so that a seed cannot be chosen after the fact. The
generator remains deterministic in `--seed`, and `--construction v1` and
`--construction v2` are retained verbatim so the historical record — including
`test_the_v1_reconstruction_reproduces_the_frozen_published_panel` — stays
reproducible. `v3` becomes the generator's default, because shipping a
known-leaking construction as the default is the defect being repaired.

## 2. How content is made label-independent

The governing principle, stated so it can be checked rather than asserted:

> **Every case in the battery is shape-identical. Families differ only in the
> values of the fields a ORION-14 hard gate is defined over.**

Concretely, for every one of the 420 cases:

- **One evidence template, battery-wide.** Every evidence record in every family
  is
  `"Synthetic source record. SUPPORT::{marker}. Host-generated evidence body {filler}."`
  with `marker` a 20-hex-character token and `filler` a 12-hex-character token.
  Every record therefore has the same length, the same word count, the same
  punctuation, the same digit and uppercase profile, and the same template.
- **The support marker is present on every record in the battery.** A record
  supports the claim iff `marker == claim.support_token`. A non-supporting record
  carries a *different*, equally well-formed token. The literal substring
  `SUPPORT::` occurs in all 840 records and carries exactly zero information;
  only token matching separates support from non-support, and token matching is
  the `SEMANTIC_SUPPORT` obligation.
- **Fixed containers.** Exactly 1 evidence object, exactly 2 retrieval-pool
  records, exactly 1 used evidence id, exactly 2 access requests, exactly 1
  search-trace entry, exactly 2 distinct source ids — in every case, in every
  family. `CITED_NON_INFLUENTIAL` now records the *peer's* id in
  `used_evidence_ids` rather than an empty list, so "cited but not influential"
  is a mismatch between two ids instead of a missing count.
- **No nulls, ever.** No field is absent or `None` in any case. All four hash
  fields are present on all 840 records.
- **Content substitution is substitution.** `CONTENT_SUBSTITUTION` replaces the
  filler with a different filler of identical width instead of appending an
  `ALTERED::` suffix, so the tampered body is the same length as an untampered
  one and the tampering is visible only by comparing the declared digest to the
  actual one — which is the `EXACT_CONTENT_BINDING` obligation.
- **`CANNOT_CHECK` is produced by two subtypes, 15 each, both shape-identical to
  each other and to `POOLED_SUPPORT_WRONG_OWNER`:**

  | | assigned record | peer record in pool | gold |
  | --- | --- | --- | --- |
  | `POOLED_SUPPORT_WRONG_OWNER` | does not support; **mis-owned** (`source_id != assigned_source_id`) | supports, owned by the cited source | `BLOCK` |
  | `INSUFFICIENT_EVIDENCE` A | does not support; correctly owned | does not support | `CANNOT_CHECK` |
  | `INSUFFICIENT_EVIDENCE` B | does not support; correctly owned | supports, owned by a **third** source | `CANNOT_CHECK` |

  So `CANNOT_CHECK` is a strict subset of "the assigned record does not support
  the claim's token" — a set that also contains 30 `BLOCK` cases — and telling
  the two apart additionally requires reading the assigned record's ownership.
  Neither "nothing in the pool supports" (true only of subtype A) nor "the
  assigned record does not support" (true of 30 `BLOCK` cases too) classifies the
  family. Subtypes are assigned by `within_family % 2`, so each custody bucket
  carries both.

What is deliberately *not* made uniform: the values of fields a hard gate is
defined over — `source_id` / `assigned_source_id`, the four digests, the support
marker token, `answer.lineage_id` and `checker.lineage_id`, `checker.hostile_probe`,
`checker.created_round`, `evaluator.frozen_round`, `evaluator.integrity`,
`search_trace[*].benchmark_gold_visible`, and `access_requests[*].scope` / `path`.
Those fields *are* the case. A probe that reads them is a second implementation of
the ORION-14 task, not a shortcut. Their residual *shapes* (e.g. `len("COMPROMISED")`
vs `len("INTACT")`) are nonetheless left inside the register's reach — see §3
probe 10 — because including them can only make the audit stricter.

## 3. The identifiability register

Fitted on the 150 `PUBLIC_*` cases (`CaseSplit.FIT`), scored on the 270
`PROTECTED_*` cases (`CaseSplit.EVAL`), majority-label-per-cue-signature,
informedness = TPR + TNR − 1, via
`orion.programme.benchmark_identifiability.audit_label_identifiability`. Probes
1–3 are the register that already exists in `orion.study.p4.promotion_cues`;
4–13 are added by this repair and cover, by name, every cue class the repair
could have introduced.

| # | probe id | kind | reads |
| --- | --- | --- | --- |
| 1 | `evidence-object-count` | COUNT | evidence / pool / used-evidence object counts |
| 2 | `declared-hash-missingness` | FIELD_MISSINGNESS | which declared hashes are null on the evidence list |
| 3 | `evidence-content-length` | STRING_SHAPE | `len(content)` of each evidence body |
| 4 | `pool-content-length` | STRING_SHAPE | `len(content)` of each *retrieval-pool* body |
| 5 | `pool-hash-missingness` | FIELD_MISSINGNESS | which declared hashes are null anywhere in the pool |
| 6 | `request-and-trace-count` | COUNT | access-request, search-trace and distinct-source counts |
| 7 | `container-length-profile` | COUNT | length of **every** list in the view, keyed by path |
| 8 | `key-shape` | FIELD_MISSINGNESS | key tuples, in order, of the view and of every evidence and pool object |
| 9 | `content-character-profile` | STRING_SHAPE | per body: length, spaces, digits, uppercase, punctuation — a template fingerprint that reads no word |
| 10 | `string-length-profile` | STRING_SHAPE | `(path, len)` for **every** string anywhere in the view, obligation-bearing enums included |
| 11 | `identifier-shape` | IDENTIFIER_SHAPE | length, prefix and separator count of every opaque identifier and URL |
| 12 | `digest-prefix` | IDENTIFIER_SHAPE | leading hex nibble of the assigned record's content digest (a noise control) |
| 13 | `scalar-value-profile` | ENUM_VALUE | `(path, value)` for every integer and boolean in the view, obligation-bearing fields included |

Every probe must carry a one-sentence rationale for why its cues carry none of
the competence; `ShortcutProbe` refuses to be constructed without one. The cue
extractor returns only integers, booleans and tuples of them, so no probe can
read a support token, a digest, a lineage id or an integrity status as a value —
except where a probe is deliberately over-inclusive (10, 13), which is declared
here and can only tighten the audit.

### Addendum, same session, after the register ran and before the panel ran

Two changes to the register, both recorded here because they happened after this
document was written. Both are strengthenings, made while iterating the
construction against the register (§0 step 2), which is what the register is for.
Neither was made with any panel outcome in view.

- **A fourteenth probe, `content-template-identity`.** Row 9 above describes
  probe 9 as "a template fingerprint"; the cues it names are character-class
  counts, which is not the same thing. The template fingerprint is now its own
  probe: it digests the evidence body with runs of eight or more hex characters
  masked out, so it reads which sentence the generator wrote and cannot read what
  was interpolated into it.
- **Probe 9 strengthened.** As first written it counted digits and uppercase over
  the *raw* body, which counts the hex of seed-derived tokens. That gave it a
  signature per case, so it generalised to nothing and reported a clean −0.03 on
  the V2 construction whose label a plain character count recovers at 1.0. It now
  takes its class counts over the masked body and carries the raw length
  alongside; on V2 it reports 1.0, as it should. A probe too fine to generalise
  cannot find a leak, which is the failure mode this register exists to avoid.

Probe 12 is registered as a control on the instrument, not on the battery: the
digest is a SHA-256 of seed-derived content, so its leading nibble is noise, and
a non-zero informedness there would be the majority-vote rule fitting sampling
noise rather than a property of the construction. It is reported either way, with
its confusion matrix, and it is not exempt from the ceiling.

**Before/after.** The same register is run on `--construction v1`, `v2` and `v3`
so the repair is measured with one instrument on all three, and every probe's
informedness is reported for each.

**Labels audited.** `CANNOT_CHECK` (primary — the terminal H3 is computed over),
plus `PROMOTE` and `BLOCK`, all reported.

## 4. The ceiling

`max_recovery = 0.0`. Strict: **no registered judgement-free cue may separate the
audited label at all.** The eval split's resolution is
`min(1/20, 1/250) = 0.004`, so 0.0 is inside what the split can express and does
not trip `TOLERANCE_FINER_THAN_RESOLUTION`.

The audit is clean for a label iff `audit_promotion_terminal(..., label=...)`
returns `Outcome.PASS` with `IdentifiabilityReason.NO_CUE_RECOVERED_LABEL` and
`worst_recovery == 0.0`. `CANNOT_CHECK` clean at this ceiling is a precondition
for reporting H3 at all: `AuditedScore` refuses at construction to carry a score
whose audit blocks.

## 5. H3 — primary outcome and threshold

Unchanged from the frozen evaluator, so that V3's H3 is comparable to V2's:

- **Comparator:** the strongest frozen comparator, selected as in
  `evaluate_campaign.py` — the `FROZEN_AUTHORITY_BASELINE_IDS` member with the
  lowest false-authority-promotion rate, tie-broken by higher claim correctness
  then by system id. Chosen by H1, not by H3.
- **Primary outcome:** `orion_minus_baseline_correct_cannot_check` — the paired
  bootstrap difference (ORION − comparator) of the per-case correct-`CANNOT_CHECK`
  indicator over the 30 gold-`CANNOT_CHECK` cases, 10,000 resamples, seed
  20260816, as computed by the frozen
  `research/paper-programme-v1/protocols/publication_stats.py`.
- **Threshold:** `SUPPORTED` iff `ci95_low > 0.0`; otherwise `NOT_SUPPORTED`.
- **Gate:** reportable only if §4's `CANNOT_CHECK` audit passes on the same
  battery.
- **Also reported, per system, all eleven:** `correct_cannot_check_rate` over 30
  cases, and `false_promotion_rate` and `clean_coverage` with their Wilson
  intervals; and H1 and H2 as the frozen evaluator computes them. The
  construction change touches every family, so H1 and H2 will move and are
  reported as they come out.

**Pre-registered interpretation.** ORION is the only system in the panel with a
non-compensatory three-valued terminal; `deepsciverify` is the only comparator
that can emit `CANNOT_CHECK` for any reason other than having nothing to look at.
If H3 comes out positive, the honest reading is that it measures *terminal
expressiveness under a hard-gate lattice* — the ability to report an inability —
and not a finer-grained scientific judgement. That reading is fixed here so it
cannot be upgraded after a good number arrives. If H3 comes out null, it is a
real negative: the systems that can express `CANNOT_CHECK` do so on the same
cases as ORION.

## 6. What a clearing register does and does not prove

It proves: **no cue in the registered set recovers the audited label above the
declared ceiling, on the split a candidate is not allowed to see, when fitted on
the split it is.**

It does not prove there is no shortcut. Three specific limits, stated in advance:

1. **It is a statement about the probes.** Thirteen probes that clear are
   thirteen probes. The register is the artifact and should grow every time a new
   cue is thought of; every campaign should be re-audited against the grown
   register.
2. **The majority-vote rule can only recover a label that dominates some cue
   bucket.** Residual structure that separates one `BLOCK` family from another is
   invisible to a `CANNOT_CHECK` audit, and will read as informedness 0.0. A
   probe scoring 0.0 means "this cue does not recover *this label*", not "this
   cue is constant".
3. **Fields the obligations are defined over are the case, and are not
   shortcuts.** A system that reads `checker.hostile_probe` or compares
   `source_id` to `assigned_source_id` is doing the task. That the battery is
   mechanical gold — each family is one field state — is a property of ORION-14's
   design, not something this audit can or should condemn.

## 7. Artefacts this campaign will produce

Under `research/campaigns/2026-08-21-p4-battery-v3-identifiable/`:

- `FREEZE.md` — this document.
- `run_identifiability.py` → `IDENTIFIABILITY_V3.json` — every probe's confusion
  matrix and informedness, for constructions v1, v2 and v3, for all three
  terminals, plus the seed sweep.
- `run_panel.sh` + `collect_panel.py` → `PANEL_V3.json` — the frozen panel's
  output on the V3 battery: H1/H2/H3 and the per-system rates. The panel scripts
  modify nothing: they mint a battery and hand it to `run_candidate.py`,
  `run_baselines_v2.py` and `evaluate_campaign_v2.py` exactly as they stand.
- `RESULT.md` — the report.

`run_identifiability.py` is run and its output committed *before* `run_panel.sh`
is invoked. That ordering is the freeze.

Code changes: `host/generate_protected_cases.py` (the repair, plus
`--construction`), `src/orion/study/p4/promotion_cues.py` (probes 4–13), and the
two ORION-14 test modules that pin the leak, which move to pinning it *historically*
under `--construction v1` / `v2` and pinning the clean register under `v3`.
