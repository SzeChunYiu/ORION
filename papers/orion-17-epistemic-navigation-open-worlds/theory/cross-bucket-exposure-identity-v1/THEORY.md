# ORION17.CROSS_BUCKET_EXPOSURE_IDENTITY.v1

**Status:** `THEORY_PROVED_FROM_FROZEN_INSTRUMENT_SEMANTICS__NEW_IDENTITY`  
**Scientific authority delta:** `NONE`  
**Historical density identity:** remains `NO_DISCRIMINATION`; this theorem does not retune or rescue it.

## Source-semantic binding

This theorem is about the donor-coarse policy as implemented by the historical P7 transition instrument:

- source branch: `shadow/orion17-density-v2-recovery-20260829`
- source path: `papers/orion-17-epistemic-navigation-open-worlds/transitions/measure_p7_closure_retention_v1.py`
- Git blob SHA: `4531c2c0230070f8a8aaf49acabee6bce9633929`

The instrument constructs a module set `M`, a transitive read set `R(m)` for each module, and the bucket map

`b(m) = m.split(".")[1]` when `m` contains a dot, otherwise `b(m)=m`.

For one transition with changed module set `C`, it defines:

- `invalid(m)` iff `R(m) intersects C`;
- `changed_buckets = {b(c): c in C}`;
- donor-coarse `keep(m)` iff `b(m) notin changed_buckets`;
- false closure retention iff `keep(m)` and `invalid(m)`.

Everything below follows algebraically from those frozen definitions.

## Theorem 1 — exact false-retention identity

For any transition `C`, the donor-coarse false-retention set is exactly

`F(C) = {m in M : R(m) intersects C and b(m) notin b(C)}`,

where `b(C)={b(c):c in C}`.

Therefore the instrument's donor false-closure-retention count over a history `C_1,...,C_T` is exactly

`FCR = sum_t |F(C_t)|`.

### Proof

The instrument increments `retained_invalid` exactly when the Boolean `keep` is true and `invalid` is true. Substituting the two definitions gives precisely the set predicate above. Summing the per-transition count gives the historical total. QED.

This is a mechanism identity for the instrument, not a fitted predictor.

## Theorem 2 — universal soundness iff there is no cross-bucket transitive dependency

Define the cross-bucket transitive pair set

`X = {(m,c) in M x M : c in R(m) and b(m) != b(c)}`.

Then the donor-coarse policy has zero false closure retention for **every possible changed-module set `C`** iff `X` is empty.

### Proof

(**If**) Assume `X` is empty. If `m` is invalid under any `C`, choose `c in R(m) intersect C`. Since `(m,c)` is not cross-bucket, `b(m)=b(c)`, hence `b(m) in b(C)`. Donor-coarse reopens `m`, so `m` cannot be falsely retained. Thus `F(C)=empty` for every `C`.

(**Only if**) If `X` is nonempty, choose `(m,c) in X` and the singleton change set `C={c}`. Then `c in R(m)` makes `m` invalid, while `b(m)!=b(c)` means `b(m) notin b(C)`, so donor-coarse keeps `m`. Therefore `m in F({c})` and the policy is not universally sound. QED.

This gives an exact static certificate:

`UNIVERSALLY_SOUND_UNDER_INSTRUMENT_SEMANTICS <=> cross_bucket_transitive_pair_count == 0`.

## Corollary 2.1 — singleton-change risk is exact, not heuristic

For a singleton change `C={c}`,

`|F({c})| = |{m : c in R(m), b(m) != b(c)}|`.

Thus the number of cross-bucket transitive readers of `c` is exactly the donor-coarse false-retention count that would result if `c` alone changed.

Define

`rho_max = max_c |{m : c in R(m), b(m) != b(c)}|`.

Then `rho_max=0` iff donor-coarse is universally sound. For `rho_max>0`, the maximizing module supplies an explicit singleton counterexample transition.

## Theorem 3 — exact preservation and unnecessary-reopen identities

For transition `C`, donor-coarse preserves exactly

`P(C) = {m : b(m) notin b(C)}`.

It unnecessarily reopens exactly

`U(C) = {m : b(m) in b(C) and R(m) intersect C = empty}`.

These identities expose the safety/efficiency tradeoff directly: coarse buckets reopen every module whose bucket appears in the changed set, whether or not that module depends on a changed premise.

## Corollary 3.1 — one-bucket degeneracy

If every module in `M` has the same bucket and `C` is nonempty, then `b(C)` contains that sole bucket, so `P(C)=empty`. Donor-coarse preserves nothing, hence false retention is mechanically zero.

This proves the `src/`-layout degeneracy diagnosed in the completed disagreement study whenever the instrument's root naming collapses all modules to a common second component. Such a SOUND label is a trivial always-reopen outcome, not evidence of a successful structural predictor.

## Corollary 3.2 — all-buckets-changed degeneracy

More generally, if `b(C)` equals the complete set of module buckets for a transition, then donor-coarse preserves nothing on that transition. A nondegenerate evaluation must therefore report preservation as well as false retention.

## What this changes scientifically

The failed density study asked whether a scalar graph-density threshold predicts SOUND/UNSOUND. This theorem shows that, **for the frozen donor-coarse instrument**, retrospective false retention is already exactly characterized by cross-bucket transitive exposure and the realized changed sets. Density, module count and edge count can at most be proxies for this mechanism.

That does not retroactively validate a new predictor: the identity was articulated after V1 outcomes and receives a new scientific identity. The valid next empirical question is different:

> Can an outcome-blind static certificate or risk functional derived from cross-bucket transitive structure provide useful prospective coverage/efficiency on untouched, correctly rooted repositories?

## Prospective candidate family

Without using new outcomes, the theorem yields three precomputable candidates from a correctly rooted import graph:

1. `C0_SAFE`: `|X|=0`. Exact universal-soundness certificate under instrument semantics.
2. `C1_MAX_EXPOSURE`: `rho_max`, the maximum singleton false-retention exposure.
3. `C2_TOTAL_EXPOSURE`: `|X|`, total cross-bucket transitive pair mass.

`C0_SAFE` is a theorem, not a statistical classifier. `C1` and `C2` are risk-ordering candidates whose practical predictive value on realized future changes requires a new untouched prospective cohort.

A fourth history-weighted quantity may be derived only on a separate training history and must be frozen before protected future transitions:

`C3_EXPECTED_EXPOSURE = sum_c p_train(c) * cross_bucket_reader_count(c)`.

It cannot use the protected transition frequencies it is evaluated against.

## Required successor controls

A valid successor must:

- root modules at the actual package root so namespace layout does not collapse the bucket map accidentally;
- verify graph construction on flat and `src/` layouts with equivalent synthetic imports;
- exclude all historical 8 + V1 20 repositories from confirmatory N;
- freeze `C0..C3`, failure semantics and any train/protected split before protected transitions;
- report preservation and unnecessary reopening together with false retention;
- retain repositories where the certificate rejects or the risk candidates fail;
- use exact-containment and always-reopen as semantic controls;
- never describe C1/C2 success as evidence for the retired density threshold.

## Scope boundary

The theorem is exact **relative to the frozen instrument's module graph, transitive-read semantics and bucket map**. It does not prove that the graph parser captures every real dependency, that a repository is correctly rooted, or that future change distributions make a risk candidate useful.

## Claim ceiling

Earned deductive claim:

> Under the frozen P7 donor-coarse semantics, false retention on transition `C` is exactly cross-bucket transitive exposure to `C`, and universal soundness over all change sets is equivalent to absence of cross-bucket transitive dependency pairs.

Not earned:

- rescue of density 1.5 or rivals 49/216;
- empirical prevalence of `C0_SAFE` on untouched systems;
- predictive accuracy of C1/C2/C3;
- correctness of the import graph as a model of all real dependencies.

`scientific_authority_delta: NONE`
