# P3 freeze: the partial-observation failure channel and the coordinate it mines

- **Record id**: `P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE`
- **Date frozen**: 2026-08-21
- **Status at freeze time**: written before the probe corpus was built, before any arm was
  implemented, and before any arm outcome was observed. Every constant below was chosen from the
  structure of the frozen atlases and the text of `orion.knowledge.semantics.compare_meaning`, not
  from any arm result. What *had* been run when this file was written is stated verbatim in §2 and
  §3.2 so that nothing here can be read as a prediction that was really a memory.
- **Gate served**: `P3-U-T5` — *"No new identity coordinate has been discovered from failure and
  prospectively validated."* Unblock as written in the ledger: *"Mine each false merge and false
  split for a candidate discriminating coordinate, then validate it on held-out cases or prove the
  coordinate unnecessary."*
- **Machine-readable twin**: `P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.json`. It carries
  the same parameter block plus its sha256. The runner recomputes that digest from its own constants
  and refuses to execute on a mismatch.
- **Verdict on T5 fixed in advance**: see §7 gate **G8**. This study is pre-committed to *not*
  discharging P3-U-T5, whatever its numbers turn out to be. The reason is structural and is stated
  now, before any number exists.

---

## 1. The failure this is derived from, and why T5's own recipe cannot be followed

T5's unblock instruction presupposes a non-empty set of ORION false merges and false splits. There
is none. Measured with `orion.study.p3.public_reference_audit`, the same instrument on all three
atlases that exist:

| atlas | n | ORION decisions | `P3.FALSE_SCIENTIFIC_MERGE` | `P3.FALSE_SCIENTIFIC_SPLIT` | `P3.OVERRESOLVED_UNRESOLVED_CASE` |
|---|---|---|---|---|---|
| `gold/adjudicated/public-reference-v1` | 32 | 28 `MERGED_CORRECTLY`, 4 `SEPARATED_CORRECTLY` | PASS, 0 of 4 | CANNOT_CHECK `COMPARATOR_NEVER_EXERCISED` | CANNOT_CHECK `NEVER_EXERCISED`, **0 of 0** |
| `gold/adjudicated/public-reference-v1.1-confirmatory` | 32 | 26 `MERGED_CORRECTLY`, 6 `SEPARATED_CORRECTLY` | PASS, 0 of 6 | CANNOT_CHECK, same | CANNOT_CHECK, **0 of 0** |
| `research/p3-coordinate-necessity-v1/cases.jsonl` | 56 | 42 `MERGED_CORRECTLY`, 14 `SEPARATED_CORRECTLY` | PASS, 0 of 14 | CANNOT_CHECK, ORION 0 of 42 | CANNOT_CHECK, **0 of 0** |

**ORION commits zero false merges and zero false splits on every atlas P3 owns.** Mining an empty
set yields nothing. That is the real reason T5 is blocked, and it cannot be repaired by mining
harder.

The one failure channel that *could* produce a candidate coordinate is over-resolution — a system
asserting a relation that the available coordinates do not determine. Its guard,
`P3.OVERRESOLVED_UNRESOLVED_CASE`, has a **zero denominator on every atlas**: no P3 atlas contains a
single gold-`UNRESOLVED` case. Zero violations out of zero opportunities is an absent measurement,
and `orion.programme.guard_exercise.assess_guard` already says so — it returns `CANNOT_CHECK`, and
`GuardAssessment.__post_init__` refuses to let a vacuity reason yield `PASS`. The three-valued
machinery is sound; what is missing is a case.

### 1.1 Why the denominator is zero — a structural fact, not a sampling accident

Census over all 9 coordinates of `ScientificMeaningProjection` across all 88 cases in the three
atlases (run before this freeze; the numbers are in §2):

> **No P3 atlas contains a single partially-observed pair.** Every coordinate is either observed on
> *both* sides of the pair or absent on *both* sides. The count of coordinates observed on exactly
> one side is zero, in every atlas, for every coordinate.

`compare_meaning` reads an absent coordinate as *agreement* — `_same_or_empty`, and the
`left.X and right.X and left.X != right.X` guards, all fall through when either side is empty; so
does the polarity contradiction test, which requires both polarities to be known. A corpus with no
partially-observed pair therefore never exercises that reading. The absent-means-agreement branch of
the identity rule has never been tested by P3's evidence.

### 1.2 The defect in the rule, stated before any measurement

`compare_meaning` overloads the single "absent" value of each coordinate three inconsistent ways
inside one function:

| coordinate group | field(s) | absent value | how absence is read |
|---|---|---|---|
| list coordinates | `referent_ids`, `construct_ids`, `measurement_ids`, `temporal_context_ids`, `assumption_ids` | `()` | **agreement** (merge-ward) |
| string coordinates | `attribution_id`, `discourse_relation` | `""` | **agreement** (merge-ward) |
| polarity | `polarity` | `Polarity.UNKNOWN` | **agreement** (merge-ward) |
| modality | `modality` | `Modality.UNKNOWN` | **a distinct value** (separation-ward) |

Eight coordinates say "not stated means the same"; the ninth says "not stated is its own value". The
type cannot express the difference between *assessed and empty* and *never assessed*, so the rule
has to guess, and it guesses differently in different places. This is the
`VACUOUS_GUARD_ZERO_DENOMINATOR` /`not None is True` shape (`research/failures/
2026-08-vacuous-guard-zero-denominator/`) pushed down one level, into the coordinate type itself.

**The failure this study is derived from is therefore:** *silencing one side of the coordinate that
carries the decision converts a separation into a merge, and the system reports the merge with the
same confidence it reported the separation.*

## 2. What had already been run when this document was written

Full disclosure, because it bounds what §7's gates can honestly be called predictions.

1. The three audits in §1's table. Reproduction of an already-recorded state.
2. A **redactability census** over the three atlases: for each case and each coordinate, is the
   coordinate observed on both sides, do the values differ, and does emptying it on one side change
   `compare_meaning`'s answer? Results:

   | atlas | redactable (case, coordinate) pairs | breakdown | every one changes the answer to |
   |---|---|---|---|
   | `public-reference-v1.1-confirmatory` | **6** | 6 `polarity`, all parent gold `CONTRADICTORY` | `COMPATIBLE` |
   | `public-reference-v1` | **4** | 4 `polarity`, all parent gold `CONTRADICTORY` | `COMPATIBLE` |
   | `coordinate-necessity-v1` | **14** | 6 `polarity`, 4 `measurement_ids`, 4 `temporal_context_ids` | `COMPATIBLE` |

   The 14 are exactly ORION's 14 separations on the extended atlas; the 6 are exactly its 6 on the
   confirmatory parent. Redaction on one side destroys **every** separation ORION makes.
3. A **one-sided-absence census**: zero, everywhere (§1.1).

Consequently gates **G3** and **G4** below are near-determined by facts already in hand, and this
document does not pretend otherwise: they are recorded as *pre-committed thresholds on an
already-characterised construction*, which is what a construction precondition is, not as blind
predictions. The quantities genuinely unknown at freeze time are **G5** (the mining census), **G7**
(the cost of the strict reading on intact corpora) and the roll-up verdicts.

## 3. What this study can and cannot be

### 3.1 Claim scope, fixed now

> **PARTIAL_OBSERVATION_OF_FROZEN_ATLASES_ONLY.** The probe is produced by mechanically redacting
> one coordinate on one side of cases in atlases that already ship in this repository. It
> establishes a property of `compare_meaning` — how the rule behaves when a decisive coordinate is
> not stated by one source — and nothing about how often scientific sources omit a decisive
> coordinate. It is **not** a corpus, **not** an accuracy benchmark, and may **not** be substituted
> for the public-reference atlas in any external-validity claim. No accuracy, false-merge,
> false-split or superiority number computed over the probe may be reported as evidence about
> ORION's competence on scientific text.

### 3.2 Why probe gold is `UNRESOLVED`

A probe case is two projections that are observationally identical to a pair which genuinely agrees
on the redacted coordinate. No decision procedure reading only the projections can separate the two
worlds. Therefore **any** relation other than `UNRESOLVED` is asserted without warrant, and
`UNRESOLVED` is the gold. This is the module's own stated contract — *"It prefers contextual
separation or UNRESOLVED over false equivalence"* — applied to its own inputs.

The alternative reading is recorded too, and reported alongside: under **`PARENT_GOLD`** scoring,
the probe case keeps the parent's adjudicated relation, on the ground that redacting a projection
did not change what the two claims are. Both scorings are computed from the *same* arm decisions, so
neither is a re-run and no parameter is chosen between them. `UNRESOLVED` is **primary**;
`PARENT_GOLD` is secondary and reported whichever way it falls.

### 3.3 No committed artifact is modified

`orion.knowledge.semantics` is **not** edited. Every candidate rule is a study-local arm. No frozen
atlas, result, receipt or evidence file is touched. Only new files are added.

## 4. The probe corpus

### 4.1 Coordinates and their absent values

Frozen, exactly these nine, with exactly these absent values:

```
referent_ids -> ()      construct_ids -> ()   measurement_ids -> ()
temporal_context_ids -> ()   assumption_ids -> ()
attribution_id -> ""    discourse_relation -> ""
polarity -> Polarity.UNKNOWN    modality -> Modality.UNKNOWN
```

### 4.2 Redaction rule

A parent case is **redactable on coordinate `c`** iff all four hold:

1. `c` is observed (not equal to its absent value) on **both** sides;
2. the two observed values **differ**;
3. the parent's gold relation is in `orion.study.p3_public_reference.NONMERGE_RELATIONS` — the pair
   is one gold says must not be merged;
4. `compare_meaning` on the untouched parent returns exactly the parent's gold — the case is one
   ORION currently gets right, so a probe failure cannot be inherited from a pre-existing error.

For each redactable `(case, c)` the probe emits **two** cases: `c` set to its absent value on the
left, and on the right. Nothing else is altered. Probe gold is `UNRESOLVED`.

Probe case id: `<parent_case_id>|redact=<c>|side=<left|right>`.

### 4.3 Corpora

| corpus id | source | role |
|---|---|---|
| `INTACT_DERIVATION` | `papers/.../gold/adjudicated/public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl` (n=32, real, published) | harm measurement; parent of the primary probe |
| `INTACT_HELDOUT_REAL` | `papers/.../gold/adjudicated/public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl` (n=32, real, separate adjudication round) | harm measurement; parent of a held-out probe |
| `INTACT_HELDOUT_SYNTHETIC` | `research/p3-coordinate-necessity-v1/cases.jsonl` (n=56; the 32 above plus 24 synthetic) | harm measurement; parent of a held-out probe reaching `measurement_ids` and `temporal_context_ids`, which no real atlas populates |
| `PROBE_DERIVATION` | redaction of `INTACT_DERIVATION` | **primary** |
| `PROBE_HELDOUT_REAL` | redaction of `INTACT_HELDOUT_REAL` | held-out |
| `PROBE_HELDOUT_SYNTHETIC` | redaction of `INTACT_HELDOUT_SYNTHETIC` | held-out |

**"Held-out" is used in a bounded sense and the bound is stated now**: `INTACT_HELDOUT_REAL` is a
different frozen adjudication round over overlapping source material, and
`INTACT_HELDOUT_SYNTHETIC` extends the derivation atlas with 24 cases authored by a different
session under a different freeze. Neither is a fresh sample from an unseen population, and neither
may be described as one. What they hold out is the *coordinate stratum*: the derivation probe
reaches only `polarity`, the synthetic held-out probe also reaches `measurement_ids` and
`temporal_context_ids`.

### 4.4 Construction precondition — checked before any arm runs

The runner aborts, reports `CONSTRUCTION_PRECONDITION_FAILED`, and emits **no arm number** if any of
these fails on any corpus:

- **C1** `PROBE_DERIVATION` is non-empty.
- **C2** every probe case has exactly one coordinate at its absent value on exactly one side, and
  that same coordinate is observed on the mirror side.
- **C3** every probe case differs from its parent on exactly that one field of that one side.
- **C4** every probe case's parent gold is a non-merge relation and `compare_meaning` reproduces it
  on the untouched parent.
- **C5** every probe case's gold is `UNRESOLVED`.

This is the P2 `echo_campaign` discipline: a world that lacks the intended structure is not the
world under study, and no arm number over it means anything.

## 5. Arms

Every arm is a total function `(left, right) -> MeaningRelation`. No arm sees gold, the corpus id,
or the case family.

- **`A0_orion_current`** — `orion.knowledge.semantics.compare_meaning`, imported and called
  verbatim. This is the system that produced the negative.
- **`A1_observedness_asymmetric`** — return `UNRESOLVED` if some coordinate is at its absent value on
  **exactly one** side; otherwise delegate to `compare_meaning`.
- **`A2_observedness_strict`** — return `UNRESOLVED` if some coordinate is at its absent value on
  **either** side; otherwise delegate to `compare_meaning`.

**Stated limitation of A1 and A2, in advance.** `ScientificMeaningProjection` has no third value, so
neither arm can actually tell *assessed-and-empty* from *never-assessed*; both approximate the
candidate coordinate by treating absence as non-observation. That approximation is the point: **A2's
cost on the intact corpora (G7) is a lower bound on how much information the missing third value
would carry.** Neither arm is proposed for adoption by this freeze.

## 6. The candidate coordinate

Mined from the failure in §1.2, and named now:

> **`observation_status`** — a per-coordinate value in `{OBSERVED, NOT_OBSERVED}` attached to each
> projection, so that "this source states no measurement" and "this source was never assessed for a
> measurement" are different states of the projection.

## 7. Primary outcome, secondary outcomes, and pre-committed gates

**Primary outcome.** `P3.OVERRESOLVED_UNRESOLVED_CASE` for arm `A0_orion_current` on
`PROBE_DERIVATION`, as a `GuardExercise` (opportunities, violations) assessed by
`orion.programme.guard_exercise.assess_guard` at `max_violation_rate = 0.0`. The guard's opportunity
definition, decision taxonomy and denominator rule are reused from
`orion.study.p3.identity_opportunity` unchanged.

**Secondary outcomes, all reported whichever way they fall.** The same guard for A1 and A2 on all
three probes; `P3.FALSE_SCIENTIFIC_MERGE` for every arm on every corpus; the `PARENT_GOLD` scoring
of §3.2; the full `IdentityDecisionKind` census per arm per corpus; and the mining census of §7.1.

### 7.1 The mining census — T5's instruction, executed

For any pair, define

> `discriminating_coordinates(L, R)` = the coordinates on which **both** sides are observed and the
> observed values **differ**.

This is "what could have told these two apart". For every decision by any arm on any corpus whose
`IdentityDecisionKind` is `FALSE_MERGE`, `FALSE_SPLIT`, `MERGED_WHERE_GOLD_UNRESOLVED` or
`SEPARATED_WHERE_GOLD_UNRESOLVED`, the runner records that set. A failure with a **non-empty** set is
explained by a coordinate ORION already carries. A failure with an **empty** set is one no coordinate
in the representation can discriminate.

### 7.2 Gates

| Gate | Statement | Consequence if it fails |
|---|---|---|
| **G1 CONSTRUCTION** | C1–C5 of §4.4 hold on every corpus | Abort. `CONSTRUCTION_PRECONDITION_FAILED`, no arm numbers reported. |
| **G2 CHANNEL_OPENED** | A0's `P3.OVERRESOLVED_UNRESOLVED_CASE` exercise on `PROBE_DERIVATION` has `opportunities >= 1` | The channel is still closed; the study reports that it failed to open it and makes no further claim. |
| **G3 FAILURE_ON_REAL_CASES** *(primary)* | A0's over-resolution violation rate on `PROBE_DERIVATION` **>= 0.90** | The failure is weaker than §1.2 claims and is reported as weaker, with no retuning. |
| **G4 HELD_OUT** | A0's over-resolution violation rate **>= 0.90** on `PROBE_HELDOUT_REAL` **and** on `PROBE_HELDOUT_SYNTHETIC` | The failure does not carry to the held-out coordinate strata; reported as stratum-specific. |
| **G5 MINING_YIELD** | (a) every failure on an **intact** corpus has a non-empty `discriminating_coordinates` set drawn entirely from the nine existing coordinates; (b) every over-resolution on a **probe** corpus has an **empty** set | On (a) failing: some intact failure demands a coordinate ORION lacks, and that coordinate — not `observation_status` — is the T5 candidate, which this freeze does not cover and which must get its own dated freeze. On (b) failing: some probe failure is discriminable by an existing coordinate and the probe is not isolating the partial-observation mechanism. |
| **G6 HARM_A1** | A1 changes **0** decisions on all three intact corpora | Blocking for any A1 adoption claim. **Pre-declared vacuous**: §1.1 already established that the intact corpora contain zero one-sided-absent coordinates, so A1 *cannot* fire on them and this gate passes for a structural reason. It is recorded as `VACUOUS` and **may not be cited as evidence that A1 is safe.** It is stated here only so the vacuity is on the record rather than discovered later as a pass. |
| **G7 COST_A2** *(reported, non-blocking)* | number and fraction of intact decisions A2 changes, and how many of those destroy a correct answer | No failure condition — this gate exists to publish a cost. |
| **G8 NOVELTY** *(blocking for T5, decided a priori)* | a candidate counts as a **new identity coordinate** only if two **fully observed** projections can differ on it | `observation_status` is by definition constant across all fully-observed pairs, so **G8 fails by construction**. Recorded now: **this study does not discharge P3-U-T5.** |

### 7.3 Verdict rules, fixed now

- The failure channel is called **`CHANNEL_OPENED_FAILURE_DEMONSTRATED`** iff G1 ∧ G2 ∧ G3.
- The held-out extension is called **`FAILURE_CARRIES_TO_HELDOUT_STRATA`** iff that verdict holds and
  G4 passes.
- The T5 entry is **`T5_NOT_DISCHARGED__CANDIDATE_IS_NOT_A_NEW_IDENTITY_AXIS`**, unconditionally, by
  G8. No combination of numbers in this study changes it.
- If G5(a) passes, the recorded finding is
  **`NO_NEW_COORDINATE_DEMANDED_BY_ANY_FAILURE_ON_RECORD`** — the "prove the coordinate unnecessary"
  branch of T5's unblock, discharged for the failures that exist.

## 8. Anti-tuning commitments

1. Every constant in §4–§7 — the nine coordinates and their absent values, the four redactability
   conditions, the two-sides-per-redactable-pair rule, the three arm definitions, the six corpus
   paths, the `0.90` thresholds of G3 and G4, the `0.0` violation ceiling of the primary guard, the
   `UNRESOLVED` primary gold, and every verdict string — is fixed by this document and hashed into
   the JSON twin. The runner recomputes that digest and aborts on mismatch.
2. The probe is derived deterministically from frozen files. There is no seed, no sampling and no
   re-draw.
3. If a number is disappointing, the number is reported. No parameter above is changed after an
   outcome is seen. If any parameter is ever changed, this file is superseded by a new dated freeze
   that states what changed and why, and the old result stands beside the new one.
4. No existing P3 result, receipt, atlas or evidence artifact is modified. Only new files are added.
5. A verdict that turns a `CANNOT_CHECK` into a `PASS` is treated as a warning sign, not a success.
   The intended movement of this study is `CANNOT_CHECK -> FAIL`: a blocker replaced by a
   demonstrated failure is a subtraction from what P3 claims, which is the only direction a repair
   may go.

## 9. Outputs this freeze commits to producing

- `src/orion/study/p3/partial_observation_probe.py` — probe construction, the three arms, the
  gates, and the runner (`main(argv)`, `argv` required, with a `__main__` guard)
- `papers/paper-03-global-knowledge-portrait/evidence/partial-observation-t5/P3_PARTIAL_OBSERVATION_RESULT_2026-08-21.json`
- `papers/paper-03-global-knowledge-portrait/evidence/partial-observation-t5/PROBE_CASES_2026-08-21.jsonl`
- `tests/unit/study/p3/test_partial_observation_probe.py`
- `research/claim_expansion/p3/claude_t5/PROGRESS.md` — the working record
