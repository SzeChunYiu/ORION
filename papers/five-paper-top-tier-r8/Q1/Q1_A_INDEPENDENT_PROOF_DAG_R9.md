# Q1-A R9 clean-room reconstruction of the sharp R6M support cap

## Status and authority

**Phase-1 terminal:** `PHASE1_LOCKED_BEFORE_REGISTERED_PROOF`

This is a same-program internal algebraic reconstruction. It is not external review, a production-resource map, a novelty opinion, or journal authority. Those authorities remain `CANNOT_CHECK`.

Phase 1 used only:

- `CLAIM_LEDGER_V3.md` (blob `67459ecca65f160b52af470fe6a2582f6af95ed3`);
- the neutral compiler/objective/feasibility definitions at lines 66--107 of canonical `MANUSCRIPT_V3_REFINED.md` (blob `6c4c59452397024d96cf6d103f474b7b0a07e536`); and
- `INDEPENDENT_SUPPORT_TWO_AUDIT_PACKET_R9.md` for the lane protocol.

Before this document and its Phase-1 receipt were committed, the lane did **not** read the registered proof `HUMAN_PROOF_R6S_2026-08-22.md`, manuscript proof sections 3--4, a registered ORION-Q solver/canonicalizer/support checker, or registered result receipts.

## 1. Atomic frozen statement

Work in the phase-free `n`-qubit Pauli group. An admitted instance has six target words in three ordered pairs. A feasible state chooses, for each block `j in {A,B,C}`:

1. nonidentity frames `(R_j0,R_j1)` with odd symplectic parity;
2. an assignment permutation of its two targets to branches;
3. one central branch, whose frame multiplier is `2` rather than `4`;
4. one Tag `S` shared by all blocks; and
5. one common ordered Tag-parity orientation: `[R_j0,S]` is the same bit for every `j`, `[R_j1,S]` is the other bit, and the two bits differ.

The exact semantic Restore words are `T_jk=P_j,pi_j(k) R_jk`, with phase discarded. For local letters `(a,b,c)`,

`F3(a,b,c)=1` if `a=b=c!=I`, and otherwise `F3(a,b,c)=w(a)+w(b)+w(c)`.

The frozen objective is

`C = sum_jk m_jk(w(R_jk)-1) + 2w(S) + sum_(k,q) F3(T_Ak[q],T_Bk[q],T_Ck[q])`,

where `m_jk` is `2` on the central branch and `4` on the other branch. Define frame support `K=max_jk w(R_jk)`.

The exact upper theorem is existential:

> For every finite `n` and every admitted instance (that is, with a nonempty finite feasible set), there exists `x` in `argmin C` with `K(x)<=2`.

The sharpness statement is:

> The least uniform frame-support cap with that property is `kappa_R6M=2`.

This is a constructive optimum-preserving normal-form theorem. It is not a polynomial-runtime theorem and says nothing by itself about T count, T depth, qubits, magic states, wall time, or physical advantage.

## 2. Independent dependency DAG

| Node | Statement | Direct dependencies | Load-bearing premises |
|---|---|---|---|
| `D0` | Phase-free Pauli words have coordinate-local symplectic parity. | neutral algebra | phases are semantically irrelevant here |
| `D1` | Frozen feasibility and objective are exactly those above. | neutral definitions | no hidden feasibility predicate depends on deleted letters |
| `L1` | Every supported coordinate of one frame has a two-bit deletion signature. | `D0`,`D1` | partner and shared Tag remain fixed |
| `L2` | A frame of support at least three has a nonempty proper deletion set of at most three coordinates whose signature XOR is `00`. | `L1` | total partner-parity bit is odd |
| `L3` | Deleting that set preserves nonidentity, partner anticommutation, Tag parity, label orientation, assignment, central branch, and all other blocks. | `L2`,`D1` | exactly one frame is edited |
| `L4` | Changing one of the three local Restore donors changes `F3` upward by at most `2`. | `D1` | the donor-owned `F3` rule is frozen |
| `L5` | The deletion changes objective by at most `-(m-2)|D|<=0`. | `L3`,`L4` | frame multiplier `m` is `2` or `4` |
| `L6` | Repeating the exchange from an exact optimum terminates at another exact optimum with all frame supports at most two. | `L5` | finite support measure; global optimality prevents a lower value |
| `U1` | Uniform support-two upper bound. | `L6` | admitted finite instance |
| `W1` | Independent two-qubit target instance below has a cost-5 support-two witness. | `D0`,`D1` | duplicate targets are not forbidden |
| `L7` | Exact min-plus enumeration gives unrestricted optimum `5` and support-at-most-one optimum `6`. | `W1`,`D1` | exhaustive finite Pauli domain; compression keeps the minimum for every Restore-pair state |
| `W2` | No support-at-most-one optimum exists on `W1`. | `L7` | objective and feasibility unchanged |
| `T1` | `kappa_R6M=2`. | `U1`,`W2` | no promotion outside the frozen grammar/objective |

Edges are also recorded as machine-readable pairs in `Q1_A_PHASE1_RECONSTRUCTION_RECEIPT_R9.json`.

## 3. Algebraic reconstruction

### 3.1 Two-bit deletion signature

Fix one frame `R=R_jk`, its unchanged partner `Q=R_j,1-k`, and shared Tag `S`. Let `U=supp(R)`. For each `q in U`, define

`s_q = ( [R[q],Q[q]], [R[q],S[q]] ) in F_2^2`,

where the bracket is the single-coordinate symplectic bit. The XOR of the first components is `[R,Q]=1`. The XOR of the second components is the current frame-Tag parity.

Deleting coordinates `D subset U` means replacing `R[q]` by `I` for `q in D`. It preserves both relevant global parities exactly when `XOR_(q in D) s_q=00`.

### 3.2 Proper zero-sum subset lemma

Suppose `|U|>=3`. Inspect any three signatures.

- A `00` signature gives a removable singleton.
- Two equal signatures give a removable pair.
- Otherwise the three are the three distinct nonzero elements of `F_2^2`, whose XOR is `00`.

In the last case, if these are all of `U`, the total first signature bit would be zero, contradicting `[R,Q]=1`. Therefore the triple is proper whenever it is used. Thus a nonempty proper `D` of size at most three always exists. In particular, deletion never produces the identity frame.

### 3.3 Feasibility and semantic invariant

For the frame `R'` obtained by deletion:

- `[R',Q]=[R,Q]` because the removed partner-signature XOR is zero;
- `[R',S]=[R,S]` because the removed Tag-signature XOR is zero;
- `R'!=I` because `D` is proper;
- Tag, partner, target assignment, central branch, and all other blocks are unchanged; and
- exact target semantics are retained by re-evaluating `T'_jk=P_j,pi_j(k) R'_jk`.

The neutral definition explicitly says no other frozen feasibility condition depends on the removed letters. This premise is load-bearing: adding any such condition changes the theorem scope.

### 3.4 Objective exchange

At each coordinate in `D`, exactly one member of one three-donor Restore triple changes. Exhaustion of the four local Pauli letters gives

`F3(new)-F3(old)<=2`.

The largest increase is the tie mechanism `F3(X,X,X)=1 -> F3(Y,X,X)=3`. Hence the total Restore increase is at most `2|D|`. The frame refund is exactly `m|D|`, with `m in {2,4}`. Tag and every other objective term are unchanged, so

`C(new)-C(old) <= -m|D|+2|D| = -(m-2)|D| <= 0`.

For `m=4` the bound is strict. Consequently an exact optimum cannot contain a support-greater-than-two noncentral frame: the exchange would contradict optimality. For `m=2`, equality can occur and the exchange preserves the optimum. Each exchange strictly lowers the sum of frame supports, so iteration terminates with `K<=2`.

## 4. Sharpness: independent exact two-qubit witness

Use qubit order left-to-right and the ordered target pairs

- `A=(ZI,XZ)`;
- `B=(IX,IZ)`;
- `C=(IZ,IZ)`.

The repeated `C` target is intentional and attacks a duplicate-target degeneracy.

A cost-5 feasible state is:

- shared Tag `S=IX`, giving Tag cost `2`;
- common Tag orientation `(0,1)`;
- `A` frames `(ZI,XZ)`, branch 1 central, Restores `(II,II)`, frame cost `2`;
- `B` frames `(IX,IZ)`, Restores `(II,II)`, frame cost `0`;
- `C` frames `(IX,IZ)`, Restores `(IY,II)`, frame cost `0`.

The only Restore charge is `F3(I,I,Y)=1` on branch 0 at the second coordinate. Total cost is `2+2+1=5` and maximum frame support is two.

`verify_q1_a_reconstruction_r9.py` independently enumerates the phase-free two-qubit grammar directly. It imports no registered solver or result. For a fixed Tag and orientation it enumerates ordered anticommuting frames, both target permutations, and both central choices. It then keeps the least local frame cost for every exact ordered Restore pair; this min-plus elimination is lossless because other blocks see a block only through that Restore pair, while all remaining local dependence is its additive frame cost.

The resulting exact terminals are:

| Restriction | Exact terminal | Optimum | Compressed global states | Optimum compressed witnesses |
|---|---:|---:|---:|---:|
| support zero | `INFEASIBLE` | none | 0 | 0 |
| support at most one | `EXACT_OPTIMUM` | 6 | 4,992 | 30 |
| unrestricted at `n=2` | `EXACT_OPTIMUM` | 5 | 3,194,880 | 2 |

Because the two-qubit Pauli domain has maximum support two, the last row is genuinely unrestricted. The exact `5<6` gap proves the uniform cap cannot be zero or one. Together with the all-size upper descent, it yields `kappa_R6M=2`.

## 5. Required hostile attacks and boundaries

### Supports 0, 1, 2, and 3+

- **0:** infeasible because every frame is required nonidentity.
- **1:** feasible in general, but not uniformly sufficient; the exact witness has optimum `6` versus unrestricted `5`.
- **2:** sufficient for an exact optimum by the descent and attained by the lower witness.
- **3+:** any such frame admits a proper parity-neutral deletion; repeated deletion reaches support at most two without increasing objective.

### Degeneracies, duplicate coordinates, and aliases

- A local `00` signature is the easiest case: delete it singly.
- Duplicate signatures delete in pairs, including duplicate-coordinate behavior.
- A frame cannot alias its partner phase-free because equal Paulis commute, contradicting required anticommutation.
- Tag/frame, Tag/partner, or cross-block aliases do not break the argument: their only relevant effect is already in the two symplectic signature bits.
- Identity local letters in the partner, Tag, targets, or Restores are explicitly included.
- Duplicate target words are admitted by the neutral grammar and occur in the independent lower witness.
- Phase aliases are outside the phase-free representation; importing phase-sensitive semantics would be a scope change.

### Objective ties

The worst local Restore increase is exactly two. On a central (`m=2`) branch this can tie the frame refund; the proof requires only nonincrease. On a noncentral (`m=4`) branch the same event remains a strict improvement. All exact minimizer ties, target-permutation ties, and central-choice ties remain admitted; the finite receipt reports multiple optimum compressed witnesses.

### Vanishing coefficients

The frozen neutral instance, feasibility predicates, support functional, and objective contain Pauli target words but no numerical target amplitudes. A zero amplitude therefore has no defined role in this theorem. If a production grammar deletes or discounts a zero-coefficient target, that is an additional admission/objective rule and the current proof terminal does not transport: `SCOPE_MISMATCH` or `DEFINITION_AMBIGUITY`, not silent inclusion.

### Hostile controls

- Removing the odd partner-parity premise permits signatures `01,10,11`; their only zero-sum subset is the full triple, which would produce the forbidden identity frame.
- Replacing multiplier `m=2` by `m=1` makes the worst exchange increase objective by one; the theorem is objective-specific.
- Editing two frames simultaneously or repairing/changing the shared Tag is outside the one-frame exchange and is rejected rather than assumed.
- Adding a feasibility rule that inspects deleted local letters invalidates `L3` unless separately proved invariant.

## 6. Phase-2 comparison gate

This Phase-1 artifact is intentionally frozen before registered-proof access. Phase 2 must content-bind and read the registered proof only after the Phase-1 commit, compare the two DAGs node by node, and preserve the first disagreement. The final Q1-A terminal must be one of those allowed by PR #1428; no manuscript wording may be silently imported to erase a scope difference.
