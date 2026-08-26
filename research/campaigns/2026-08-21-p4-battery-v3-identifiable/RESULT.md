# P4 protected battery V3 — result

Protocol: `FREEZE.md` beside this file, written before the construction was
repaired and before any panel outcome was observed. Artefacts:
`IDENTIFIABILITY_V3.json` (written before the panel ran), `PANEL_V3.json`.

Nothing under `papers/orion-14-verified-scientific-discovery/evidence/` was
edited. `PUBLICATION_METRICS_V2.json` stands as the record of what the cued
battery produced.

## 1. The repair

`--construction v3`, now the generator's default. `v1` (empty evidence list) and
`v2` (the first repair) stay selectable so the batteries whose results are
already published remain reproducible.

Measured on a regenerated 420-case battery, all three constructions, one
instrument:

| | v1 | v2 | v3 |
| --- | --- | --- | --- |
| distinct evidence-body lengths | 2 (0 and 86…) | **5** — 86×330, 78×30, 108×30, 107×15, 122×15 | **1** — 98×420 |
| `{107, 122}` = the `CANNOT_CHECK` set | — | yes | — |
| evidence objects per case | 0 or 1 | 1 | 1 |
| pool records per case | 0 or 1 or 2 | 1 or 2 | **2** |
| used-evidence ids per case | 0 or 1 | 0 or 1 | **1** |
| access requests per case | 1 or 2 | 1 or 2 | **2** |
| distinct pool source ids | 0–2 | 1 or 2 | **2** |
| null hash fields in the battery | 30 | 30 | **0** |
| distinct evidence key tuples | 1 | 1 | 1 |
| per-family pool-length signatures | 6 distinct | 6 distinct | **1** — `(98, 98)` for all thirteen families |

How the label was made independent of construction:

- **One body template for all 840 records.** `"Synthetic source record.
  SUPPORT::{marker}. Host-generated evidence body {filler}."` with a 20-hex-char
  marker and a 12-hex-char filler. Same length, same words, same punctuation,
  same template, every case, every family. The only thing that varies between
  bodies is how many hex characters inside the two tokens happen to be digits,
  which is a SHA-256 and therefore noise — which is why the register's
  character-class probe takes its counts over the body with the tokens masked.
- **The support marker is on every record in the battery.** A record supports the
  claim iff its marker token *is* the claim's `support_token`; a non-supporting
  record carries a different, equally well-formed token. So `SUPPORT::` occurs in
  all 840 records and carries zero information — only token matching separates
  support from non-support, and token matching is the `SEMANTIC_SUPPORT`
  obligation. V2's bodies named their own family in English
  (`"No corroborating record exists in the pool."`), which is a worse leak than
  their length.
- **Fixed containers, no nulls.** `CITED_NON_INFLUENTIAL` records the *peer's* id
  in `used_evidence_ids` instead of an empty list, so behavioural influence fails
  on an id mismatch rather than on a count. `CONTENT_SUBSTITUTION` substitutes a
  same-width filler instead of appending `ALTERED::…`, so tampering is visible
  only by comparing declared digest to actual — which is `EXACT_CONTENT_BINDING`.
  `EVALUATOR_TAMPER` and `HOLDOUT_ACCESS` *replace* the second access request
  instead of appending one.
- **`CANNOT_CHECK` is two shape-identical subtypes, 15 each,** and is a strict
  subset of a set that also holds 30 `BLOCK` cases:

  | | assigned record | peer in pool | gold |
  | --- | --- | --- | --- |
  | `POOLED_SUPPORT_WRONG_OWNER` | does not support; **mis-owned** | supports, cited owner | `BLOCK` |
  | `INSUFFICIENT_EVIDENCE` A | does not support; owned right | does not support | `CANNOT_CHECK` |
  | `INSUFFICIENT_EVIDENCE` B | does not support; owned right | supports, **third** source | `CANNOT_CHECK` |

  Neither "nothing in the pool supports" (true of A only) nor "the assigned
  record does not support" (true of 30 `BLOCK` cases too) classifies the family.
  Separating them additionally requires reading the assigned record's ownership.

## 2. Identifiability register — informedness per probe

Fourteen probes, fitted on the 150 `PUBLIC_*` cases and scored on the 270
`PROTECTED_*` cases, majority-label-per-signature, informedness = TPR + TNR − 1,
ceiling 0.0, seed `v3-audit-20260821`. Probes 1–3 are the pre-existing register;
4–14 were added by this repair.

### `CANNOT_CHECK` — the terminal H3 is computed over

| probe | v1 | v2 | **v3** |
| --- | --- | --- | --- |
| `evidence-object-count` | 1.0 | 0.0 | **0.0** |
| `declared-hash-missingness` | 1.0 | 0.5 | **0.0** |
| `evidence-content-length` | 1.0 | **1.0** | **0.0** |
| `pool-content-length` | 1.0 | **1.0** | **0.0** |
| `pool-hash-missingness` | 1.0 | 0.5 | **0.0** |
| `request-and-trace-count` | 1.0 | 0.0 | **0.0** |
| `container-length-profile` | 1.0 | 0.0 | **0.0** |
| `key-shape` | 1.0 | 0.0 | **0.0** |
| `content-character-profile` | 1.0 | **1.0** | **0.0** |
| `content-template-identity` | 1.0 | **1.0** | **0.0** |
| `string-length-profile` | 1.0 | **1.0** | **0.0** |
| `identifier-shape` | 1.0 | 0.5 | **0.0** |
| `digest-prefix` (noise control) | 1.0 | 0.0 | **0.0** |
| `scalar-value-profile` | 0.0 | 0.0 | **0.0** |
| **audit** | FAIL | FAIL | **PASS** |

On v3 every probe scores 0/20 true positives and 0/250 false positives with
**0 unscored**: not one of the fourteen ever predicts `CANNOT_CHECK` for any
protected case.

### `PROMOTE` and `BLOCK`

| construction | `PROMOTE` | `BLOCK` |
| --- | --- | --- |
| v1 | FAIL, worst 0.0625 (`digest-prefix`) | FAIL, worst 0.419 (`digest-prefix`; 0.400 for every deterministic probe) |
| v2 | FAIL, worst 0.05 (`digest-prefix`) | FAIL, worst 0.400 (`evidence-content-length`, `pool-content-length`, `content-character-profile`, `content-template-identity`, `string-length-profile`) |
| **v3** | **PASS, worst 0.0** | **PASS, worst 0.0** |

The failure record predicted this: `BLOCK`'s 0.4 on v1/v2 is the `CANNOT_CHECK`
leak seen through a one-vs-rest lens — the probe's true negatives are exactly the
`CANNOT_CHECK` cases and its false positives are exactly the clean positives.
Closing the `CANNOT_CHECK` leak took it with it, as predicted.

### Seed sweep, v3, thirteen seeds

`CANNOT_CHECK` is **PASS at worst-recovery 0.0 on all thirteen seeds.** The
construction's cleanliness on the H3 axis is a property of the construction, not
of a seed.

`PROMOTE` and `BLOCK` fail on 3 of the 13 seeds, at 0.012–0.083. **Every one of
those failures is `digest-prefix`, the declared noise control**, and no other
probe exceeds 0.0 on any seed. That is the control doing its job: a 16-bucket
majority vote over the leading nibble of a SHA-256 will occasionally find a
bucket dominated by a minority label, and a ceiling of 0.0 cannot tell that from
a leak. It is a limit of the ceiling, not a property of the battery — and it is
reported rather than tuned away, because raising the ceiling after seeing which
probe tripped it is the move this whole exercise exists to refuse.

## 3. H3 on the repaired battery

Frozen panel, unmodified: `run_candidate.py` (ORION) and `run_baselines_v2.py`
(ten comparators), five repeats each, scored by the frozen
`evaluate_campaign_v2.py` with the frozen statistics module. Battery seed
`p4-v3-panel-20260821`, construction `v3`, 420 cases. `PANEL_V3.json`.

**H3 is SUPPORTED, at 1.0, CI95 [1.0, 1.0].** The pre-registered threshold was
`ci95_low > 0.0`.

| system | correct `CANNOT_CHECK` / 30 | false promotions / 360 | clean coverage |
| --- | --- | --- | --- |
| **ORION** | **30** | **0** | 1.000 |
| `deepsciverify-abstract-to-full-escalation` | 15 | 225 | 1.000 |
| `attributionbench-multisource-attribution` | 0 | 255 | 1.000 |
| `citation-presence-format` | 0 | 360 | 1.000 |
| `claim-level-auditability-provenance` | 0 | 240 | 1.000 |
| `claimbench-sciclaimhunt-scientific-evidence` | 0 | 345 | 1.000 |
| `fire-iterative-retrieve-or-verify` | 0 | 315 | 1.000 |
| `pooled-evidence-nli-support` | 0 | 345 | 1.000 |
| `provenai-citation-fidelity-influence` | 0 | 180 | 1.000 |
| `provenanceguard-style-source-routing` | 0 | 210 | 1.000 |
| `rewardhackingagents-search-contamination` | 0 | 225 | 1.000 |

The comparator is `provenai-citation-fidelity-influence`, chosen by H1 as the
lowest false-promotion rate, exactly as the frozen evaluator does it. It scores
0/30, so the H3 point estimate is ORION's 1.0 minus its 0.0. **`deepsciverify`
scores 15/30 and is not the comparator**; against it the margin would be 0.5, not
1.0. Both numbers belong in any sentence about H3.

The other two hypotheses, on the same battery: H1 PASS at −0.5, CI
[−0.55, −0.45] (ORION 0/360 against the comparator's 180/360 — the same 180 the
V2 campaign recorded for this system). H2 PASS at 0.0, CI [0.0, 0.0]: clean
coverage is 1.0 for all eleven systems, so H2 remains a saturated axis and is
still not a comparative finding. The typed panel returns PASS with no blockers.

### What H3's 1.0 is made of

Per subtype, per system, on the 30 `CANNOT_CHECK` cases:

| system | subtype A (15) — nothing supports | subtype B (15) — third-source support |
| --- | --- | --- |
| ORION | `CANNOT_CHECK` ×15 | `CANNOT_CHECK` ×15 |
| `deepsciverify` | `CANNOT_CHECK` ×15 | `PROMOTE` ×15 |
| `attributionbench`, `claimbench`, `fire`, `pooled-evidence-nli`, `rewardhackingagents` | `BLOCK` ×15 | `PROMOTE` ×15 |
| `claim-level-auditability`, `provenai`, `provenanceguard` | `BLOCK` ×15 | `BLOCK` ×15 |
| `citation-presence-format` | `PROMOTE` ×15 | `PROMOTE` ×15 |

The two subtypes do different work, which is what they were for. Subtype B is
what separates the pooled-support systems: six of the ten comparators promote a
claim on support that exists in the pool but belongs to a third party, and the
subtype exists precisely so that "no matching token anywhere in the pool" is not
a rule that classifies the family. Subtype A is what `deepsciverify`'s escalation
gets right.

For ORION both subtypes are the same gate state — `SEMANTIC_SUPPORT` is
indeterminate on the assigned record either way — so the subtypes differentiate
the comparators, not ORION.

### The honest reading, as pre-registered

`FREEZE.md` §5 fixed this interpretation before the panel ran, and the result is
what it anticipated: **H3 measures terminal expressiveness under a
non-compensatory gate lattice — the ability to report an inability — and not a
finer-grained scientific judgement.** ORION is the only system in the panel whose
terminal is three-valued for a reason other than having nothing to look at;
`deepsciverify` is the only comparator with any such path, and it gets exactly
the half of the family that path reaches. Nine systems score 0 because they
cannot emit `CANNOT_CHECK` at all once the empty-evidence case is gone.

That is a real difference and it is not a construction cue: the register says no
judgement-free feature of these 30 cases distinguishes them, on thirteen seeds,
across fourteen probes. It is also a narrower claim than "better at knowing when
it cannot check". A panel of eleven systems in which ten are two-valued cannot
separate those two readings, and this battery does not.

### What this does *not* do to the V2 record

`PUBLICATION_METRICS_V2.json` is untouched. Its H3 — `NOT_SUPPORTED`, all eleven
systems at `correct_cannot_check_rate` 1.0 — remains the correct record of what
the V1 construction produced, and the correct reading of it remains the one
`test_p4_metric_headroom.py` pins: an instrument with no resolving power, not a
comparative finding. V3 is a different battery. Nothing here licenses restating
V2's number.

## 4. What a clearing register does and does not prove

Fixed in advance, `FREEZE.md` §6, and restated here so this document stands alone.

**It proves:** no cue in the registered set recovers the audited label above the
declared ceiling, on the split a candidate is not allowed to see, when fitted on
the split it is. On this battery: fourteen probes, thirteen seeds, three
terminals, informedness 0.0 throughout on the `CANNOT_CHECK` axis.

**It does not prove there is no shortcut.** Four limits, all of them properties
of the method rather than excuses for this instance:

1. **It is a statement about the probes.** Fourteen probes that clear are
   fourteen probes. The register is the artifact and should grow every time a new
   cue is thought of; it grew from three to fourteen for this repair precisely
   because three had been enough to condemn a construction and were never enough
   to clear one. Every future campaign should be re-audited against the grown
   register.
2. **The majority-vote rule can only recover a label that dominates some cue
   bucket.** Residual structure that separates one `BLOCK` family from another is
   invisible to a `CANNOT_CHECK` audit and reads as informedness 0.0. A probe
   scoring 0.0 means "this cue does not recover *this label*", not "this cue is
   constant". Section 1's shape table is the direct check that the cues are in
   fact constant, and it is separate evidence.
3. **Fields the obligations are defined over are the case, and are not
   shortcuts.** A system that reads `checker.hostile_probe`, or compares
   `source_id` to `assigned_source_id`, is doing the task. That this battery is
   mechanical gold — each family is one field state — is a property of P4's
   design that no identifiability audit can or should condemn. What the audit can
   say is that the field states, not the packaging, are what a system has to
   read.
4. **The 0.0 ceiling cannot distinguish a small leak from sampling noise.** The
   `digest-prefix` control demonstrates this from inside the register: it fires
   at 0.012–0.083 on the `PROMOTE` or `BLOCK` axis of 3 of 13 v3 seeds, purely by
   a majority vote over sixteen buckets of a cryptographic digest. It never fires
   on the `CANNOT_CHECK` axis, on any seed — but that is a fact to be reported,
   not a ceiling to be raised after the fact.

And the one thing this repair specifically cannot claim: **that it is the last
one.** The V1-to-V2 repair was written against a named cue, succeeded against
that cue, and shipped another. This one was written against the property and
measured against a register built for the property, which is a better argument
and not a proof. The correct posture is the failure record's: treat a repair as a
new construction requiring a fresh audit, not as a discharged obligation.

## 5. Files, and what was deliberately not touched

Created:

- `research/campaigns/2026-08-21-p4-battery-v3-identifiable/FREEZE.md`,
  `RESULT.md`, `IDENTIFIABILITY_V3.json`, `PANEL_V3.json`,
  `run_identifiability.py`, `run_panel.sh`, `collect_panel.py`.

Modified:

- `papers/orion-14-verified-scientific-discovery/host/generate_protected_cases.py`
  — `--construction {v1,v2,v3}`, default `v3`; the V3 base case, body template
  and family mutations; `case_construction` recorded in the run manifest and prep
  summary.
- `src/orion/study/p4/promotion_cues.py` — eleven new cues and eleven new probes;
  the structural walker; `content-character-profile` strengthened to profile the
  masked body so it generalises.
- `tests/unit/p4/test_p4_promotion_cue_identifiability.py` — the v1 and v2 leaks
  pinned at their measured values under their own constructions; the v3 register
  pinned clean.
- `tests/unit/p4/test_p4_battery_requires_judgement.py` — rewritten for the v3
  subtypes and shape uniformity; no longer shells out to git.
- `research/failures/2026-08-label-recoverable-from-construction-cue/README.md` —
  a dated pointer to this repair appended under "Correct response" item 7.

Not touched, deliberately:

- `papers/orion-14-verified-scientific-discovery/evidence/protected_v2/` —
  `PUBLICATION_METRICS_V2.json` and `RESULT_ATTESTATION_V2.md` stand as the
  record of what the cued battery produced.
- `papers/orion-14-verified-scientific-discovery/protocol/PROTECTED_RUN_BINDINGS_V2.json`
  and the `p4_*_v2` workflows. These bind the generator by digest, through the
  composite `harness_sha256`
  `094f43cb320f8e8e3196049269b20ac22e7e94fa9890b80f27f38ef49f7c82ea`, which the
  repair invalidates — the same recipe over the repaired host directory no longer
  reproduces it. That binding is a record of what the frozen V2 execution ran,
  not a checksum of the current tree, so **it is left stale on purpose** —
  regenerating it would rewrite
  the record rather than improve it. `test_p4_v2_execution_freeze.py` asserts the
  *recorded* value rather than recomputing it, and still passes. The generator
  appears in no `SHA256SUMS`; the journal package binds only the manuscript, the
  claim ledger and the two `protected_v2` result files.
- `papers/orion-14-verified-scientific-discovery/manuscript/main.tex` and
  `tests/unit/p4/test_p4_metric_headroom.py`, which pin the manuscript's H3
  saturation language to the V2 metrics. Both remain true of V2 and are outside
  this repair's scope; a V3 campaign that reached publication would have to
  revisit them.
