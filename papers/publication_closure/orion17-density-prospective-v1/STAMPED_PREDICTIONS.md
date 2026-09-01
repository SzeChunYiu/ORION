# ORION-17 — stamped prospective predictions from import-graph density

**Paper:** ORION-17 — Epistemic Navigation in Open Worlds
**Successor id:** `ORION17.DENSITY_PROSPECTIVE.v1`
**Governing issue:** #1649 / blueprint §4.12
**Status:** `PREDICTIONS_STAMPED__POLICY_OUTCOMES_NOT_OPENED`
**Scientific authority delta:** `NONE`

Written and committed **before** any policy comparison is run on any held-out
package. Only the import graph has been computed; no closure-retention outcome
has been produced or inspected.

---

## 1. What is being tested and why this rather than a multi-hop chain

`ORION17.CLOSURE_CHAIN_COMPOSITION.v1` recorded honestly that its arbitrary-chain
theorem was already owned by `CLAIM_LEDGER_V4.md` row `ORION-17.V4.5`, and
returned the paper to its bounded lane. Its one genuinely new observation was
**explanatory, not predictive**: across the frozen three-domain campaign,
`donor-coarse` was unsound on numpy and scipy but merely conservative on flask,
and it attributed the difference to dependency-structure richness.

That attribution was made after the outcomes were visible. It becomes a
scientific claim only if it **predicts** the next case. This lane converts it
into a prospective test, which is cheaper and sharper than the naturalistic
multi-hop study and tests a mechanism the paper actually asserts.

## 2. The rule, frozen

From the three observed domains:

| domain | modules | import edges | edges/module | `donor-coarse` outcome |
|---|---|---|---|---|
| flask | 24 | 19 | **0.79** | sound (0 false retentions) |
| numpy | 426 | 1076 | **2.53** | **unsound** (27,348) |
| scipy | 813 | 2156 | **2.65** | **unsound** (50,282) |

**Frozen decision rule.** Predict `donor-coarse` **unsound** iff
`import_edges / modules >= 1.5`; otherwise predict it merely conservative.

The threshold is fixed here at `1.5` and will not be moved after outcomes.

## 3. Held-out corpus and stamped predictions

Five packages from five organizations, none of them numpy, scipy or flask.
Densities below were computed with the campaign's own `build_import_graph`; no
policy was evaluated.

| package | source | modules | edges | edges/module | **prediction** |
|---|---|---|---|---|---|
| requests | psf/requests | 19 | 16 | 0.84 | **sound / conservative** |
| networkx | networkx/networkx | 583 | 1245 | 2.14 | **unsound** |
| django | django/django | 906 | 3336 | 3.68 | **unsound** |
| tornado | tornadoweb/tornado | 74 | 412 | 5.57 | **unsound** |
| sympy | sympy/sympy | 1566 | 13622 | 8.70 | **unsound** |

## 4. The confound, and the case that resolves it

In the observed campaign the sound domain (flask, 24 modules) is both **small**
and **sparse**, so size and density are confounded and a referee is right to ask
which one carries the result. `requests` repeats that confound: it is small and
sparse.

**`tornado` separates them.** At 74 modules it is small — three times flask, far
below numpy — but at 5.57 edges/module it is denser than numpy or scipy.

- The density rule predicts `tornado` **unsound**.
- A size-based explanation predicts `tornado` **sound**.

**`tornado`'s outcome is therefore the load-bearing case**, and it is registered
as such before it is run. If `tornado` comes out sound, the density attribution
in `ORION17.CLOSURE_CHAIN_COMPOSITION.v1` §4 is wrong and will be recorded as
refuted.

## 5. Success and failure, fixed in advance

- **Success:** all five predictions correct, including `tornado` unsound.
- **Partial:** four of five correct with `tornado` correct — the mechanism holds
  and one boundary case is mispredicted.
- **Failure:** `tornado` mispredicted, or two or more of the five wrong. Either
  outcome refutes the density attribution and will be reported as a refutation,
  not reinterpreted.

No threshold, package or criterion moves after the outcomes are opened.

## 6. Authority

`scientific_authority_delta = NONE`. The frozen three-domain campaign, its
counts, its policies and every `CANNOT_CHECK` are untouched. This document
stamps predictions and contains no outcome.
