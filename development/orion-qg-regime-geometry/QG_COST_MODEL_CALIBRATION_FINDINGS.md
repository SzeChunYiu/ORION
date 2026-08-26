# Calibrating `config_cost` to a physical resource — findings

## HEADLINE

The QG-39 probe family **structurally cannot see frame support**. All six frame
Paulis are weight-1 by construction, so the frame term is identically 18 and the
`-18` annihilates it under *every* weight vector. QG-39 is therefore a result
about the factored-Restore coordinate alone — on a construction whose entire
subject matter (support>=3 exchange, weight-2 trades, support-2 sufficiency) is
frame support. Its regret figure reduces exactly to `t_r * 5`.

## TASK 1 — what `config_cost` mechanically counts

`research/extensions/orion-q/max_r6s_all_n_composition.py:251-271`:

    config_cost = SUM_{j=0..2} [ m_{j,0}*w(R_{2j}) + m_{j,1}*w(R_{2j+1}) ]   # frame support
                + 2*w(S)                                                     # shared-Tag support
                + SUM_{k in {0,1}} F3(T_k R_k, T_{2+k} R_{2+k}, T_{4+k} R_{4+k})  # factored Restore
                - 18

`w(.)` = Pauli weight (`p10.wt`, `(x|z).bit_count()`). `m = 2` for the central
branch of block j and `4` for the non-central branch. `F3` per qubit = 1 if all
three letters are equal and non-identity (shared factor extracted), else the
number of non-identity letters. `-18 = 3*(t_nc + t_c)`, which makes it
SUM_i t_i*(w(R_i)-1): frame support is counted as EXCESS over weight one.

So it is a **role-weighted count of Pauli support**, with declared coefficient
vector (t_nc, t_c, t_tag, t_r, rho) = **(4, 2, 2, 1, 0)** over five named
coordinates: non-central frame support, central frame support, shared-Tag
support, factored-Restore support, and rotations. Confirmed identical in the
parameterized clone `qg2_objective_robustness.py:95-118` (`OB_O0`).

**Rotations are priced at exactly zero.** They are a frozen non-compensatory
coordinate — candidates had to be rotation-nonworse and ties (9 vs 10) were
never priced. The T-cost driver is not in the objective.

### What the documents claim
`QG2_OBJECTIVE_ROBUSTNESS_PROTOCOL.md` calls it "raw support-count objective"
and constructs **O1 = (7, 1, 4, 3, 0)** as the explicitly *T-count-weighted*
alternative, on the stated rationale that the non-central branch carries the
arbitrary-angle rotation whose magic-state cost dominates (~7-15 T per
synthesized rotation) while the central branch is Clifford-dominated.

**Computed and claimed agree, and the disagreement a referee might hope for is
absent.** The programme never claims O0 is a physical count; it says the
opposite. `papers/archive/2026-08-pre-unification/QG-paper-01-compilation-regime-geometry/MANUSCRIPT_V1.md:304-306, 324, 344` states the
geometry is "a property of the (family, objective) pair", that the R6S
sufficiency bound is "objective-scoped, not universal", and that "the support-2
world is the unit-cost objective's". No overclaim found in the referee-facing
artifacts.

## TASK 2 — verdict: (c), with one precisely-bounded (b) inside it

### (a) is refuted by the programme's own declaration
O0's 4:2 frame ratio is contrasted *by the protocol itself* with the 7:1 ratio a
T-count model implies. O0 is not a T count, and rotations — the T driver — carry
weight 0.

### (b) in its strong form is refuted by executed machine evidence
`QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json`, `outcome_overall: MIXED`:

- **O1 (T-count-weighted): `GEOMETRY_OBJECTIVE_DEPENDENT`.**
  - 7752 / 9261 structured instances (83.7%) change regime
    (DONOR_EXACT->BORROW 6014, SPLIT->BORROW 1738).
  - Chemistry inverts: donor-exact on **0 of 30** matchings (O0: 30/30).
  - Two-trade identity fails on 4484 instances (`NEW_BEYOND_TWO_TRADES`).
  - The R6S support-2 sufficiency **theorem fails** (`NEW_SUPPORT3`, 53
    criticals; witness C_DP 11 < C_D++ 13).
  - Membership predicate P1: 327 errors; re-induction still leaves 273 ->
    `OBJECTIVE_SPECIFIC`.
- **O2: `GEOMETRY_ROBUST`** — but O2 differs from O0 only by adding rho*rotations
  with rotations frozen at the constant 9, i.e. O0 + 45. Its robustness is a
  constant-shift lemma, not evidence.

Since the argmin moves for 83.7% of instances under a plausible reweighting,
ordinal alignment with a physical resource fails. (b) does not hold in general.

### What DOES hold — the QG-39 regret number specifically (new computation)
Recomputed from the same primitives QG-39 consumed (my rebuild is byte-identical
to the cached `K`, 715x384, and the decomposition below is exact on all 274,560
(type, probe) pairs):

- **The frame term is identically 18** at n=1 — all six frame Paulis are
  weight-1 by construction of the probe family — so `-18` annihilates it *for
  every weight vector*. The frame coefficients (4, 2), which are what the entire
  surrounding R6 chain is about, contribute **nothing** to QG-39.
- **The Tag weight w(S) is identically 1** across all 48 accepted (frame, Tag)
  probes, so the Tag term is the constant `t_tag` and cancels in every difference.
- Therefore **K = t_tag + t_r * dF3**, an affine function of ONE structural
  count: `dF3` in [-5, 5], the factored-Restore support relative to the unframed
  target. (O1 is exactly `K_O1 = 3*K_O0 - 2`.)

**These invariances are entailed, not discovered.** With a single varying
coordinate and `t_r > 0`, `K` is a positive-affine image of `dF3`; positive-affine
maps preserve argmin, preserve the induced partition, and scale differences by
`t_r`. The table below is therefore a *consistency check on that collapse*, run
over the weight sweep {(2,1),(4,3),(0,1),(20,1),(7,1),(2,5),(2,10),(1,1),(100,7)},
not independent robustness evidence:

| invariant | result |
|---|---|
| budget-0 worst-case regret | **exactly 5 * t_r** in every case |
| optimal-frame sets | **0 / 715 types change**, every weighting |
| spectrum partition (the compiler's summary) | invariant (analytic: bulk is weight-free, spectrum is an affine image); 54 spectra computed |
| budget-to-zero depth | **3**, invariant |
| regret / spread of optima | **5/7 = 0.714**, invariant |
| t_r = 0 (limiting case) | K constant, **regret 0**, partition collapses |

So QG-39 is a **one-coordinate result**. Its ordinal content is
weight-invariant *within this single-qubit probe family*, by the affine collapse
above — this says nothing about the n>=2 setting, where QG-2 shows the ordinal
content does not survive. Its magnitude is exactly proportional to `t_r`, whose
unmeasured span is:

- `t_r = 1` — stipulated in the committed objective O0;
- `t_r = 3` — declared in the programme's own T-count model O1;
- `t_r = 0` — the limiting case if Restore Paulis are absorbed into the classical
  Pauli frame at no cost. **The programme's own O1 rationale rejects this**
  (Restore Paulis "must be commuted through a non-Clifford layer"), so it is a
  bound on the span, not a claim that the result is vacuous.

Across that declared span the regret figure is 5, 15, or 0. The spread is the
point: nothing in the construction fixes which.

**Verdict (c)**, sharpened: the coordinates are physically *named* and
physically meaningful — frame support, Tag checks, Restore/Pauli-frame
corrections, rotations — but the **exchange rates between them are stipulated,
not measured**, and the programme has machine-checked that a plausible
alternative set of rates inverts its own conclusions. Calibration is not
achievable by further work inside this construction; it would require an
external circuit-level compilation and measurement that does not exist here.

Residual caveat, stated not buried: QG-34/39 pins `centrals = (0,0,0)` and n=1,
whereas the referee DP optimizes over all eight central configurations.

## TASK 3 — not attempted, because Task 2 returned (c)

Producing a T-count or CNOT figure would require inventing precisely the
conversion factor (`t_r`, physical cost of one Restore-layer single-qubit Pauli)
that Task 2 shows is unmeasured, and whose declared span (1 stipulated, 3 in the
programme's own T-model, 0 in the rejected free-Pauli-frame limit) spans a factor
of three even before the limiting case. Any such number would be manufactured,
not estimated.

What can be said without inventing anything: the regret is **5 single-qubit
Pauli letters in the factored Restore layer, per column type selected**. That is
a real countable quantity. Multiplying it by a per-column count and by a
physical price per Restore Pauli is the step that has no support.

## TASK 4 — the sentence

> Costs are reported in the frozen support-count objective's own units — a
> role-weighted tally of Pauli support with stipulated weights (4, 2, 2, 1) over
> frame, shared-Tag and factored-Restore coordinates, rotations priced at zero —
> and these are not counts of any physical resource: the selection-regret figure
> reduces exactly to `t_r x 5` factored-Restore Pauli letters, the frame
> coordinate being identically constant on the single-qubit probe family, and
> under the T-count reweighting the programme itself declared, 83.7% of instances
> change regime and chemistry donor-exactness falls from 30/30 to 0/30.

Scope note for whoever places it: the ordinal invariance established here holds
*within the single-qubit probe family* and is entailed by that family having one
varying coordinate. It must not be quoted as general ordinal robustness — QG-2
shows the opposite at n>=2.
