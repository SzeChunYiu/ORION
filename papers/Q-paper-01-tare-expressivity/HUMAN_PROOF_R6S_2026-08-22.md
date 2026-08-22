# Human proof of the R6S support-two theorem — 2026-08-22

Status: mathematical derivation from the frozen R6M definitions already committed in ORION-Q. No new subject data. The original R6S machine enumeration remains valuable as an independent exhaustive check, but the two finite lemmas used by the published proof can be proved analytically.

## Theorem

For the frozen R6M three-block shared-one-bit-Tag TARE-M2 grammar with the donor-owned three-way Restore factoring rule and support-count multipliers `m in {2,4}`, every feasible configuration can be transformed, without increasing cost, into a feasible configuration in which every frame Pauli has support at most two.

Therefore the unrestricted optimum equals the support-two optimum for every qubit count and every admitted instance:

\[
C_{DP}=C_{D^{++}}.
\]

Together with the exact R6O support-one counterexample, this implies `kappa_R6M=2`.

---

## 1. Local cost identity

For local Restore letters `a,b,c in {I,X,Y,Z}`, the frozen three-way factor cost is

\[
F_3(a,b,c)=
\begin{cases}
1,&a=b=c\neq I,\\
w(a)+w(b)+w(c),&\text{otherwise},
\end{cases}
\]

where local `w(I)=0` and `w(X)=w(Y)=w(Z)=1`.

Equivalently,

\[
F_3(a,b,c)=W(a,b,c)-2\,\mathbf 1[a=b=c\neq I],
\]

with `W=w(a)+w(b)+w(c)`.

This identity makes the R6S local exchange inequality transparent.

---

## 2. Analytic Lemma E: zeroing one frame letter costs at most two Restore units

Fix one branch/slot, one qubit, target letter `p`, and nonidentity frame letter `f`. Before the exchange the local Restore letter in this slot is

\[
t_{old}=p f,
\]

and after zeroing the frame coordinate it is

\[
t_{new}=p.
\]

The other two Restore letters at that branch/qubit are fixed arbitrarily.

### Claim

\[
F_3(t_{new},u,v)-F_3(t_{old},u,v)\le 2.
\]

The same argument applies whichever of the three block slots is modified.

### Proof

Only one local letter changes, so the ordinary nonidentity count satisfies

\[
\Delta W:=W_{new}-W_{old}\le1.
\]

Let `I_old` and `I_new` indicate whether the old/new triple, respectively, consists of three identical nonidentity letters. Then

\[
\Delta F_3=\Delta W+2I_{old}-2I_{new}.
\]

There are two cases.

**Case 1: `I_old=0`.** Then

\[
\Delta F_3\le \Delta W\le1\le2,
\]

because the new all-equal discount, if present, only decreases the cost further.

**Case 2: `I_old=1`.** Then `t_old` is nonidentity. Since `f` is nonidentity and `t_old=p f`, the choice `p=f` is impossible here because it would give `t_old=I`. Thus either:

- `p=I`, in which case the changed slot goes nonidentity -> identity and `Delta W=-1`; or
- `p` is a nonidentity letter different from `f`, in which case both `t_old` and `t_new=p` are nonidentity and `Delta W=0`.

Hence whenever the old two-unit all-equal discount is destroyed,

\[
\Delta W\le0.
\]

Therefore

\[
\Delta F_3\le0+2=2.
\]

This proves the claim. Equality can occur only in Case 2 with `Delta W=0` and the old discount destroyed, exactly matching the exhaustive R6S table's maximum increase of 2.

Since every removed frame-support coordinate refunds `m=2` on a central branch or `m=4` on a noncentral branch,

\[
\Delta F_3\le2\le m.
\]

Thus **zeroing one support coordinate never increases total cost if the relevant frame/Tag parity constraints are preserved.**

This replaces the 18,432-case Lemma-E enumeration as a logical requirement. The enumeration remains an independent full-domain regression check of the analytic statement.

---

## 3. Analytic Lemma B: a proper parity-preserving subset exists whenever support >=3

Let `R` be one frame Pauli of support `w>=3`, `R'` its anticommuting partner, and `S` the shared Tag. For every `q in supp(R)`, define

\[
\alpha_q=\langle R_q,R'_q\rangle\in\mathbb F_2,
\qquad
\beta_q=\langle S_q,R_q\rangle\in\mathbb F_2,
\]

and the class

\[
c_q=(\alpha_q,\beta_q)\in\mathbb F_2^2.
\]

Because `R` and `R'` anticommute globally,

\[
\sum_{q\in supp(R)}\alpha_q=1\pmod2.
\]

### Claim

For `w>=3`, there exists a nonempty proper subset `Q subset supp(R)` of size at most two satisfying

\[
\sum_{q\in Q} c_q=(0,0).
\]

### Proof

If any support qubit has class `(0,0)`, choose it as a singleton `Q`.

Otherwise all classes lie in the three-element set

\[
\{(0,1),(1,0),(1,1)\}.
\]

If any class repeats, choose two equal-class qubits. In `F_2^2`, an equal pair sums to zero. Because `w>=3`, that pair is proper.

The only remaining possibility would be that all classes are distinct. Since there are only three nonzero classes and `w>=3`, this forces `w=3` and the multiset to be exactly

\[
\{(0,1),(1,0),(1,1)\}.
\]

But its alpha-sum is `0+1+1=0 mod 2`, contradicting the required odd alpha-sum.

Therefore the required subset always exists.

Again, the R6S enumeration of odd-alpha class tuples is a corroborating implementation check, not a necessary proof step.

---

## 4. Feasibility of the exchange

Choose the subset `Q` from Lemma B and replace `R_q` by identity for every `q in Q`.

### Frame anticommutation is preserved

The global symplectic bit between `R` and its partner changes by

\[
\sum_{q\in Q}\alpha_q=0.
\]

So an anticommuting pair remains anticommuting.

### Shared-Tag syndrome is preserved

The frame-Tag symplectic bit changes by

\[
\sum_{q\in Q}\beta_q=0.
\]

Thus the same shared Tag remains feasible. **No Tag repair is needed.**

### The modified frame remains nonidentity

`Q` is proper and `|Q|<=2<w`, so at least one support coordinate of `R` remains.

All other grammar constraints are unchanged.

---

## 5. Cost of the exchange

The frozen objective is coordinate-separable for the affected frame-support and Restore terms.

For each `q in Q`:

- removing the frame letter refunds multiplier `m in {2,4}`;
- analytic Lemma E bounds the associated `F3` increase by at most 2;
- the Tag is unchanged;
- other frame branches and other coordinates are unchanged.

Hence

\[
\Delta C
\le
\sum_{q\in Q}(2-m)
\le0.
\]

So the exchange never increases cost and strictly reduces the total frame support.

---

## 6. Global normal form

Start from an unrestricted optimal configuration. If any frame Pauli has support at least three, apply the exchange above to that Pauli. The result is feasible and has cost no larger than the optimum; therefore its cost is equal to the optimum. Total frame support strictly decreases.

Repeat. The process must terminate because total support is a nonnegative integer. At termination every frame Pauli has support at most two, and the configuration is still optimal.

Therefore

\[
C_{D^{++}}\le C_{DP}.
\]

The reverse inequality is automatic because `D++` is a restriction of the unrestricted family:

\[
C_{DP}\le C_{D^{++}}.
\]

Thus

\[
\boxed{C_{DP}=C_{D^{++}}\quad\text{for every admitted instance and every }n.}
\]

---

## 7. Why the argument cannot be pushed to support one

For `w=2`, a zero-sum singleton/pair need not be a **proper** nonempty subset satisfying both parity conditions. The four R6S failing class patterns are exactly

\[
(1,2),(1,3),(2,1),(3,1)
\]

under the receipt's class code `2*alpha+beta`: one coordinate has `alpha=0,beta=1` and the other carries the odd anticommutation parity. Removing the locally commuting coordinate would flip the Tag syndrome.

This is not merely a proof artifact. R6O realizes the obstruction as an exact optimal support-two frame-for-Tag trade with

\[
C_{DP}=5<C_{D^+}=6.
\]

Hence support one is genuinely insufficient, and the human proof plus counterexample yields

\[
\boxed{\kappa_{R6M}=2.}
\]

---

## 8. Publication significance

The revised paper can now present R6S as a mostly elementary analytic theorem with exhaustive computation used for **verification rather than logical closure**:

- Lemma B: one-paragraph pigeonhole/parity proof;
- Lemma E: one-paragraph support-minus-discount inequality;
- global theorem: monotone support-reduction iteration;
- sharpness: exact `n=2` counterexample.

This materially strengthens mathematical readability and reduces dependence on a large finite table in the main proof. The machine checks should remain in the supplement/reproducibility package as independent exhaustive confirmation of the analytic derivation.
