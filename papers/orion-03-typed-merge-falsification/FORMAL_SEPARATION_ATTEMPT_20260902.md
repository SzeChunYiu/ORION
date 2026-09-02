# ORION-03 formal-separation attempt — 2026-09-02

**Rung:** 1 of the disposition ladder (issue SzeChunYiu/ORION-paper#78, ORION-03 section)
**Outcome:** `ATTEMPTED__NOT_AIRTIGHT` — rung (1) does not land; fell to rung (2).
**scientific_authority_delta:** `NONE` — documented negative; it *strengthens* the
narrowing disposition rather than widening any claim.

## Target proposition

> No provenance-semiring or ATMS encoding at matched interface can express
> origin-witness nonpromotion.

Landing it would have turned the manuscript's *declared* donor subtraction into a
*demonstrated* one. The landing condition (issue): every proof step airtight from
`MANUSCRIPT_V3.md`'s own definitions — no hand-waving, no smuggled assumptions.

## Where airtightness fails, step by step

### Step A — the semiring branch refutes itself at its first quantifier

The manuscript's transfer (MANUSCRIPT_V3.md, "Finite typed authority system") is

```
tau_r(x) = K_r ∩ ⋂_{a∈A_r} x_a          (per rule)
F_R(x)_q = σ(q) ∪ ⋃_{r: h_r=q} τ_r(x)   (per claim, non-refuted case)
```

With ⊕ = ∪ and ⊗ = ∩ over `2^Λ`, this *is* annotated-semiring evaluation at one fixed
annotation configuration — precisely the machinery of the cited donors (annotation
domains in generalized annotated logic programming, `kifer1992`; semiring provenance and
its recursive-Datalog extensions, `green2007` / `bourgaux2022` / `abokhamis2022`). An
impossibility quantified over "provenance-semiring encodings" therefore has the paper's
own algebra inside the quantifier. The proposition is not merely unproven; in this
branch it is false.

### Step B — even "without per-rule caps" is not a separating interface

Inside the manuscript's own definition space, every capped rule `(A_r → h_r, K_r)` is
simulated exactly by adding a fresh seed claim `c_r` with `σ(c_r) = K_r` and replacing
the rule by `(A_r ∪ {c_r} → h_r, Λ)`:

- transformed transfer: `Λ ∩ K_r ∩ ⋂_{a∈A_r} x_a = τ_r(x)`;
- seed and head aggregation unchanged; `c_r ∉ R` (never refuted);
- simultaneous induction on the synchronous iterates from bottom gives equality of the
  `Q`-coordinates of the two least fixed points.

The manuscript itself notes "rules with empty bodies are represented as seeds", so the
simulation never leaves the declared definition space. The nonpromotion core
(intersection transfer) is therefore expressible *without* the cap construct.

### Step C — matching the refutation clamp needs external definitions

The manuscript clamps `q ∈ R` to the empty label *against re-derivation*. Matching that
clause to published semiring deletion-by-zeroing semantics (Bourgaux et al. 2022 and
successors) requires importing those frameworks' deletion definitions — exactly the
"new assumptions smuggled in" that the landing condition forbids. Steps A–B already
refute the proposition, so this mismatch is not load-bearing; it marks where the
internal-only argument stops.

### Step D — the ATMS branch fails on a label post-filter

In an assumption-based truth maintenance system, each node carries its minimal
consistent assumption environments (`dekleer1986`, verified 2026-09-02: Johan de Kleer,
"An Assumption-Based TMS", Artificial Intelligence 28(2):127–162, 1986,
doi:10.1016/0004-3702(86)90080-9). Take assumptions to be the origin-tagged native
adjudication inputs. The origin-witness decision `d = v_A ∨ v_B` (MANUSCRIPT_V3.md,
"Native-engine study outcome definitions") is then recovered by the post-filter
"accept iff some environment is origin-homogeneous": under positive (monotone)
derivability, any homogeneous environment contains a minimal homogeneous sub-environment,
so ATMS minimality pruning does not erase the witness. The decision function is
expressible; the impossibility fails in this branch too.

## What survives as honest residual distinctions

1. **Enforcement locus.** The typed rule makes nonpromotion an invariant of propagation;
   the ATMS/semiring routes recover the same decision function by post-hoc inspection of
   computed annotations or environments. Decision functions coincide; architecture differs.
2. **Cost.** Measured, not definitional: retaining origin witnesses costs 3,924 parent
   evaluations over 1,962 tasks vs 1,962 for textual union
   (`evidence/round2-x509-truststore/COST_ROUND2_V2.json`, 3,924 present; ledger D3-C14).
3. **Curation.** License vocabulary, seeds, caps, and refutations are author-supplied
   policy inputs (MANUSCRIPT_V3.md, "Reference evaluator"); no donor framework supplies
   the scientific-record vocabulary itself.

None of these is an expressiveness theorem. None is claimed as one.

## Consequence

Rung (1) is closed as `ATTEMPTED__NOT_AIRTIGHT`. The ladder falls to rung (2)
(second-live-corpus preflight, `SCIENCE_ITEM_DISPOSITION_20260902.md`) and lands at
rung (3): the manuscript's Limitations now state the expressiveness gate as OPEN, as a
deliberate boundary, and the filed claim is stated as a formal license-propagation
system plus one measured hybrid-authorization phenomenon.

Constructions B and D are retained here as internal documentation of *why* no
separation proposition was written into the manuscript. They are not asserted as
theorems in the manuscript, and no ledger status was changed by this note.

skills-applied: nature-writing, nature-citation, nature-publication-closure
