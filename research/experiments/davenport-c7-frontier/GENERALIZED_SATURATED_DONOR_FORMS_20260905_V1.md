# Generalized saturated-donor forms and the remaining Davenport target — 2026-09-05

Status: **the two inverse classifications below are proved, including their converses**. The all-prime, all-multiwise-level Davenport formula remains a research target. This checkpoint distinguishes the generalized structural form actually obtained from the global equality that has not been proved.

## 1. One notation for both exceptional types

Let \(p=2H+1\) be prime, put \(m=p+H=(3p-1)/2\), and fix a basis \((f_1,f_2,f_3)\) of \(C_p^3\). For \(a\in\{1,2\}\), define

\[
s_a=a^{-1}(f_1+f_2)+f_3,
\qquad
\mathcal F_{a,K}(y)=f_1^{p-1}f_2^{p-1}f_3^{p-1}s_a^K y^{p-1}.
\]

Coordinates below refer to this basis. Say that a sequence is **short-free below \(m\)** if it contains no nonempty zero-sum subsequence of length less than \(m\). This threshold differs from the exponent-short-free condition used in the global packing-defect reduction.

The following is the generalized inverse form established in this continuation:

| Type and domain | Exact condition for \(\mathcal F_{a,K}(y)\) to be short-free below \(m\) |
|---|---|
| \(a=1\), \(p\ge5\), \(K\ge1\) | \(K\le\lfloor(p+1)/4\rfloor\), and \(y\) is a coordinate permutation of \((1,b,-b)\), \(b\ne0\). |
| \(a=2\), \(p\ge7\), \(3\le K\le H+1\) | \(y=(A,-A,1)\), \(A\ne0\); additionally \(y=(\pm3^{-1},\mp3^{-1},2)\) is allowed exactly when \(K=3\) or \((p,K)=(11,4)\). |

These are equivalences. Every listed value actually survives every subsequence test on the displayed donor, and every omitted value has an occurrence-valid shorter zero-sum. The second row's four-copy exception at \(p=11\) is real; five copies eliminate it. No companion relation, atomicity, or new-support hypothesis is needed for either classification.

Complete proofs:

- [Type-one inverse classification and sharp threshold](A1_SATURATED_AUGMENTATION_ELIMINATION_V1.md).
- [Type-two constant-donor classification and exact exceptions](A2_CONSTANT_DONOR_INVERSE_CLASSIFICATION_V1.md).
- [Underlying six-entry pairing and two-point anomaly elimination](A2_RANK3_EXTREME_FULL_ELIMINATION_V1.md).

## 2. Why these are structural proofs

For a saturated extra value \(y=(A,B,C)\), complete each power \(y^j\) using the three saturated basis values. Its length is

\[
L_j=j+[-jA]_p+[-jB]_p+[-jC]_p.
\]

Nonzero coordinates give the complementary identity \(L_j+L_{p-j}=4p\). Replacing selected basis occurrences by one, two, or three copies of \(s_a\) tightens the permitted interval of these lengths.

For type one, that interval is too narrow to accommodate distinct residues unless \(A+B+C=1\). An established four-entry Bernoulli-pairing theorem gives the coordinate family; a parity-aware interval argument identifies the exact donor threshold.

For type two, the saturated lengths have only a centered pattern or a two-point anomaly. Six-entry Bernoulli pairing classifies the centered pattern. Donor substitutions normalize the anomaly, and the symbolic multipliers \(p-3\) and \(p-5\) eliminate it, with an explicit endpoint certificate at \(p=7\). The remaining plane family is then classified exactly with three, four, and five donor copies.

The Bernoulli-pairing theorem is an attributed external input, not an ORION novelty claim. [Batyrev--Hofscheier, Proposition 1.8](https://arxiv.org/pdf/1004.3411). No prime sweep or enumeration of hypothetical companions supplies these proofs.

## 3. Consequences for the active frontier

The previous continuation closed the entire exceptional \(a=3\) rank-three boundary. This continuation supplies the following additional results:

- **The entire saturated \(a=2\) rank-three boundary is empty:** for every prime \(p\ge7\) and every \(1\le c\le H-1\), a zero-sum companion \(V=s^c g x^{H-c}y^{p-1}\) forces a zero-sum shorter than \(m\) in its product with the canonical maximal atom. This includes the original extreme row. The complete proof is assembled from [the one-share theorem](A2_RANK3_ONE_SHARE_SATURATED_ELIMINATION_V1.md), [the two- and three-share theorem](A2_RANK3_SATURATED_BOUNDARY_C2_C3_ELIMINATION_V1.md), and [the theorem for every overlap at least four](A2_RANK3_SATURATED_BOUNDARY_C_GE4_ELIMINATION_V1.md).
- The complementary mechanisms behind this whole-boundary result are explicit. Adaptive circular gaps eliminate \(p<(c+1)^2\); a generalized prime-multiple selector covers the complementary range after elementary remainder distinctions. At \(c=1\), the actual power \(x^{H-4}\) eliminates both inverse families uniformly for \(p\ge11\), with four sign-orbit certificates at \(p=7\). See [the mixed gap theorem](A2_RANK3_SATURATED_BOUNDARY_CIRCULAR_GAP_ELIMINATION_V1.md) and [the generalized remainder theorem](A2_RANK3_SATURATED_BOUNDARY_SMALL_OVERLAP_ELIMINATION_V1.md).
- The rank-two \(a=2\) endpoints \((c,r,t)=(H,1,p-1)\) and \((H-1,2,p-1)\) are empty. Equal-sum exchanges create maximal atoms with a saturated new value; quotient structure gives the contradiction. See [the singleton endpoint](A2_RANK2_TOP_SINGLETON_QUOTIENT_ELIMINATION_V1.md) and [the two-occurrence endpoint](A2_RANK2_TWO_NEW_OCCURRENCES_ENDPOINT_ELIMINATION_V1.md).
- For \(a=1\), the whole rank-two \(t=p-1\) boundary is eliminated whenever \(c\ge\lfloor(p+1)/4\rfloor\). For both light types, all rank-two overlap layers with \(2\le c\) and \(4c^2\le p\) are empty. See [the type-one corollary](A1_SATURATED_AUGMENTATION_ELIMINATION_V1.md) and [the positive-even selector](RANK2_POSITIVE_EVEN_GENERAL_SELECTOR_V1.md).
- Even without shared donor occurrences, a saturated type-two extension must have nonzero coordinates and \(T=1-A-B-C\in\{0,C/2,-C/2\}\). See [the three-plane restriction](A2_SATURATED_VALUE_THREE_PLANE_RIGIDITY_V1.md).

The quotient theorem used for the rank-two two-occurrence endpoint is a published prime-uniform result whose authors use bounded computer-assisted inputs. Its provenance is explicit in that proof note. The present continuation performs no brute-force search and does not relabel that donor as an independently elementary proof.

## 4. Exact global target and the proved reduction

The desired global formula is

\[
D_k(C_p^3)=kp+\frac{5(p-1)}2
\qquad(p\ge5,\ k\ge2).
\]

The established \(k=2\) value and the matching lower line do not prove this equality for later levels. In the block formulation, the missing statement is the uniform inequality

\[
|B|-p\,z(B)\le\frac{5(p-1)}2
\]

for every zero-sum block \(B\), where \(z(B)\) is its largest number of zero-sum factors.

The new global result is a **reduction**: for all sufficiently large primes, it suffices to prove the line at levels \(2\le k\le7\). One prime threshold works simultaneously for every prime power \(p^a\), with \(p^a\) replacing \(p\) in the line. The threshold is not numerically specified; in particular this does not put \(p=7\) into the asymptotic regime. There is also an explicit all-prime cutoff of \(20229\) levels. See [the complete constant-level reduction](GENERAL_FORM_CONSTANT_LEVEL_REDUCTION_V1.md).

The recent donor bound used for the seven-level reduction is Zakharov's proved \(s(C_p^3)\le(11+o(1))p\), from Theorem 1.2 and Proposition 1.3. The mentioned but omitted argument for the stronger constant \(9\) is not imported. [Zakharov, published version](https://arxiv.org/html/2002.09892v6).

## 5. Preserved failures and remaining scope

The exact inverse converses explain why pure-power donor tests cannot finish the mixed problem: the main type-two family really survives those tests. Likewise, every optimized relation scalar fails on the two-parameter rank-two family \(p=4Rk+1\), \((c,r,t)=(H+1-R,R,p-1)\). This is a theorem about a method's limitation, not a construction of a full companion. See [the exact scalar barrier](A2_RANK2_EXACT_SCALAR_BARRIER_V1.md).

The circular-gap note also preserves an infinite obstruction to its particular all-\(x\) certificate, and corrects a discarded partial-\(x\) projection that omitted the shared \(s\) contribution. The correct coordinate is \(x_3=-c/(H-c)\), not zero.

No saturated-new-value rank-three row remains. Combining the new theorem with the earlier doubling and overlap bounds, every surviving exceptional rank-three type-two row must have

\[
d=1,\qquad 1\le c\le2\lfloor H/2\rfloor,\qquad
r=H-k,\qquad t=p-c-1+k,\qquad 0\le k\le c-1.
\]

In particular, both new multiplicities are at most \(p-2\). The earlier balanced-band eliminations continue to apply inside this smaller strip. These unsaturated rank-three rows and the remaining rank-two high-overlap families are still open.

The full all-prime first-corridor theorem and \(D_3(C_7^3)\) are not proved or claimed by this checkpoint.

## 6. Continuation and verification record

Work began from the published continuation head `eea6aeafd767773ddf095e34417b8da5345bbe21`, which preserves the user's original `86f089ab` baseline and the preceding exceptional-type-three closure. The active checkout is the session-owned branch `shadow/davenport-general-form-20260905`.

Before research and again before publication, all 24 visible Davenport branch heads were checked. No newer external-session head displaced the live branch or supplied stronger work to absorb. The earlier detailed branch inventory remains in `DAVENPORT_BRANCH_AUDIT_20260905_V1.md`; this continuation adds only new proof notes and this checkpoint.

Each mathematical advance receives its own commit. The proof notes record independent internal review of the exact hypotheses, residue identities, occurrence capacities, converse arguments, and donor-source mappings. Git formatting checks supplement those mathematical audits; no machine calculation is being substituted for theorem authority. No manuscript or global claim ledger is promoted.
