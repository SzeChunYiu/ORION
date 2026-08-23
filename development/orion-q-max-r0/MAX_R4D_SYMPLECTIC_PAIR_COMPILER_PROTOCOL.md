# ORION-Q MAX-R4D exact symplectic TARE pair compiler protocol

Date: 2026-08-20
Parent: #698 / #679
Status: frozen before untouched H2O Pauli-transform outcome.

## Question
Can an exact compiler for two-term TARE blocks jointly reduce subnormalization and TARE-specific implementation structure compared with coefficient-only pairing, while preserving a non-compensatory resource vector?

## Exact local identities
For a two-term block with magnitudes x,y:

- Pauli-LCU norm = x+y.
- TARE block normalization = sqrt(2)*sqrt(x^2+y^2).
- Relative TARE normalization factor = sqrt(1+CV(x,y)^2).

This is independent of Pauli labels; labels only affect implementation structure.

## Pair representation search
For target Pauli strings P0,P1 on n qubits, optimize auxiliary anti-commuting Pauli strings R0,R1 and tag S satisfying the m=2 TARE algebraic contract:

- R0 and R1 anticommute;
- S commutes with R0;
- S anticommutes with R1;
- T0 = P0*R0 and T1 = P1*R1 are valid Pauli strings up to phase;
- all algebra is checked in binary symplectic representation.

The implementation may use an exact finite-state dynamic program rather than brute-force enumeration: the three commutation conditions are three global parity bits and the support/resource cost is additive over qubits. Exactness is required for the registered local objective.

For every admissible representation record a vector, never one scalar:

1. `lambda_pair = sqrt(2)*sqrt(x^2+y^2)`;
2. `uanti_rotation_count = 3` for m=2;
3. `uanti_entangler_proxy` from the registered standard m=2 Uanti Pauli-exponential support model;
4. `tag_restore_control_factor = wt(S)+wt(T0)+wt(T1)`;
5. `ancilla = 1`;
6. `direct_unitary = true` only if original P0,P1 anticommute, in which case no TARE tag/restore is needed for the normalized linear combination block;
7. explicit Pauli/symplectic receipts.

The compiler returns the local Pareto set under `(lambda_pair, uanti_entangler_proxy, tag_restore_control_factor, ancilla)`.

## Global partition
For an even term count, choose a perfect matching of target Pauli terms. Global coordinates:

- `Lambda = sum lambda_pair`;
- `E = sum uanti_entangler_proxy`;
- `C = sum tag_restore_control_factor`;
- `D = number direct_unitary pairs`;
- ancilla peak under outer sequential-composition assumption;
- exact source-term reconstruction.

### Frozen odd-parity rule
If the nonidentity Pauli-term count is odd, leave exactly the **smallest-magnitude** term as a singleton unitary block. It contributes `|a|` to `Lambda`, requires no TARE Tag/Restore correction, and is excluded from the pair matching. This rule is fixed before observing the H2O Pauli-term count and cannot improve the paired normalization theorem.

No arbitrary scalar objective may define scientific superiority. Report the Pareto frontier and dominance relationships.

## Scalable global compiler
The coefficient-only optimum is exact and scalable. Structure-aware search may use theorem-bounded local rematching rather than an all-pairs dense matching on large Hamiltonians:

1. sort terms by coefficient magnitude;
2. adjacent pairing gives the exact `Lambda` lower bound;
3. partition the sorted sequence into fixed local windows/quartets independent of Pauli labels;
4. enumerate all pairings inside each local window;
5. compute exact local TARE representation cost for each candidate pair;
6. combine local nondominated choices under explicit normalization-overhead gates.

This produces a constructive Pareto subset; it must never be called the globally minimal implementation-cost matching unless independently proved.

## Theorem-coordinate baseline
Coefficient-only optimum is fixed by the previously frozen majorization theorem: sort coefficient magnitudes and pair adjacent magnitudes. This gives the global minimum possible `Lambda` among all pair partitions.

The structure-aware compiler may trade normalization for lower `E`/`C` but may never claim normalization below that theorem bound.

## Development evidence (not confirmation)
On H2, exact m=2 representation search exposed points reducing a logical Pauli/control-factor metric from 42 to 37 at ~0.235% normalization increase and to 35 at ~3.59% increase. H2 and LiH are development subjects only.

## Fresh confirmation subject
Use the locked public H2O DUCC Hamiltonian source:

- repository: `npbauman/DUCC-Hamiltonian-Library`;
- repository commit: `be306f5830549304176365750d712093950bbdde`;
- raw DUCC integral blob: `5f157e7bd05aac26b30b10dcea44b7650b7f8648`;
- active space fixed by repository output: 5 occupied + 5 virtual spatial orbitals (20 spin orbitals);
- mapping fixed prospectively: repository extractor semantics followed by Jordan-Wigner, no tapering/truncation chosen after outcome;
- identity term excluded from TARE partition comparison, consistently across all arms.

Primary R4D confirmation is vectorial:

- exact semantic reconstruction must pass;
- coefficient optimum must be reproduced as the `Lambda` lower bound;
- the structure-aware frontier must contain at least one point that is **strictly Pareto-better in implementation coordinates** than the coefficient-optimal representation at no more than 5% normalization overhead;
- and at least one point with <=1% normalization overhead and >=5% reduction in either `E` or `C` relative to the coefficient-optimal representation, unless that coordinate is already zero;
- report negative if either gate fails.

The 5%/1% gates were frozen from H2 development before H2O Pauli-transform outcome.

## Baselines
- coefficient-optimal adjacent matching + locally cheapest TARE representation;
- direct-unitary/anticommuting matching where available;
- random pairings where scale permits;
- greedy Pauli-weight matching;
- TARE paper split-and-combine without optimized grouping (represented as unoptimized structural split, not authors' implementation claim);
- ordinary LCU normalization as reference only.

## Hostiles
- verify locked external Git blob hash before parsing;
- strip identity term consistently;
- signed Pauli labels canonicalized;
- phase ignored only where mathematically irrelevant;
- no stronger access/oracle assumptions;
- no hiding outer-LCU composition cost;
- no scalarization of `Lambda,E,C,ancilla` into a post-hoc winner;
- result cannot self-authorize novelty.

## Promotion
A positive fresh subject earns only `R4D_IMPLEMENTATION_AWARE_SPLIT_TARE_COMPILER_SUPPORTED__REAL_PUBLIC_HAMILTONIAN`.

R5 additionally requires outer-composition/full circuit accounting and independent replay. R6 additionally requires hostile current novelty review and external scientific authority.
