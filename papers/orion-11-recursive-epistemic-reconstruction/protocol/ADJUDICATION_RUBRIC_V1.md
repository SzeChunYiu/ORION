# ORION-P1 Adjudication Rubric V1 — MODEL-BASED PANEL

**Provenance: MODEL-BASED. This rubric governs a panel of language-model judges, not humans.**
Every label produced under it carries `AdjudicationStatus.MODEL_ADJUDICATED`, which is a tier
distinct from `ADJUDICATED` (human panel) and from `MECHANICAL_GOLD` (constructed ground truth).
No artifact produced under this rubric may be reported, cited or re-tiered as human adjudication.
Issue #98 Step 3 asks for "at least two independent adjudicators … written adjudication rubric +
agreement reporting". This document supplies the written rubric; `orion.study.p1.adjudication`
supplies blinded independence, agreement statistics and a mechanically-applied disagreement policy.
No human panel was convened, and none is claimed.

| Field | Value |
| --- | --- |
| Rubric id | `P1.adjudication-rubric.v1` |
| Status | `FROZEN` |
| Adjudicator kind | `model_panel` |
| Binds | `PROTOCOL_V1.json` → `access_policy.hidden_labels`, `access_policy.evaluator_custody` |
| Mechanism | `src/orion/study/p1/adjudication.py` |
| Hash covers | the bytes strictly between the `RUBRIC-BODY-BEGIN` / `RUBRIC-BODY-END` markers |

<!-- RUBRIC-CONTENT-SHA256: 543139fb00d71258c7fa11fb025bd8e307f981fe9c7562049f3852fd5d2914b8 -->

Verify with `orion.study.p1.adjudication.load_rubric(path)`, which recomputes the digest over the
body and refuses the file on mismatch. A panel run stamps this digest into every verdict; a judge
that answered from a different rubric revision is refused, not silently pooled.

<!-- RUBRIC-BODY-BEGIN -->

## 0. What a judge is deciding

**Provenance — inside the freeze, not a header note.** This panel is **model-based**. Every label it
issues carries `AdjudicationStatus.MODEL_ADJUDICATED`, a tier distinct from `ADJUDICATED` (human
panel) and from `MECHANICAL_GOLD` (constructed ground truth). No result produced under this rubric
may be reported, cited or re-tiered as human adjudication. Promotion out of the model tier requires a
real human adjudication record, which this mechanism cannot supply and `AdjudicationRecord` refuses
to accept from it. A blinded, rubric-driven, kappa-reported model panel is a legitimate published
methodology; calling it a human panel would be fabricated provenance. This paragraph is covered by
the content hash, so stripping it changes the digest and voids every run stamped with the old one.

The unit of adjudication is a **case**, not a system's run. For each case the judge decides, from
the public view alone, whether the task *as stated* can be carried to a correct root answer without
revising the problem's own coordinates. The panel exists to establish non-mechanical labels — cases
whose gold cannot be constructed by fiat — and its output is an input to evaluation, never a
participant in it.

## 1. Inputs — exactly what a judge may see

A judge receives the frozen `PublicView` (`src/orion/study/p1/cases.py`) and this rubric body:

- `case_id` — opaque identifier; it is refused at construction if it names its own label;
- `public_prompt` — the task exactly as a system under test receives it;
- `observable_resources` — the observable trace: the manifest of everything any system may see or
  retrieve for this case;
- `budget_class` — the matched resource envelope.

A judge **never** receives `ProtectedGold`, `HiddenShiftCase.task_family`, another judge's verdict,
or any prior panel result. This is enforced by type: the panel entry point accepts `PublicView`
instances only and refuses any object carrying a `protected_gold` attribute. If a future revision
supplies execution traces beyond `observable_resources`, this rubric must be re-frozen as V2 — the
input set is part of what the content hash covers.

## 2. Output — three questions plus rationale

| Field | Domain |
| --- | --- |
| `reframe_warranted` | `true` / `false` / `null` (ABSTAIN) |
| `responsibility_class` | one of the six classes in §3, or `null` (ABSTAIN) |
| `coordinates` | the revised coordinates, from §4; empty when no reframe is warranted |
| `reopen` | prior closure ids to reopen; `()` when no reframe is warranted; `null` = ABSTAIN |
| `confidence` | `[0, 1]`, self-reported |
| `rationale` | required, including for an abstention — an unexplained verdict is not auditable |

`confidence` is **recorded and reported, never gating**. A model judge's self-reported confidence is
not a calibrated probability, so V1 does not let it move a label; it is retained for post-hoc
calibration analysis.

Coherence is mechanically enforced: `reframe_warranted` must equal `responsibility_class ∈
{formulation, representation, decomposition, measurement}`; a warranted reframe must name at least
one coordinate; a non-warranted verdict must name none and must reopen nothing.

## 3. Decision rules — applied in order, first match wins

**R1 — Solvability-as-stated.** Could a competent solver, using only `observable_resources` within
`budget_class`, reach a correct root answer *without* changing the problem's formulation,
representation, decomposition or measurement model?

- yes → no reframe is warranted; go to **R2**;
- no → a reframe is warranted; go to **R3**;
- cannot be determined from the public view → **ABSTAIN** (§5).

**R2 — Non-warranting class.** The blocker is one of exactly two kinds:

- `evidence` — a fact, record or measurement is missing but obtainable: it is listed in
  `observable_resources`, or a further retrieval of the same kind would supply it;
- `execution` — a tooling, runtime, format or budget failure, with the problem statement intact.

Neither warrants a reframe. Over-broad reframing on these two classes is the specific defect this
rubric exists to catch (`PROTOCOL_V1.json` → `P1.H2`).

**R3 — Warranting class.** Apply in this order; the first that matches wins:

1. `formulation` — the statement omits the governing parent domain, or states an objective that
   cannot express the true requirement. Test: naming the omitted discipline or objective changes
   what counts as success.
2. `representation` — the objective is right, but the stated variables, coordinate system or
   encoding cannot express the structure. Test: a change of variables makes it tractable *without*
   changing what success means.
3. `decomposition` — objective and representation are right, but the stated subproblem split or
   interface boundary is wrong: a subproblem is unsolvable in isolation, or the interface drops a
   needed coupling.
4. `measurement` — objective, representation and decomposition are right, but the stated metric or
   operationalization does not measure the construct it claims (proxy mismatch, wrong population,
   wrong unit or normalization).

**R3-tiebreak.** If two classes both match, choose the **upstream-most** in the order above:
revising an upstream coordinate invalidates the downstream ones, so the upstream class is the
responsible one. If the two candidates are genuinely independent — neither is upstream of the other,
and repairing either alone leaves the task unsolvable — **ABSTAIN**. Never split the difference.

**R4 — Which prior closures reopen.** Reopen a closure `C` **iff** `C`'s justification cites,
assumes, or was derived under the coordinate being revised. Closures independent of the revised
coordinate are **not** reopened: full reset is a failure mode, not a safe default. State the minimal
set. If closure dependencies are not observable from the public view, answer `null` (ABSTAIN on this
question only) — **never** the empty set, because the empty set is the positive claim that nothing
depends on the revision.

**R5 — Coordinates.** Name the coordinates actually revised, drawn from §4. One class may revise
more than one coordinate. Coordinates are recorded for reframe-target scoring; they are not part of
the panel's agreement statistics.

## 4. Coordinate vocabulary

| Class | Coordinates |
| --- | --- |
| `formulation` | `objective`, `parent_domain`, `constraint_set`, `scope_boundary` |
| `representation` | `state_encoding`, `coordinate_system`, `variable_set`, `units_basis` |
| `decomposition` | `subproblem_split`, `interface_contract`, `ordering`, `coupling` |
| `measurement` | `metric_definition`, `estimator`, `population`, `normalization` |
| `evidence` | *(none — no reframe)* |
| `execution` | *(none — no reframe)* |

## 5. The ABSTAIN branch — a judge that cannot tell must not guess

Abstain — `reframe_warranted = null` — whenever any of these hold:

- the public view contains no artifact that discriminates between a warranting class (§3) and a
  non-warranting one (§2);
- R3-tiebreak leaves two independent candidate classes;
- the case requires domain competence the judge does not have, and the resources do not supply it;
- `observable_resources` is empty, so evidence-availability under R2 cannot be assessed at all.

Abstention is a first-class outcome, not a failure. It is never a coin flip, never "pick the more
likely one", and never resolved by looking at what the other judges said. A per-question abstention
is permitted on `reopen` alone (R4); an abstention on `reframe_warranted` abstains on all three.

## 6. Worked examples

### P-1 — positive, `formulation`

*Prompt:* "Fit a decaying exponential to the attached sensor series and report the decay constant τ
with a 95% interval." *Resources:* `series.csv`, `sensor_datasheet.pdf`, `site_log.txt`.
The datasheet records two co-located sensors multiplexed onto one channel; the site log records a
calibration swap mid-series. A single-source exponential cannot express a two-source mixture with a
mid-record instrument change, so solving the stated problem returns a τ for a signal that does not
exist. R1 → no. R3(1) matches: the governing discipline (instrument metrology) is omitted and the
objective cannot express the requirement.
**Verdict:** warranted; `formulation`; coordinates `(parent_domain, objective)`; reopen
`(C-baseline-estimate, C-outlier-policy)` — both were derived under "single homogeneous source" —
but **not** `C-file-parsing`, which is independent of the revision (R4).

### P-2 — positive, `measurement`

*Prompt:* "Rank these five retrieval configurations by quality and report the best. Quality = mean
top-1 exact-match accuracy against the reference answer." *Resources:* `eval_set.jsonl`, `configs/`,
`annotation_notes.md`. The notes record that 38% of eval items admit several correct answers by
design, with one listed as the reference. Objective, representation and decomposition are sound; the
stated metric systematically mismeasures the stated construct on more than a third of the set.
R3(1)–(3) do not match; R3(4) does.
**Verdict:** warranted; `measurement`; coordinates `(metric_definition,)`; reopen
`(C-config-shortlist,)` if the shortlist was pruned with the same metric, **not**
`C-eval-set-provenance`.

### N-1 — negative, `evidence`

*Prompt:* "Report subsidiary X's FY2024 revenue and the year-on-year change." *Resources:*
`consolidated_report_2024.pdf`, `filings_index.csv`. The consolidated report does not break out
subsidiary X, but the filings index lists the standalone subsidiary filing, unretrieved. Formulation,
representation, decomposition and measurement are all adequate; the blocker is a fact not yet
fetched from a listed resource. R1 → yes; R2 → `evidence`.
**Verdict:** not warranted; `evidence`; coordinates `()`; reopen `()`.

### N-2 — negative, `execution`

*Prompt:* "Compute the pairwise correlation matrix over the 400 series in `panel.parquet` and report
the three most correlated pairs." *Resources:* `panel.parquet`. The first attempt dies out of memory
in the parquet reader. The statement is exactly right; chunked re-execution resolves it. R1 → yes;
R2 → `execution`.
**Verdict:** not warranted; `execution`; coordinates `()`; reopen `()`.

### A-1 — ABSTAIN

*Prompt:* "Determine whether treatment A outperforms treatment B in the attached trial data."
*Resources:* `trial.csv`. There is no protocol document, no endpoint definition and no allocation
record. The judge cannot tell whether the stated comparison mismeasures the endpoint
(`measurement`, warranting) or whether the endpoint definition is simply an unretrieved record
(`evidence`, non-warranting). The two candidates sit on opposite sides of the reframe line and no
observable artifact discriminates them.
**Verdict:** ABSTAIN on all three questions. The rationale must name the artifact that would resolve
it — here, the trial protocol's primary-endpoint definition.

## 7. Frozen disagreement policy

Frozen **before any verdict was seen**, and covered by this document's content hash. The mechanism
parses this exact block and refuses to run against a `DisagreementPolicy` that differs from it.

<!-- POLICY-BEGIN -->
```json
{
  "policy_id": "P1.model-panel-adjudication.v1",
  "min_judges": 2,
  "quorum": 2,
  "kappa_threshold": 0.6,
  "require_defined_kappa_for_majority": true,
  "require_strict_majority": true
}
```
<!-- POLICY-END -->

Applied mechanically, per case and per question, in this order:

1. **Independence not witnessed** (§9) → the whole panel run is void. No record is emitted.
2. **Fewer than `quorum` non-abstaining verdicts** → `CANNOT_CHECK`. An abstention that breaks
   quorum is reported as `ABSTENTION_BREAKS_QUORUM`, distinct from a panel that was never large
   enough.
3. **Unanimous among the non-abstaining verdicts** → labelled `MODEL_ADJUDICATED`. Unanimity is not
   gated on κ: κ gates *majority* resolutions, because dissent is where chance agreement could
   manufacture a label. When unanimity is total across the batch, κ is undefined by construction and
   the panel is flagged degenerate (§8) — the label stands, the caveat is published.
4. **Strict majority, κ defined for that question and κ ≥ 0.6** → labelled `MODEL_ADJUDICATED` with
   every dissenting judge id recorded on the record.
5. **No strict majority** (a 1-1 tie, or any tie at the top) → `CANNOT_CHECK`. Never a coin flip,
   never the ordering of the judge list.
6. **Majority but κ undefined** → `CANNOT_CHECK` (`AGREEMENT_UNDEFINED`). Could-not-check is never
   reported as checked-and-fine.
7. **Majority but κ < 0.6** → `CANNOT_CHECK` (`AGREEMENT_BELOW_THRESHOLD`). Low agreement degrades to
   `CANNOT_CHECK`; it never degrades to "the majority regardless".

The κ floor of 0.6 is the lower bound of Landis & Koch "substantial" agreement. A `CANNOT_CHECK`
case is **excluded from adjudicated analysis and retained in the archive**, consistent with
`PROTOCOL_V1.json` → `exclusion_policy`: the excluded record remains archived, never deleted.
Questions are resolved independently, so a case may be labelled on `reframe_warranted` while its
`reopen` set remains `CANNOT_CHECK`; the per-question inclusion flag, not the case status, governs
which metric may use it.

## 8. Agreement reporting

Reported **per question** — `reframe_warranted`, `responsibility_class`, `reopen_set` — never as one
pooled number:

- Cohen's κ for exactly two judges; Fleiss' κ for three or more; raw mean pairwise agreement and the
  unanimity rate alongside both, always.
- κ is computed on **complete cases** — items every judge rated — with the number of items dropped to
  abstention reported next to it.
- κ is undefined when fewer than two items survive, or when expected agreement is 1 (degenerate
  marginals). Undefined is reported as undefined with its reason, never as zero and never omitted.
- Raw agreement alone is not reportable. Two judges can agree 90% of the time on a 90%-prevalent
  label and carry κ = 0 — an agreement rate that is entirely chance under the observed marginals.
  That is the reason κ gates this panel and raw agreement does not.
- The `reopen_set` κ is **sparsity-dominated**: exact-set categories are near-unique, expected
  agreement approaches 0 and κ approaches raw agreement. Its scale is not comparable to the binary
  `reframe_warranted` κ, and the two must not be averaged. Category counts are published so a reader
  can see the sparsity directly.

## 9. Panel independence

At least two judges, and independence is **verified before any verdict is accepted**, not asserted.
Verified mechanically: distinct judge objects; distinct, non-empty `judge_id`; distinct, non-empty
`lineage_id` (model family and prompt lineage — two judges from one lineage are one judge); a fresh
context per `(judge, case)`, with every issued context id globally unique across the run, so no judge
carries memory of another case; and each verdict stamped with the context id it was actually issued.
A missing or empty id **fails the witness** — the witness never treats "could not determine" as
"independent". Structural, by construction rather than by check: no verdict is ever passed to a
backend, so no judge can see another's answer or its own prior answers.

## 10. Change control

Any edit to this body changes the content hash and therefore invalidates every panel run stamped
with the old digest. Rubric revisions are new versions (`V2`), never in-place edits.

<!-- RUBRIC-BODY-END -->

---

*Not a human adjudication record.* This rubric, the panel it governs and every
`MODEL_ADJUDICATED` label produced under it are model-based. Promotion to `AdjudicationStatus.ADJUDICATED`
requires a real human panel record and is refused mechanically by `AdjudicationRecord`.
