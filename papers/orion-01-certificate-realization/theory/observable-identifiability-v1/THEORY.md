# ORION01.OBSERVABLE_IDENTIFIABILITY.v1 — terminal metrics cannot certify hidden semantics

**Paper:** ORION-01 — Certificate Realization  
**Parent evidence:** `experiments/move-census-and-confluence-v1/RESULT_V1.json`  
**Status:** `THEORY_PROVED_FROM_EXISTING_ADVERSE_WITNESS`  
**Scientific authority delta:** `NONE`

This packet turns the hostile Stage-2 result into a permanent structural boundary. It does
not claim that a hidden operation exists in the pinned PyZX build. It says what follows if
the admissible system class contains two systems that the declared observable cannot
distinguish.

## 1. Setting

Let `C` be a class of rewrite systems. Let

- `O : C -> Y` be an observable used by a verifier;
- `N : C -> M` be the extensional semantic object of interest (here the normal-form map);
- a verifier be **O-only** when its output is a function of `O(c)` alone.

For the parent experiment, the strong observable is `terminal_complexity` and `N(c)` is
the complete state-to-normal-form map.

## 2. Theorem 1 — factorisation criterion for identifiability

There exists an exact decoder `d : Y -> M` satisfying

`N(c) = d(O(c))` for every `c in C`

**iff** `N` is constant on every fibre of `O`.

**Proof.** If such `d` exists, `O(c)=O(c')` implies
`N(c)=d(O(c))=d(O(c'))=N(c')`. Conversely, if `N` is constant on every `O`-fibre,
define `d(y)` to be that common value on any nonempty fibre and extend arbitrarily away
from `O(C)`. ∎

Therefore one collision

`O(c)=O(c')` but `N(c) != N(c')`

is enough to prove that no O-only method, regardless of algorithm, model class, search
budget, or expression size, can reconstruct the extensional semantics on the whole class.

## 3. Corollary — the ORION-01 MIMIC witness is an impossibility certificate

The parent result contains a `MIMIC` witness for which `terminal_complexity` is unchanged
while the normal-form map changes. By Theorem 1, `terminal_complexity` is not sufficient
for the normal-form semantics on the hostile system class.

This is stronger than saying mimicry is frequent. The measured count
`250,683 / 778,502` describes prevalence in the frozen finite sweep; **one** witness is
already logically sufficient for non-identifiability.

It also explains why increasing the state cap cannot repair this specific defect. More
samples of the same observable cannot distinguish two systems that have the same
observable value by construction.

## 4. Theorem 2 — an O-only semantic decision is possible exactly when it is fibre-constant

For any semantic predicate `Q : M -> {0,1}`, an exact O-only decision rule for
`Q(N(c))` exists iff `Q∘N` is constant on every O-fibre.

This is Theorem 1 with the target compressed to the decision actually being certified.
Hence every production claim must name the semantic decision it wants and demonstrate
that the chosen observation separates all systems on which that decision differs.

## 5. Theorem 3 — ordinal progress also fails under FALSE_IMPROVEMENT

Suppose an observable is interpreted as a progress score, with smaller values treated as
better. If there exist systems `c,c'` such that

`O(c') < O(c)`

while a declared semantic-preservation functional gets strictly worse, then `O` is not
monotone with respect to that semantics and cannot by itself justify "improvement".

The parent `FALSE_IMPROVEMENT` witness has exactly this form: terminal complexity falls
to its best value while at least one state loses its normal form. This is an order failure,
not merely a calibration error.

## 6. What repairs the claim

A sufficient production certificate needs at least one of the following.

1. **Closed-world theorem:** prove that every semantically effective operation is in the
   declared registry, so the hostile extension class is excluded.
2. **Stronger observation:** use an observable `O'` whose fibres refine the semantic
   equivalence classes relevant to the claim.
3. **Direct semantic check:** verify the target normal-form/reachability property rather
   than infer it from a scalar proxy.

For full normal-form-map identification, any sufficient observable must separate every
pair of systems with different normal-form maps. Equivalently, equality of the observable
must imply equality of the normal-form map.

## 7. Boundaries

This theorem does **not** establish a hidden operation in production PyZX, production
non-confluence, or failure of the bounded abstract source-completeness theorem. The
parent packet keeps both production questions `CANNOT_CHECK`, and this packet does not
change them.

The result is conditional but exact: **if the admissible production class includes the
observed collision shape, terminal complexity alone cannot certify extensional
realisation.** The scientific next move is therefore registry closure or a stronger
semantic observation, not another raw cap increase.
