# ORION07.AGREEMENT_NONIDENTIFIABILITY.v1 — CLAIM DISPOSITION

**Date:** 2026-08-28
**Lane:** THEORY
**Terminal reached:** `THEORY_PROVED__INDEPENDENTLY_CHECKED`
**Scientific authority delta for ORION-07 manuscript claims:** `NONE`

---

## 1. What changed

One additive directory was created:

```
papers/orion-07-dual-instrument/theory/agreement-nonidentifiability-v1/
```

Nothing else. No manuscript, ledger, receipt, score, digest, terminal or
submission byte was modified. `submission_tmlr/` was not read, written or
depended upon, so the byte bindings asserted by
`papers/publication_closure/PACKAGE_ADOPTION_V2.json` under issue #1601 are
unaffected.

## 2. What was established

An exact, finite-sample, assumption-free characterization of how much
information inter-instrument agreement carries about instrument accuracy.

| statement | content | status |
|---|---|---|
| Lemma 1 | pointwise accounting identity on `{0,1}^3` | proved, exhaustively checked |
| Theorem 1 | `q = (1-a)/2 + c` | proved, checked |
| Theorem 2 | `(1-a)/2 <= q <= (1+a)/2`, width exactly `a`, sharp | proved, checked |
| Theorem 3 | attainable accuracy pairs are exactly `R(a) = conv{(1-a,0),(1,a),(a,1),(0,1-a)}` | proved, checked both directions |
| Cor. 2.1 | `a=1` implies `q in [0,1]` — perfect agreement is vacuous | proved, checked |
| Cor. 2.2 | `a=0` implies `q = 1/2` exactly | proved, checked |
| Cor. 2.3 | interval width equals `a`; agreement destroys level information | proved, checked |
| Cor. 3.1 | `|pX - pY| <= 1-a`, sharp | proved, checked |
| Cor. 3.2 | agreement constrains neither instrument alone | proved, checked |

Independent verification: two routes that import no proof logic and use exact
rational arithmetic — exhaustive enumeration of all `6434` multiset samples up to
`n=7` across `19` distinct agreement levels, and exact polytope-vertex
enumeration with convex-hull completeness on a `13`-point agreement grid. Both
`PASS` (`RESULT.json`).

Checker discrimination: `5/5` negative controls fire while the unperturbed
statement is accepted (`NEGATIVE_CONTROLS.json`). A `PASS` from this checker is
therefore informative rather than vacuous.

## 3. Relationship to the existing ORION-07 claim — claim-preserving, not claim-widening

`MANUSCRIPT_V3.md` already asserts, and supports with the QG-20 case, that

> this explicit case shows why inter-instrument agreement is not validation.

This lane supplies the **reason** behind that sentence. It converts a
one-counterexample justification into a theorem. It is therefore strictly
claim-preserving:

- it **narrows** nothing and **widens** nothing;
- it does not create, rescore or reinterpret any frontier unit;
- it adds no data, so it cannot and does not relieve `n_valid = 3`;
- it makes the paper's refusal to compute an accuracy figure from agreement a
  **derived consequence** rather than a stated caution.

The `#1609` ORION-07 requirements are respected exactly: `n_valid = 3` stands,
agreement-not-validation remains central, and **no reliability rate is
promoted**. Cor. 2.1 makes reliability promotion formally impossible from
agreement alone, which is the opposite of promotion.

## 4. The frozen case series instantiates the vacuity corollary

On the responsibility axis over the three valid units:

```
a_hat = 3/3 = 1      c_hat = 2/3      pX_hat = pY_hat = q_hat = 2/3
```

Theorem 1 holds with residual `0`. Corollary 2.1 then says the observed perfect
agreement constrains mean accuracy to `[0,1]` — to nothing at all. The value
`2/3` is carried entirely by the deferred outcomes.

This is a descriptive re-reading of already-frozen scored artifacts, listed with
SHA-256 in `SOURCE_MANIFEST.json`. It is **not** a reliability estimate: `2/3` is
three units, and Cor. 2.1 is precisely the statement that it could not have been
inferred without them.

## 5. Adverse and null evidence

All preserved and none softened. The QG-20 adverse result — both instruments
agreed, both were scored misaligned — becomes **more** load-bearing under this
lane, since it is the empirical witness for the `c = 0` edge of an agreement
event. See `EXPECTED_TERMINALS.json` for the full preservation list, which also
retains the contaminated-question dispositions and the open QG19 sharpness
terminal.

No `CANNOT_CHECK` was converted to a pass. The checker reserves exit code `3`
for that outcome and did not use it.

## 6. Donor boundary and novelty

**No novelty is claimed.** The mathematics is elementary and donor-owned:
two-by-two accounting identities, Fréchet-type bounds on joint events given
marginals, and the classical non-identifiability of accuracy from agreement in
no-gold diagnostic-test and latent-class theory. Corollary 2.1 restates the
familiar fact that concordance does not establish validity.

The ORION-specific residual is narrow and stated as such in `THEORY.md` §8: the
exact binding of these donor facts to the ORION-07 dual-instrument contract, and
the homogeneity-versus-correctness formulation in §4. Any future manuscript
treatment must subtract the donor literature explicitly.

## 7. Recommended manuscript action — referred, not taken

This packet does **not** edit the manuscript. The editorial options are:

1. **Do nothing.** ORION-07 remains coherent and submittable exactly as it
   stands. This lane is optional breadth and is **not** a submission blocker.
2. **Cite in Limitations** (recommended, low risk): one sentence replacing the
   qualitative caution with the exact bound, e.g. *"the observed agreement rate
   bounds mean instrument accuracy only to the interval `[(1-a)/2, (1+a)/2]`,
   which at the observed `a = 1` is the whole of `[0,1]`; the reported alignment
   is carried entirely by the deferred outcomes."*
3. **Cite in Discussion** as the formal ground for the agreement-is-not-
   validation position.

Option 2 or 3 would require a manuscript edit and therefore a separate PR with
its own authority record. **Neither is taken here**, because `submission_tmlr/`
is byte-bound under #1601 and any manuscript edit must be sequenced against that
package deliberately rather than as a side effect of a theory lane.

## 8. Blocker status

`ORION-07 IS NOT BLOCKED BY THIS LANE.`

Per issue #1608's portfolio rule and #1617's Wave-1 filing rule, this is
successor theory and must not hold a coherent bounded paper open. The prospective
reliability series described in the candidate note remains separate successor
science with no claim on the current submission.
