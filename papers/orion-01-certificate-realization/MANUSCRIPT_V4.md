# Restore-Sensitive Certificate Realization: Normal Forms and Intrinsic Support in Quantum Compilation

## Abstract

Support ceilings in exact quantum compilation can describe either an intrinsic property of the compiler objective or only the reach of a chosen normalization language. We connect these layers for explicit extensions of Tag-and-Restore Encoding (TARE). First, a whole-instance deletion contract and terminating global descent turn zero-sum deletion into a simultaneous support normal form. For the phase-quotiented MultiTag grammar studied here, the binary signature ceiling equals the rank of the generated span, deleting one frame coordinate changes one argument of one charged Restore term, and the exact upward sensitivity is \(b-1\). Hence every admitted instance has an optimum with frame support at most \(s+1\) whenever \(\mu\geq(b-1)t_R\). We then formalize the same binary deletion rule as a rank-only certifiable-support calculus whose only transition is that deletion rule, and compare its budget with intrinsic optimal support under fixed objectives and fixed support statistics. In a matched one-Tag, three-block family, both quantities equal two. In a dependent-triple family, the rank-only joint active-column budget is five whereas whole-system Tag relocation gives intrinsic joint active-column support one. Because the calculus contains exactly one rule, the exactness of its budget holds by construction within that one-rule system rather than as a bound over alternative certificate rules. The separation is therefore relative to the declared one-rule proof language and does not imply a lower bound for richer systems, a production-compiler transfer, or a physical quantum advantage.

**Keywords:** quantum compilation; Pauli strings; support normal forms; certifiable support; intrinsic support; sparse optimization

## 1. Scientific question and contribution

Tag-and-Restore Encoding maps a mutually anticommuting Pauli family to target Pauli strings and uses shared Tag operators to identify branches [1]. Its Tag equations can have multiple solutions, and the original construction explicitly leaves minimum-weight and joint optimization open. This flexibility creates two related questions. When does a local deletion certificate produce a valid support normal form for the complete compiler objective? When such a ceiling exists, does it equal the support intrinsically required by an optimum, or only the support that a restricted certificate language can establish?

These questions must be answered together. A zero-signature deletion can be locally correct yet fail to preserve the full instance or its charged objective. Conversely, a sound normalization can yield a sharp upper bound while a certificate language still discards whole-system transformations that reach a smaller optimum. Classical zero-sum theory supplies the forcing mathematics [3-5], sparse integer optimization supplies broader support context [6], and relative proof-system efficiency supplies the conceptual warning that a bound may depend on the chosen calculus [7]. None of these donor theories establishes the compiler-specific semantic or objective bridge.

The paper supplies that bridge for two frozen formal families. It proves the whole-instance conditions needed for a global simultaneous deletion descent, derives the exact Restore sensitivity and objective cone for the stated MultiTag grammar, and then defines intrinsic optimal support and an operational rank-only support budget on the same underlying signatures. The matched family \(F_M\) acts as an equality control: a support-two normal form and an exact support-one obstruction give both certifiable and intrinsic value two. The dependent-triple family \(F_I\) provides the contrasting mechanism: rank-only deletion has joint active-column budget five, while whole-system Tag relocation and reconstruction reaches intrinsic support one under the same family statistic. This paired result identifies what the certificate language omits without turning that omission into an unrestricted lower bound.

The contribution is deliberately bounded. The binary rank identity, Davenport-type theory, generic proof-system relativity, and direct-product arithmetic are scaffolds rather than standalone novelty. The results do not establish general MultiTag sharpness, completeness of a production move language, algorithm-independent complexity, or hardware advantage.

## 2. Intrinsic and certifiable support

Let \(F\) be a family of finite exact-compilation instances. For an instance \(I\), let \(X(I)\) be its feasible set, \(C_I:X(I)\to\mathbb{R}\) its fixed objective, and \(\sigma_I(x)\) the support statistic under study.

**Definition 1 (intrinsic optimal support).** Define

\[
\kappa(I;C)
=
\min\{\sigma_I(x):x\in\operatorname*{arg\,min}_{y\in X(I)} C_I(y)\},
\]

and, when finite,

\[
\kappa(F;C)=\sup_{I\in F}\kappa(I;C).
\]

This is a mathematical property of the family and objective. An upper theorem and a lower witness establish its exact value; they are not part of the definition.

The second quantity is deliberately proof-system-relative. To make its lower-bound obligation checkable, we define the proof system operationally rather than referring to an unspecified notion of what it can prove.

## 3. Fixed alphabets and zero-sum-free sequences

Let \(H\) be a finite abelian group written additively, and let \(A\subseteq H\) be a finite alphabet fixed independently of the optimum to be bounded. A subsequence selects an arbitrary set of positions and need not be contiguous. A sequence over \(A\) is **zero-sum-free** if no nonempty subsequence has sum zero. Define

\[
\operatorname{zsf}(H;A)
=
\max\bigl(\{0\}\cup\{|W|:W\text{ is zero-sum-free over }A\}\bigr).
\]

The explicit zero handles degenerate alphabets. If \(D(H)\) denotes the least length forcing a nonempty zero-sum subsequence over the full finite group, then

\[
\operatorname{zsf}(H;H\setminus\{0\})=D(H)-1.
\]

For restricted \(A\), \(\operatorname{zsf}(H;A)+1\) is the corresponding forcing length. This is donor mathematics, not a contribution of this paper.

## 4. Simultaneous deletion theorem

Fix an optimization instance with a nonempty finite feasible set, so an exact optimum exists. For every constrained generator \(R\), let \(A_R\) be the set of signatures realizable by any admissible local state of that instance, fixed before optimization. Let every active coordinate \(q\) of \(R\) carry \(v_q\in A_R\subseteq H_R\).

Assume the following.

1. **Nonzero total.** Every feasible constrained generator satisfies \(\sum_q v_q\neq 0\).
2. **Whole-instance deletion soundness.** Deleting any nonempty zero-sum subsequence of coordinates of \(R\) preserves every constraint of the full instance, not only constraints local to \(R\).
3. **Objective dominance.** The same deletion does not increase the objective.
4. **Support monotonicity.** Deleting coordinates of one generator does not activate coordinates of another generator or otherwise increase any generator's support.

**Theorem 2 (simultaneous alphabet ceiling).** Every admitted instance has an exact optimum \(x^\star\) such that, simultaneously for every constrained generator \(R\),

\[
\operatorname{support}_R(x^\star)
\leq
\operatorname{zsf}(H_R;A_R).
\]

**Proof.** Start from any optimum. While some generator contains a nonempty zero-sum subsequence, delete that subsequence. Its nonzero total excludes deletion of the whole active sequence. Assumptions 2 and 3 preserve feasibility and optimality. Assumption 4 makes total support over all constrained generators decrease strictly and prevents any individual support from increasing. Total support is a nonnegative integer, so the process terminates. At termination every active signature sequence is zero-sum-free over its fixed alphabet and hence has length at most the corresponding \(\operatorname{zsf}\) value. The same terminal optimum therefore satisfies all generator bounds. \(\square\)

The global descent is essential: reducing one generator only once would not establish the existential-optimum/universal-generator quantifier when generators share constraints.

## 5. Binary specialization and the rank-only calculus

The restricted alphabet does not improve the rank ceiling once the binary signature group is defined to be the span of that alphabet.

**Theorem 3 (binary generated-span identity).** Let \(A\subseteq \mathbb{F}_2^d\), and let \(H=\langle A\rangle\). Then

\[
\operatorname{zsf}(H;A)=\operatorname{rank}(H).
\]

**Proof.** A sequence over \(A\) is zero-sum-free exactly when its listed vectors are linearly independent: any binary linear dependence selects a nonempty set of positions whose bitwise exclusive-or (XOR) is zero, and the converse is immediate. Thus every zero-sum-free sequence has length at most \(\operatorname{rank}(H)\). Because \(A\) spans \(H\), it contains a basis of \(H\); listing that basis gives a zero-sum-free sequence of length \(\operatorname{rank}(H)\). \(\square\)

This equality is special to the elementary binary setting. It must not be generalized to arbitrary finite abelian groups. For example, in \(\mathbb{Z}_n\) with alphabet \(\{1\}\), the sequence of \(n-1\) ones is zero-sum-free although the group has rank one.

The equality is still only a certificate ceiling. It becomes an intrinsic compiler value only when a separate compiler witness rules out every smaller-support optimum.

Let \(A\subseteq\mathbb{F}_2^d\) be an alphabet fixed before optimization and let \(H=\langle A\rangle\). Write

\[
\mathcal{L}(A)=\{(v_1,\ldots,v_m)\in A^*:v_1\oplus\cdots\oplus v_m\neq 0\}.
\]

A subsequence selects an arbitrary set of positions and need not be contiguous. The rank-only calculus \(P_{\mathrm{rank}}(A)\) has exactly one transition:

\[
(v_1,\ldots,v_m)
\longrightarrow
(v_i)_{i\notin Q}
\quad\text{when}\quad
\varnothing\neq Q\subseteq\{1,\ldots,m\},
\quad
\bigoplus_{i\in Q}v_i=0.
\]

Deleting a zero-sum subsequence preserves the nonzero total, so the deleted set cannot be the whole word and the successor remains in \(\mathcal{L}(A)\). A word is terminal precisely when it is zero-sum-free. For \(w\in\mathcal{L}(A)\), define its best rank-only normal-form length by

\[
\nu_A(w)=
\min\{|u|:w\longrightarrow^*u\text{ and }u\text{ is terminal}\},
\]

and define the **rank-only certifiable support budget**

\[
\beta_{\mathrm{rank}}(A)
=
\sup\bigl(\{0\}\cup\{\nu_A(w):w\in\mathcal{L}(A)\}\bigr).
\]

The identity derivation is allowed, and every nonidentity transition strictly shortens the word, so the minimum exists. The term *certifiable support budget* is used to avoid collision with the established Boolean-function quantity called certificate complexity.

For a compiler family \(F\), each constrained object \(G\) has a fixed alphabet \(A_{I,G}\), and one word position represents one unit of the support statistic assigned to \(G\). Once the deletion rule has been proved sound for the objective \(C\), set

\[
\beta_{P_{\mathrm{rank}}}(F;C)
=
\sup_{I\in F,G}\beta_{\mathrm{rank}}(A_{I,G}).
\]

Here \(C\) records the soundness binding. It does not add an unlisted inference rule to the rank-only calculus.

**Proposition 4 (compiler soundness).** Suppose every admitted instance has an exact \(C\)-optimum, and every rank-only transition on the signature word of a \(C\)-optimal compiler state is realized by a feasible \(C\)-optimal compiler state whose support for the constrained object is the successor-word length. Then

\[
\kappa(F;C)\leq\beta_{P_{\mathrm{rank}}}(F;C).
\]

**Proof.** Start from a \(C\)-optimum and apply rank-only transitions until a terminal word is reached. Strict length descent gives termination, the hypothesis preserves feasibility and optimality, and the terminal support is at most the declared family budget. Taking the supremum over instances gives the inequality. \(\square\)

The reverse inequality does not follow. The calculus may omit a valid compiler transformation.

**Corollary 5 (exact rank-only budget).** For every finite \(A\subseteq\mathbb{F}_2^d\),

\[
\beta_{\mathrm{rank}}(A)=\operatorname{rank}(\langle A\rangle).
\]

**Proof.** Theorem 3 bounds every terminal word by the rank of the generated span and provides a basis word attaining that length. The identity derivation leaves the basis word terminal, so no smaller uniform conclusion holds in the declared state language. \(\square\)

The basis word is a countermodel to a smaller conclusion from the rank-only premises. It is not automatically a compiler lower bound. A compiler may use structure discarded by the alphabet model, and a richer proof system may formalize that structure.

## 6. Phase-quotiented MultiTag-TARE parity grammar

We now define the formal compiler grammar to which the abstract deletion theorem is applied. An \(n\)-qubit Pauli is represented up to phase by \(P=(x,z)\in\mathbb{F}_2^n\times\mathbb{F}_2^n\). Multiplication is componentwise XOR, support is

\[
w(P)=|\{q:(x_q,z_q)\neq(0,0)\}|,
\]

and the binary symplectic product is

\[
\langle (x,z),(x',z')\rangle=x\cdot z'+z\cdot x'\pmod 2.
\]

Fix \(b\geq2\) ordered blocks, a finite set of frame roles \(u\), and \(s\geq0\) shared Tag Paulis \(S_1,\ldots,S_s\). Block \(\ell\) contains a frame \(R_{\ell u}\) for each role and a designated partner \(R'_{\ell u}\). The parity constraints involving that frame are

\[
\langle R_{\ell u},R'_{\ell u}\rangle=1,
\qquad
\langle S_j,R_{\ell u}\rangle=\lambda_{j,\ell u}
\quad (j=1,\ldots,s),
\]

where the required label bits \(\lambda_{j,\ell u}\) are part of the instance. These parity equations are the only feasibility constraints in which the letters of \(R_{\ell u}\) participate. Targets, central-role choices, and any other variables are held fixed during a frame deletion, although they may be optimized before the deletion step is selected.

For an active coordinate \(q\) of a frame \(R=R_{\ell u}\), define

\[
v_q=
\bigl(
\langle R_q,R'_q\rangle,
\langle S_{1q},R_q\rangle,
\ldots,
\langle S_{sq},R_q\rangle
\bigr)
\in \mathbb{F}_2^{s+1},
\]

where \(\langle\cdot,\cdot\rangle\) is the local binary symplectic product. The XOR of the first components is

\[
\sum_q \langle R_q,R'_q\rangle
=
\langle R,R'\rangle
=1,
\]

because the global symplectic product is the sum of its local products and \(R\) anticommutes with \(R'\). The remaining components sum to the prescribed Tag labels. The total signature is therefore nonzero.

For each frame \(R\), define \(A_R\) from all local signatures allowed by the instance grammar, not from a selected optimum, and set \(H_R=\langle A_R\rangle\).

### 6.1 Deletion semantics

For \(Q\subseteq\{1,\ldots,n\}\), deletion of \(Q\) from \(R\) replaces \(R_q\) by \(I\) for every \(q\in Q\) and changes no other variable. The change in the partner and Tag parity vector is exactly

\[
\bigoplus_{q\in Q}v_q.
\]

Consequently a zero-signature deletion preserves every parity equation of the grammar. Because no other feasibility constraint contains the deleted letters, it preserves whole-instance feasibility. It only turns active letters into identities, so it cannot increase any frame support.

### 6.2 Restore incidence and objective

Each frame role \(u\) has fixed target Paulis \(T_{1u},\ldots,T_{bu}\). At coordinate \(q\), its Restore term takes the ordered residual letters

\[
a_{\ell uq}=(T_{\ell u}R_{\ell u})_q,
\qquad \ell=1,\ldots,b.
\]

For each pair \((R_{\ell u},q)\), this is the only Restore term containing the letter \((R_{\ell u})_q\). Deleting that letter replaces exactly the \(\ell\)-th argument of this one term, from \((T_{\ell u}R_{\ell u})_q\) to \((T_{\ell u})_q\).

The objective is

\[
C=C_0+C_{\mathrm{Tag}}(S_1,\ldots,S_s)
+\sum_{\ell,u,q}\mu_{\ell uq}\mathbf{1}[(R_{\ell u})_q\neq I]
+t_R\sum_{u,q}F_b(a_{1uq},\ldots,a_{buq}),
\]

where \(C_0\) is independent of the frame letters, \(C_{\mathrm{Tag}}\geq0\) is unchanged by a frame deletion, \(\mu_{\ell uq}\geq\mu\), and \(t_R\geq0\). The coefficients \(\mu_{\ell uq}\) may depend on a central-role or target-order choice, but that choice is held fixed while the deletion is evaluated and the lower bound \(\mu\) is uniform over all allowed choices.

This one-occurrence incidence is part of the formal grammar. A compiler in which one frame deletion changes several Restore terms requires a different coefficient and is outside the theorem below.

## 7. Restore sensitivity and the MultiTag normal form

For a local Pauli alphabet containing the identity and at least two distinct nonidentity letters, define

\[
F_b(a_1,\ldots,a_b)=
\begin{cases}
1, & a_1=\cdots=a_b\neq I,\\
|\{i:a_i\neq I\}|, & \text{otherwise}.
\end{cases}
\]

**Lemma 6 (one-argument sensitivity).** Replacing one argument of \(F_b\) can increase its value by at most \(b-1\), and this bound is attained.

**Proof.** Away from the all-equal nonidentity state, changing one argument raises ordinary nonidentity Hamming weight by at most one; entering the exceptional state lowers the value. Leaving an all-equal nonidentity state by replacing one letter with a different nonidentity letter changes the value from \(1\) to \(b\), an increase of \(b-1\). No case is larger. \(\square\)

Deleting \(k\) coordinates refunds at least \(k\mu\). By the incidence contract and Lemma 6, the Restore increase is at most \(k(b-1)t_R\). This bound is also valid when several one-argument replacements affect the same local functional: order the replacements and telescope the one-argument bound. The deletion is therefore objective-nonincreasing when

\[
\mu\geq (b-1)t_R.
\]

**Theorem 7 (MultiTag support normal form).** Under the stated semantic and incidence contracts, if \(\mu\geq (b-1)t_R\), every admitted instance has an exact optimum satisfying

\[
\operatorname{support}(R)
\leq
\operatorname{zsf}(H_R;A_R)
=
\operatorname{rank}(H_R)
\leq s+1
\]

simultaneously for every constrained frame \(R\).

**Proof.** Section 6.1 proves whole-instance feasibility and support monotonicity for a zero-signature deletion. The cost calculation above establishes objective dominance. Theorem 2 gives the simultaneous \(\operatorname{zsf}\) ceiling. Since \(H_R=\langle A_R\rangle\) is an elementary binary subgroup of \(\mathbb{F}_2^{s+1}\), Theorem 3 gives equality with its rank, which is at most \(s+1\). \(\square\)

Outside the stated cone, this proof is unavailable. That fact does not establish that larger support is necessary.

## 8. Matched family: the certificate ceiling is intrinsic

An instance of \(F_M\) supplies three ordered target pairs \((T_{\ell0},T_{\ell1})\), with \(\ell\in\{A,B,C\}\). A compiler state contains six frame Paulis \(R_{\ell k}\), one shared Tag \(S\), a central role \(c_\ell\in\{0,1\}\) for each block, and an allowed within-pair target order \(\pi_\ell\). It is feasible when

\[
\langle R_{\ell0},R_{\ell1}\rangle=1
\quad\text{for every }\ell,
\]

and the two Tag labels are block-independent and distinct:

\[
\langle S,R_{A k}\rangle
=\langle S,R_{B k}\rangle
=\langle S,R_{C k}\rangle
=\lambda_k,
\qquad
\lambda_0\neq\lambda_1.
\]

Set \(m_{\ell k}=2\) when \(k=c_\ell\) and \(m_{\ell k}=4\) otherwise. The frozen unit objective is

\[
\begin{aligned}
C_M={}&
\sum_{\ell,k}m_{\ell k}w(R_{\ell k})+2w(S)-18\\
&+\sum_{q=1}^n\sum_{k=0}^1
f_3\!\left(
(T^{\pi_A}_{Ak}R_{Ak})_q,
(T^{\pi_B}_{Bk}R_{Bk})_q,
(T^{\pi_C}_{Ck}R_{Ck})_q
\right).
\end{aligned}
\]

The support statistic is \(\sigma_M(x)=\max_{\ell,k}w(R_{\ell k})\). Each constrained object is one frame, and each word position is one active coordinate of that frame. Its signature records the symplectic bit with its partner and with \(S\), so the rank-only span has dimension at most two.

In \(F_M\), the frame alphabet spans two binary signature coordinates and admits a basis word. Corollary 5 gives

\[
\beta_{P_{\mathrm{rank}}}(F_M;C_M)=2.
\]

Separately, the whole-instance normalization gives an exact optimum of support at most two for every admitted size. The lower direction can be checked on the following two-site instance. Pauli keys are the binary masks \((x,z)\) defined in Section 6. Each displayed integer is the decimal encoding of a two-bit mask, so \((0,2)\) and \((3,0)\) denote two-qubit Paulis rather than individual coordinates.

| Block | Target pair \((T_{\ell0},T_{\ell1})\) | Feasible support-two frame pair | A minimizing support-at-most-one frame pair |
|---|---|---|---|
| \(A\) | \(((0,1),(0,1))\) | \(((0,1),(1,1))\) | \(((0,1),(1,0))\) |
| \(B\) | \(((0,1),(0,1))\) | \(((0,1),(1,1))\) | \(((0,1),(1,0))\) |
| \(C\) | \(((0,2),(2,0))\) | \(((0,2),(3,0))\) | \(((0,1),(1,1))\) |

Both displayed states use \(S=(0,1)\). For the support-two state, the central choices are \((0,0,1)\) and the target orders are unchanged. Its objective components are

| State | Weighted frame | Tag | Constant | Restore | \(C_M\) |
|---|---:|---:|---:|---:|---:|
| displayed support-two state | 20 | 2 | -18 | 1 | 5 |
| displayed support-at-most-one state | 18 | 2 | -18 | 4 | 6 |

The second row is not merely an example. The independent checker enumerates all \(7^6=117{,}649\) six-frame tuples with frame support at most one, including all \(12^3=1{,}728\) anticommuting frame tuples, all \(16\) Tags, all eight central choices, and all four allowed relative target orders. Its exact minimum is \(6\). The feasible support-two state costs \(5\), so no support-at-most-one state can be optimal for this instance. Therefore support one is not a uniform optimum bound and

\[
\kappa(F_M;C_M)=2.
\]

**Proposition 8 (matched equality control).** Consequently

\[
\beta_{P_{\mathrm{rank}}}(F_M;C_M)
=
\kappa(F_M;C_M)
=2.
\]

The rank-only certificate is therefore sharp for this family and objective. This does not imply sharpness for general MultiTag grammars.

## 9. Dependent-triple family: a rank-only separation

An instance of \(F_I\) has two blocks \(j\in\{A,B\}\). Each block contains independent frames \(R_{j0},R_{j1}\) with \(\langle R_{j0},R_{j1}\rangle=1\) and dependent frame \(R_{j2}=R_{j0}R_{j1}\). For a transparent canonical-label subfamily, two shared Tags satisfy, in both blocks,

\[
\begin{aligned}
(\langle S_0,R_{j0}\rangle,\langle S_0,R_{j1}\rangle)&=(0,1),\\
(\langle S_1,R_{j0}\rangle,\langle S_1,R_{j1}\rangle)&=(1,0).
\end{aligned}
\]

The broader compiler acceptance rule allows any ordered pair of distinct nonzero two-bit Tag-label vectors. The fixed pair above defines the narrower family used in this paper; the parent normalization covers it, and no claim about the broader label family is needed below.

For target triples \(T_{jk}\), an allowed target permutation, and central role \(c_j\in\{0,1,2\}\), let \(m_{jk}=2\) for \(k=c_j\) and \(m_{jk}=4\) otherwise. The frozen unit objective is

\[
C_I=
\sum_{j}\left[
\sum_{k=0}^2m_{jk}\bigl(w(R_{jk})-1\bigr)
+\sum_{k=0}^2w(T_{jk}R_{jk})
\right]
+2\bigl(w(S_0)+w(S_1)\bigr).
\]

For block \(j\), define its active-column set and the family statistic by

\[
U_j(x)=\operatorname{supp}(R_{j0})\cup\operatorname{supp}(R_{j1}),
\qquad
\sigma_I(x)=\max_{j\in\{A,B\}}|U_j(x)|.
\]

This joint statistic is essential. One rank-only word position represents one column \(q\in U_j(x)\), and its symbol is the parity-change vector induced by simultaneously replacing \((R_{j0,q},R_{j1,q})\) with \((I,I)\); the dependent letter \(R_{j2,q}\) then also becomes \(I\). The production transition is recorded in ten binary coordinates. For either block, its changes lie in and span a five-dimensional subspace, which is the alphabet used by the rank-only abstraction.

A zero-sum set of these block-column symbols preserves all five block parities. Objective soundness is a separate obligation: the exact local analysis covers all 46,080 active-letter, target-letter, Tag-letter, and central-role rows and finds that the new local contribution to \(C_I\) is at least four units smaller for every deleted active column. Because the objective is coordinate-additive and the Tags are held fixed, a simultaneous zero-sum deletion is therefore feasible and objective-nonincreasing. The compiler semantics additionally permit each dependent-triple block to be localized to one anticommuting core and the shared Tags to be reconstructed at whole-system scope.

Every comparison below keeps the relevant objective and support statistic fixed between \(\beta\) and \(\kappa\). Neither rank-only language is claimed to be a complete move registry for an external production implementation.

The enumerated block alphabets contain the following rank-five bases, written as integer encodings of their ambient 10-bit binary change vectors:

\[
B_A=(1,68,136,272,544),
\qquad
B_B=(2,4,8,16,32).
\]

Each basis word is nonzero-total and zero-sum-free. The block word is built from active columns, not from the support positions of one selected frame. Since \(P_{\mathrm{rank}}\) admits all nonzero-total words over the declared alphabet and has no rule other than zero-signature deletion, Corollary 5 gives the exact joint-column budget

\[
\beta_{P_{\mathrm{rank}}}(F_I;C_I)=5.
\]

The compiler can perform a transformation outside that language. It localizes both independent frames of each dependent-triple block to the same anticommuting core and then relocates or reconstructs the shared Tags. The fixed-objective exchange inequality pays for this transformation at every non-core coordinate. The all-size construction yields \(|U_A|=|U_B|=1\), while joint support zero is infeasible because two zero-supported frames cannot anticommute. Therefore

\[
\kappa(F_I;C_I)=1.
\]

**Theorem 9 (dependent-triple separation).** The exact separation is

\[
\kappa(F_I;C_I)=1
<5
=\beta_{P_{\mathrm{rank}}}(F_I;C_I).
\]

Thus both sides of the inequality use the same statistic \(\sigma_I\). The result diagnoses the operation missing from \(P_{\mathrm{rank}}\); it does not show that every stronger local or unrestricted proof system needs budget five.

## 10. Declared product amplification

Let \(F_I^t\) be the direct product of \(t\) independent \(F_I\) components on disjoint coordinates, with product objective \(C_I^{\oplus t}\) and support statistic \(\sigma_I^{\oplus t}(x_1,\ldots,x_t)=\sum_{h=1}^t\sigma_I(x_h)\). By definition, objectives and these component joint-column supports add, compiler moves remain componentwise, and the product proof system has no cross-component inference rule.

**Proposition 10 (componentwise product budgets).** For every integer \(t\geq 1\),

\[
\beta_{P_{\mathrm{rank}}}(F_I^t;C_I^{\oplus t})=5t,
\qquad
\kappa(F_I^t;C_I^{\oplus t})=t.
\]

**Proof.** Componentwise constructions give the upper bounds. In the direct-sum signature space, the union of the \(t\) disjoint five-vector bases is a zero-sum-free word of length \(5t\). The product calculus has no cross-component rule, so this word is terminal and supplies the matching rank-only lower bound. Intrinsically, every component needs joint active-column support at least one because support zero is infeasible, while the one-core normalization acts independently in each component. Additivity of \(\sigma_I^{\oplus t}\) gives the two equalities. \(\square\)

The additive gap is \(4t\), while the ratio remains five. This is a definitional amplification of the one-component mechanism, not an independent compiler phenomenon.

### 10.1 Direct-enumeration corollary

For a direct enumerator over \(n\) candidate block columns with fixed local alphabet and fixed joint active-column budget \(B\), the leading search volume is \(\Theta(n^B)\). At fixed \(t\), the declared product budgets therefore give volumes \(\Theta(n^{5t})\) and \(\Theta(n^t)\), with ratio \(\Theta(n^{4t})\) as \(n\to\infty\). The separate statement that the additive gap grows with \(t\) concerns a different limit. Neither statement is an algorithm-independent complexity lower bound.

## 11. Discussion and relation to prior work

The closest combinatorial donor is the subset-conditioned Davenport literature [3], with generalized and weighted variants providing broader context [4,5]. In the elementary binary grammar used here, however, the restricted-alphabet ceiling collapses exactly to the rank of the alphabet's generated span. The novelty therefore does not lie in a smaller zero-sum invariant. It lies in the compiler transfer: the admissible alphabet is fixed before optimization, deletion is sound for the entire instance, the global descent closes the simultaneous quantifier, and the Restore incidence exposes the exact objective condition.

Sparse integer optimization gives general support bounds for optimal solutions [6], while binary symplectic representations of Pauli operators are standard [8,9]. The present normal form is neither a generic sparsity theorem nor a new stabilizer formalism. It identifies when one local deletion operation preserves the semantics and objective of the stated compiler grammar.

The intrinsic-support comparison adds a second layer. Cook and Reckhow's account of relative proof-system efficiency provides the conceptual predecessor [7], but the quantities here are not propositional proof complexity. The rank-only calculus is an operational compiler certificate language with one shortening rule. The matched family shows that this language can be sharp when a separate compiler witness excludes smaller support. The dependent-triple family shows that it can also be loose when whole-system Tag reconstruction uses information the rank abstraction discards. Block-wise compiler frameworks such as Paulihedral illustrate more broadly why global transformations can escape termwise reasoning [2], but they do not supply the formal separation proved here.

The two families therefore serve different evidential roles within one paper. \(F_M\) validates the normal-form ceiling against intrinsic support under \(C_M\); \(F_I\) isolates a missing operation under \(C_I\). Neither result indicts local reasoning in general, establishes a lower bound for every richer proof system, or transfers the formal state language to a production compiler.

## 12. Reproducibility and adverse transfer record

The accompanying source binds the exact objectives, family definitions, signature alphabets, basis obstructions, support-two lower witness for \(F_M\), and dependent-triple lemmas for \(F_I\). One deterministic checker enumerates binary alphabets in dimensions one through three, checks the generated-span identity, verifies zero-sum deletion and global descent on finite fixtures, exhausts Restore sensitivity for \(b=2,\ldots,7\), and reproduces the exact two-site support-one obstruction. A second verifier exhausts 2,880 deletion rows, 6,912 core-alignment rows, 576 same-site rigidity rows, and 9,216 distinct-site Tag rows, then checks the composition arithmetic, support-zero obstruction, rank-five bases, and product statements. These finite computations corroborate transcription and bounded case analyses. They do not replace the all-size proofs or constitute external replication.

An earlier finite production-realization study of the matched family rejected its proposed certificate. The declared optimizer values were corroborated, but the study did not establish a complete production move registry; a source-bound follow-up again left production transfer unestablished. These are adverse transfer results, not failures of the formal normal-form or support-budget theorems. Their exact machine terminals remain in the accompanying provenance ledger.

A separate, prospectively ordered production-transfer attempt used pinned PyZX 0.10.5. It executed 74 of 4,681 ordered two-qubit circuit words before failing closed on three consecutive Hadamard gates on qubit 0. After a semantics-preserving prefix, the callable guard accepted a second boundary-pivot simplification that changed the dense linear map even up to a nonzero scalar, whereas the scheduled production reduction preserved the map on the same word. This result refutes only the proposed freely reorderable language of twelve macros under their callable guards. It does not refute the scheduled production reduction, establish complete move coverage, realize a certificate gap, or authorize a complete-domain null. The machine terminal remains `CANNOT_CHECK_MOVE_COMPLETENESS`: the round is consumed as an indeterminate completeness study and is not retuned or relabelled.

## 13. Limitations

The normal-form theorem is conditional on whole-instance deletion soundness, objective dominance, and support monotonicity. Its MultiTag specialization also requires the one-deletion/one-Restore-argument incidence contract. The binary rank identity applies only to the generated elementary-binary signature groups, and the proof is silent outside \(\mu\geq(b-1)t_R\). Failure of that inequality means only that this deletion proof is unavailable; it does not establish a larger-support necessity.

The certifiable-support values are relative to the explicitly defined rank-only calculus. We prove no lower bound for every local, syndrome-preserving, or unrestricted proof system. The \(F_M\) and \(F_I\) comparisons are tied to their stated objectives and support statistics. In particular, the \(F_I\) statistic is joint active-column support rather than maximum individual-frame weight. The product result additionally assumes additive support, additive objective, and no cross-component move or inference rule. Its enumeration exponent concerns the declared direct block-column enumerator rather than arbitrary algorithms.

These formal boundaries also limit physical interpretation. Structural support is not gate count, depth, runtime, qubit count, error rate, or quantum advantage. The adverse PyZX result shows that callable macro guards omit load-bearing scheduler context, so the formal families have not been established as complete production move languages. Finally, the author-side checks are not independent proof certification, novelty authority, peer review, or external replication. This work belongs to a single-author research programme using AI assistance, so the verification described here is author-side throughout and lacks the independent perspective of multi-author or externally replicated work.

## 14. Conclusion

A support certificate becomes a compiler normal form only after its semantic and objective obligations are proved, and a normal-form ceiling becomes an intrinsic value only after a separate lower witness excludes smaller optima. For the stated MultiTag grammar, global anticommutation supplies a nonzero signature total, Restore has exact one-argument sensitivity (b-1), and a global descent yields one optimum satisfying every frame ceiling. The matched family then shows that the resulting support-two ceiling can be intrinsic. The dependent-triple family supplies the complementary result: a rank-only budget of five over joint active columns can coexist with intrinsic support one because whole-system Tag reconstruction lies outside the certificate language. Together these results distinguish compiler structure from certificate-language structure without promoting the distinction into an unrestricted complexity or hardware claim.

## Data and code availability

The submission source contains the deterministic checkers, expected outputs, finite control records used for both formal families, and the immutable adverse PyZX transfer record summarized above. No external dataset is used. These artifacts corroborate finite case analyses and exact witnesses but do not establish external replication or production move completeness. The exact source archive is available to editors and referees with the manuscript and will accompany the public manuscript record.

## Author contributions

Sze Chun Yiu is the sole author and is responsible for the scientific claims and final manuscript. Generative AI tools assisted literature discovery, drafting, language editing, adversarial review, and submission-package preparation.

## References

1. N. Schillo, A. Sturm, and R. Quay, "TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation," [arXiv:2601.05740v4](https://arxiv.org/abs/2601.05740v4) [quant-ph] (2026).
2. G. Li, A. Wu, Y. Shi, A. Javadi-Abhari, Y. Ding, and Y. Xie, "Paulihedral: A Generalized Block-Wise Compiler Optimization Framework for Quantum Simulation Kernels," in *Proceedings of ASPLOS 2022*, 554-569 (2022), [DOI](https://doi.org/10.1145/3503222.3507715).
3. A. Plagne and S. Tringali, "The Davenport Constant of a Box," *Acta Arithmetica* **171**(3), 197-219 (2015), [DOI](https://doi.org/10.4064/aa171-3-1).
4. M. Freeze and W. A. Schmid, "Remarks on a Generalization of the Davenport Constant," *Discrete Mathematics* **310**(23), 3373-3389 (2010), [DOI](https://doi.org/10.1016/j.disc.2010.07.028).
5. G. Wang, "The Universal Zero-Sum Invariant and Weighted Zero-Sum for Infinite Abelian Groups," *Communications in Algebra* **53**(4), 1581-1599 (2025), [DOI](https://doi.org/10.1080/00927872.2024.2418017).
6. I. Aliev, J. A. De Loera, F. Eisenbrand, T. Oertel, and R. Weismantel, "The Support of Integer Optimal Solutions," *SIAM Journal on Optimization* **28**(3), 2152-2157 (2018), [DOI](https://doi.org/10.1137/17M1162792).
7. S. A. Cook and R. A. Reckhow, "The Relative Efficiency of Propositional Proof Systems," *Journal of Symbolic Logic* **44**(1), 36-50 (1979), [DOI](https://doi.org/10.2307/2273702).
8. J. Dehaene and B. De Moor, "Clifford Group, Stabilizer States, and Linear and Quadratic Operations over GF(2)," *Physical Review A* **68**(4), 042318 (2003), [DOI](https://doi.org/10.1103/PhysRevA.68.042318).
9. S. Aaronson and D. Gottesman, "Improved Simulation of Stabilizer Circuits," *Physical Review A* **70**(5), 052328 (2004), [DOI](https://doi.org/10.1103/PhysRevA.70.052328).
