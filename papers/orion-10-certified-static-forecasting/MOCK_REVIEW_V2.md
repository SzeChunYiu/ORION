# QG2 mock peer review V2

**Subject:** `MANUSCRIPT_V2.md`  
**Method:** three mutually blind reviews, then editor synthesis.  
**Authority:** internal adversarial review only.

---

# Reviewer 1 — Formal methods / certification

## Major R1.1 — make the certificate lattice explicit in one formal object

The manuscript explains the authority classes well, but the central scientific contribution would be clearer if the forecast returned a typed record rather than prose-level categories.

Recommended definition:

`ForecastCertificate = {value, upper_bound_proof, exact_support_theorem, closed_form_status, exact_receipt_status, scope}`.

The manuscript need not change the implementation, but it should give a formal reporting schema and populate it for (i) an exact old-panel row, (ii) the QG5 refuting row, and (iii) an unverified library row.

**Severity:** P1, text/formalization only.

## Major R1.2 — distinguish theorem-backed exactness of `F2` from runtime implementation correctness

`C_DP=C_D++` is a theorem about the mathematical family. The executable `F2` implementation is exact only if its enumerator faithfully computes the family minimum. The manuscript currently approaches this distinction but should state the implementation binding/checker that connects code output to the theorem object.

**Severity:** P1 reproducibility/formal boundary.

## Decision

Revision required, no new science.

---

# Reviewer 2 — Quantum compilation / nearest work

## Major R2.1 — avoid claiming a general quantum-resource-estimation contribution

The Related Work section is appropriately cautious, but the title/abstract phrase “quantum compilation” could still be read as broad. The manuscript should say early that the objective is a frozen structural TARE support-count cost, not gate count, T-count, physical qubits or runtime.

**Severity:** P1 framing.

## Major R2.2 — the QG7 second refutation must not make QG2 look unfinished

The manuscript uses later QG7 as evidence that cheap closed forms may fail again. Good. But readers may ask why submit before the latest all-`n` closed-form family is proved.

Recommended response: make the paper's object **certificate-layered forecasting**, for which the absence of a final smallest closed form is not a missing prerequisite because `F2=C_D++` is already theorem-backed exact. The interpretability search is explicitly a companion/open optimization.

**Severity:** P1 argument architecture, no experiment.

## Decision

Strong paper after scope clarification.

---

# Reviewer 3 — Statistics / reproducibility / reporting

## Major R3.1 — 9,545/9,546 needs panel decomposition in the main evidence table

The manuscript correctly rejects a population-accuracy interpretation. It should nevertheless show where the denominator comes from so the one error cannot be perceived as benchmark cherry-picking. Add a table with structured `n=2`, fresh seeded, chemistry/receipt-bound and other exact comparison counts, plus the protocol/seed/source.

**Severity:** P1 display/reporting.

## Major R3.2 — timing belongs in supplement unless a target journal requires systems evaluation

Because the scientific story is exactness/refutation, cache-sensitive speedup summaries may distract and invite systems-level comparisons that the paper is not designed to support. Default to supplement and retain environment/profiling data there.

**Severity:** P2 editorial.

## Major R3.3 — unverified forecasts must never enter exactness plots

Keep forecast-only library rows in a separately styled table/figure. A figure combining verified and forecast-only values with the same glyph would be misleading even if the caption explains it.

**Severity:** P1 figure-integrity blocker.

## Decision

Revision required, no new data.

---

# Editor synthesis

## Shared conclusion

All three reviewers agree that the paper's scientific object is complete on the current evidence cut. The missing work is **formal reporting structure, scope discipline and display integrity**, not another forecasting experiment.

## Minimum-sufficient repairs

1. Add a typed `ForecastCertificate` reporting schema and three worked rows (exact, refuted, forecast-only).
2. Add the executable-to-theorem binding statement for `F2` and name its independent enumeration/referee gates.
3. Put “frozen structural support-count objective” in Abstract/Introduction before any broad resource-estimation comparison.
4. Explain explicitly why QG7's open smallest-closed-form problem is not a blocker for theorem-backed `F2` exactness.
5. Add exact benchmark decomposition table; do not present 9,545/9,546 alone.
6. Keep forecast-only rows visually separate from verified results.
7. Move timing to supplement by default.

## Editorial disposition

`REVISION_REQUIRED__NO_NEW_SCIENCE__CENTRAL_REFUTATION_STORY_ACCEPTABLE`