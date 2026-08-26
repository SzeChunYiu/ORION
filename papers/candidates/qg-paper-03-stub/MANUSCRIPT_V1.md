# Intrinsic Support Numbers for Quantum Compilation Families: Descent Ladders, Objective Cones, and the Limits of Syndrome-Rank Certificates

Manuscript V1 — 2026-08-21. Branch `claude/orion-harness-verification-b17qdj`.
Every number is transcribed from a committed receipt or frozen protocol; the
receipt path is cited inline at first use, relative to the repository root.
Nothing here carries R6 (compiled-resource novelty) authority: every receipt
cited records `novelty_authority: false` and
`physical_quantum_advantage_claim: false`, and every parent authority string it
binds terminates in `NOT_R6`. No claim of physical quantum advantage, hardware
performance, or priority over any donor discipline is made anywhere.

---

## Abstract

Sufficiency bounds on the structural support of compilation optima are usually
reported as whatever a proof happened to reach — "support ≤ 5 suffices", "support
≤ 2 suffices" — with no statement of how far from the truth the bound sits. We
compute, for two compilation families under fixed objectives, the exact value of
the **smallest support size of an optimal solution** — written κ here — meaning
the exact bound such that every optimum admits generators of support ≤ κ and no
smaller bound holds. **This quantity is not introduced here.** It is studied in
integer optimization, where Aliev, De Loera, Eisenbrand, Oertel and Weismantel
bound the support of an optimal solution of `max{cᵀx : Ax = b, x ≥ 0, x ∈ ℤⁿ}` by
`2m·log(2√m‖A‖_∞)`, independently of the objective, with a nearly matching
asymptotic lower bound (*The Support of Integer Optimal Solutions*, SIAM J. Optim.
28(3):2152–2157, 2018). The contribution claimed here is **the exact values for
two specific frozen families and the machine-checked ladders that reach them**,
not the quantity, not the two-sidedness, and not the idea of asking for a matching
lower bound. (i) For the frozen R6I rank-2
dependent-triple shared-2-bit-Tag grammar under its frozen unit objective,
**κ = 1 exactly**, proved by a five-rung machine-checked descent ladder starting
from the published support-5 theorem and terminating at
`QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED` with support 0 infeasible
(`research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json`,
`intrinsic_support_number: 1`, `support0_infeasible: true`); each rung's
*obstruction census* — 36 unresolved support-4 descriptor patterns, 21 unsafe
support-3 profile cases, 36 accepted unsafe support-2 type cases — is the exact
input domain of the next rung, so the ladder is auditable rung by rung.
(ii) κ is **objective-indexed**: QG-16 exhibits the exact four-facet cone of
structural weights inside which κ(θ) = 1 for all n, with the unit objective
exactly on a Tag-relocation facet at margin 0
(`research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json`), while the
TARE analogue QG-8 gives the support-2 cone `t_c ≥ 2·t_r ∧ t_nc ≥ 2·t_r` with an
outside control carrying an exact support-3 witness
(`research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json`;
`research/extensions/orion-qg/QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`). Both cones
preserve `GLOBAL_PHASE_BOUNDARY_SHARPNESS = OPEN`: outside a cone means only that
*this certificate does not apply*, never that a larger support is required.
(iii) Syndrome-rank certificates inferred automatically from production compiler
semantics are **sound but loose**: the R6I block-deletion syndrome quotient has
rank 5 while κ_R6I = 1
(`research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json`). (iv) The
moral is a limit: the rungs that stalled all used per-block, syndrome-preserving
edit grammars, and no such grammar can express the whole-system Tag relocation
that closed the ladder. A negative rung — V5's 211,248-candidate search that
found no support-2 tightness witness and correctly refused to grant support-1
authority — is reported as a first-class result.

---

## 1. What an intrinsic support number is, and why compilation needs it

**Prior art, stated before the definition.** Asking for the smallest support of an
optimal solution, and for a matching lower bound that makes the answer two-sided,
is established practice in integer optimization (Aliev et al. 2018, above; and the
sparsity-over-lattices line that follows it). Nothing in this section is a new kind
of invariant. What is specific to this paper is that the quantity is computed
*exactly*, for two named compilation families under frozen objectives, by ladders
whose every rung is machine-checked and receipt-bound — where the integer-programming
results give general bounds rather than exact values for a named family. The
hostile external-novelty lane `QG19_HOSTILE_NOVELTY_RESULTS.json` records this
claim's verdict as `INSTANCE_OF_KNOWN_GENERAL`, and this framing is the correction
that verdict requires.

Fix a compilation optimization family F over structured inputs and an objective
C. A *support bound* for (F, C) is an integer B such that for every instance the
exact optimum is attained by some configuration whose structural generators each
have global support ≤ B. Support bounds convert an unrestricted optimization over
an unbounded index set into a finite enumerable search, and they are what makes a
DP-free static forecaster possible at all (companion paper,
`papers/archive/2026-08-pre-unification/QG-paper-02-certified-static-forecasting/MANUSCRIPT_V1.md`, Section 2.2).
The trouble is that a support bound is a property of a *proof*, not of a family.
Two theorems about neighbouring grammars here report B = 2 and B = 5: the R6M
three-block shared-one-bit-Tag grammar closes at support 2 for every n
(`research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`,
`theorem_statement`: "frame Paulis of global support >= 3 never strictly pay"),
while the R6I two-block rank-2 dependent-triple shared-two-bit-Tag grammar closed
at support 5 (`research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json`,
`support_bound_B: 5`, authority
`ORIONQ_QG1_RANK2_ALL_N_THEOREM_MACHINE_CHECKED__GENERATOR_SUPPORT5_SUFFICES_ALL_N__CAP5_EQUALS_UNRESTRICTED__NOT_R6`).
The natural reading — that R6I is structurally heavier, needing five qubits of
generator support where R6M needs two — was, we now know, wrong by a factor of
five. The bound moved with the F₂³ pigeonhole the proof used, not with the
family. We therefore name the family-intrinsic quantity:

> **Definition (intrinsic support number).** For a compilation family F under a
> fixed objective C, κ(F, C) is the least B such that every instance's exact
> optimum is attained by a configuration with all structural generators of global
> support ≤ B. Equivalently: B is a valid support bound and B − 1 is not.

κ is two-sided: establishing it requires an upper bound (a normal-form theorem
pushing every optimum down to support ≤ κ) *and* a lower bound (an infeasibility
or an exact instance witness showing κ − 1 fails). A one-sided result — the
ordinary state of the art, including this programme's own prior theorems — is a
support bound, not an intrinsic support number, and this paper keeps the
distinction throughout. Three consequences follow. **Search cost is governed by κ, not B**: the certified
enumeration of support-≤d configurations is `O(n^d A^d)` for fixed d and local
alphabet size A (`research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json`,
`search_complexity_corollary`; Section 6), so between d = 5 and d = 1 the
certified search space for R6I differs by four polynomial orders in n.
**Bounds are objective-scoped**, so κ takes two arguments: under the
frozen coefficient-weighted objective O1 (t_c = 1, t_nc = 7, t_r = 3, t_tag = 4)
a support-3 factorization strictly beats every support-≤2 one, with the exact
witness `C_DP = 11 < C_Dxx = 13 < C_Dplus = 23` at n = 3
(`research/extensions/orion-qg/QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`,
`objectives.O1.new_trade_witnesses.NEW_SUPPORT3[0]`) among 53 support-2 closure
failures (`objectives.O1.support2.failure_count: 53`). And **method reach becomes
measurable**: once κ is known independently, any certificate yielding a bound B
can be scored against it (Section 6).

This paper claims exactly three things, each bounded to its receipt: κ_R6I = 1
under the frozen R6I grammar and objective, established two-sidedly; the
objective-indexed cones inside which the support-1 (R6I) and support-2 (R6M)
certificates hold, with sharpness explicitly open; and the sound-but-loose
relationship between automatic syndrome-rank certificates and κ. It claims no
novelty for finite-field dependence, support sparsification, Pauli symplectic
representations, or parametric/polyhedral optimization
(`development/orion-qg-regime-geometry/QG6_SYNDROME_DIMENSION_COMPRESSION_PROTOCOL_V1.md`
and
`development/orion-qg-regime-geometry/QG16_R6I_SUPPORT1_PHASE_PROTOCOL_V1.md`,
"Novelty boundary").

## 2. The descent ladder as a proof technique

A descent ladder proves a sequence of support bounds B₀ > B₁ > … > B_k, each rung
consuming the previous rung's theorem as a premise and its *obstruction census* —
the exact finite set of boundary patterns the previous edit grammar could not
reduce — as its input domain. Each rung is a separately frozen protocol with its
own honest-terminal list, an independent generic verifier rebuilt without
importing production tables, and a native verifier bound to production semantics;
a rung may claim only its own bound and is forbidden from claiming the next one
or claiming tightness. The R6I ladder has five rungs above the published
support-5 parent
(`development/orion-qg-regime-geometry/QG_WAVE2_RECORD.md`, "QG-9 ladder"):

| Rung | Terminal | Bound |
|---|---|---|
| QG-1 (parent) | `THEOREM_MACHINE_CHECKED` | support ≤ 5, all n |
| V2 | `QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED` | ≤ 4 |
| V3 | `QG9_RANK2_ALL_N_SUPPORT3_SUFFICIENCY_MACHINE_CHECKED` | ≤ 3 |
| V4 | `QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED` | ≤ 2 |
| V5 | `QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL` | (honest negative) |
| V6 | `QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED` | **κ = 1** |

**Rung V2 — combined per-column deletion (5 → 4).** QG-1 used *separate* solo
moves on non-coincidence columns and pair moves on coincidence columns, leaving a
finite zero-sum-free support-5 boundary
(`development/orion-qg-regime-geometry/QG9_SUPPORT4_COMBINED_EXCHANGE_PROTOCOL_V1.md`,
"Motivation"). V2 enlarges the *local edit only*, admitting combined per-column
deletions `d0`, `d1`, `db`, `none`, and admits a multi-column edit as
semantics-preserving exactly when the XOR of the five-bit local signatures
`(⟨R0,R1⟩, ⟨S0,R0⟩, ⟨S1,R0⟩, ⟨S0,R1⟩, ⟨S1,R1⟩)` vanishes. States are grouped by
the descriptor `(a_active, b_active, coincidence, α, β00, β10, β01, β11)`, and
each descriptor/action pair uses the *worst* ΔC across all representatives and
target triples, per central choice — an adversarial certificate valid
independently of the instance's actual targets. Result
(`research/extensions/orion-qg/QG9_SUPPORT4_COMBINED_EXCHANGE_RESULTS.json`):
28 descriptors, 240 local representatives, 119,808 action-profile target cases;
all **324** retained irreducible support-5 patterns have a safe combined move —
324 safe, **0 unsafe**, worst-cost histogram {−22: 72, −18: 72, −15: 60, −14: 12,
−4: 72, 0: 36}. The support-4 control retains 432 patterns, 396 safe and **36
unsafe** ({−18: 72, −11: 120, −6: 12, −4: 36, −3: 12, 0: 144}), recorded verbatim
as "The frozen deletion-only combined edit grammar does not close support 4. This
blocks a support<=3 claim from this grammar but is not support-4 tightness
evidence" (`support4_control.interpretation`). Both harnesses accept
(`generic_verification.decision: ACCEPT`; `native_verification.decision:
ACCEPT_SUPPORT4`, scope `R6I_UNIT_OBJECTIVE_ONLY`) with `support3_claim: false`
and `tightness_claim: false`.

**Rung V3 — relabelling, not just deleting (4 → 3).** V3 lets an active generator
letter be *relabelled* to any of {I, X, Y, Z} while never adding support on a
previously inactive coordinate
(`development/orion-qg-regime-geometry/QG9_SUPPORT3_RELABEL_EXCHANGE_PROTOCOL_V1.md`,
"New edit grammar"). Because concrete representatives sharing a V2 descriptor can
admit different relabel signatures, V3 groups states by *action-profile type*:
same V2 descriptor and same complete Pareto-minimal action profile. Its attack
surface is exactly V2's census. The receipt
(`research/extensions/orion-qg/QG9_SUPPORT3_RELABEL_EXCHANGE_RESULTS.json`)
records 46 action-profile types and, on the **36** V2 survivors, 288 type cases
of which **288 safe, 0 unsafe** ({−10: 96, −9: 108, −8: 12, −6: 24, −5: 48}). The
support-3 boundary control gives 180 descriptor survivors, 612 type cases, 591
safe, **21 unsafe** — "Broad-superset method boundary only. V3 grants no
support<=2 or tightness authority" (`support3_boundary_control.interpretation`).

**Rung V4 — no new edit, a realizability filter (3 → 2).** V4 asks whether V3's
21 residual obstructions are realizable compiler states, applying the full R6I
block acceptance condition: XOR the local coordinates across the selected support
to get α, u0, v0, u1, v1, form branch labels c0 = 2u0 + v0 and c1 = 2u1 + v1, and
require α = 1, c0, c1 ∈ {1,2,3}, c0 ≠ c1
(`development/orion-qg-regime-geometry/QG9_SUPPORT2_FULL_ACCEPTANCE_PROTOCOL_V1.md`,
"Full R6I block acceptance"). The gate — that **zero** V3-rich-unsafe support-3
profile cases are fully accepted R6I blocks — passes: from 252 QG-1 irreducible
descriptors and 180 V2 survivors, the 612 V3 type cases with 21 broad-unsafe
reduce to **300 fully accepted type cases, 300 safe, 0 unsafe**
(`research/extensions/orion-qg/QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json`,
`support3_full_acceptance`). The support-2 boundary control is where the ladder
stops: 72 irreducible descriptors, 144 type cases, 93 broad-unsafe, and after the
acceptance filter **72 accepted type cases, 36 safe, 36 unsafe** — "Nonempty
accepted method obstruction under the current relabel grammar. This blocks
support<=1 from this proof stack but is not support-2 tightness evidence"
(`support2_boundary_control.interpretation`).

**Why the discipline matters.** The censuses chain literally — V2's 36 unsafe
support-4 patterns are V3's
`support4_parent_survivors.descriptor_survivors: 36`, and V4's 36 accepted unsafe
support-2 type cases are V5's `candidate_generator.accepted_unsafe_type_cases:
36` — so a reader can check that no rung quietly widened its own domain. Each
rung carries an explicit non-promotion (`support3_claim: false`,
`support2_claim: false`, `support1_claim: false`, `tightness_claim: false`), and
each distinguishes a *method obstruction* from a *tightness result* in its own
receipt text — the distinction Sections 3 and 4 depend on entirely.

## 3. κ_R6I = 1: the whole-system Tag relocation (V6)

V2–V4 all preserved the shared Tag and edited within blocks. V6 abandons that
constraint: for each block choose an anticommuting local core q_j (a column with
`local_symp(r0, r1) = 1`, which exists because the global symplectic product is
one), delete both generator letters at *every other* column, recompute the
dependent third frame, and then **relocate the shared Tag** to canonical letters
at the new cores — changing no target, B permutation or central choice
(`development/orion-qg-regime-geometry/QG9_V6_SUPPORT1_NORMALIZATION_PROTOCOL_V1.md`,
"Construction and proof obligations"). The receipt is
`research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json`,
terminal `QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED`.

**L1 (deletion credit).** For any active non-core local column, over all target
letters and every central choice, zeroing both independent local generator
letters changes the objective by at most **−4** for locally commuting active
patterns and at most **−7** for locally anticommuting ones. Complete domain:
**2,880** rows (15 local pairs × 64 target triples × 3 centrals), 1,728
commuting and 1,152 anticommuting; exact maxima `max_delta_commuting: -4`,
`max_delta_anticommuting: -7` (`finite_lemmas.deletion`).

**L2 (core alignment).** Any ordered local anticommuting basis has all three
frame letters non-identity, so its weighted frame contribution is exactly **10**
for every central choice; replacing one ordered anticommuting basis by another
changes frame cost by **zero** and worsens at most three Restore letters, exact
bound **+3**. Complete domain: **6,912** rows (6 old × 6 new bases × 64 target
triples × 3 centrals), `frame_contribution_invariant: 10`,
`max_restore_increase: 3`, `max_triple_hamming: 3`
(`finite_lemmas.core_alignment`).

**L3 (canonical shared Tag) and L3′ (same-qubit rigidity).** For every ordered
local anticommuting basis there are unique nonzero local Tag letters generating
canonical labels (c0, c1) = (1, 2): same qubit and same basis costs Tag **4**,
distinct localization qubits Tag **8**. Every feasible original configuration has
both global Tag strings nonzero, hence an original Tag cost floor of **4**
(`finite_lemmas.original_feasible_tag_cost_floor: 4`). Over the complete
**576**-row rigidity domain, **36** rows are feasible under equal nonzero
distinct labels and **0** have differing ordered bases:
`different_basis_counterexamples: 0` (`finite_lemmas.same_qubit_tag_rigidity`).

**L4/L5 (distinct and same cores).** Over the complete **9,216**-row domain
(6 × 6 ordered basis pairs × 16 × 16 two-qubit letter choices) the exact minimum
shared-Tag cost is **8** for every one of the **36** basis pairs
(`finite_lemmas.distinct_qubit_tag.minimum_cost_all_basis_pairs: 8`). If
q_A ≠ q_B and both blocks are already support-1, feasibility with equal nonzero
distinct labels forces each Tag string nonzero at both frame qubits, giving an
original floor of 8 which pays the new cost 8; otherwise at least one block
deletes a non-core active column, earning ≥ 4 credit against an original floor of
4 and a new cost of 8. If q_A = q_B, equal ordered bases need no alignment and
the new Tag cost is 4; differing bases cannot occur when both blocks are already
support-1 (L3′), so at least one differing-basis block has a non-core active
column, whose deletion earns ≥ 4 credit against an alignment cost of ≤ 3.

**Composition and the lower bound.** The machine record verifies the arithmetic
explicitly: extra-active-column credit floor **4** exceeds the core-alignment
ceiling **3**; distinct-core new Tag cost **8** is paid by old-Tag floor 4 plus
one extra credit 4; same-core new Tag cost **4** does not exceed the old-Tag
floor 4; `all_cases_closed: true` (`composition`). Support 0 is infeasible for a
rank-2 block because `symp(0,0) = 0` contradicts the global anticommutation
requirement (`QG9_V6_SUPPORT1_NORMALIZATION_PROTOCOL_V1.md`, "Composition
audit"), recorded as `support0_infeasible: true`; with the support-1 upper bound
this closes both sides at `intrinsic_support_number: 1`. The native verifier
records the *reason* in its own field —
`native_orion_q.tightness_by_support0_infeasibility: true` — rather than
inferring tightness from any search. Both harnesses return
`ACCEPT_SUPPORT1_THEOREM` with `all_checks: true` (`both_accept: true`). The
stress arm, which "cannot authorize the theorem; it can only refute it or
corroborate the finite proof", generated deterministic feasible support-≤2
configurations at n = 2..6 (seed 20260821): **60 rows, 0 failures**, deltas from
−33 to −7 (`stress`). The receipt's interpretation is the paper's thesis in one
sentence: "The earlier fixed-Tag local-edit proof systems stopped at support2
because they preserved auxiliary Tag structure. Whole-system Tag relocation
removes those method obstructions … Support0 is infeasible, so kappa_R6I=1
exactly."

## 4. The honest negative rung: V5, and why refusing authority mattered

Between V4 and V6 sits a rung that proved nothing positive and is nonetheless
load-bearing. After V4's 36 accepted unsafe support-2 type cases, the natural
next question was tightness from below: is there an actual n = 2 instance with
`C_cap2 = C_unrestricted < C_cap1`? At n = 2, cap 2 *is* the unrestricted
frame-pair space, so a strict gap would prove support 2 necessary there and —
with the V4 theorem — make the all-n bound tight
(`development/orion-qg-regime-geometry/QG9_SUPPORT2_TIGHTNESS_PROTOCOL_V1.md`,
"Question"). V5 was an inverse-design search frozen before any cap outcome,
seeded by exactly
the V4 obstruction census: the **36** accepted-unsafe type cases expanded to
**1,296** unique blocks, giving **4,104** compatible block pairs, with four
target-template families opened in frozen order — `IDENTITY_RESTORE`,
`ONE_DEFECT_A`, `ONE_DEFECT_B`, `MATCHED_DEFECT` — each exhausted before the next
and no widening permitted after outcome
(`research/extensions/orion-qg/QG9_V5_SUPPORT2_TIGHTNESS_RESULTS.json`,
`candidate_generator`; generator digest `bb07c127…` recorded *before scoring*).
The complete ladder tested **211,248** candidates (4,104 / 69,768 / 69,768 /
67,608 by family, in that order), refereed by
QG-1's exact capped `PairTables(2)` with an exact min-plus cache (936 A-side and
936 B-side entries, `canonical_bind_all_pass: true`,
`scientific_order_unchanged: true`) and a hostile n = 2 binding check on 4 rows.

`selected_witness: null`. Terminal
`QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL`; generic lane
`NEGATIVE_PANEL_NOT_INDEPENDENTLY_REPLAYED`, native lane `RECORD_NEGATIVE_PANEL`
with `parent_support2_protected: true`, `tightness_authority: false` and
`support1_authority: false`. The protocol had pre-committed the reading: "A
negative panel result is not a support<=1 theorem."

Three things make this a result rather than a gap. **It refused an available
inference.** Finding no necessity witness across 211,248 frozen candidates is
suggestive that support 1 might suffice; a less disciplined lane would have
reported "support 2 appears unnecessary" and let the reader promote it. V5
instead recorded the negative and stated that the panel "motivates a new
prospective support<=1 theorem/counterexample programme but grants no support1
authority" — which is what happened: V6 opened as a new packet with its own
pre-outcome freeze and binds V5 as a parent *without using the negative panel as
proof* (`QG9_V6_SUPPORT1_NORMALIZATION_PROTOCOL_V1.md`, frozen domain 7). **It
did not weaken the referee**: `production_dp_opened: false`. **It predicted the
shape of the answer**: V5's failure and V4's nonempty method obstruction are
consistent in exactly one way — the obstruction was an artifact of the *proof
system*, not of the family. V6 confirmed that, which is why the wave-2 record can
say the earlier rungs "were not wasted: each obstruction census is what showed
the residue was structural rather than local, motivating a change of proof system
instead of a bigger move menu"
(`development/orion-qg-regime-geometry/QG_WAVE2_RECORD.md`, "Method finding").
The same entry records the consequence: the two open tightness hunts — "is
support-4 tight?" and "is support-2 tight?" — are both answered **no** by V6,
settled two rungs below where they were asked.

## 5. Objective cones: κ is a function of (family, objective)

A support theorem proved under one weighting says nothing about another. Both of
this programme's support theorems have therefore been re-derived *parametrically*,
producing the exact polyhedral cone of objective weights inside which the
certificate holds for all n.

### 5.1 QG-16: the R6I support-1 cone

QG-16 reweights only structural coordinates of the R6I objective,

`C_θ = Σ_blocks [ t_c·(w(R_c) − 1) + t_nc·Σ_{k≠c}(w(R_k) − 1) ] + t_tag·(w(S0) + w(S1)) + t_r·Σ_k w(Restore_k)`

with nonnegative coefficients and t_r > 0, and asks for which θ the V6
normalization still runs (`QG16_R6I_SUPPORT1_PHASE_PROTOCOL_V1.md`, "Target").
A parent structural lemma does the reduction: under the protected support-≤2
theorem w(R0), w(R1) ≤ 2, and global ⟨R0, R1⟩ = 1 forces an odd number of local
anticommuting columns, so there is **exactly one** anticommuting core and every
non-core active column is locally commuting — leaving only the resource geometry
of deleting a *commuting* active column. QG-16 enumerates that complete domain —
**1,728** rows — in credit coordinates (refund_c, refund_nc, delta_restore),
obtaining **10** realized resource vectors and, after Pareto reduction, **2**
worst vectors, `[0,2,2]` and `[1,1,2]`, each with a serialized equality witness
(`research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json`,
`commuting_deletion_resource_domain`, `all_resource_vectors`,
`worst_resource_vectors`, `worst_vector_witnesses`); the alignment domain is
re-derived at **6,912** rows with `frame_delta_zero: true` and
`max_restore_increase: 3`. Requiring both worst credits to dominate both
composition obligations — alignment `3·t_r` and Tag relocation `2·t_tag` over the
universal old-Tag floor — gives the irredundant four-facet cone
(`full_cone_halfspaces`):

```
2·t_nc ≥ 5·t_r              t_c + t_nc ≥ 5·t_r
2·t_nc ≥ 2·t_r + 2·t_tag    t_c + t_nc ≥ 2·t_r + 2·t_tag
```

Under the separately declared ordering t_c ≤ t_nc the first and third become
redundant, leaving `t_c + t_nc ≥ 5·t_r` and `t_c + t_nc ≥ 2·t_r + 2·t_tag`
(`simplified_under_t_c_le_t_nc`). Inside the cone,
`support_bound_inside_cone: 1` and `intrinsic_support_number_inside_cone: 1` for
every n. The exact rational controls (θ ordered as (t_nc, t_c, t_tag, t_r)) are
the sharpest part of the receipt (`controls`):

| Control | θ | Inside? | Minimum margin |
|---|---|---|---|
| O0 (unit objective) | (4, 2, 2, 1) | yes, **on boundary** | **0** |
| O_in | (5, 3, 2, 1) | yes, strict interior | 2 |
| O_tag_out | (4, 2, 5/2, 1) | no | −1 |
| O_restore_out | (4, 2, 2, 5/4) | no | −1/2 |
| O_nc_out | (3/2, 3/2, 1, 1) | no | −2 |

The unit objective — under which κ_R6I = 1 was proved in Section 3 — sits
**exactly on a Tag-relocation facet at margin 0**; raising the Tag price to 5/2,
the Restore price to 5/4, or flattening the frame prices to (3/2, 3/2) each
leaves the cone. The support-2 core census is bound as a cross-check: ordered
anticommuting support-2 pair counts {1: 6, 2: 120, 3: 666, 4: 1968} with
`every_pair_exactly_one_local_anti_core: true` (`support2_core_census`) — the same
census that appears in the R6M all-n theorem
(`MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`, `anticommuting_support2_pair_counts`).

**The mandatory caveat.** `global_phase_boundary_sharpness: "OPEN"`, and the
receipt spells out what "outside" means:
`outside_cone_semantics: "THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY__NOT_SUPPORT2_REQUIRED"`.
No row above is a claim that support 2 is required at O_tag_out, O_restore_out or
O_nc_out; nothing has been proved about κ there at all. The protocol made this a
standing condition of native acceptance, not an afterthought
(`QG16_R6I_SUPPORT1_PHASE_PROTOCOL_V1.md`, ORION-16 and "Native ORION-Q").

### 5.2 QG-8: the R6M support-2 cone, and an outside control with teeth

The TARE analogue was proved first. QG-8 re-enumerates the complete R6S Lemma-E
local domain — **18,432** cases, 9,216 per resource kind — from production local
Pauli/F3 tables, recovering maximum `df3 = 2` for both central and non-central
frame deletions with matching histograms ({−2: 288, −1: 2304, 0: 4032, 1: 2304,
2: 288} on each side) and an explicit central equality witness at `delta_f3 = 2`
with `unit_objective_central_net: 0`
(`research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json`,
`local_resource_domain`). Weighted deletion is therefore non-increasing exactly
in the cone `t_c ≥ 2·t_r ∧ t_nc ≥ 2·t_r` (`support2_cone.conditions`), inside
which `all_n_support_bound: 2` for every admitted frozen-R6M instance; two
coefficients are absent by proof, not omission (`tag_coefficient:
"UNCONSTRAINED_BY_EXCHANGE"`, `rotation_coefficient:
"WITHIN_FAMILY_CONSTANT_DIRECTION"`). The controls are bound to the committed QG-2 receipt (`qg2_binding`, all checks
true, receipt sha256 `d9f38dab…`). **O0** (t_c = 2, t_nc = 4, t_r = 1, t_tag = 2)
is inside with central margin **0.0** — exactly on the central hyperplane — and
non-central margin 2.0; **O2** (O0 plus ρ = 5 per rotation) is inside with
identical margins; **O1** (t_c = 1, t_nc = 7, t_r = 3, t_tag = 4) is **outside**,
central margin **−5.0**, non-central margin 1.0. O1 gives objective-indexing its
lower bound, because QG-2 supplies not merely a failed certificate but exact
global witnesses: two serialized support-3 witnesses with `C_DP = 11`,
`C_Dxx = 13`, `C_Dplus = 23` (`qg2_binding.support3_witnesses`; primary source
`QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`,
`objectives.O1.new_trade_witnesses.NEW_SUPPORT3`, whose DP witness records
`max_frame_support: 3` and `cost_recomputed_ok: true`). Under O1 the restriction
to support ≤ 2 is strictly worse than the optimum, so κ_R6M(O1) ≥ 3; with the
inside-cone theorem this proves **no objective-independent support-2 theorem
exists** for R6M
(`development/orion-qg-regime-geometry/QG8_OBJECTIVE_SUPPORT_PHASE_PROTOCOL_V1.md`,
"Controls").

**The same caveat, differently placed.** QG-8 records two distinct sharpness
facts and never conflates them: `certificate_boundary_sharpness:
"CENTRAL_HYPERPLANE_EXACT"` — the serialized `df3 = 2` central witness makes the
*R6S certificate* exact at t_c = 2·t_r, so below that hyperplane the same local
rewrite can increase weighted cost — while `global_boundary_sharpness: "OPEN"`.
The proof audit states the non-inference explicitly:
`outside_cone_not_equated_with_support3_required: true` and
`o1_global_witness_only_refutes_objective_independent_support2: true`
(`proof_audit`). O1 refutes objective-independence; it does not locate the true
boundary of the support-2 region.

Read together, the two cones say the same thing about contingency: in *both*
families the unit-cost objective sits exactly on a facet rather than in the
interior, so an arbitrarily small change in the Tag price (R6I) or the central
frame price (R6M) exits the certified region.

## 6. Syndrome-rank certificates: what production semantics can and cannot certify

QG-6 asks whether the finite-support dimension behind an all-n theorem can be
*inferred from production exact-DP transition semantics* rather than
hand-specified from a proof sketch
(`development/orion-qg-regime-geometry/QG6_SYNDROME_DIMENSION_COMPRESSION_PROTOCOL_V1.md`,
"Scientific question"). The instrument is deliberately elementary and
donor-owned, recorded as a checked proof object
(`research/extensions/orion-qg/QG6_SYNDROME_DIMENSION_RESULTS.json`,
`meta_theorem`): over F₂, if active coordinates carry syndrome contributions in
F₂^d whose global XOR is a required nonzero syndrome, and every nonempty proper
zero-sum subset admits a semantics-preserving, cost-non-increasing deletion with
ties strictly decreasing a well-founded support measure, then some optimum has at
most d active coordinates (`meta_theorem.proof_steps`, `support_bound: "d"`,
`novelty_credit: false`).

Run on production semantics: for R6M, over the full 16,384-row local option
domain, each of the six frame slots has single-letter-deletion change vectors of
**rank 2**, contained in and spanning its declared analytic basis (`r6m`,
`auto_dimension: 2`, `all_slot_ranks_2: true`, per-slot `rank: 2` with
`unique_change_count: 4`); binding the committed R6S receipt (sha256
`b6d72913…`, authority
`MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED__SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N__NOT_R6`,
all gates true) yields `support_theorem_status:
"RECOVERED_FROM_EXISTING_R6S_CERTIFICATE"` — the support-2 theorem recovered from
production semantics alone, a genuine positive. For R6I, the same procedure over
the 4,096-row local domain, deleting both independent generators of one block,
gives **rank 5** for both blocks (`r6i`, `auto_dimension: 5`,
`all_block_ranks_5: true`, blocks A and B each with `rank: 5`,
`unique_change_count: 26`, `width: 10`), with local-cost corroboration over the
complete **46,080**-case domain: zero cases with Δ > −4, exact maximum Δ = −4,
zero violations (`r6i.local_cost_corroboration`).

**The 5-versus-1 gap.** Visible only once QG-6 and QG-9 V6 are both bound: the
syndrome-quotient rank for R6I is **5** while its intrinsic support number is
**1**. The production-syndrome pipeline is therefore **sound but loose** — it
certifies that *some* finite-support normal form exists and gives a valid bound,
but the rank is not the intrinsic support number (`QG_WAVE2_RECORD.md`, "QG-6 —
production syndrome-rank inference, and a sound-but-loose bound"). This is not an
implementation defect: rank d is the dimension of the linear quotient a
*single-block deletion* rewrite can move, so a certificate built from it proves
only what that rewrite class proves, while V6's descent relocates the shared Tag
across the whole system — exactly the operation the rank argument holds fixed.
The wave-2 record states the consequence as the programme's sharpest statement
about the reach of its own meta-method: closing the gap "needed exactly the
whole-system Tag relocation of V6, which no per-block syndrome-preserving
argument — including the rank argument itself — can express."

QG-6's own discipline deserves recording alongside the gap: its protocol forbids
inferring a support theorem from rank alone (§4) and forbids self-authorizing its
motivating theorem, so the R6I entry is pinned at `support_theorem_status:
"PENDING_QG1_INDEPENDENT_DUAL_HARNESS"` and the terminal reads
`QG6_PRODUCTION_SYNDROME_RANK_INFERENCE_VERIFIED__R6M_D2_RECOVERS_SUPPORT2__R6I_D5_FOUND_THEOREM_PENDING_QG1`.
The lane later shown loose by a factor of five had already refused to claim more
than it could check.

**Rank bounds the search, not the optimum.** The certified enumeration size for a
finite local alphabet A is
`N_support(n, d, A) = sum_{k=0}^{d} binom(n,k)·A^k = O(n^d·A^d)` for fixed d,
scoped `CERTIFIED_COMPONENT_ONLY` — it "applies only to the certified compilation
component/rewrite, not to an arbitrary full compiler"
(`QG6_SYNDROME_DIMENSION_COMPRESSION_PROTOCOL_V1.md`, §7). So d = 5 says an R6I
optimum is *findable* by an O(n⁵A⁵) certified enumeration; it does not say the
optimum *uses* five qubits of support. V6 proves it uses one, and the same
corollary at d = 1 gives O(nA) — four polynomial orders of certified search
separating what the automatic pipeline certifies from what is true.

## 7. Cross-family comparison: what κ is, and what varies

| Family | Objective | Support bound (all n) | κ status | Receipt |
|---|---|---|---|---|
| R6I (rank-2 dependent-triple, shared 2-bit Tag) | frozen unit R6I objective | **1** | **κ = 1 exactly** (upper bound by V6; lower bound by support-0 infeasibility) | `QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json` |
| R6I | any θ in the four-facet QG-16 cone | 1 | κ(θ) = 1 inside the cone; outside, no claim | `QG16_R6I_SUPPORT1_PHASE_RESULTS.json` |
| R6I | frozen unit objective, via the QG-1 proof system | 5 | superseded upper bound (loose by 4) | `QG1_RANK2_ALL_N_RESULTS.json` |
| R6M / TARE (three-block, shared 1-bit Tag) | frozen unit-cost support objective | **2** | **κ_TARE = 2 exactly** (upper R6S; lower QG-18 necessity witness) | `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`; `QG18_TARE_KAPPA_RESULTS.json` |
| R6M / TARE | any θ with t_c ≥ 2·t_r ∧ t_nc ≥ 2·t_r | 2 | κ(θ) ≤ 2 inside the cone; outside, no claim | `QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json` |
| R6M / TARE | O1 (t_c = 1, t_nc = 7, t_r = 3, t_tag = 4) | — | **κ ≥ 3** by exact witness (C_DP = 11 < C_Dxx = 13) | `QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json` |

**κ is not monotone in apparent structural complexity.** R6I carries a two-bit
shared Tag, a dependent third letter (R₂ = R₀R₁) and a rank-5 syndrome quotient —
every visible indicator says it is the heavier family — yet κ_R6I = 1, below
R6M's support-2 bound. Structural richness bought R6I *more* normalization
freedom, not less: the extra Tag bits are what the whole-system relocation
spends.

**κ_TARE = 2 exactly, settled two-sidedly.** R6S supplies the upper bound
(support ≤ 2 for all n), and its claim boundary records that the exchange "fails
exactly at w = 2 with class pattern {(1,\*),(0,1)} … the R6O weight-2 trade,
realized by 559 recorded DP optima" (`MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`,
`claim_boundary.support_2_boundary`) — a *certificate* boundary, not by itself a
proof that no support-1 optimum of equal cost exists. QG-18 supplies the missing
lower bound with an exact necessity witness
(`research/extensions/orion-qg/QG18_TARE_KAPPA_RESULTS.json`, terminal
`QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS`, `kappa_interval: [2,2]`):
at n = 2 with targets A=(Z₀,Z₀), B=(Z₀,Z₀), C=(Z₁,X₁),

    C_DP = C_Dxx = 5 < 6 = C_cap1,

with `C_DP` recomputed four independent ways and `C_cap1` six, including a
from-primitives brute force over all 7⁶ frame six-tuples × all Tags. The
optimum-attaining configuration is serialized verbatim; its single support-2
Pauli is X₀X₁ in block C. The gap is not exotic: it occurs on 1,836 of the
46,656 instances of the complete structured n = 2 slice (3.93%), always by
exactly 1, and never at n = 1 (where support ≤ 1 is vacuous — the completeness
control).

**Why the R6I proof cannot be borrowed, and the principle that generalizes.**
QG-18 also ran the V6 lemma chain against TARE on complete domains, and it dies
at the first obligation. R6I's rank-2 dependent triple (R₂ = R₀R₁) makes each
local frame column carry three multiplied slots, so deleting a non-core column
refunds at least 4 (10 when anticommuting) against a Restore penalty of at most
3 — leaving budget to pay alignment and rebuild the Tag. R6M's objective instead
carries the all-three-blocks factor rule F3, which discounts a branch qubit by
exactly 2 when the three Restore letters coincide; a frame letter can be
*earning* that discount, so its deletion refund is exactly cancelled and TARE's
credit floor is **0** (2,304 zero-credit rows of 221,184). There is no budget,
and the chain ends before the Tag is touched. Stated generally:

> Whole-system Tag relocation is available to a family exactly when its
> per-column frame refund **strictly** exceeds the maximum Restore penalty of
> deleting that column.

That margin is 4 for R6I and 0 for TARE — and the zero is the same fact QG-8
records geometrically, with the unit objective O0 sitting *on* the central
hyperplane t_c = 2·t_r at margin 0
(`QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json`, `CENTRAL_HYPERPLANE_EXACT`). The
proof-theoretic obstruction and the polyhedral boundary are one measurement seen
twice. This makes the margin of a family's exchange inequality a cheap a-priori
test of whether its support bound is likely to equal its intrinsic support
number, before any descent ladder is attempted.

So the two families differ in their intrinsic values, not merely in which edit
class reaches them: **κ_R6I = 1 < 2 = κ_TARE**, with the structurally *richer*
family carrying the *smaller* κ.

## 8. Method: the provable limits of per-block, syndrome-preserving grammars

The stalled rungs share a signature. V2 admitted combined per-column deletions;
V3 added relabelling; V4 added a realizability filter but no new edit. All three
preserved the full five-bit single-block syndrome and left the shared Tag fixed,
by construction (`QG9_SUPPORT3_RELABEL_EXCHANGE_PROTOCOL_V1.md`: "No target, Tag,
central choice, permutation, or other block coordinate is changed"). And all
three left a nonempty census at their frontier: enlarging the move menu within
the class helped monotonically but with shrinking returns (324/324 then 396/432;
288/288 then 591/612; 300/300 then 36/72), each enlargement repairing the
previous residue and generating a new one — the empirical signature of a *method*
obstruction rather than a family obstruction.

Section 6 gives that limit its algebraic form. A per-block syndrome-preserving
edit acts inside the linear quotient whose dimension QG-6 measures automatically;
for R6I that dimension is 5. Any argument that only deletes or relabels within
blocks while holding the shared Tag fixed is confined to that quotient, so the
best support bound it can certify is governed by the quotient's rank — which no
enlargement of the within-block move menu can lower. Reaching κ = 1 required
leaving the quotient: localizing each rank-2 block to one anticommuting core and
relocating the shared Tag to canonical letters at the new cores, paying the
relocation out of deletion credit (L1's floor of 4 against L2's ceiling of 3 and
L3/L4's Tag costs of 4 and 8). That is a whole-system rebuild, inexpressible in
every grammar V2–V4 used.

Two rules follow, as method proposals rather than theorems: **measure the
syndrome quotient first, then treat its rank as a budget for the search, not as
an estimate of κ**; and **when successive enlargements of a local edit grammar
each repair the last residue and produce a new one, change the proof system
rather than the move menu** — the obstruction censuses are the diagnostic, each a
finite serialized set the next rung consumes as its input domain. Neither rule is
claimed beyond the two families receipted here, and neither as novel: linear
dependence over F₂, support sparsification and normal-form arguments are donor
mathematics carrying zero novelty credit in this programme
(`QG6_SYNDROME_DIMENSION_COMPRESSION_PROTOCOL_V1.md`, §11).

## 9. Claim boundary

**Status vocabulary, per claim.** THEOREM (machine-checked, all n): κ_R6I = 1
under the frozen R6I grammar and unit objective, including V6's finite lemmas
over their complete stated domains and the support-0 lower bound; the V2/V3/V4
support-≤4/3/2 sufficiency theorems; the QG-16 and QG-8 cones, each for all n
inside its stated cone; the R6S support-2 and QG-1 support-5 theorems; the QG-6
meta-theorem and search-complexity corollary as checked proof objects; and every
exact counterexample cited, including QG-2's O1 support-3 witnesses — an exactly
verified counterexample is a theorem that the corresponding closure fails.
EVIDENCED (machine-verified on stated finite frozen domains, not theorems for all
n): the V6 stress panel (60 rows at n = 2..6, seed 20260821, 0 failures); QG-6's
R6I local-cost corroboration (46,080 cases), which its own receipt pins at
`PENDING_QG1_INDEPENDENT_DUAL_HARNESS`; and V5's negative panel (211,248
candidates, no witness), evidence about a frozen panel and nothing more. OPEN:
global sharpness of both
cones; and κ for every objective outside the certified cones.

**The two mandatory non-inferences.** First,
`GLOBAL_PHASE_BOUNDARY_SHARPNESS = OPEN` holds for QG-16 and QG-8 alike; outside
either cone the only licensed statement is
`THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY__NOT_SUPPORT2_REQUIRED`
(`QG16_R6I_SUPPORT1_PHASE_RESULTS.json`, `outside_cone_semantics`) and
`outside_cone_not_equated_with_support3_required: true`
(`QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json`, `proof_audit`). Nothing here asserts
that support 2 is required at any objective outside the R6I cone, or support 3
outside the R6M cone; O1's role is solely to refute objective-independence.
Second, method obstructions are not tightness results: V2's 36 unsafe support-4
patterns, V3's 21 unsafe support-3 cases and V4's 36 accepted unsafe support-2
cases are each labelled in their receipts as blocking the next claim *from that
proof stack*, never as evidence that the corresponding support is necessary — a
reading V6 vindicated by settling both open tightness questions at once.

**Scope.** The R6I theorems cover the frozen R6I two-block rank-2 dependent
TARE-3 shared-2-bit-Tag grammar under the frozen R6I objective — (4,4,4) frame
multiplicities with the central branch reduced to 2, Tag paid twice, per-branch
Restore supports with no factor rule — for every qubit count, target-triple pair,
relative B permutation and central pair (`QG1_RANK2_ALL_N_RESULTS.json`,
`claim_boundary.covers`), with native scope `R6I_UNIT_OBJECTIVE_ONLY` on every
ladder rung; they do not cover the R6K restore-factor variant, the R6M/R6S
three-block grammar, larger Tag ranks, or non-support objectives outside the
certified cones (`claim_boundary.does_not_cover`). The R6M theorem covers the
frozen R6L/R6M three-block TARE-M2 shared-one-bit-Tag grammar under the frozen
raw support-count objective and explicitly does not cover the R6I grammar
(`MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`, `claim_boundary.does_not_cover`).
Stress panels are corroboration, not proof, in both families' own words.

**No novelty, no advantage, no R6.** Every receipt cited records
`novelty_authority: false` and `physical_quantum_advantage_claim: false`; the
QG-9 rungs additionally record `new_theorem_authority: false`, and every parent
authority string they bind terminates in `NOT_R6`
(`ORIONQ_QG1_RANK2_ALL_N_THEOREM_MACHINE_CHECKED__…__NOT_R6`;
`MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED__…__NOT_R6`;
`ORIONQ_QG2_OBJECTIVE_ROBUSTNESS_MIXED__FROZEN_REWEIGHTED_OBJECTIVES__NOT_R6`).
Donor-owned machinery — finite-field linear dependence, Davenport-type pigeonhole
bounds, Carathéodory-style support sparsification, fixed-parameter complexity,
Pauli symplectic representations, multi-objective and polyhedral parametric
optimization, hardware-aware cost selection, and the TARE primitive itself —
receives zero novelty credit. No claim of physical quantum advantage, hardware
resource improvement, full-circuit optimality, or priority over any external
discipline is made or implied; the candidate contributions are exactly the
compiler-specific, proof-carrying artifacts named above, each requiring external
review.

**Integrity envelope and reproducibility.** No lane cited here read any chemistry
source or protected subject: `chemistry_sources_read: false` and
`protected_subject_read: false` in QG-6 and QG-8,
`no_new_chemistry_or_protected_access: true` in QG-8's gates. The protected
stretched-N2 subject
(`N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt`) was
never read by any receipt cited here and remains sealed. Every lane ran under a
protocol frozen before its outcome with an explicit honest-terminal list, a
generic verifier rebuilt without importing production tables, and a native
verifier bound to production semantics; both harnesses had to accept
(`both_accept: true` in every one of the QG-9, QG-16, QG-6 and QG-8 protected run
receipts under `development/orion-qg-regime-geometry/`). Independent
pre-merge verification is recorded in `QG_WAVE2_RECORD.md`: V6's analyzer re-run
reproduced `result_digest` `587b4b80…d31a4f` bit-identically against its
committed protected receipt and again on the merged tree; the support-4/3/2
analyzers were re-run with all gates true; QG-6's digest `f065afc8…b023eb` was
reproduced bit-identically by an independent verifier that does not import
`_DELTA`, 10/10 gates. Every number here replays from the receipts and protocols
listed in the accompanying claim ledger; numbers not present in them do not
appear.
