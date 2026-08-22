# An anti-laundering receipt whose verdict is a string literal beside its rates

**Observed:** 2026-08-21, tracing why every one of P8's five superiority
terminals (#656) is blocked while the paper's authority artifacts report clean
runs, perfect contract accuracy and a terminal that reads `CLEAR`.

**Terminal repaired:** 2026-08-21, see *Repair* below. Everything from here to
that section describes the receipt as observed, before the repair; the quoted
JSON and source are the pre-repair artifact. The `claim_ceiling` half, the
transcribed gold and the X4 donor axis are **not** repaired, and the audit still
blocks on all three.

## Failure

P8 is the authority paper. Its subject is exactly the move where a system grants
itself standing it did not earn, and its extension bench is named after it:
`research/extensions/p8-method-authority/run_anti_laundering_bench.py`, which
scores fifteen frozen coercion and revocation cases against
`orion.transfer.v2.p8_method_authority` and emits
`P9_P10_ANTI_LAUNDERING_SUMMARY_V1.json`:

```json
"contract_accuracy": 1.0,
"illicit_coercion_block_rate": 1.0,
"clean_legal_coverage": 1.0,
"revocation_accuracy": 1.0,
"terminal": "P8_P9_P10_ANTI_LAUNDERING_CLEAR",
"claim_ceiling": "The suite tests bounded coercion/revocation semantics ..."
```

Four rates and a verdict. The rates are computed. The verdict is not:

```python
out = {..., 'illicit_coercion_block_rate': sum(r['pass'] for r in attacks)/len(attacks),
       ..., 'terminal': 'P8_P9_P10_ANTI_LAUNDERING_CLEAR',
       'claim_ceiling': panel['claim_ceiling']}
```

`terminal` is a string literal in the dict display. `claim_ceiling` is the input
echoed back. Neither reads a row, a rate or a digest.

Run the shipped `run()` verbatim against inputs the suite exists to refuse
(`python -m orion.study.p8.terminal_audit`):

| input to the shipped emitter | contract | block rate | clean | revocation | failing rows | `terminal` |
| --- | --- | --- | --- | --- | --- | --- |
| as shipped | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0/15 | `…_CLEAR` |
| every expectation in the frozen panel inverted | **0.0000** | **0.0000** | **0.0000** | **0.0000** | 15/15 | `…_CLEAR` |
| panel untouched, authority table launders everything | 0.5333 | **0.0000** | 1.0000 | 1.0000 | 7/15 | `…_CLEAR` |
| panel untouched, no defeater propagates | 0.7333 | 1.0000 | 1.0000 | **0.0000** | 4/15 | `…_CLEAR` |

The third row is the one that names the failure. The panel is not edited; the
*mechanism* is replaced by one under which every capability output may set every
authority coordinate — total laundering, the exact thing the suite is named
after. All seven registered attacks succeed:

```
p9_confidence_to_validity        BLOCKED -> SUPPORTED
p9_applicability_to_adoption     BLOCKED -> SUPPORTED
p10_generation_to_novelty        BLOCKED -> SUPPORTED
p7_library_stop_to_global_stop   BLOCKED -> SUPPORTED
p6_fibre_to_applicability        BLOCKED -> SUPPORTED
p4_validity_to_novelty           BLOCKED -> SUPPORTED
novelty_to_correctness           BLOCKED -> SUPPORTED
```

`illicit_coercion_block_rate` falls from 1.0 to 0.0, and the receipt still
publishes `P8_P9_P10_ANTI_LAUNDERING_CLEAR`. Over the whole register the number
of distinct terminals the emitter can produce is **1**.

This is not the P6 failure with a new name. There the predicate was a tautology,
so the verdict could not vary because nothing could satisfy its false branch.
Here the measurement varies across its whole range — four independent rates, 1.0
to 0.0 — and the verdict does not move, because the verdict is not downstream of
the measurement at all. A check with no falsifier at least has a check.

`research/development/p8-method-authority-v1/PACKET.md` names that word as a
closure marker: "may close #424 as `P8_P9_P10_ANTI_LAUNDERING_CLEAR`". The
manuscript bridge quotes it as a result: "All fifteen frozen outcomes pass,
yielding `P8_P9_P10_ANTI_LAUNDERING_CLEAR` for this bounded contract suite." The
sentence is true of the shipped run and would have been printed unchanged had
none of the fifteen passed.

### The ceiling is written by the thing it bounds

`claim_ceiling` is `panel['claim_ceiling']`. Replace the panel's ceiling with a
sentence the suite plainly has no right to and re-run:

| field | injected into the panel | emitted in the summary |
| --- | --- | --- |
| `claim_ceiling` | "This suite establishes real method validity, novelty, utility and adoption." | *identical* |

All four rates stay at 1.0. Thirty-three JSON artifacts in this repository carry
a `claim_ceiling`. Of the fourteen emitters that write one, **ten** — this bench
among them — assign `panel["claim_ceiling"]` or `protocol["claim_ceiling"]`
straight through from their own input; the other four hard-code a sentence,
which is at least the emitter's own. A limit only the claimant can set is a
statement of intent that arrives in the same field as a measured bound, and
nothing downstream can tell them apart.

### The 1.0s grade a transcription of the tables they score

The four rates are real numbers over a real denominator, and they compare the
panel's `expected` against the shipped rules. But the panel's `expected` labels
*are* those rules:

| panel slice | cases | whose `expected` equals the shipped table lookup |
| --- | --- | --- |
| coercion | 11 | **11** — `'SUPPORTED' if coordinate in LEGAL[source] else 'BLOCKED'` |
| revocation | 4 | **4** — `DEFEATER_COORDS[defeater]` plus the three-defeater reopen set |

Asked as `divergence_of(declared_gold, reference=mechanism_verdict, space=…)`,
the frozen gold departs from the mechanism it grades on **0 of 15** points. It
is `2026-08-label-recoverable-from-construction-cue/` with the construction cue
being the system under test itself: a 1.0 here says the transcription was
faithful, which is a fact about a copy-paste. And the copy is thin — the panel
visits 11 of the 56 `(capability, coordinate)` pairs the table defines (7 of the
49 illegal ones, 4 of the 7 legal ones) and 4 of the 56 `(defeater, coordinate)`
pairs.

None of that is what makes the terminal unconditional. It is why the terminal
had nothing to be conditional on that a reviewer would have accepted.

### The same word at the ledger-cited artifact

The superiority ledger names `P8_X4_AUTHORITY_LIFTING_RESULT_V1.json` for
P8-U-T1, and #656 opens by calling its numbers "a powerful finite law":
"`169/169` valid compositions paired with `169` unbridged widening failures".

`check_p8_x4_authority_lifting.py` produces those 169s from

```python
for _left in DONORS:
    for _right in DONORS:
        assert scientific_terminal(True, full, True, "REFUTED", True, False, False) == "DISCHARGE"
        chain_ok += 1
        assert scientific_terminal(True, full, False, "REFUTED", True, False, False) == "BLOCK"
        chain_widening += 1
```

`scientific_terminal` takes seven arguments — `native, flags, narrowing,
blocker, support_a, support_b, coercion` — and the donor is not among them. Both
loop variables are unused. Measured with `axis_sensitivity` over the checker's
own enumerated space, re-derived here to the published
`canonical_rows_sha256 = ed186b82…`:

| axis | values | comparable sibling pairs | verdict-changing |
| --- | --- | --- | --- |
| `donor` | 13 | 239,616 | **0** |
| `native_valid` | 2 | 19,968 | 19,968 |
| `blocker` | 3 | 39,936 | 7,943 |
| `narrowing_ok` | 2 | 19,968 | 4,615 |
| `protected_coercion` | 2 | 19,968 | 1,209 |
| `support_a` / `support_b` | 2 | 19,968 | 429 each |

So every quantity the artifact publishes is a multiple:

| published | distinct facts | multiplicity |
| --- | --- | --- |
| `state_evaluations` 39,936 | 3,072 | ×13 |
| `terminal_counts` 19,968 / 15,353 / 3,328 / 1,287 | 1,536 / 1,181 / 256 / 99 | ×13 |
| `type_separation_witnesses` 65 | 5 | ×13 |
| `protected_coercion_successes` 65 | 5 | ×13 |
| `blocker_*` 13 / 13 / 13 | 1 each | ×13 |
| `single_support_revocation_survivals` 26 | 2 | ×13 |
| `heterogeneous_chain_successes` **169** | **1** | **×169** |
| `heterogeneous_chain_widening_countermodels` **169** | **1** | **×169** |

The two headline 169s are one argument tuple each. Like the terminal string,
they are constants of the source text: given the script terminates, both are 169
for any theory anyone writes.

Two of the counters are constants in the harder sense. Replaying the shipped
enumeration under five wrong theories of scientific discharge:

| rule for `scientific_terminal` | `donor_conservativity_violations` | `ideal_product_mismatches` |
| --- | --- | --- |
| as shipped | 0 | 0 |
| always discharge | 0 | 0 |
| blocker irrelevant | 0 | 0 |
| widening permitted | 0 | 0 |
| support irrelevant | 0 | 0 |
| scientific type irrelevant | 0 | 0 |

because the checker writes `ideal = scientific_terminal(<the same seven
arguments>)` and `projected_native = native` on the line above its own
comparison. That is the shape `2026-08-unfalsifiable-check-zero-refutation-
capacity/` records, and it is here too; it is not the new part.

### What the existing guard does and does not do

`tests/test_p8_anti_laundering_bench.py` re-derives the summary and asserts each
of the four rates equals 1.0, so a broken authority table does red the suite.
That guard is real and this record does not deny it. What it guards is the
*rates*. Its last line is

```python
assert summary['terminal']=='P8_P9_P10_ANTI_LAUNDERING_CLEAR'
```

— a literal in the test compared against the same literal in the emitter, with
no run in between. The published JSON, the manuscript bridge sentence and the
development packet's closure marker all quote the terminal, and the terminal is
the one field in the receipt that no state of the system under test can change.

## Failure class

`UNCONDITIONAL_TERMINAL_SELF_ISSUED_AUTHORITY`

A receipt publishes a measurement and a verdict, and the verdict is not a
function of the measurement. The rates are real, the denominator is real, the
digest is stable, the emitter is deterministic and reproducible — and the word
that carries the authority is a constant in the emitter's source, alongside a
bound the receipt's own input supplied.

This extends the family rather than repeating it:

- `2026-08-unreachable-operator-inert-ablation/` — the **independent** variable
  never varied.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable never
  varied.
- `2026-08-unapplied-treatment-vacuous-null/` — the **cause** did not vary.
- `2026-08-label-recoverable-from-construction-cue/` — both varied and the
  correlation was with the construction.
- `2026-08-invertible-commitment-vacuous-custody/` — the **commitment** opened.
- `2026-08-unfalsifiable-check-zero-refutation-capacity/` — the **verdict** could
  not vary, because its predicate was a tautology.
- here — **the verdict was never computed.** The dependent variable moved across
  its entire range, on four independent rates, in the same object that published
  the verdict, and the verdict did not move, because there is no predicate to be
  tautological. P6's instrument cannot see this: `measure_refutation_capacity`
  needs a check to measure, and this receipt has a string.

Three properties let it survive review, and each is the P8 subject matter turned
on the paper itself.

1. **A verdict word is indistinguishable from a computed one once serialized.**
   Every reader of `P9_P10_ANTI_LAUNDERING_SUMMARY_V1.json` sees `"terminal":
   "P8_P9_P10_ANTI_LAUNDERING_CLEAR"` next to four 1.0s and reads a conclusion.
   The four 1.0s did not produce it and never could have.
2. **The ceiling protects the claim and is chosen by the claimant.** A
   `claim_ceiling` is exactly the right instrument, and copying it from the input
   turns it into the thing P8 calls a self-certification. The receipt records its
   own limits and no run can dispute them.
3. **A guard on the metric is not a guard on the verdict.** The pytest suite
   pins the rates and would catch a broken table, so the failure never shows as a
   red build. It shows only in the artifact — which is the object that leaves the
   repository.

## Correct response

1. Do not quote a verdict before establishing that some input would have
   withheld it. `orion.programme.terminal_responsiveness` takes the *shipped*
   emitter, a baseline input and a register of **declared withholding cases** —
   inputs a reader can read and agree must not earn the baseline verdict — and
   reports which of them moved it.
2. Return three values. A register that moved nothing is `Outcome.CANNOT_CHECK`,
   which by `Outcome.blocks` stops a promotion exactly as `FAIL` does; a verdict
   that ignored a live case is `FAIL`. The verdict is built from
   `GuardExercise` rather than beside it — the opportunities are the live
   withholding cases and the violations are the ones the verdict ignored — so
   "nobody proposed an input that should have been refused" and "the guard was
   never pressed" are one state with one answer, and `GuardAssessment` already
   refuses to pair `PASS` with a vacuity reason.
3. Trace the receipt's own measured quantities separately from its verdict.
   `contradicted` names the cases where a published rate moved and the verdict
   did not: it is the one state in which the artifact holds a number and a word
   that disagree about the same run, and it is far stronger evidence than a
   verdict that merely failed to move.
4. Exclude the cases that perturbed nothing. A payload leaving every traced
   field where it was is `orion.study.p3.treatment_contrast`'s unapplied
   treatment — the emitter was re-run, not pressed — so it leaves the
   denominator and is reported, exactly as `measure_refutation_capacity` drops
   theories that never diverge from the reference.
5. Perturb the mechanism, not only the panel. A wrong rule cannot be expressed
   as a different benchmark, and the case that names this failure —
   `authority-table-launders-everything` — leaves the frozen panel untouched.
   `overridden` swaps the shipped module's tables for one emitter call and
   restores them unconditionally.
6. Treat a bound the input supplied as a failed bound. `measure_declared_bound`
   injects a ceiling the artifact plainly has no right to and reports whether the
   receipt repeats it; `require_earned` refuses to quote one that does.
7. Ask whether the declared gold could have disagreed with the thing it grades.
   `divergence_of(declared_gold, reference=mechanism_verdict, …)` returns
   `points_changed = 0` of 15 for this panel — the same instrument that named P6's
   "independent" verifier a paraphrase, asked about a benchmark instead.
8. Point the instrument at the shipped artifact. `orion.study.p8.authority_terminals`
   loads `run_anti_laundering_bench.py` and `check_p8_x4_authority_lifting.py`
   from the repository and reproduces the committed `result_digest` and
   `canonical_rows_sha256` before transcribing a claim; one test execs the
   published X4 checker itself. An instrument that only ever runs on its own
   fixture is the failure it was written to catch.
9. Name the axes that only multiply, and divide the published counts through by
   them before quoting any of them. `donor` is inert over 239,616 sibling pairs,
   so #656's "169/169" is one composition fact and one widening fact.
10. Compute the terminal. Done — see *Repair*. It changes the emitted receipt,
    which is pinned by a committed `result_digest`, asserted by
    `tests/test_p8_anti_laundering_bench.py` and cited by
    `METHOD_AUTHORITY_MANUSCRIPT_BRIDGE_V1.md` and
    `research/development/p8-method-authority-v1/PACKET.md`, so the artifact and
    those documents were regenerated together.

## Repair

2026-08-21. `run_anti_laundering_bench.py` now scores each of its four rates as
an `orion.programme.guard_exercise.GuardExercise` — a denominator stated in a
sentence, and the cases that failed against it — and the terminal is
`worst_outcome` over the four assessments:

| input to the shipped emitter | contract | block rate | clean | revocation | `terminal` |
| --- | --- | --- | --- | --- | --- |
| as shipped | 1.0000 | 1.0000 | 1.0000 | 1.0000 | `…_CLEAR` |
| every expectation in the frozen panel inverted | 0.0000 | 0.0000 | 0.0000 | 0.0000 | `…_VIOLATED` |
| panel untouched, authority table launders everything | 0.5333 | 0.0000 | 1.0000 | 1.0000 | `…_VIOLATED` |
| panel untouched, no defeater propagates | 0.7333 | 1.0000 | 1.0000 | 0.0000 | `…_VIOLATED` |
| a panel with no `BLOCKED` coercion case in it | 1.0000 | `null` | 1.0000 | 1.0000 | `…_CANNOT_CHECK` |

The terminal is three-valued. An empty slice emits its rate as `null` and its
assessment as `CANNOT_CHECK/NEVER_EXERCISED`, never as 1.0 — and the terminal
reads the assessments, never the rates, because `not None` is `True` and a
two-valued reader would have scored an absent measurement as clean.

The published verdict does not change: on the shipped panel all four rates
really are 1.0, all four guards are exercised, and `CLEAR` is now earned rather
than asserted. What changed is the receipt: `result_digest` moved from
`sha256:45f359f5…` to `sha256:3103fcd0…`, `terminal_basis` was added (per rate:
guard id, opportunity definition, opportunities, violations, rate, outcome,
reason), and `claim_ceiling` was renamed to `declared_claim_ceiling_from_input`
with a `declared_claim_ceiling_note` saying it is the input's sentence. That
ceiling is still the input's — `measure_declared_bound` still returns `FAIL` for
it, and `python -m orion.study.p8.terminal_audit` still exits 3 on the ceiling,
the transcribed gold and the inert donor axis. Only the responsiveness leg moved,
from `FAIL` (three live withholding cases, three ignored) to `PASS` (three live,
none ignored, two distinct terminals over the register).

## General lesson candidate

**A verdict is evidence only for as long as the run could have produced a
different one.** Deterministic reproduction, a content digest, a real
denominator, a frozen panel, a passing test suite and four rates at 1.0 all
survive a literal intact — every one of them held here — because none of them is
a statement about where the verdict came from.

The sharper form: **ask which field of a receipt the measurement actually
reaches.** A receipt is not one claim, it is a set of fields with different
provenances, and the field a reader quotes is usually the one furthest from the
computation. Every artifact in this repository that publishes a `terminal`, a
`status`, a `state` or a `claim_ceiling` should be asked to produce an input
under which that exact string comes out different — and any field for which no
such input exists should be deleted or derived, because publishing it grants an
authority the run never conferred.

Stated once for the family this extends: `UNREACHABLE_OPERATOR_INERT_ABLATION`
is a mechanism that never ran, `VACUOUS_GUARD_ZERO_DENOMINATOR` an outcome that
could not vary, `UNAPPLIED_TREATMENT_VACUOUS_NULL` a cause that did not vary,
`LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE` a label explained by the construction,
`INVERTIBLE_COMMITMENT_VACUOUS_CUSTODY` a seal that opened,
`UNFALSIFIABLE_CHECK_ZERO_REFUTATION_CAPACITY` a predicate that could not be
false — and this one a **verdict with no predicate behind it at all**.

## Residuals and reopen coordinates

- The terminal repair is made (see *Repair*); the responsiveness leg of the audit
  now passes and the other three legs still block, which is the honest state.
- The ceiling is renamed, not derived. `declared_claim_ceiling_from_input` says
  where the sentence came from, which is all a rename can do; a bound the run
  establishes would be different work.
- `P8_P9_P10_ANTI_LAUNDERING_SUMMARY_V1.json` is *not* wrong as shipped: with
  the shipped tables the four rates really are 1.0. What is denied is that the
  terminal reports it.
- The four rates grade a 15-case transcription of two lookup tables covering 11
  of 56 coercion pairs and 4 of 56 revocation pairs. Widening that panel is a
  separate piece of work and would not by itself make the terminal conditional.
- The same literal-terminal shape appears in the P6 and P7 method-space benches
  (`run_method_fibre_bench.py`, `run_method_space_bench.py`). Neither is audited
  here; both should be, by the same instrument.
- Reopen if `LEGAL`, `DEFEATER_COORDS`, the frozen panel, or the bench's `run()`
  changes: the pinned `result_digest` and `canonical_rows_sha256` will red first.
- The bench's `--check` compares bytes, and the committed receipt is
  `json.dumps(indent=2, sort_keys=True)` with its `rows` re-compacted by hand, so
  `--check` reds on formatting alone. Pre-existing, shared with the P6 and P7
  sibling benches, and untouched by this repair.
