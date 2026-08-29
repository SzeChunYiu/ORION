# typed-merge-evaluator

A reusable, domain-agnostic evaluator for the ORION-03 typed authority
("typed merge") calculus. Encode your own domain as a `SCHEMA_V1.json`
document; no evaluator code changes.

## What it provably does

The evaluator implements the operator of `MANUSCRIPT_V2.md` section 3 exactly:

```
F_R(x)_q = {}                                                  if q in R
F_R(x)_q = sigma(q) | union over rules r with head q of tau_r  otherwise
tau_r((l_a)_{a in A}) = cap_r & intersection_{a in A} l_a
Auth(R) = lfp(F_R)
```

on the finite powerset lattice `(2^Lambda)^Q`. It computes:

1. **Least fixed point** (Theorem 1) — finite convergence, rule-order
   independent. The iteration is bounded by `|Q|·|Lambda| + 1` rounds, the bound
   the theorem itself gives; exceeding it raises rather than truncating.
2. **Untainted proof-tree authorization** (Theorem 2) — a license belongs to a
   claim's label exactly when a finite proof tree carries it through every leaf
   seed and every rule cap. `proof_tree()` extracts one; well-foundedness comes
   from descending strictly in the iteration rank at which each pair appeared,
   so cyclic rule sets cannot produce an infinite tree.
3. **Minimal well-founded retraction** (Theorem 5) — `Ret(R) = A_pre \ A_post`
   as claim-license pairs.
4. **Typed versus flat, and first mixing** — the flat (license-erased) reading is
   the *same* operator over a one-element license universe, not a second
   algorithm. A claim is a **first-mixing** authorization when the flat reading
   derives it but its typed label is empty: the merged system authorizes it and
   no single constituent authority does.

There are no domain constants and no ORION paths in `typed_merge_evaluator/`.
Every parameter that could have been a magic number is either declared in the
instance (licenses, caps, seeds, refutations) or derived from a theorem (the
iteration bound). The round-2 structural model's depth cap is a domain constant
of that study and is deliberately **not** present here.

## Scope and non-claims

The following are copied verbatim from the claim ledgers and are binding on any
use of this package. Rows in the ledgers state the claim text and then its
status; a `DONOR-OWNED`, `OUT OF SCOPE`, `FORBIDDEN` or `NOT CLAIMED` status
means the paper does **not** assert that row.

From `CLAIM_LEDGER.md`:

| ID | Claim | Evidence | Status / boundary |
|---|---|---|---|
| D-C9 | Least-fixed-point, truth-maintenance, Datalog provenance or belief-revision mathematics are new. | Doyle / Martins–Shapiro / Datalog provenance donors. | DONOR-OWNED. |
| D-C10 | The current calculus handles negation, defaults, probabilistic evidence, inconsistency or arbitrary scientific disagreement. | none | OUT OF SCOPE. |

From `CLAIM_LEDGER_R2.md`:

| ID | Claim | Status | Boundary |
|---|---|---|---|
| D2-C8 | Least fixed points, semiring provenance, minimal supports, or deletion robustness are new. | DONOR-OWNED | Explicitly subtracted. |
| D2-C9 | The calculus handles arbitrary negation/probability/inconsistency. | OPEN; NOT CLAIMED | Positive conjunctive core only. |
| D2-C10 | The current cases establish broad human-science usability. | FORBIDDEN | No user study or cross-institution deployment. |

Consequently:

- **No novelty is claimed for anything this code computes.** Least fixed points,
  truth maintenance, positive Datalog, semiring and annotated provenance,
  minimal supports and deletion robustness are donor-owned (Doyle 1979;
  Martins & Shapiro 1988; Bourgaux et al. KR 2022; Abo Khamis et al.
  arXiv:2105.14435; Thapa & Staab arXiv:2607.16443, arXiv:2608.21141). The
  residual is the license vocabulary tied to evidence classes, cap-preserving
  transfer as a statement of nonpromotion, and exact typed retraction.
- **Rules are positive and conjunctive.** Negation, defaults, probabilistic
  evidence and inconsistency are out of scope, and the evaluator will not warn
  you if you try to encode them — it will silently evaluate a different system.
- **Shipping this package is not evidence of broad usability.** D2-C10 forbids
  claiming broad human-science usability, and a reusable package is exactly the
  artifact a reader is likely to over-read as evidence for it. There is no user
  study and no cross-institution deployment. Reusability of an implementation
  and demonstrated usability by third parties are different claims; only the
  first is supported here.
- **The license universe and caps are curated policy, not inferred.** The
  evaluator computes consequences of the typing you declare. It cannot tell you
  that your typing is right.

## Two things the packaged evaluator does *not* support

Recorded here because they came out of auditing the evidence, not out of using
the package.

1. **Round-2's M5 optimality is an identity, not a measurement.** In
   `run_round2.py`, `M5_TYPED_WITNESS := vA or vB` and
   `hybrid := vU and not (vA or vB)`. Therefore `unsafe[M5]` and `needless[M5]`
   are identically false and obstruction precision = recall = 1.0 *for any input
   data whatsoever*. The committed results record this themselves
   (`m5_decision_equals_parent_authorization: true`). What is genuinely
   empirical in round 2 is that 46 hybrids **exist** on upstream-authored
   material, that M1 (the deployed textual merge) authorizes all of them, the
   C3 structural-versus-engine agreement (0 violations in 1962 tasks), the C1
   anchor agreement (186/191), and the 2x invocation cost. The test
   `test_m5_optimality_is_an_identity_not_a_measurement` pins this.
2. **The structural encoding explains 1 of the 46 hybrids.** 45 are recorded
   `structural_kind: "POLICY"`: at least one store *can* build the chain in the
   issuance graph and the engine denies it on policy grounds
   (purpose/EKU/trust admission, which `PROTOCOL_V2.md` section 9 leaves
   deliberately unmodeled). Those are representable here only by seeding the
   engine's per-origin verdicts as oracle facts — see
   `examples/x509-truststore/FU-0379-policy-oracle.json`, which is labelled as
   deriving nothing on its own.

## Layout

```
SCHEMA_V1.json                     normative JSON Schema for a problem instance
REPRODUCTION.md                    exact commands for a third party
typed_merge_evaluator/core.py      the operator, lfp, proof trees, retraction
typed_merge_evaluator/model.py     SCHEMA_V1 parsing and validation
typed_merge_evaluator/analysis.py  typed vs flat, first-mixing, expectations
typed_merge_evaluator/enumeration.py  exhaustive fixed-point check (§11)
typed_merge_evaluator/cli.py       command line entry point
examples/cedar-multipolicy/        8 round-1 origin-witness controls
examples/x509-truststore/          4 round-2 trust-store merge instances
examples/manuscript-cases/         MANUSCRIPT_V2.md section 9 (evidence classes)
examples/build_examples.py         regenerates every example from its source
tests/                             theorem corner cases + committed regressions
```

## Usage

```bash
python -m typed_merge_evaluator examples/x509-truststore/C6-HOSTILE-SPLIT.json
```

Exit codes are distinct so that "could not check" is never reported as "checked
and fine": `0` all expectations held, `1` an expectation failed, `2` an instance
could not be read, parsed or validated.

```python
from typed_merge_evaluator import Problem, Report, retraction_report

problem = Problem.load("my_domain.json")
report = Report(problem)
report.typed_label("my_claim")      # which authorities carry it end to end
report.first_mixing("my_claim")     # merged system yes, every single authority no
retraction_report(problem, ["falsified_claim"])["pairs"]   # Theorem 5
```

## Encoding your own domain

A **license** is whatever independent authority must carry a derivation end to
end. The two shipped domains use different readings, which is the point:

- `examples/cedar-multipolicy/` — licenses are **origin records**. Each required
  atom is seeded with the origins whose record carries it, so the capped
  transfer (intersection of body labels) yields exactly the origins carrying
  every required atom.
- `examples/x509-truststore/` — licenses are **trust stores**. The anchor is
  seeded with the stores that trust it, and each issuance link is capped by the
  stores that hold the subject certificate, so the accumulated intersection is
  the set of stores whose independent closure derives the leaf.

**Two ways to express retraction, and they are not interchangeable.** Use the
`refuted` field for a claim that has been *falsified in the system*: it is
forced to bottom, Theorem 5 gives the exact pairs withdrawn, and the refutation
applies to the typed and flat readings alike. Filter at encoding time — simply
omit a source's licenses from the seeds it would have contributed — for a source
that *never contributes* a license, such as a retracted record. The shipped
examples use both: `examples/x509-truststore/C4-retraction-non-resurrection.json`
uses `refuted`, and `examples/cedar-multipolicy/retracted_evidence_erasure.json`
filters at encoding time and then uses `flat_seeded_claims` to state that the
flat merge lost the retraction marker. Note that `flat_seeded_claims` overrides
**seeds only**: a claim in `refuted` is refuted in both readings, and no value
there can express otherwise.

`MANUSCRIPT_V2.md` uses a third reading in which licenses are evidence classes
(`THEOREM`, `FINITE_EXACT`, `PROSPECTIVE`, `POST_OUTCOME`, ...) and caps encode
nonpromotion. `tests/test_cap_blocks_nonpromotion` exercises that reading, and
`examples/manuscript-cases/case3-d4-bounded-computation.json` encodes section 9
of the manuscript in full. That instance is the sharpest demonstration in the
package: the analytic lemmas are seeded `THEOREM`, the internal support-frontier
scan is seeded `{BOUNDED_COMPUTATION, EXTERNAL_REPLAY}`, and exact `D_4` comes
out with an **empty** label rather than merely a weaker one, because its two
premises share no license. The license-erased reading still derives it, so the
evaluator reports it as first mixing: an untyped record would call it
supported.
