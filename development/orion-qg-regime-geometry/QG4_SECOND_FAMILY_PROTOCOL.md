# QG-4 second-family instance protocol — six-term Pauli LCU PREP/SELECT compilation

Date: 2026-08-21
Parent programme: ORION-QG (PROGRAMME_CHARTER_V1.md, issue #740), lane QG-4.
Template source: the TARE instance MAX_R6N (dominance audit) -> MAX_R6O (trade
discovery) -> MAX_R6P (sufficiency closure) -> MAX_R6Q (predicate), receipts
committed under research/extensions/orion-q/.
Branch: claude/orion-harness-verification-b17qdj.
Status: FROZEN BEFORE ANY QG-4 OUTCOME. No instance of any verification domain
below has been evaluated under this family or cost model before this freeze;
the analytic derivations recorded below are consequences of the frozen cost
model only (no instance data).
Authority ceiling: development/research registration of a template-transfer
test; not R6, no novelty credit, no donor credit, no new subject data. The
protected stretched-N2 subject is never read. No network access is used: all
domains are synthetic with frozen seeds; the committed open chemistry batches
are declared OUT OF SCOPE for this lane run (their loader requires a source
fetch; the lane is executed fully offline).

## 1. Scientific question

The TARE chain produced a complete regime geometry for one compilation family.
QG-4 is the field-defining transfer test: apply the identical four-stage
template (dominance audit -> trade search -> sufficiency closure -> membership
predicate) to a materially different compilation family. Success is the
template transferring (all four stages instantiate with receipts, whatever the
science says); failure localizes what was TARE-specific. Both outcomes are
first-class.

## 2. The frozen second family: "SixLCU"

### 2.1 Instances

An instance is a batch of six formal LCU terms `T = (t_1..t_6)`, each a
non-identity Pauli on `n` system qubits, `n in {1,2,3}` for the synthetic
domains. Letters are coded `0=I, 1=X, 2=Y, 3=Z`; a term is the integer code
`p in [1, 4^n)` with letter at qubit `q` equal to `(p >> 2q) & 3`. Repeated
terms are allowed (the batch is formal; see the donor-refusal clause in 2.6).
Coefficients are outside the frozen objective: the cost model is purely
structural (support / node counts), so amplitudes never enter and the run is
exactly deterministic. Instance cost is invariant under term reordering
(machine-checked, gate G5); exhaustive domains therefore enumerate canonical
nondecreasing 6-tuples.

### 2.2 Compilation family F (the unrestricted family)

A member is a triple `(G, phi, a)`:

- `G`: a set partition of `{1..6}` into `k` blocks (203 set partitions;
  canonical enumeration: restricted-growth-string lexicographic order; blocks
  listed by ascending minimum element, elements ascending). Grouping fixes the
  frozen hybrid coefficient-register encoding: one flag qubit per block
  (one-hot across blocks) when `k >= 2`, no flag layer when `k = 1`; within a
  block of size `m`, `b(m) = ceil(log2 m)` binary index bits
  (`b(1)=0, b(2)=1, b(3)=b(4)=2, b(5)=b(6)=3`).
- `phi_g in {0,1}` per block: whether the block's common Pauli factor is
  extracted in SELECT (see 2.4).
- `a in {shared, dedicated}`: the ancilla-reuse assignment for the index bits
  (one common reusable pool sized by the largest block, vs a dedicated
  register per block).

The pure unary encoding is `G` = six singletons; the pure binary encoding is
`G` = one block of six; every other `G` is a frozen hybrid grouping.

### 2.3 Common factor and residuals (support semantics)

For block `g` with `m = |g|`: `F_g[q] = v` if every `i in g` has
`t_i[q] = v != I`, else `F_g[q] = I`. Residual `r_i[q] = I` where
`F_g[q] != I`, else `t_i[q]` (this equals the Pauli product `t_i * F_g` up to
phase, and exactly at the support level since factored columns cancel to `I`).
`wt(.)` is support count; `sum_{i in g} wt(r_i) = sum wt(t_i) - m*wt(F_g)`.

### 2.4 Frozen cost model (declared exactly; weights frozen at 1,1,1)

`C = SELECT + PREP + WIDTH`, all integers.

Controlled-Pauli cost rule: applying a Pauli of support `w` under `c`
controls costs `(c+1)*w` (fan-out ladder count: one primitive per target
letter per control-or-target layer). Rationale: this is the control-support
count for SELECT demanded by the lane brief, with the `+1` keeping an
uncontrolled layer non-free.

- `flag = 1` if `k >= 2` else `0`.
- SELECT: per block `g` (`m = |g|`, `b = b(m)`):
  - `phi_g = 0`: `sel_g = sum_{i in g} (flag + b + 1) * wt(t_i)`
  - `phi_g = 1`: `sel_g = (flag + 1) * wt(F_g)
                        + sum_{i in g} (flag + b + 1) * wt(r_i)`
  (the common factor needs only the block flag as control — or nothing when
  `k = 1`; each residual needs flag + all local index bits.)
- PREP (prep-tree node counts; node cost `1 + #controls`):
  - unary flag layer: `0` if `k = 1`, else `2k - 3` (cascade of `k-1`
    rotation nodes, the first uncontrolled, the rest singly controlled).
  - per block with `m >= 2`: canonical balanced prep tree over `m` leaves,
    split `m -> (ceil(m/2), floor(m/2))`, `m - 1` internal nodes, node at
    recursion depth `d` controlled by the block flag plus `d` tree bits:
    cost `= (m-1)*(1+flag) + ds(m)` with depth sums
    `ds(2)=0, ds(3)=1, ds(4)=2, ds(5)=4, ds(6)=6`.
- WIDTH (register qubits): flags (`k` if `k >= 2`, else `0`) plus index bits
  (`sum_g b(m_g)` if dedicated, `max_g b(m_g)` if shared).

Closed incumbent forms (analytic, from the model; asserted in-run against the
direct member evaluator on every instance): with `W = sum_i wt(t_i)`,

- Unary incumbent `U` (six singletons; `phi` irrelevant, `a` irrelevant):
  `C_U = 2W + 9 + 6 = 2W + 15`.
- Binary incumbent `B` (one block of six, `phi = 0`, standard binary-tree
  PREP/SELECT): `C_B = 4W + 11 + 3 = 4W + 14`.

`C_inc = min(C_U, C_B)`. Analytic note (recorded pre-outcome):
`C_U - C_B = 1 - 2W < 0` since `W >= 6`, so under the frozen weights the
unary incumbent is the operative donor everywhere; this is itself reported as
a finding about the frozen objective and asserted in-run.

### 2.5 Referee optimizer (exact, exhaustive)

`C_F = min over all (G, phi, a) of C`. The full sweep (all 203 partitions x
all `2^k` phi vectors x both `a`) is exact by enumeration. A fast referee
(phi = 1 on every block, `a = shared`, per-subset precomputation over the 57
non-singleton subsets) is used on large domains; its exactness rests on two
column-local dominances that Stage 1 verifies exhaustively (factoring
dominance and ancilla-share dominance, 3.1), and is additionally bound to the
full sweep by exact-equality samples: every 7th instance of domain (a), every
97th of (b), every 10th of (c) and of H2 (gate G2). Witness tie-break
(deterministic): first minimum in partition canonical order; full-sweep
binding uses phi lexicographic (block order), `shared` before `dedicated`.

### 2.6 Donor first right of refusal

Incumbent family = {U, B} exactly (the standard unary-encoding LCU and the
standard binary-tree PREP/SELECT), per the lane brief. Any trade claim must
beat `C_inc` with a serialized minimal witness. Additionally, one further
donor-owned mechanism is granted refusal rights at the *analysis* level:
collecting literally identical terms is standard Hamiltonian preprocessing
(coefficients add), so the run also computes
`C_collect = ` family optimum restricted to partitions whose non-singleton
blocks contain only identical terms (plus U, B), and reports the trade counts
both against `C_inc` (formal trades) and against
`C_inc+ = min(C_inc, C_collect)` (structural trades — the discoveries that
survive donor refusal). Both tables are receipted; the structural table is
the field-relevant one.

## 3. The four template stages (all prespecified; report each even if negative)

### 3.1 Stage 1 — dominance audit (R6N analogue)

Structural resource: encoding-register control support (the `b(m)` index-bit
controls each grouped term pays beyond the unary incumbent's single flag).

Candidate exchange inequality, frozen:

> **Claim D (index-control dominance, per column).** For every
> `m in {2..6}`, `f in {0,1}`, and column `A in {I,X,Y,Z}^m`:
> `save(A; m, f) <= surcharge(A; m, f)` where
> `save` = the exact per-column SELECT saving of factoring
> (`[sum_i (f+b+1)*1[A_i != I]] - [(f+1)*1[allEq(A)] + sum_i (f+b+1)*1[res_i != I]]`,
> `allEq(A)` = all `m` letters equal and non-identity), and
> `surcharge` = `b(m) * sum_i 1[A_i != I]` (the index-control surcharge of
> grouped SELECT over unary at that column).

If Claim D held everywhere, grouping could never strictly beat the unary
incumbent through SELECT, and — modulo the declared global gap below — the
incumbent family would be closed. Exhaustive domain:
`sum_{m=2..6} 2 * 4^m = 10,912` configurations (`f=0` is realizable only at
`k=1`, i.e. `m=6`; it is audited for all `m` as stated). Report: violation
count, every violating column class verbatim (m, f, column letters, save,
surcharge, excess), tie count (save == surcharge), and the maximum
save/surcharge ratio over columns with positive surcharge.

Auxiliary dominance facts audited on the same domains (these underwrite the
fast referee):

- **D-phi (factoring dominance, exact closed form).** For every column,
  `save(A; m, f) = 1[allEq(A)] * (m*(f+b+1) - (f+1)) >= 0`. Verified
  exhaustively per column (same 10,912 configurations).
- **D-a (ancilla-share dominance).** `WIDTH(shared) <= WIDTH(dedicated)` for
  all 203 partitions (block-size data only; exhaustive over partitions).

Declared gap (recorded pre-outcome, mirroring R6N's declared Tag gap): Claim
D bounds only the SELECT channel; grouping also moves PREP (`2k-3` plus tree
costs) and WIDTH (flag count vs shared index bits). The joint incumbent-
closure question is therefore decided at Stage 2 on finite instance domains,
never inferred from Stage 1 alone.

Honest outcome space: `LOCAL_DOMINANCE_HOLDS` (0 violations) or
`LOCAL_DOMINANCE_REFUTED` (violation catalogue = the family's local trade
currency, feeding Stage 2). Either is a valid stage instantiation.

### 3.2 Stage 2 — trade search (R6O analogue)

Exact domains (all frozen):

- (a) **Exhaustive n=1**: all `3^6 = 729` ordered tuples over `{X,Y,Z}` —
  the entire instance space at n=1.
- (b) **Exhaustive n=2**: all `C(20,6) = 38,760` canonical nondecreasing
  6-multisets over the 15 non-identity two-qubit Paulis (codes 1..15
  ascending) — the entire n=2 instance space up to reordering.
- (c) **Seeded random panel**: `numpy.random.default_rng(20260821)`; 120
  instances at n=2 then 120 at n=3; each instance six iid draws
  `int(rng.integers(1, 4**n))`, in draw order.

Per instance: `C_F` (fast referee; full-sweep binding per 2.5), `C_U`, `C_B`,
`C_collect`. Trade := `C_F < C_inc`; structural trade := `C_F < C_inc+`.
Hard per-instance assertions: `C_F <= C_collect <= C_U`, `C_F <= C_B`,
incumbent closed forms equal direct member evaluation.

Report per domain: instance count, trade count, structural-trade count, gap
histogram (`C_inc - C_F`), structural-gap histogram, witness block-shape
distribution over trade instances, and serialized minimal witnesses: the
first instance (enumeration order) achieving the minimal positive gap, the
first achieving the maximal gap, the first 20 trade rows verbatim, and the
same for structural trades. Mechanism characterization of each verbatim
witness: partition, per-block common factors, factored-column count, and the
cost ledger (SELECT/PREP/WIDTH vs the unary incumbent's).

Honest outcome space: `NO_TRADES` (incumbent/family closure: `C_F == C_inc`
everywhere — family closure evidence) or `TRADES_FOUND` (counts + witnesses).

### 3.3 Stage 3 — sufficiency closure (R6P analogue)

Frozen nested extension ladder, incumbent-anchored (`r` = number of
non-singleton blocks in a partition; `r <= 3` always):

- `E0 = {U, B}` (the incumbents).
- `E1 = E0 + {single block of six, phi = 1}` (global common-factor
  extraction only — the minimal, donor-adjacent enlargement).
- `E2 = E1 + {all partitions with r <= 1, all phi, both a}` (one merged
  group plus singletons).
- `E3 = E2 + {r <= 2}`.
- `E4 =` the full family F (`r <= 3` = all 203 partitions).

Primary verdict: the minimal `j` with `C_Ej == C_F` on every instance of
domains (a), (b), (c); per-level residual-gap counts reported. `E4` closes by
construction (hard assertion `C_E4 == C_F`). If no `j < 4` closes, the honest
outcome is `NO_STRICT_SUBEXTENSION_CLOSES` (sufficiency only at the full
family). Secondary axis (reported): the minimal max-block-size
`s in {2..6}` such that partitions with every non-singleton block of size
`<= s` (unlimited `r`) close all gaps; plus the full `(j, s)` closure matrix
(does the sub-family {r <= j, sizes <= s} tie `C_F` on all instances?).

Honest outcome space: `CLOSED_AT_LEVEL_j` (with the exact `j`, `s`) /
`NO_STRICT_SUBEXTENSION_CLOSES` / `NONE_NEEDED` (if Stage 2 found no trades,
`E0` already closes — stated as family closure).

### 3.4 Stage 4 — membership predicate (R6Q analogue)

Target label: `incumbent_exact := (C_F == C_inc)`, decided from batch
structure alone with no referee call.

Frozen closed-form features (derived analytically from the cost model before
any outcome; recorded here so the families are stated mathematical objects):
`sh(i,j) = #{q : t_i[q] = t_j[q] != I}`; for any index set `g`,
`wF(g)` = number of all-equal non-identity columns of `g`;
`sw(g) = sum_{i in g} wt(t_i)`. Single-merged-block gains vs `C_U`
(constants follow from 2.4; the in-run identity check binds each formula to
`C_U -` direct member evaluation on every 512th instance of domain (b)):

- pair `{i,j}`: `g2 = 4*sh(i,j) - wt_i - wt_j`
- triple: `g3 = 10*wF - 2*sw - 1`
- quad: `g4 = 14*wF - 2*sw - 1`
- quint: `g5 = 23*wF - 3*sw - 3`
- six (k=1, phi=1): `g6 = 23*wF - 2*W + 1`
- multi-pair width bonuses: two disjoint pairs `g2 + g2' + 1`; three
  disjoint pairs `g2 + g2' + g2'' + 2`.

Frozen predicate ladder (evaluated in this order; fit domain = the exhaustive
n=2 panel (b), 38,760 instances):

- `P0` (pairs only): `max pair g2 <= 0` AND `max two-disjoint-pair bonus
  sum <= 0` AND `max three-pair bonus sum <= 0`.
- `P1` (bounded mechanisms): `P0`'s clauses AND `g3 <= 0` for all 20 triples
  AND `g4 <= 0` for all 15 quads AND `g5 <= 0` for all 6 quints AND
  `g6 <= 0`.
- `P2` (full structural formula): `max over all 203 partitions of the
  closed-form gain <= 0`, where the closed-form gain is
  `C_U - C_closed(G)` with `C_closed` the phi=1/shared structural form of
  2.5. `P2` is exact by construction given gate G2; if only `P2` reaches
  zero error, the honest outcome is that no *bounded-mechanism* predicate
  was found.
- `P3` (fallback): the best conjunction of at most 3 literals from the
  frozen list {`[max g2 <= 0]`, `[max g2 < 0]`, `[wF({1..6}) == 0]`,
  `[max g3 <= 0]`, `[two-pair bonus <= 0]`, `[W >= 12]`,
  `[max_i wt_i == n]`, `[max_{i<j} sh(i,j) == 0]`}, ranked by (training
  error, size, lexicographic literal index).

Selection rule: the first of `P0, P1, P2` with zero training error on (b);
else the best `P3`. All confusion matrices reported regardless of selection.

Held-out panels (run only after the predicate is fixed by the selection
rule): `H1` = the Stage-2 seeded panel (seed 20260821; declared reuse,
mirroring R6Q's H1); `H2` = a FRESH panel, seed `20260825`, identical recipe
(120 at n=2 then 120 at n=3), generated and labeled only after selection;
plus the exhaustive n=1 domain (a).

Honest outcome space: `EXACT_PREDICATE_FOUND_P0` / `EXACT_PREDICATE_FOUND_P1`
(bounded-mechanism predicate, zero error on fit + all held-out) /
`EXACT_BY_FULL_FORMULA_ONLY` (`P2`) / `SUFFICIENT_CONDITION_ONLY` (zero
false positives everywhere; coverage reported) / `NO_CLEAN_PREDICATE`
(confusion matrices verbatim). If Stage 2 found no trades anywhere, the
constant predicate TRUE is exact and the outcome is `FAMILY_CLOSURE` —
stated as such.

## 4. Prespecified gates

- G1 `stage1_audit_complete`: all 10,912 column configurations plus D-phi
  and D-a domains enumerated; statuses and catalogues recorded verbatim.
- G2 `referee_soundness_and_binding`: `C_F <= C_inc` and
  `C_F <= C_collect <= C_U` on every instance; fast referee == full sweep on
  every binding sample; recorded witness costs recompute exactly through the
  direct member evaluator.
- G3 `incumbent_formula_binding`: closed forms `C_U`, `C_B` equal direct
  member evaluation on every instance of every domain.
- G4 `exhaustive_domains_complete`: exactly 729 and 38,760 instances in
  frozen canonical order (first/last instance and sha256 of the enumeration
  recorded).
- G5 `reorder_invariance`: on every 36th instance of (a) and every 512th of
  (b), the referee cost of the reversed tuple equals the canonical cost.
- G6 `ladder_nesting`: `C_E0 >= C_E1 >= C_E2 >= C_E3 >= C_E4 == C_F` on
  every instance.
- G7 `predicate_discipline`: selection by the frozen rule; H2 generated
  after selection; gain-formula identity checks pass; all confusion matrices
  reported.
- G8 `determinism`: stdout receipt line and RESULTS JSON contain no
  wall-clock field (runtime goes to stderr only); a double run must be
  byte-identical in both.
- G9 `no_new_subject_data_no_network`: no chemistry source read, no network
  access, protected stretched-N2 never read, no committed file modified.

Any integrity failure aborts nonzero with the failing assertion; no
authority string is emitted.

## 5. Transfer verdict (the lane's headline, decided by stage executability)

- `TEMPLATE_TRANSFERRED`: all four stages instantiate and complete with
  receipts under their honest outcome spaces — whatever the science says
  (trades or closure, predicate or none).
- `TEMPLATE_PARTIAL`: some stage fails to instantiate (cannot be posed or
  cannot be decided on the frozen domains); the receipt must state which
  stage and why — that localizes what was TARE-specific.

Authority string:
`ORION_QG4_SECOND_FAMILY_<VERDICT>__SIXLCU_PREP_SELECT_REGIME_GEOMETRY_ON_VERIFIED_DOMAINS__NOT_R6`
(with `<VERDICT>` in {TEMPLATE_TRANSFERRED, TEMPLATE_PARTIAL}).

## 6. Claim boundary (must be restated in the receipt)

The claim covers exactly the frozen SixLCU family: six-term Pauli batches,
the frozen hybrid one-hot/binary coefficient-register encodings indexed by
set partitions of six, phi factoring bits, shared/dedicated index-ancilla
assignments, and the frozen support/node-count objective with weights
(1,1,1) as defined in 2.4. All equalities and trade catalogues are
machine-evidenced only on the stated finite domains (exhaustive at n=1 and
n=2, seeded panels at n=2..3); nothing is a theorem for all n or for other
weights, cost rules, term counts, or encodings (qubitization walk operators,
coherent alias sampling, and amplitude-dependent PREP costs are all out of
scope). The incumbents are donor-owned; identical-term collection is
donor-owned preprocessing and is given refusal rights via `C_inc+`; the
hybrid-grouping enlargement is bookkeeping over the frozen encoding axes and
earns no novelty credit. The template itself (stages, gate discipline,
receipt shapes) is the object under test. Not R6. No new subject data; the
protected stretched-N2 subject is untouched.

## 7. Runtime and outputs

Single run under 15 minutes with the session venv python (stdlib + numpy
only); the determinism double run stays under 30 minutes total. Outputs:

- stdout: `ORIONQ_QG4_SECOND_FAMILY=<canonical sorted JSON receipt>`.
- research/extensions/orion-qg/QG4_SECOND_FAMILY_RESULTS.json (pretty,
  sorted keys; byte-identical across runs).
- stderr: runtime seconds (the only non-deterministic output).
- No existing file is modified; only this protocol, the script
  research/extensions/orion-qg/qg4_second_family.py, and the RESULTS file
  are added.
