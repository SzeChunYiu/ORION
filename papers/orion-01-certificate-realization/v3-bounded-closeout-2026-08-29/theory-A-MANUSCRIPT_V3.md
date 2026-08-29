# Zero-Sum Support Certificates for Multi-Tag Quantum Compilation

**ORION-01 Paper A — bounded manuscript V3**  
**Status:** candidate successor to the frozen V2 text; no external review or submission authority claimed

## Abstract

Finite-support normal forms can make exact compiler optimization enumerable, but the numerical support ceiling may belong to a certificate language rather than to the compiler itself. Let `H` be a finite abelian group and let `A` be a fixed set of admissible signatures. Write `zsf(H;A)` for the maximum length of a sequence over `A` having no nonempty zero-sum subsequence, where a subsequence may use any set of positions and the empty sequence is admitted. This is a standard restricted/subset zero-sum invariant; no novelty is claimed for the invariant or for its elementary binary rank bound.

We prove a compiler-transfer theorem. For a finite family of constrained generators, suppose each generator has a fixed admissible signature alphabet, every feasible signature sequence has nonzero total, deleting any zero-sum subsequence preserves feasibility of the whole instance, and the deletion does not increase the objective. Then an exact optimum exists in which every generator has support at most its corresponding `zsf` value. The proof is a global fixed-point descent, so reductions of one generator cannot invalidate the simultaneous quantifier over all generators.

For an explicit MultiTag-TARE grammar, the global anticommutation constraint gives the required nonzero total. A coordinate-indexed `b`-way Restore functional changes in exactly one argument when one frame letter is deleted. Its exact one-argument increase is `b-1`; therefore deleting `k` coordinates refunds at least `k mu` and adds at most `k(b-1)t_R`. In the cone `mu >= (b-1)t_R`, the zero-sum certificate applies. The one-Tag, three-block R6M specialization has a certificate ceiling two and is separately bound to an exact compiler upper/lower result with intrinsic support two. No general multi-Tag sharpness, physical resource advantage, production move completeness, or external novelty authority follows.

## 1. Scope and contribution

The upstream TARE construction and classical zero-sum theory are donor work. This paper's bounded residual is the conjunction of four compiler-specific facts:

1. a semantic signature map for the stated MultiTag grammar;
2. a whole-instance deletion-soundness obligation;
3. exact Restore sensitivity and objective accounting;
4. a separately bound sharp R6M control.

The binary linear-dependence corollary and the restricted zero-sum invariant are used, not claimed.

## 2. Restricted zero-sum sequences

Let `H` be a finite abelian group written additively and let `A subseteq H` be fixed before optimization outcomes are inspected.

A **subsequence** of `W=(w_1,...,w_m)` is `(w_i)_{i in I}` for any index set `I subseteq {1,...,m}` in increasing order. It need not be contiguous. Unless explicitly called proper, it may be the whole sequence. A sequence is **zero-sum-free** when no nonempty subsequence has sum zero.

The empty sequence is admitted and has length zero. Define

`zsf(H;A) = max { |W| : W is a zero-sum-free sequence over A }`.

Because `H` and `A` are finite, the maximum is finite. If no positive-length zero-sum-free sequence exists, the value is zero. For the full nonzero alphabet this equals the usual small Davenport constant; for a restricted alphabet it is the corresponding subset/restricted value.

Two cautions are essential.

- The invariant concerns arbitrary subsequences, not contiguous factors.
- A rank bound is special to elementary binary groups. For `H=Z_n` and `A={1}`, `zsf(H;A)=n-1` although the group has one generator. No general rank bound is asserted.

## 3. Simultaneous deletion theorem

Consider a finite optimization instance with constrained generators indexed by a finite set `G`. For each `R in G`, fix before optimization:

- a finite abelian signature group `H_R`;
- an instance-level admissible alphabet `A_R subseteq H_R`, consisting of signatures realizable by any admissible local configuration, not merely by the optimum later selected;
- for every feasible configuration `x`, a signature sequence `W_R(x)` over `A_R`, indexed by the active coordinates of `R`.

Assume the following.

**A1 — nonzero total.** For every feasible `x` and every constrained `R`, the sum of `W_R(x)` is nonzero.

**A2 — global deletion soundness.** If a nonempty subsequence of `W_R(x)` has sum zero, setting the corresponding coordinates of `R` to identity produces a configuration `x'` that is feasible for the whole instance, including constraints attached to every other generator.

**A3 — deletion dominance.** The same operation does not increase the objective.

**A4 — support monotonicity.** Such a deletion strictly decreases `support(R)` and cannot increase the support of another generator.

### Theorem 1 (simultaneous restricted-zero-sum normal form)

Under A1–A4, every admitted instance has an exact optimum `x*` satisfying

`support_R(x*) <= zsf(H_R;A_R)`

for every constrained generator `R` simultaneously.

### Proof

Start from an exact optimum. If some `R` violates the bound, its signature sequence is longer than `zsf(H_R;A_R)` and therefore has a nonempty zero-sum subsequence. By A1 that subsequence cannot be the whole signature sequence, because the whole sequence has nonzero total. Apply the deletion from A2. Feasibility is preserved globally, and A3 preserves optimality. By A4 the total support

`Phi(x)=sum_{R in G} support_R(x)`

strictly decreases and no individual support increases.

Repeat while a violation remains. `Phi` is a nonnegative integer, so the process terminates at a global fixed point. At that point no generator has a signature sequence longer than its `zsf` ceiling; otherwise another legal deletion would exist. The terminal configuration is still optimal and satisfies every bound simultaneously. QED.

Deleting a zero-sum subsequence preserves each affected sequence's total, so A1 remains true along the descent.

## 4. Binary corollary

Let `H=F_2^d`. Any sequence of more than `d` vectors is linearly dependent, hence contains a nonempty subsequence with XOR zero. Thus

`zsf(F_2^d;A) <= d`

for every `A subseteq F_2^d`. If `A` contains a basis, the basis sequence is zero-sum-free, so equality holds. This is elementary linear algebra and classical zero-sum theory, not a new theorem.

The number `d` is exact for the stated deletion language when a basis is realizable. It becomes an intrinsic compiler lower bound only after a separate compiler witness excludes all optima below `d`.

## 5. Explicit MultiTag grammar

Fix `b>=2` ordered target blocks and `s>=0` shared Tag Paulis `S_1,...,S_s`. Each constrained frame Pauli `R` has a globally anticommuting partner `R'`. At an active coordinate `q`, define

`v_q = (<R_q,R'_q>, <S_1q,R_q>, ..., <S_sq,R_q>) in F_2^(s+1)`,

where `<.,.>` is the local binary symplectic product.

The first component of `sum_q v_q` is

`sum_q <R_q,R'_q> = <R,R'> = 1 mod 2`,

because the global symplectic product is the sum of the local products and `R` anticommutes with `R'`. Hence the total signature is nonzero.

The admissible alphabet `A_R` is fixed at the instance level: it is the set of local partner/Tag signatures allowed by the grammar over all admissible configurations of that instance. It is not defined from a selected optimum and therefore does not shrink circularly during deletion.

### 5.1 Restore incidence

For each frame `R` and active coordinate `q`, the explicit grammar has one coordinate-indexed Restore term `F_{b,q}`. Deleting `R_q` replaces exactly the `R`-controlled argument of `F_{b,q}`; it does not alter an argument of a Restore term at another coordinate. Frame and Restore costs are additive over coordinates. This is the incidence assumption used below.

Define, on a local alphabet containing identity and at least two distinct nonidentity Paulis,

`F_b(a_1,...,a_b) = 1`

when all letters are the same nonidentity Pauli, and otherwise let `F_b` be the number of nonidentity letters.

### Lemma 2 (exact one-argument Restore sensitivity)

Replacing one argument of `F_b` increases its value by at most `b-1`, and the bound is attained.

### Proof

If the original tuple is not all equal and nonidentity, `F_b` is ordinary nonidentity Hamming weight. A one-argument replacement raises that weight by at most one; entering the exceptional all-equal state lowers the value to one. If the original tuple is all equal to a nonidentity Pauli, changing one argument to a different nonidentity Pauli changes the value from `1` to `b`, an increase of `b-1`. Such a distinct nonidentity Pauli exists in the Pauli alphabet. No case is larger. QED.

## 6. MultiTag normal form

Let each deleted frame coordinate refund at least `mu` in frame cost, and let the associated Restore coefficient be `t_R>=0`. Tag-support charges are nonnegative and unchanged by the signature-preserving deletion.

### Theorem 3 (MultiTag support certificate)

In the explicit incidence model of Section 5.1, if

`mu >= (b-1)t_R`,

then every admitted instance has an exact optimum satisfying

`support(R) <= zsf(H_R;A_R) <= rank(H_R) <= s+1`

for every constrained frame `R`.

### Proof

Take a zero-signature subsequence of `k` active coordinates. The partner and every Tag component sum to zero, so the declared deletion preserves their represented semantic constraints; global deletion soundness is an explicit grammar obligation. By coordinate additivity, frame cost decreases by at least `k mu`. Lemma 2 and the one-coordinate/one-argument incidence bound the total Restore increase by at most `k(b-1)t_R`. Tag cost is unchanged. The net objective change is therefore at most

`-k mu + k(b-1)t_R <= 0`.

Theorem 1 applies. Since `H_R` is an elementary binary subgroup of `F_2^(s+1)`, its restricted zero-sum ceiling is at most its binary rank, and its rank is at most `s+1`. QED.

Outside the cone the proof is silent. It does not establish a larger-support necessity result.

## 7. R6M bounded sharp control

For the frozen one-Tag, three-block R6M grammar,

`b=3`, `s=1`, `mu=2`, and `t_R=1`.

The instance lies on the cone boundary. Its production signature alphabet realizes a basis of `F_2^2`, so the rank-only deletion certificate ceiling is two. The all-size upper theorem and the exact support-one obstruction witness are bound directly to:

- `research/extensions/orion-qg/paper_a_a1_multitag_tare.py`;
- `research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json`;
- lower parent `research/extensions/orion-qg/QG18_TARE_KAPPA_RESULTS.json`;
- upper parent `research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`.

Those bindings support the bounded statement `kappa_R6M=2` for this specialization. They do not grant general multi-Tag sharpness, CI authority, external novelty authority, physical quantum advantage, outside-cone necessity, or transfer to unrelated grammars.

## 8. Relation to prior work

Davenport constants, restricted/subset zero-sum invariants, elementary binary dependence, sparse integer optima, Pauli symplectic algebra, and proof-system-relative reasoning are established donor areas. The current TARE work also recognizes that its Tag linear system can be non-unique and that minimum-weight or joint row-wise optimization may be desirable. Those donors own the general mathematical and compiler context.

The residual claimed here is narrower: the semantic binding of a restricted zero-sum deletion certificate to the stated MultiTag grammar, the exact Restore incidence and cost cone, and the separately established R6M control. The invariant itself, the binary bound, and generic sparse-optimum language are not listed as original contributions.

## 9. Reproducibility and independent checking

`proof_checker_v3.py` is derived from the theorem statements. It imports no ORION implementation and no PyZX code. It exhaustively checks small restricted alphabets, the binary bound in declared finite scopes, the cyclic counterexample to a general rank reading, terminal/deletion equivalence, and exact Restore sensitivity for `b=2,...,7`. Finite checks corroborate definitions and case analysis; all-size authority remains analytic.

The parent R6M result is not regenerated by that checker. Its exact upper and lower witnesses remain separately bound artifacts.

## 10. Limitations

1. The general theorem is conditional on whole-instance deletion soundness and objective dominance.
2. Computing `zsf(H;A)` may itself be difficult.
3. The rank chain is binary-only.
4. The MultiTag cone uses the explicit one-coordinate/one-Restore-argument incidence.
5. Outside `mu >= (b-1)t_R`, no necessity statement follows.
6. General multi-Tag sharpness remains open.
7. Structural support is not T count, depth, runtime, qubits, hardware advantage, or production move completeness.
8. Author-side replay is not external investigator authority.
9. Round-3 terminal `CANNOT_CHECK_MOVE_COMPLETENESS` remains active and adverse.

## 11. Conclusion

A restricted zero-sum invariant supplies an exact ceiling for a named deletion language, but the compiler inherits that ceiling only after semantic and objective obligations are discharged. In the stated MultiTag grammar, global anticommutation provides nonzero total, coordinate-indexed Restore incidence gives the exact `b-1` penalty, and a global descent proves simultaneous support bounds. R6M supplies the bounded sharp control. The result is a compiler-specific use of donor mathematics, not a new Davenport invariant and not a production-completeness claim.

## Selected primary references

- N. Schillo, A. Sturm, and R. Quay, TARE preprint, arXiv:2601.05740 (current version to be pinned in the release manifest).
- A. Plagne and S. Tringali, *The Davenport Constant of a Box*, Acta Arithmetica 171 (2015), DOI `10.4064/aa171-3-1`.
- I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel, and R. Weismantel, *The Support of Integer Optimal Solutions*, SIAM Journal on Optimization 28 (2018), DOI `10.1137/17M1162792`.

## Bounded disposition

`BOUNDED_PAPER_RETAINED`

The separately frozen production-completeness programme remains active under a new identity. Nothing in this manuscript converts the old capped execution into a stronger terminal.
