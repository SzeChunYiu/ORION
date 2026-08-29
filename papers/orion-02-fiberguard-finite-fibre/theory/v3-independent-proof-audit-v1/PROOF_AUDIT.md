# ORION02.V3_INDEPENDENT_PROOF_AUDIT.v1

**Paper:** ORION-02 — Finite-Fibre Certifiability  
**Canonical subject:** `MANUSCRIPT_V3.md` + `CLAIM_LEDGER_V3.md`  
**Status:** `V3_C1_C7_PROOF_AUDIT_PASS`  
**Scientific authority delta:** `NONE`

This is a second derivation of the canonical V3 theorem spine. It does not import the
existing fibre-floor or refinement checker and does not use the superseded `A_t/B_t`
compiler construction.

## Independent proof review

### C1 / C4 — sharp point-certificate radius and exact threshold

For a finite fibre with minimum `m`, maximum `M`, and diameter `D=M-m`, every constant
certificate `c` satisfies

`D = |M-m| <= |M-c| + |c-m|`.

Hence at least one endpoint has error at least `D/2`. The midpoint `(m+M)/2` has error at
most `D/2` on every fibre member, so the minimax radius is exactly `D/2`. Therefore an
`eps`-valid fibre-constant point certificate exists iff `D <= 2 eps`.

This proves V3-C1 and V3-C4 without reference to the generating experiment.

### C2 / C3 — intervals and the balanced endpoint witness

Any interval containing both diameter endpoints has width at least `D`, hence radius at
least `D/2`. If an interval has radius `<D/2`, it excludes at least one endpoint. A
conditional law assigning probability `1/2` to each diameter endpoint therefore gives
miscoverage at least `1/2`. This is exactly the scoped worst-case witness in V3-C3, not a
claim about arbitrary empirical fibre distributions.

### C5 — minimum unconstrained refinement

Sort a fibre's targets `v1 <= ... <= vn` and set `L=2 eps`. Any feasible part has target
diameter at most `L`. A part containing the smallest uncovered value `v1` cannot contain a
point greater than `v1+L`. The greedy first part contains every point any feasible first
part containing `v1` could contain. Replacing an optimal first part by the greedy first
part cannot increase the number of parts. Induction on the remaining suffix proves the
greedy interval-cover count is optimal.

The independent executable checker compares this sweep against **every set partition**,
not another interval-cover implementation.

### C6 — separator realizability

Let the complete joint signature of the prospectively declared separator family `S`
partition the fibre into `S`-atoms. Any `S`-measurable representation is constant on each
such atom.

Necessity: if two members of one atom have target gap `>2 eps`, every `S`-measurable
refinement keeps them together, so its fibre is uncertifiable by C4.

Sufficiency: if every `S`-indistinguishable pair has target gap `<=2 eps`, then every
`S`-atom itself has target diameter `<=2 eps`. The **atom partition itself** is therefore
an `S`-measurable feasible refinement, with the midpoint certificate valid on every atom.

This also corrects one sentence in the older
`experiments/refinement-to-certifiability-v1/THEORY.md`. That file said the converse
worked "after applying R3 within each `S`-atom". Such a split could use distinctions not
available to `S` and is neither necessary nor licensed. The canonical V3 manuscript
already uses the correct atom-partition proof, so **the theorem and manuscript claim do
not change; only the provenance proof wording is repaired by this additive audit note**.
The older frozen theory file is retained byte-for-byte rather than rewritten after its
outcome-bearing packet existed.

### C7 — whole-fibre refine-or-abstain coverage

If the decision unit is the original fibre and the system must either certify the whole
fibre or abstain on it, C4 says exactly which fibres are eligible: `D(z)<=2 eps`.
Therefore maximum coverage is the sum of the population masses of those and only those
fibres. No stochastic estimation claim is implied; the masses are inputs to this identity.

## Executable independent regression

`check_v3_fibre_theorems_independent.py` is standard-library only and imports no ORION
module or existing ORION-02 checker. It independently tests:

1. midpoint sharpness and the `D<=2 eps` equivalence;
2. greedy refinement count against exhaustive set-partition minima;
3. the separator theorem using the joint-atom partition against exhaustive
   `S`-measurable coarsenings;
4. the whole-fibre coverage identity against exhaustive accept/abstain subsets;
5. planted positive/negative controls and the canonical claim-ledger boundaries.

The finite regression is a transcription/control layer. General authority comes from the
proofs above.

## Claim ceiling

This audit does not establish OpenML or other cross-domain transfer, learn a useful
separator family, estimate fibre diameters on R24, or supply external-investigator
authority. R23/R24 remain adverse evidence; V3-C14 and V3-C15 remain forbidden; V3-C16
remains superseded for submission.

**Terminal:** `V3_C1_C7_PROOF_AUDIT_PASS__EXTERNAL_TRANSFER_STILL_OPEN`.
