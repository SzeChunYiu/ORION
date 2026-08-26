# ORION-10 forecast certificate and benchmark map V2

**Purpose:** close ORION-10 mock-review items R1.1–R3.3 by formalizing forecast authority, executable/theorem binding, benchmark denominators and verified-vs-forecast-only display rules.

## 1. Reporting object

For publication, every reported static forecast should be interpretable as the following logical record:

```text
ForecastCertificate {
  instance_id
  forecast_value
  forecast_method
  feasible_upper_bound_status
  support_theorem_status
  closed_form_exactness_status
  exact_truth_status
  regime_label_status
  scope
  authority
}
```

Recommended status vocabulary:

- `PROVEN_CONSTRUCTIVE`
- `PROVEN_ALL_N`
- `MACHINE_EVIDENCED_FINITE`
- `EXACT_RECEIPT_BOUND`
- `REFUTED_BY_EXACT_COUNTEREXAMPLE`
- `FORECAST_ONLY_NO_TRUTH_RECEIPT`
- `OPEN`

A final JSON/CSV version should be generated from receipts rather than hand-authored.

## 2. Worked certificate rows

### Row A — ordinary verified exact row

```text
instance_id: structured-n2:<row>
forecast_method: original F = min(C_R6L, C_Dplus, f_B)
feasible_upper_bound_status: PROVEN_CONSTRUCTIVE
support_theorem_status: PROVEN_ALL_N (R6S, R6M/raw-support)
closed_form_exactness_status: MACHINE_EVIDENCED_FINITE
exact_truth_status: EXACT_RECEIPT_BOUND
regime_label_status: VERIFIED_ON_REGISTERED_PANEL
scope: frozen structured-n2 panel
```

Interpretation: equality is observed exactly on this frozen row; the all-`n` theorem attaches only to the support-two family, not to the three-family closed form.

### Row B — QG5 refuting instance

```text
instance_id: fresh-seed-20260826:n3:index7
C_DP: 10
F_original: 11
C_Dxx: 10
forecast_method: original F = min(C_R6L, C_Dplus, f_B)
feasible_upper_bound_status: PROVEN_CONSTRUCTIVE__SURVIVES (10 <= 11)
support_theorem_status: PROVEN_ALL_N__SURVIVES (C_Dxx = 10)
closed_form_exactness_status: REFUTED_BY_EXACT_COUNTEREXAMPLE
exact_truth_status: EXACT_RECEIPT_BOUND
regime_label_status: REFUTED_ORIGINAL_LABEL
scope: exact frozen n=3 witness
```

Interpretation: the counterexample refutes only the equality/regime layer. It is not a failure of the safe upper bound or support theorem.

### Row C — unverified library forecast

```text
instance_id: <library subject/matching without committed DP truth>
forecast_method: F/F2 as recorded
feasible_upper_bound_status: according to family-feasibility contract
support_theorem_status: only if instance is demonstrably within R6M/raw-support scope
closed_form_exactness_status: OPEN_OR_FINITE_MODEL_ONLY
exact_truth_status: FORECAST_ONLY_NO_TRUTH_RECEIPT
regime_label_status: FORECAST_ONLY
```

Interpretation: the row may be operationally useful but cannot enter an exactness denominator or be described as a confirmation.

## 3. `F2=C_Dxx` theorem-to-executable binding

The mathematical theorem is:

> Under R6M/raw-support scope, `C_DP=C_Dxx` for every `n`/instance.

The executable forecaster `F2` is publication-authoritative only if its implementation actually computes the exact minimum over the registered D++ family.

The binding chain is:

1. **D++ family definition** — registered/frozen in R6P protocol/result.
2. **Family containment / feasibility** — `C_DP <= C_Dxx` by feasible-family construction.
3. **All-`n` theorem** — R6S proves an optimum exists in D++, so `C_DP=C_Dxx`.
4. **QG5b executable** — independent D++ enumerator implements `F2` without unrestricted DP call.
5. **Hostile witness/referee binding** — QG5b records 658 D++ witness rows checked with zero failures and binds exact matcher/weight-one source rows.
6. **Finite panel zero-error** — implementation consistency evidence; not the source of the theorem.

Publication wording:

> `F2` is theorem-backed exact **provided its D++ enumerator is faithfully bound to the registered family**; QG5b's witness/referee checks test that implementation binding.

Do not write “zero errors prove F2 exact.”

## 4. Benchmark decomposition

The headline `9,545 / 9,546` must never appear without a domain decomposition. The final table should be generated directly from `QG5_CERTIFIED_FORECAST_RESULTS.json`.

At minimum show:

| Panel / source | Exact-truth basis | Instances entering exactness denominator | Original F exact | Original F errors | Notes |
|---|---|---:|---:|---:|---|
| structured `n=2` | unrestricted committed DP reader | 9,261 | 9,261 | 0 | exhaustive registered slice |
| fresh seeded `n=2–3` | frozen-config unrestricted DP | 240 | 239 | 1 | seed `20260826`; exact refuting row at `n=3,index=7` |
| receipt-bound chemistry / public subjects | committed exact receipts where available | derive from receipt | derive | derive | rows without truth receipt excluded |
| other registered exact comparison rows | exact matcher/receipt | derive | derive | derive | include only receipt-authorized truth |
| **Total** | — | **9,546** | **9,545** | **1** | finite frozen benchmark, not population sample |

Do not hand-fill the rows marked `derive` in a submission source file; generate them from the committed receipt and fail if the total disagrees with 9,546.

## 5. Verified versus forecast-only visual grammar

Publication figures/tables must distinguish:

- **verified/exact-truth rows** — solid marker / exact-receipt status;
- **prospective prediction later verified/refuted** — solid marker plus pre-outcome freeze flag;
- **forecast-only/no truth receipt** — open marker or separate table/panel, never included in accuracy/error plots.

A caption is not enough to repair identical glyphs for verified and unverified data.

## 6. Timing policy

Default: timing/speedup evidence moves to supplement unless target-journal fit explicitly requires systems-performance evaluation.

If retained:

- report environment/runtime/cache condition;
- identify cold versus warm cache;
- label timing as descriptive and non-canonical under the inherited convention;
- do not combine timing with exactness into one score;
- do not compare against broad quantum-resource-estimation systems unless the semantic/output units are actually matched.

## 7. Why the open smallest closed form is not a publication blocker

QG7/QG7c leave one all-`n` consolidation link open for a small named-family identity such as `min(C_D+,f_B′,f_B″)`.

This is **not** an unresolved exactness gate for ORION-10 because:

- the full support-two family D++ is already theorem-sufficient all `n` under R6M/raw-support scope;
- `F2` computes the D++ family minimum rather than relying on the smallest named closed form;
- the open question is about interpretability/computational simplification of the exact family, not whether `F2`'s mathematical target equals `C_DP`.

ORION-10 must therefore state:

> exact static forecasting via D++ is closed in scope; finding the smallest explanatory closed form remains companion open science.

## 8. Figure contract after review

1. Certificate-layer schematic with statuses above.
2. Benchmark decomposition, with the single error highlighted.
3. Exact refuting-instance anatomy showing survived versus failed certificate components.
4. Repair lineage `B -> refutation -> B′/F2 -> QG7 boundary`, with protocol freezes chronological.
5. Separate forecast-only library table.

The paper should never use a single “accuracy” plot as its main figure.