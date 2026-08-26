# ORION-01 figures plan V2 — theorem-first submission

The original figure plan was written before R6S. V2 reorganizes the visual story around the sharp theorem `kappa_R6M=2` and uses computation primarily as corroboration/application.

## Figure 1 — The sharp normal-form result

**Purpose:** communicate the paper in one picture.

Left: unrestricted auxiliary-frame space, showing possible frame support growing with system size.

Center: analytic exchange arrow removing support-three-or-larger coordinates while preserving frame anticommutation and Tag syndrome.

Right: highlighted support-two normal form.

Bottom annotation:

`support >=3 removable` | `support 2 can be strictly optimal` | `support 1 insufficient uniformly`

and headline equation

\[
\kappa_{R6M}=2.
\]

Include the raw candidate-count contrast only as a secondary annotation:

- arbitrary Pauli frame space: exponential raw representation family;
- support-two raw frame family: `[3n+9*C(n,2)]^6 = O(n^12)`.

Do not imply the production DP has exponential runtime.

## Figure 2 — Human proof mechanism in one qubit/class diagram

Two panels.

### (a) F2^2 class exchange

For each support qubit show class

`c_q = (alpha_q,beta_q)`

where alpha tracks frame-partner anticommutation and beta tracks Tag syndrome.

Illustrate the two valid zero-sum removals:

- `(0,0)` singleton;
- equal-class pair `c+c=0`.

Show why support >=3 with odd total alpha must contain one of these.

### (b) Restore-cost inequality

Show

`F3 = ordinary nonidentity count - 2*(all-three-equal-nonidentity)`.

When one frame coordinate is removed, ordinary count can increase by at most 1; if the old 2-unit discount is destroyed, ordinary count cannot increase. Hence `Delta F3 <=2 <= frame refund m`.

This figure should make the theorem understandable without reading code or the 18,432-case table.

## Figure 3 — Why the theorem is sharp: two coupling trades

Panel A: **Tag-for-anchor** witness (`n2_b`):

- A anchored q0, B/C anchored q1;
- weight-two shared Tag;
- exact `8 < 9` donor comparison.

Panel B: **frame-for-Tag** witness (`instance_index=16`):

- support-two central frame;
- compressed shared Tag / improved Restore alignment;
- exact `5 < 6` all-support-one optimum.

Panel C: proof-boundary inset showing the four weight-two class patterns for which the parity-preserving proper subset need not exist. Arrow from the patterns to Panel B: **the proof obstruction is realized by the optimizer**.

This should be the paper's most memorable mechanistic figure.

## Figure 4 — Evidence ladder and finite regime prediction

Horizontal evidence ladder:

1. local support-dominance audit — 688,041,472 zero-violation configurations;
2. exact counterexamples to weight-one closures;
3. R6P finite support-two closure — all 559 prior criticals repaired;
4. R6Q finite classifier — 9,771 registered rows, zero classification errors;
5. R6R prospective public subject — prediction frozen before DP, 15/15 matchings confirmed;
6. analytic all-n theorem.

Inset: structured-n2 regime census from R6Q, but label it explicitly **finite-domain first-two-trade taxonomy**, not universal.

A caption note must disclose that later QG work found additional support-two subregimes at higher n without affecting `kappa=2`.

## Figure 5 — Public-Hamiltonian grounding

Panel A: H4/N2 30 matching equality: unrestricted and donor family tie; simple diagram rather than large table.

Panel B: LiH split-normalization comparison:

- Pauli L1 = 0.8971267;
- sorted-contiguous optimum = 0.9008506;
- random mean = 1.104149;
- random p05/p50/p95 shown from receipt.

Panel C: H2O:

`C: 8078 -> 4972`

at relative normalization overhead `9.087e-6`, 20 qubits / 8082 nonidentity Paulis.

Caption: structural/Pareto grounding, **not fault-tolerant physical-resource advantage**.

## Table 1 — Theorem assumptions and scope

Rows:

- three ordered two-term TARE-M2 blocks;
- one-bit shared Tag;
- donor-owned F3 three-way factoring;
- frame multipliers central=2/noncentral=4;
- Tag multiplier=2;
- support-count objective;
- arbitrary n/targets/matchings/permutations/central choices.

Right column: what is outside theorem (other objectives, R6I, larger Tag ranks, arbitrary block encodings).

This table should appear near Theorem 3 to prevent scope drift.

## Table 2 — Claim strength

Separate:

- `THEOREM`: support-two all-n / kappa=2;
- `EXACT COUNTEREXAMPLE`: 8<9 and 5<6;
- `FINITE EXACT`: R6Q/R6P panels;
- `PROSPECTIVE FINITE`: R6R;
- `PUBLIC SUBJECT SUPPORT`: LiH/H2O/H4/N2.

This helps reviewers see that evidence levels are intentionally not conflated.

## Supplement figures

- full R6Q confusion tables;
- R6P critical-gap histograms;
- R6S machine-check class counts/tie census as **verification of the analytic proof**;
- witness serializations;
- coefficient-partition exhaustive controls;
- source/data custody diagram for public Hamiltonians.
