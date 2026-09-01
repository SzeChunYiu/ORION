# ORION08.BINDING_SUFFICIENCY_LATTICE.v1 — THEORY

**Paper:** ORION-08 — Typed State
**Successor id:** `ORION08.BINDING_SUFFICIENCY_LATTICE.v1`
**Candidate source:** PR #1617, Priority B
**Authored:** 2026-08-28
**Status:** `THEORY_PROVED__INSTANTIATED_ON_FROZEN_RECEIPTS`
**Scientific authority delta:** `NONE`
**Frozen paper bytes modified:** NONE (`submission_tmlr/` untouched — see §7)

---

## 1. Why this successor exists

ORION-08 correctly avoids claiming that more typed or scoped state always helps:
its six exact-synthetic studies contain both value and no-value regimes.

What the paper does not yet have is a statement of **when** binding has decision
value, and **how much** of the available value each binding actually captures.
This packet supplies both: the criterion as a theorem, and the magnitude as an
exact recomputation from the frozen N4 receipts.

---

## 2. Setting

Let world states `x` carry a binding `B(x)` — the typed/scoped information a
policy may read — and let `A*(x)` be the set of optimal actions in world `x`.
`B` partitions the worlds into **fibres**; a deterministic policy that reads only
`B` must emit one action per fibre.

### Theorem 1 (binding sufficiency)

A deterministic zero-regret policy using only `B` exists **iff** every
positive-mass fibre has a common optimal action:

```
intersection over { x : B(x) = z } of A*(x)  !=  empty      for every reachable z.
```

**Proof.** *(⇐)* Choose, in each fibre, an action from the nonempty intersection;
it is optimal in every world of that fibre, so total regret is zero.
*(⇒)* If some fibre `z` has empty intersection, then whatever single action the
policy emits on `z` is suboptimal in at least one positive-mass world of `z`, so
regret is strictly positive. ∎

### Theorem 2 (refinement monotonicity, and when it is strict; corrected)

If `B'` refines `B` then Bayes risk under `B'` is no larger, because every
`B`-measurable policy is `B'`-measurable. For each positive-mass `B'`-subfibre
`G`, let `O_G` be the actions minimizing aggregate loss on `G`. The decrease is
**strict exactly when** at least one positive-mass `B`-fibre has
`intersection_G O_G = empty` across its `B'`-subfibres. If the intersection is
nonempty, one action attains every subfibre minimum and the coarse and refined
risks agree on that fibre; if it is empty, no coarse action can attain the sum
of the subfibre minima. ∎

The earlier sentence "strict exactly when it splits an action-impure fibre" was
underspecified and is withdrawn. The correction and its interpretive consequence
are recorded in `THEOREM_CORRECTION_2026-09-01.md`.

### The lattice reading

Bindings form a lattice under refinement, and decision value is **not** monotone
in "amount of typed state" — it is monotone only in *fibre purity with respect to
optimal actions*. Adding typed state that does not induce disagreement among the
aggregate optimal actions of refined subfibres is free of benefit, however
detailed it is.

This is generic decision-sufficiency / Blackwell-style **donor** theory. No
novelty is claimed, and per #1617 it should be implemented once across the
programme rather than claimed independently by ORION-08 and ORION-22.

---

## 3. Instantiation on the frozen ORION-08 receipts

The theorem predicts that a binding's measured advantage should track the
fraction of the achievable (oracle) gap it closes. Recomputed from the frozen
receipts:

### 3.1 N4-B — scoped receipt reopening: binding is far from sufficient

Terminal: `N4_B_SCOPED_REOPENING_SUPPORTED__EXACT_SYNTHETIC`, all four gates pass.

| arm | pooled mean regret vs oracle |
|---|---|
| `ORACLE_AVAILABILITY` | `0` |
| `ORION_SCOPED_REOPEN` | `5.099` |
| `NEVER_REOPEN` | `5.515` |
| `ALWAYS_REOPEN` | `17.522` |

The scoped binding closes **`7.6%`** of the strongest baseline's oracle gap.
Per regime, by round utility:

| regime | never | scoped | oracle | gap closed |
|---|---|---|---|---|
| `REOPEN_WASTEFUL` | `3.468` | `3.528` | `7.014` | **`1.7%`** |
| `STALE_MATTERS` | `2.096` | `2.870` | `9.581` | **`10.3%`** |

This is exactly Theorem 2's prediction. In `REOPEN_WASTEFUL`, never-reopening is
already near-optimal, so the refinement splits fibres that were effectively
already action-pure and buys almost nothing. In `STALE_MATTERS` the fibres do
differ in optimal action, so the refinement buys something — but still leaves
`89.7%` of the gap open, so the binding is **not sufficient** there either.

### 3.2 N4-F3 — typed remint transport: binding is nearly sufficient

Terminal: `N4_F3_TYPED_REMINT_TRANSPORT_SUPPORTED__EXACT_SYNTHETIC`.

| arm | regret vs oracle |
|---|---|
| `FULL_ORACLE` | `0` |
| `ORION_TYPED_TRANSPORT` | `0.188` |
| `RE_DERIVE_SCRATCH` | `1.034` |
| `NAIVE_CARRY_FORWARD` | `11.449` |

The typed binding closes **`98.4%`** of the naive baseline's gap and **`81.9%`**
of the strongest non-oracle baseline's gap.

### 3.3 The contrast is the result

Two exact-synthetic families, both with `SUPPORTED` terminals, differ by more
than an order of magnitude in how much of the achievable decision value the
binding actually captures — `7.6%` versus `98.4%`.

A `SUPPORTED` terminal therefore certifies **direction**, not **magnitude**. This
is the precise, quantitative form of the paper's existing refusal to claim that
more typed state always helps.

---

## 4. Independent verification

`independent_checker/check_binding_sufficiency.py` imports no ORION-08 or N-lane
module. Theorems 1 and 2 are verified on freshly enumerated finite decision
problems; the N4 receipts are read as **data** and never executed.

| check | result |
|---|---|
| A — sufficiency iff common optimal action | holds |
| B — refinement never increases risk | holds |
| B2 — strict iff no action jointly minimizes all refined subfibres | holds over 641,034 coarse/refined partition pairs |
| exhaustive over | **2,233,980** world/action/binding configurations |
| C — instantiation recomputed from frozen receipts | as tabulated above |
| D — negative controls | **3/3 fire**, including a counterexample to the withdrawn shorthand |

Arithmetic is integer throughout (uniform mass makes division unnecessary), so
nothing is approximated. Controls: a fibre mixing worlds with disjoint optimal
actions must have strictly positive regret; splitting an already-pure fibre must
add nothing.

`CANNOT_CHECK` has exit code `3` and is never reported as a pass.

---

## 5. Strongest falsifier

A finite decision problem where a binding with an action-incompatible fibre still
admits a zero-regret deterministic policy, where a refinement increases Bayes
risk, or where strict decrease disagrees with the corrected joint-subfibre-optimum
criterion. The first two conditions were checked over 2,233,980 configurations and
the strictness equivalence over 641,034 coarse/refined partition pairs. The old
impure-split shorthand is not a falsifier because the checker now contains a
counterexample to it.

For the instantiation, the falsifier is arithmetic: if the recomputed gap
fractions disagreed with the frozen receipts, the reading would be wrong. They
are recomputed directly from those receipts.

The honest limit is that **both families are exact-synthetic**. Nothing here
speaks to real-domain behaviour.

---

## 6. Donor boundary

Decision sufficiency, the common-optimal-action criterion and refinement
monotonicity are **donor-owned** (comparison of experiments, Blackwell ordering,
sufficient statistics). **No novelty is claimed.** Per #1617 this generic theory
belongs to the programme once, shared with ORION-22's information boundary, not
to ORION-08 alone.

The ORION-specific content is the exact instantiation: the gap-closed fractions
for N4-B and N4-F3 and the order-of-magnitude contrast between them.

---

## 7. Authority boundary

`scientific_authority_delta = NONE`.

- Both family terminals are unchanged; no gate is re-evaluated. `SUPPORTED`
  stays `SUPPORTED`.
- The **exact-synthetic scope is preserved and reinforced**; no real-domain
  generalization language is introduced, per #1609.
- `novelty_authorized: false` and `p10_authorized: false` in the N4-B
  interpretation record are unchanged.
- The N4-B recorded scope limit ("initial receipts only; no intra-episode receipt
  accrual") is unchanged.
- `submission_tmlr/` is **not read, written or depended upon**, so the byte
  bindings asserted by `papers/publication_closure/PACKAGE_ADOPTION_V2.json`
  under issue #1601 are unaffected.
### Content-freeze pin — disclosed, not glossed

`check_orion05_10_final_freeze.py` reports `FROZEN` with this directory present,
but **that is not evidence of unchanged content**: the script *writes*
`paper_tree_oid` and rewrites `subject_commit` to the current `HEAD`, then
reports. It re-pins rather than verifies. Running it mutates the freeze receipt;
that mutation was reverted and is not part of this PR.

The honest statement is therefore:

| | |
|---|---|
| pinned `paper_tree_oid` | `5f923e9a9d1e` |
| live tree oid with this additive directory | `e353f6691507` |

Adding any file under `papers/orion-08-typed-state/` changes that paper's tree
oid. ORION-08's pin is one of the eight currently matching on `main` per issue
**#1625**, so this PR will move it into the mismatching set. **No existing byte
is modified** — the change is purely additive — but the pin change is real and is
flagged here rather than hidden behind a checker that cannot fail.

**ORION-08 is not blocked by this lane.** Real-domain transfer remains successor
work, exactly as #1609 requires.
