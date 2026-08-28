# ORION-19 — the invariant-orbit coverage gate

**Paper:** ORION-19 — Structured Epistemic Learning
**Successor id:** `ORION19.INVARIANT_ORBIT_COVERAGE_GATE.v1`
**Governing issue:** #1649 / blueprint §ORION-19
**Status:** `GATE_EVALUATED__REPRESENTATION_SUCCESSOR_NOT_INDICATED`
**Terminal:** `READY_TO_SUBMIT_SECOND_TIER`
**Scientific authority delta:** `NONE`
**Frozen bytes modified:** NONE

---

## 1. The gate

The blueprint makes ORION-19 conditional rather than open:

> *"First compute the invariant-orbit error floor. Run the representation
> successor only if the preregistered ceiling leaves meaningful upside."*

and names the real gap as unified resource accounting under matched budgets,
*"not another generic invariance theorem."*

This evaluates the gate. It computes the floor before anything is built, so the
decision rests on the number rather than on appetite.

## 2. Method

The frozen colouring is rebuilt from the frozen D1 v1.2 splits and each instance
is mapped to its typed invariant profile. Instances sharing a profile form an
**orbit cell**: any isomorphism-invariant rule must decide identically on all of
them, so per cell it can be right at most as often as the cell's plurality label.
Summing the remainder gives the floor.

Nothing is trained. The recorded result is read as data; no frozen byte moves.

## 3. The protected split has seven orbit cells, one of them mixed

| cell | cases | gold composition | model emits | model right | plurality right |
|---|---|---|---|---|---|
| 0 | 48 | ALIGNED 32, OBSTRUCTION 16 | OBSTRUCTION | 16 | **32** |
| 1 | 32 | UNRESOLVED 32 | UNRESOLVED | 32 | 32 |
| 2 | 15 | OBSTRUCTION 15 | OBSTRUCTION | 15 | 15 |
| 3 | 14 | OBSTRUCTION 14 | OBSTRUCTION | 14 | 14 |
| 4 | 11 | OBSTRUCTION 11 | OBSTRUCTION | 11 | 11 |
| 5 | 4 | OBSTRUCTION 4 | OBSTRUCTION | 4 | 4 |
| 6 | 4 | OBSTRUCTION 4 | OBSTRUCTION | 4 | 4 |

- **Orbit-majority ceiling: `112/128 = 0.875`** — the most any invariant rule can score.
- **Frozen model: `96/128 = 0.750`**, as recorded.
- **Irreducible floor: 16 cases (`0.125`)** — the OBSTRUCTION minority inside cell 0.
- **Apparent recoverable gap: 16 cases (`0.125`)**.

Model predictions are constant within every cell, which independently confirms
the representation is invariant in the deployed path.

## 4. The gap is not a representation deficiency

The obvious reading of §3 — the model picks the minority label in cell 0, so
majority decoding would recover 16 cases — is wrong, and checking it is what
makes the gate answerable.

**Cell 0 contains no training and no development instance.** Extending the
measurement to the whole split gives the reason:

| split | cases | orbit cells | cases whose cell appears in training | accuracy |
|---|---|---|---|---|
| train | 288 | 18 | — | — |
| dev | 96 | 18 | **96 / 96 = 100%** | 0.958 |
| protected | 128 | 7 | **0 / 128 = 0%** | 0.750 |

Training and protected share **no orbit cell at all**. The protected split is
therefore an entirely out-of-orbit evaluation, and the `0.958 → 0.750` drop is
exactly the in-orbit to out-of-orbit transition rather than ordinary overfitting.
The model is not choosing a minority it could have learned: in cell 0 there was
no majority available to learn, and its answer there is an extrapolation.

So the ceiling of `0.875` is not attainable by any learner trained on these
splits. It is an upper bound on invariant rules, not a reachable target.

## 5. Why refining the representation cannot be the lever

Let coverage be the fraction of evaluation cases lying in a cell that contains at
least one training case, and let the floor be the summed non-plurality mass.

**Lemma (coverage/floor tradeoff).** If `φ'` refines `φ` then
`coverage(φ') <= coverage(φ)` and `floor(φ') <= floor(φ)`.

*Proof.* Refinement splits cells. A cell holding no training case splits into
subcells holding none, and a cell holding one may split into subcells that do
not, so the set of evaluation cases in populated cells can only shrink.
Partitioning a cell cannot increase its non-plurality mass, so the floor cannot
rise. ∎

Both directions are therefore blocked:

- **Refining** lowers the floor but cannot raise coverage — and coverage is
  already `0`, so it stays `0`. A finer invariant buys a lower bound that no
  learner can approach.
- **Coarsening** can raise coverage, but only by merging cells, which never
  lowers the floor and generally raises it.

A representation successor optimises the floor. On this benchmark the floor is
not what binds; coverage is, and coverage is a property of how the frozen split
was constructed. This is precisely the blueprint's point that the gap is not
another generic invariance theorem.

## 6. Gate verdict

**The representation successor is not indicated and is not run.** The ceiling
leaves `0.125` of nominal headroom, but that headroom is unreachable in principle
by the class of change a representation successor makes. Building it would spend
the promotion budget on the one lever the measurement rules out.

The remaining scientific gap named by the blueprint — unified model, inference
and representation resource accounting under matched budgets — is already
discharged by the executed unified I/A/C/M resource ledger V2, which is bound to
workflow run `32664198718` with committed artifacts.

## 7. What is preserved

Every frozen disposition stands unchanged: the recorded `0.750` protected
accuracy, the `0.958` development accuracy, the four-variant stability result,
the `T4_ATTACK_SUCCEEDED` reminting verdict and the transport gate's
`P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET` terminal with its five
`CANNOT_CHECK` results. Nothing here converts a `CANNOT_CHECK`, and no accuracy
is re-derived or improved.

The finding is diagnostic. It explains a recorded number; it does not change one.

## 8. Independent verification

`independent_checker/check_orbit_gate.py` recomputes the partition from the
frozen colouring without importing any ORION-19 scoring path, and writes
`RESULT.json`.

| check | result |
|---|---|
| A — ceiling is 112/128 | **pass** |
| B — model scores 96/128, constant within every cell | **pass** |
| C — dev 100% in-orbit, protected 0% in-orbit | **pass** |
| D — refinement/coarsening tradeoff holds | **pass** |
| negative controls (4) | **4/4 fire** |

The checker was validated against a mutant: forcing the expected ceiling to
`111` makes check A fail, so the check is capable of failing on real data.
`CANNOT_CHECK` has exit code `3` and is never reported as a pass — the first
run took that exit on a bad path rather than reporting success.
