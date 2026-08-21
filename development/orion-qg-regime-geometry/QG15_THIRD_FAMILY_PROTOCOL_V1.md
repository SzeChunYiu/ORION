# QG-15 third-family instance protocol V1 — StabPrep: stabilizer-state preparation / Clifford synthesis regime geometry

Date: 2026-08-21
Parent programme: ORION-QG (PROGRAMME_CHARTER_V1.md, issue #740), template-transfer lane
QG-15 (third instance; predecessors: TARE wave-1 chain R6N..R6S, SixLCU QG-4 upgraded by
QG-12). Branch: `claude/orion-harness-verification-b17qdj`, base `40e0160f`.
Status: FROZEN BEFORE ANY QG-15 OUTCOME. No instance of any verification domain below has
been evaluated under this family or cost model before this freeze. The analytic
derivations recorded below (donor well-definedness, lower-bound validity, conjugation
tables) are consequences of the frozen model only — no instance data was computed.
Authority ceiling: development/research registration of a template-transfer test; NOT_R6;
no novelty credit, no donor credit, no new subject data, no network access. The protected
stretched-N2 subject is never read. Runtime cap: < 25 minutes per analyzer run (double
run < 50 minutes); all caps disclosed in section 8.

## 1. Scientific question

Two materially different compilation families (TARE Tag/Restore; SixLCU PREP/SELECT)
have instantiated the full five-component regime-geometry template. QG-15 is the third
transfer: a stabilizer-circuit synthesis family over F2 symplectic machinery — circuit
compilation proper (weighted gate synthesis against an exact shortest-path referee),
with no Tag/Restore structure and no PREP/SELECT structure. Success is the template
transferring; a component failure localizes what was family-specific. Either outcome is
first-class. Secondary question: do the wave-2 motifs ("exchange-refuted-at-
characterizable-column -> trade currency -> closed-form predicate", "boundary-is-low-
order") appear a third time?

## 2. The frozen third family: "StabPrep"

### 2.1 Instances

An instance is an n-qubit stabilizer state, n in {1,2,3} for the exhaustive domains and
n = 4 for the prospective panel. Canonical representation: the full stabilizer group of
2^n signed Pauli elements. A Pauli element is encoded as the integer
`e = (s << 2n) | (x << n) | z` with sign bit `s` (phase (-1)^s; stabilizer groups of
states carry real signs only), X-bitmask `x`, Z-bitmask `z` (qubit q's letter is
I/X/Y/Z as (x_q,z_q) = 00/10/11/01). Canonical state key = the sorted tuple of the 2^n
element encodings. The exhaustive domain at each n <= 3 is the complete set of
stabilizer states (counts must equal `2^n * prod_{k=1..n} (2^k + 1)` = 6, 60, 1080),
enumerated in canonical-key ascending order; this exceeds the lane brief's "structured
n=3 slice" (the full n=3 space is taken). Start state |0..0> has group
{(s=0, x=0, z=m) : m in [0, 2^n)}.

### 2.2 Gate set and frozen costs

`H(q)` cost 1, `S(q)` cost 1, `SDG(q)` cost 1, `CNOT(c,t)` (ordered pair, c != t) cost 3.
Frozen gate enumeration order at each n: H(0..n-1), S(0..n-1), SDG(0..n-1), CNOT over
ordered pairs in lexicographic (c,t) order. Conjugation tableau rules (frozen; s,x,z
bits at the acted qubits, primes = new values):

- H(q): swap x_q,z_q; s ^= x_q & z_q.
- S(q): z_q ^= x_q; s ^= x_q & z_q(old).
- SDG(q): z_q ^= x_q; s ^= x_q & ~z_q(old).
- CNOT(c,t): x_t ^= x_c; z_c ^= z_t; s ^= x_c & z_t & (x_t(old) ^ z_c(old) ^ 1).

Applying a gate to a state conjugates every group element and re-sorts.

### 2.3 Exact referee (the family optimum)

`C_opt(psi)` = the cost of a minimum-cost circuit over the frozen gate set preparing psi
from |0..0>, computed exactly by Dijkstra (uniform-cost search) over the full
stabilizer-state graph at each n, edge weights = gate costs. This is exact by
construction (shortest path); its ground truth is independently gated (G2). An optimal
witness circuit is extracted deterministically by backward walk: from state s, over
gates in frozen enumeration order, take the first g with
`dist[apply(inv(g), s)] + cost(g) == dist[s]`; recurse to the start.

### 2.4 Donor family D (frozen greedy echelon synthesis, "GE")

The donor emits a disentangling circuit driving psi to |0..0>, qubit by qubit in
ascending order q = 0..n-1, then returns the reversed inverse gate list as the
preparation circuit (inverses: H->H, S->SDG, SDG->S, CNOT->CNOT; costs preserved).
"Processed" qubits are those already completed; all candidate filters require identity
(x and z bits zero) on processed qubits. Micro-steps at qubit q, on the current group:

X-branch (taken iff the X-candidate set {elements with x_q = 1, identity on processed}
is nonempty): pivot = the candidate minimizing the key (x, z, s) lexicographically
(integers). Track the pivot through every emitted conjugation. Then, in this frozen
order:
  (a) if pivot letter at q is Y: emit S(q).
  (b) for j != q ascending (unprocessed): if letter(j) = Y: emit S(j); then if
      letter(j) = X: emit CNOT(q,j); else if letter(j) = Z: emit H(j), CNOT(q,j), H(j)
      (the CZ-composite, cost 5).
  (c) pivot is now +-X_q (asserted); if sign is -: emit S(q), S(q).
  (d) emit H(q); pivot is now +Z_q (asserted).

Z-fallback (X-candidate set empty): the group then contains +-Z_q exactly (proof: the
group's symplectic span L is Lagrangian; if every element has x_q = 0 then the vector
of Z_q is symplectically orthogonal to L, hence in L^perp = L, so the element with that
vector — support exactly {q} — is in the group with some sign). If its sign is -: emit
H(q), S(q), S(q), H(q) (cost 4). Else emit nothing.

After all qubits: the group must equal the |0..0> group with all + signs (asserted:
once +Z_q is in the group for every q, closure forces all signs +). Donor cost
`C_D` = sum of emitted gate costs. Donor validity is a hard gate: replaying the
returned preparation circuit on |0..0> must reproduce the instance's canonical key
exactly (G3); hence `C_opt <= C_D` always.

Donor trace features (frozen; structure-only, no referee call):
`nCZ` = count of step-(b) Z-letter clears (CZ-composites); `nY` = count of S emissions
for Y letters (steps a+b); `nSignX` = count of step-(c) sign fixes; `nSignZ` = count of
Z-fallback sign fixes; `nCN` = count of emitted CNOTs; and `C_D` itself.

### 2.5 Structural invariants and the frozen lower bound

- `r_X(psi)` = F2 rank of the set of x-vectors of all group elements. Pre-outcome
  derivation: r_X(|0..0>) = 0; S and SDG preserve every element's x-vector; CNOT maps
  x-vectors by an invertible linear map (rank-invariant); H(q) swaps one coordinate
  pair and changes the projection rank by at most 1. Hence every preparation circuit
  contains at least r_X Hadamards.
- `c(psi)` = number of tensor factors: qubit subsets S are "product cuts" iff the
  subgroup supported inside S has rank |S| and the complement subgroup rank n-|S|
  (checked over all 2^n subsets); c = number of atoms of the partition generated by
  all product cuts. Every preparation circuit contains at least n - c CNOTs (a
  two-qubit gate merges at most two tensor factors; single-qubit gates preserve the
  factorization).
- Frozen lower bound: `LB(psi) = r_X + 3*(n - c)`. Validity `LB <= C_opt` is
  derived above and additionally machine-gated on every instance of every domain (G5).

## 3. The five template components (all prespecified; every honest outcome first-class)

### 3.1 Component 1 — regime map (donor-optimal region)

On each exhaustive domain n = 1, 2, 3: census of `gap = C_D - C_opt`; donor-exact
region = {gap = 0}; report per-n instance counts, donor-exact counts and fractions,
the full gap histogram, and the cross-tabulation of gap>0 against (r_X, c).
Outcome space: `REGIME_MAP_COMPLETE` (always, unless a gate aborts).

### 3.2 Component 2 — elementary trades (minimal witnesses)

Trade := instance with gap > 0. Trade classes are defined by the sufficiency ladder of
3.3: class(psi) = minimal level j >= 1 with `C_Ej(psi) == C_opt(psi)`, labeled
1 = ORDER_TRADE (adaptive qubit reordering recovers optimality),
2 = PIVOT_TRADE (+ pivot-generator choice needed),
3 = ROUTE_TRADE (+ X/Z elimination-route choice needed),
4 = GLOBAL_TRADE (no schedule variant recovers it; genuinely outside the
row-reduction family). Report per-n class census; serialize verbatim, per n and per
class, the minimal witness (smallest n, then smallest C_opt, then canonical key order):
canonical key, all 2^n Pauli strings, C_D, C_opt, gap, C_E1..C_E3, donor circuit,
extracted optimal circuit, donor trace features. Also the first 20 trade rows per n in
canonical order (cap disclosed). Every serialized witness is recomputed from its
serialized state alone through donor + referee + circuit replay (G6).
Outcome space: `TRADES_FOUND` (counts + witnesses) / `NO_TRADES` (donor absorption).

### 3.3 Component 3 — sufficiency bound (schedule closure)

Frozen nested ladder of schedule enlargements of the donor (all members are complete
synthesis schedules; every evaluated variant is a valid circuit):

- `E0` = the frozen donor (ascending qubit order, min-key pivot, X-route).
- `E1` = adaptive qubit order (branch over which unprocessed qubit to process next);
  pivot and route rules as E0.
- `E2` = E1 + pivot freedom (branch over every X-candidate; Z-fallback as E0 when the
  X-candidate set is empty).
- `E3` = E2 + route freedom: at each qubit step additionally branch over the Z-route,
  defined frozen as the H-dual schedule: candidates = elements with z_q = 1 (identity
  on processed); micro-steps (i) if letter(q) = Y: emit S(q), H(q); (ii) for j != q
  ascending: letter Y: emit S(j), H(j), CNOT(j,q); letter X: emit H(j), CNOT(j,q),
  H(j); letter Z: emit CNOT(j,q); (iii) pivot now +-Z_q (asserted); if sign -: emit
  H(q), S(q), S(q), H(q); (iv) no final H. (The E0 Z-fallback is the Z-route with
  pivot forced to +-Z_q.)
- `E4` = the full circuit space (the referee).

`C_Ej(psi)` = minimum emitted cost over the level's schedule tree (memoized exact
search; deterministic tie-break: minimal (cost, gate-tuple) with branches explored in
ascending qubit / route X-before-Z / pivot key order). Hard nesting gate G4:
`C_E0 = C_D >= C_E1 >= C_E2 >= C_E3 >= C_E4 = C_opt` on every n <= 3 instance, and the
argmin circuit at every level replays to the instance.

Primary verdict: minimal j with `C_Ej == C_opt` on every instance of every exhaustive
domain; outcome `CLOSED_AT_LEVEL_j` or `NO_STRICT_SUBEXTENSION_CLOSES` (only E4
closes; the GLOBAL_TRADE census then delimits the residue). Per-level residual counts
reported per n.

Secondary axis (budget bounds, the support-bound analogue): by lexicographic-cost
Dijkstra compute per state the minimum H-count (resp. S+SDG-count, CNOT-count) among
cost-optimal circuits; report `h*(n)`, `s*(n)`, `c*(n)` = the maxima over each domain,
and the count of states whose minimal optimal H-count exceeds r_X (sharpness of the
H-rank bound: if 0, "r_X Hadamards suffice" is machine-checked on the complete domain).

Exchange argument on the complete local domain (n = 1, all 6 states): enumerate all
1093 words of length <= 6 over {H,S,SDG}; machine-check (i) brute minimum equals the
referee on every state (also G2's n=1 arm), and (ii) the frozen normal form
NF1 = {words with <= 2 H's, no adjacent HH, no adjacent S,SDG or SDG,S pair, no S- or
SDG-run longer than 2} achieves the referee optimum on every state. Outcome:
`EXCHANGE_NF1_HOLDS` / `EXCHANGE_NF1_REFUTED` (either first-class).

### 3.4 Component 4 — membership predicate (donor-exact region, no referee call)

Target label: `donor_exact := (C_opt == C_D)`. All features are computable from the
instance's group structure alone (donor trace features are deterministic functions of
the tableau; the referee is never called). Frozen literal list (index order):

L0: nCZ == 0; L1: nSignX == 0; L2: nSignZ == 0; L3: nY == 0; L4: C_D == LB;
L5: C_D <= LB + 1; L6: r_X <= 1; L7: c == n; L8: nCN <= n - 1; L9: C_D <= 2n.

Frozen predicate ladder, evaluated in this order on the fit domain = exhaustive n = 3
(1080 instances):

- `P0`: L0 (nCZ == 0).
- `P1`: L0 AND L1 AND L2.
- `P2`: L4 (C_D == LB; certified-sufficient direction by construction).
- `P3`: best conjunction of 1..3 distinct literals from L0..L9, ranked by (training
  error, size, lexicographic index tuple).

Selection rule: the first of P0, P1, P2 with zero training error on the fit domain;
else the best P3. Confusion matrices (TP/FP/FN/TN, positives = donor_exact) reported
for the selected predicate — and for P0, P1, P2 regardless — on every panel:
n = 1 (6), n = 2 (60) (declared reuse: refereed in components 1–2), n = 3 (fit), and
the held-out n = 4 prospective panel of 3.5 (fresh; labeled only after selection and
after the prospective stamp).
Outcome space: `EXACT_PREDICATE_FOUND_P0/P1` / `EXACT_BY_LOWER_BOUND_ONLY (P2)` /
`EXACT_PREDICATE_FOUND_P3` / `SUFFICIENT_CONDITION_ONLY` (zero false positives
everywhere, coverage reported) / `NO_CLEAN_PREDICATE` (matrices verbatim) /
`FAMILY_CLOSURE` (if component 2 found no trades, constant TRUE is exact).

### 3.5 Component 5 — prospective forecast (digest-stamped before referee)

Held-out panel: n = 4, seed 20260821, `numpy.random.default_rng(20260821)`; repeat
until 120 distinct states: apply to |0000> a circuit of 24 gates, each drawn as
kind = rng.integers(0,4) (0:H, 1:S, 2:SDG, 3:CNOT); for kinds 0-2 the qubit is
rng.integers(0,4); for CNOT, c = rng.integers(0,4) and t = the u-th qubit != c with
u = rng.integers(0,3); dedupe by canonical key, keep first occurrences in draw order.

Frozen forecast rule (fixed by fit-domain data before the panel referee runs):
predicted regime = selected predicate's verdict; predicted gap = 0 if predicate-true,
else the mode (ties -> smallest) of observed n=3 gaps among fit instances with the
same key `(nCZ, nSignX, nSignZ, nY)`, defaulting to 0 for unseen keys; predicted
`C_opt = max(LB, C_D - predicted gap)`.

Prospective discipline (enforced in code order): all 120 predictions are serialized
(canonical JSON: panel index, canonical key, C_D, LB, features, predicted regime,
predicted C_opt), their sha256 is computed and printed to stdout as the FIRST receipt
line `ORIONQG_QG15_PROSPECTIVE_PREDICTIONS_SHA256=...` BEFORE the n = 4 referee
(Dijkstra) is invoked; the n = 4 referee runs only after the stamp. Then: regime
confirmations/refutations and exact-cost confirmations/refutations counted; up to 20
refutation witnesses serialized verbatim. Outcomes (each axis separate, refutation
first-class): `REGIME_FORECAST_EXACT` / `REGIME_FORECAST_REFUTED(counts)` and
`COST_FORECAST_EXACT` / `COST_FORECAST_REFUTED(counts)`.

## 4. Prespecified hostile gates

- G1 `state_space_ground_truth`: reachable-state counts equal 2^n prod(2^k+1)
  (6/60/1080; 36720 at n=4 when computed); exhaustive enumeration in canonical order
  with first/last key and enumeration sha256 recorded.
- G2 `independent_brute_agreement`: n=1 referee equals exhaustive word enumeration
  (all 1093 words, complete because max referee distance is asserted < 6); n=2 referee
  equals an independent Bellman-Ford fixpoint relaxation over the complete 60-state
  space. Complete sub-domain agreement, no sampling.
- G3 `donor_validity`: on every instance of every domain (n=4 panel included) the
  donor preparation circuit replays to the instance's canonical key and C_opt <= C_D
  (n <= 3 and panel, where referee values exist).
- G4 `ladder_nesting_and_replay`: C_E0 >= C_E1 >= C_E2 >= C_E3 >= C_opt on every
  n <= 3 instance; every per-level argmin circuit replays to its instance at the
  recorded cost.
- G5 `lower_bound_validity`: LB <= C_opt on every instance with a referee value.
- G6 `witness_recompute`: every serialized witness recomputed from its serialized
  canonical key alone: donor rerun (C_D match), referee lookup (C_opt match), donor
  and optimal circuits replayed (preparation and cost match).
- G7 `predicate_discipline`: selection by the frozen rule on the fit domain only;
  features referee-free; all confusion matrices reported on all panels, none omitted.
- G8 `prospective_discipline`: the predictions sha256 is computed and printed before
  the n=4 referee call (code-structural: the referee-n4 function is first invoked
  after the stamp; the RESULTS records the stamp and the panel definition digest).
- G9 `determinism`: no wall-clock content in stdout receipt lines or in any
  digest-covered RESULTS field (timing lives in the RESULTS `timing` key, excluded
  from the result digest, and in stderr); a double run must produce byte-identical
  stdout and byte-identical RESULTS-minus-timing.
- G10 `no_new_subject_data_no_network`: no chemistry source read, no network access,
  protected stretched-N2 never read, no existing file modified.

Any integrity failure aborts nonzero with the failing assertion; no authority string
is emitted.

## 5. Terminals (the lane's headline, decided by component executability)

- `TEMPLATE_TRANSFERRED`: all five components instantiate and complete with receipts
  under their honest outcome spaces — whatever the science says.
- `TEMPLATE_PARTIAL__<COMPONENT>_FAILED`: a named component cannot be posed or cannot
  be decided on the frozen domains; the receipt states which and why.
- `CANNOT_CHECK`: infrastructure failure (gate abort, referee disagreement).

Authority string:
`ORION_QG15_THIRD_FAMILY_<TERMINAL>__STABPREP_CLIFFORD_SYNTHESIS_REGIME_GEOMETRY_ON_VERIFIED_DOMAINS__NOT_R6`.

## 6. Claim boundary (must be restated in the receipt)

The claim covers exactly the frozen StabPrep family: stabilizer-state preparation from
|0..0> over the gate set {H, S, SDG, CNOT} with frozen costs (1,1,1,3), the frozen GE
donor and its E1-E3 schedule enlargements, and the frozen structural lower bound. All
censuses, trade catalogues, sufficiency verdicts, predicates, and forecasts are
machine-evidenced only on the stated finite domains (exhaustive n <= 3; one seeded
n = 4 panel); nothing is a theorem for all n, for other gate costs or gate sets, for
mixed stabilizer codes, or for measurement-assisted preparation. The referee optimum
is the shortest-path cost in the frozen metric — no physical-runtime or
quantum-advantage claim. The donor is a standard Gaussian-elimination-style synthesis
and earns no novelty credit; the ladder is bookkeeping over frozen schedule axes. The
template itself is the object under test. NOT_R6. No new subject data; the protected
stretched-N2 subject is untouched.

## 7. Independent generic verification (frozen scope)

`development/orion-qg-regime-geometry/qg15_generic_verify.py` — a pure-primitive
rebuild importing nothing from the analyzer: its own tableau representation, its own
uniform-cost referee, its own donor implementation written from this protocol text.
It must: recompute the n = 1..3 state spaces and referee tables; recompute the full
donor censuses and gap histograms and compare to RESULTS; recompute r_X, c, LB and
the G5 check; re-verify every serialized witness (donor, referee, circuit replays);
recompute all predicate confusion matrices on n = 1..3 from RESULTS' selected
definition; regenerate the n = 4 panel from the seed, recompute predictions under the
frozen forecast rule with RESULTS' fit-derived gap table, re-verify the predictions
sha256, run its own n = 4 referee, and recompute the confirmation counts; verify the
result digest. Ladder values are verified through the serialized witnesses' recorded
per-level costs and argmin replays (full ladder recomputation is out of verifier
scope, disclosed). Prints exactly one token line
`ORIONQG_QG15_GENERIC_VERIFY={"decision":"ACCEPT"|"REJECT",...}`.

## 8. Runtime, caps, outputs

Runtime cap < 25 min per analyzer run (scratchpad venv python, stdlib + numpy only;
numpy used solely for the seeded panel rng). Disclosed caps: serialized trade rows
capped at 20 per n; refutation witnesses capped at 20; minimal witnesses one per
(n, class); panel size 120; witness optimal-circuit extraction returns one
deterministic optimum (not all optima). Outputs (only these four files are added; no
existing file is modified):

- stdout line 1: `ORIONQG_QG15_PROSPECTIVE_PREDICTIONS_SHA256=<hex>`;
  stdout line 2: `ORIONQG_QG15_THIRD_FAMILY=<canonical sorted compact JSON receipt>`.
- `research/extensions/orion-qg/QG15_THIRD_FAMILY_RESULTS.json` (pretty, sorted keys;
  byte-identical across runs after removing the `timing` key).
- `research/extensions/orion-qg/qg15_third_family.py` (the analyzer),
  `development/orion-qg-regime-geometry/qg15_generic_verify.py` (the verifier),
  this protocol.
- stderr: runtime seconds per stage (the only non-deterministic output).
