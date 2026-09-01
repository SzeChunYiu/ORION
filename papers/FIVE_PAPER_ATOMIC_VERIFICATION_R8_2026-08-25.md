# Five-Paper Atomic Verification Ledger R8

Date: 2026-08-25

Scope: mathematical claims added or materially re-scoped in the recovered V3 plus R4 campaign.

Verdicts:

- `VERIFIED`: complete proof is present in the repository and the assumptions are explicit.
- `VERIFIED_CONDITIONAL`: proof is complete once a named premise or external donor theorem is granted.
- `FINITE_REPLAY`: an executable finite sanity check passes; this is supporting evidence, not a universal proof.
- `EXTERNAL_DONOR`: theorem is owned by prior literature and must be cited, not claimed as new.
- `UNRESOLVED`: not proved in the current branch.
- `NOT_CLAIMED`: deliberately outside scope.

## 1. Paper A

| ID | Atomic claim | Evidence route | Verdict | Boundary |
|---|---|---|---|---|
| A-R4-01 | Axis-separated restricted-alphabet invariant is additive under direct sum. | Split any zero-sum-free word by axes for the upper bound; concatenate maximum component words for the lower bound. | `VERIFIED` | Alphabet must contain only coordinate-axis letters. |
| A-R4-02 | Finite axis direct sums have invariant equal to the sum of component invariants. | Induction from A-R4-01. | `VERIFIED` | Same axis-separation premise. |
| A-R4-03 | For a homomorphism `phi:H->K`, `zsf(H;A)>=zsf(K;phi(A))`. | Lift every occurrence of a maximum image word; a source zero sum would map to an image zero sum. | `VERIFIED` | This is a lower obstruction, not an upper bound. |
| A-R4-04 | The invariant has a finite multiplicity formulation with `0<=u_i<ord(a_i)`. | A zero-sum-free word cannot contain `ord(a_i)` copies of one letter; remaining constraints are exactly nonzero submultiset sums. | `VERIFIED` | No polynomial-time claim. |
| A-R4-05 | Per-event defect at most `epsilon` yields support at most `z` and cost at most `OPT+epsilon max(0,n-z)`. | Iterative deletion; each step reduces support by at least one; telescope at most `n-z` defects. | `VERIFIED_CONDITIONAL` | Semantic deletion and nonzero-total hypotheses must persist. |
| A-R4-06 | Per-coordinate defect at most `delta|T|` yields support at most `z` and cost at most `OPT+delta n`. | Deleted coordinate sets are disjoint; total deleted coordinates are at most `n`. | `VERIFIED_CONDITIONAL` | Structural objective only. |
| A-R4-07 | In the declared MultiTag grammar, `delta=max(0,(b-1)t_R-mu)` is a valid local defect coefficient. | V3 local cost sensitivity: at most `(b-1)t_R` added Restore cost and at least `mu` refunded per coordinate. | `VERIFIED_CONDITIONAL` | Requires the frozen V3 grammar. |
| A-R4-08 | The small direct-sum and quotient examples in the verifier agree with the theorems. | `verify_five_math_extensions_r4_v2.py`. | `FINITE_REPLAY` | Examples only. |
| A-GATE-01 | The abstract grammar faithfully models a production TARE optimization. | No complete production equivalence proof in the branch. | `UNRESOLVED` | Must not be inferred from motivation. |
| A-GATE-02 | Support normalization improves T count, depth, fidelity, or hardware performance. | Those quantities are not the theorem objective. | `NOT_CLAIMED` | Requires separate compiler/physical evidence. |

## 2. Paper B

| ID | Atomic claim | Evidence route | Verdict | Boundary |
|---|---|---|---|---|
| B-R4-01 | Terminal complexity of an independent product of finite attained shortening systems is the sum of component terminal complexities. | A product tuple is terminal iff each component is terminal. | `VERIFIED` | Components and moves must be independent. |
| B-R4-02 | Intrinsic support of independent compiler products is additive under component normalizations and lower witnesses. | Apply normalizations for the upper bound; take the product of lower-witness instances for the lower bound. | `VERIFIED_CONDITIONAL` | Cartesian feasibility, additive objective, no cross moves. |
| B-R4-03 | The four-part production-realization criterion is sufficient for exact production certificate complexity `beta(P)`. | Abstract normalization gives the upper bound; a production preimage terminal under every named proof rule gives the lower bound. | `VERIFIED` | Exact only for the named production proof system. |
| B-R4-04 | If proof language `Q` contains all moves of `P`, then `beta_Q(F)<=beta_P(F)`. | Every `Q`-terminal state is `P`-terminal. | `VERIFIED` | Both proof languages must be sound on the same state family. |
| B-R4-05 | `V_B(n)=sum_{j=0}^B binom(n,j)q^j=Theta(n^B)` for fixed `B,q>=1`. | Leading polynomial term `binom(n,B)q^B`. | `VERIFIED` | Fixed budget and label count. |
| B-R4-06 | For fixed `B>K`, `V_B(n)/V_K(n)=Theta(n^(B-K))`. | Divide leading asymptotics. | `VERIFIED` | Enumerator architecture only. |
| B-R4-07 | Product certificate gaps add and direct-enumeration exponent gaps add once every component realization and intrinsic lower witness is proved. | Combine B-R4-01, B-R4-02, and B-R4-06. | `VERIFIED_CONDITIONAL` | All component gates are load-bearing. |
| B-R4-08 | Finite product arithmetic and normalized enumeration ratios pass replay. | `verify_five_math_extensions_r4_v2.py`. | `FINITE_REPLAY` | Arithmetic only. |
| B-GATE-01 | The current dependent-triple compiler has production certificate complexity five per component. | Abstract terminal word exists; production realization/nonreducibility is not established. | `UNRESOLVED` | Central numerical production claim. |
| B-GATE-02 | The exponent comparison is an algorithm-independent time lower bound. | The theorem counts one declared enumeration architecture. | `NOT_CLAIMED` | Other algorithms may use different state spaces. |

## 3. Paper C

| ID | Atomic claim | Evidence route | Verdict | Boundary |
|---|---|---|---|---|
| C-R4-01 | Deterministic absolute minimax radius of a representation fiber is half its target diameter. | Endpoint triangle inequality and midpoint attainment. | `VERIFIED` | Finite real-valued target. |
| C-R4-02 | Integer-output minimax radius is `ceil(d_y/2)`. | Round the real midpoint; lower bound is the rounded real radius. | `VERIFIED` | Integer-valued target and estimator. |
| C-R4-03 | Randomization cannot lower worst expected absolute loss below `d_y/2`. | Take expectation of `|Z-a|+|Z-b|>=d_y`. | `VERIFIED` | Estimator distribution depends only on the representation. |
| C-R4-04 | Randomized squared-loss minimax risk is `d_y^2/4`. | Endpoint-average identity around the midpoint; deterministic midpoint attains. | `VERIFIED` | Same representation-only restriction. |
| C-R4-05 | Any exactly valid representation-only interval has width at least the fiber diameter. | It must contain both endpoint target values. | `VERIFIED` | Exact all-instance coverage, not probabilistic coverage. |
| C-R4-06 | Opposite Boolean instance properties in one fiber force randomized worst-case classification error at least `1/2`. | Errors are `q` and `1-q`. | `VERIFIED` | Property must be well-defined despite nonunique optima. |
| C-R4-07 | No single optimizer can certify two fiber members with disjoint optimizer sets. | A valid candidate set must intersect each optimizer set. | `VERIFIED` | Set-valued certificate formulation. |
| C-R4-08 | V3 pair family gives diameter `2t-1`, integer radius `t`, and the corresponding absolute/squared/interval bounds. | Substitute exact V3 values `12t-2` and `10t-1`. | `VERIFIED_CONDITIONAL` | Depends on exact V3 feature equality and optimum proofs. |
| C-R4-09 | V3 high-order parity fiber yields unbounded representation-only error for fixed order and growing scale. | Substitute the V3 exact gap `G(m,L)` into C-R4-01–05. | `VERIFIED_CONDITIONAL` | Depends on the V3 parity and Möbius theorem chain. |
| C-R4-10 | Representative fiber radii pass finite replay. | `verify_five_math_extensions_r4_v2.py`. | `FINITE_REPLAY` | Arithmetic examples only. |
| C-DONOR-01 | Two-point minimax and midpoint arguments are generic prior mathematics. | Explicit donor boundary in the addendum. | `EXTERNAL_DONOR` | Novelty rests on exact compiler fibers and query separation. |
| C-GATE-01 | Every V3 family proof has received independent external hostile replay. | Internal replay only in this campaign. | `UNRESOLVED` | Required before selective submission. |
| C-GATE-02 | A model receiving richer information than `Phi` obeys the same lower bound. | The theorem is representation-specific. | `NOT_CLAIMED` | Enriching inputs changes fibers. |

## 4. Paper D

| ID | Atomic claim | Evidence route | Verdict | Boundary |
|---|---|---|---|---|
| D-R4-01 | Membership of one license in the set-valued least fixed point equals reachability in a positive Horn system. | Project every Kleene approximant onto one Boolean license coordinate. | `VERIFIED` | Positive rules and frozen direct-refutation semantics. |
| D-R4-02 | Fixed-refutation evaluation is `O(M)` per license and `O(|Lambda|M)` for all licenses. | Standard counters-and-worklist Horn closure; each incidence processed once. | `VERIFIED` | Explicit incidence representation and preprocessed membership. |
| D-R4-03 | A refutation blocks target license iff it hits every inclusion-minimal finite proof footprint. | V3 finite proof-tree theorem plus footprint disjointness. | `VERIFIED` | Least-fixed-point, seed-founded proofs. |
| D-R4-04 | Minimal seed interventions are hitting sets of minimal leaf-support families. | Restrict D-R4-03 to refutable seed leaves. | `VERIFIED` | Only designated seed claims may be refuted. |
| D-R4-05 | `SEED-BLOCKER` is in NP. | Verify a proposed seed set by D-R4-02. | `VERIFIED` | Finite explicit graph. |
| D-R4-06 | `SEED-BLOCKER` is NP-hard on depth-two acyclic graphs. | Polynomial reduction from HITTING SET using conjunctive set nodes and singleton target rules. | `VERIFIED` | One license; declared rule construction. |
| D-R4-07 | Weighted seed intervention is the corresponding weighted hitting-set optimization. | Same support family with seed costs. | `VERIFIED` | Generic weighted-hardness donor boundary. |
| D-R4-08 | Every subset in the finite reduction example satisfies “hitting set iff target blocked.” | `verify_five_math_extensions_r4_v2.py`. | `FINITE_REPLAY` | Example only. |
| D-DONOR-01 | Generic hitting-set hardness and provenance-witness ideas are prior mathematics. | Explicitly not claimed as generic novelty. | `EXTERNAL_DONOR` | Paper-specific claim is the frozen license semantics and derived boundary. |
| D-GATE-01 | The framework is novel relative to all database provenance, resilience, and abduction models. | Full primary-source overlap audit not yet complete. | `UNRESOLVED` | Editorial novelty gate. |
| D-GATE-02 | Authority equals truth or legal compliance. | Model tracks declared licenses under rules. | `NOT_CLAIMED` | Domain validation is separate. |

## 5. Non-quantum paper

| ID | Atomic claim | Evidence route | Verdict | Boundary |
|---|---|---|---|---|
| NQ-V3-01 | Saturated length-31 5-short-free total-zero sequences have multiplicities in `{1,2,4}`. | Recovered V3 saturation and extraction argument. | `VERIFIED_CONDITIONAL` | Depends on the V3 theorem chain. |
| NQ-V3-02 | `c_2=31-s-3c_4`, `c_1=2s-31+2c_4`, and `|H|=62-2(s+c_4)`. | Eliminate variables from support and length equations. | `VERIFIED` | Pure arithmetic. |
| NQ-DONOR-01 | `eta(C_5^2)=13`. | Rank-two short zero-sum literature. | `EXTERNAL_DONOR` | Final bibliography must cite a primary source. |
| NQ-DONOR-02 | Every length-12 5-short-free sequence in `C_5^2` has Property-C form `T^4`, `|T|=3`. | Property C is known for the relevant modulus. | `EXTERNAL_DONOR` | This inverse theorem is load-bearing. |
| NQ-R4-01 | A length-12 boundary subsequence cannot have rank one. | `D(C_5)=5`: five terms in a cyclic subgroup contain a nonempty zero sum of length at most five. | `VERIFIED_CONDITIONAL` | Uses classical cyclic Davenport theorem. |
| NQ-R4-02 | If `s+c_4=25` and `rank(H)<=2`, then `(s,c_1,c_2,c_4)=(22,19,0,3)`. | Apply Property C; distinctness forces three multiplicity-four points; substitute multiplicity equations. | `VERIFIED_CONDITIONAL` | Depends on NQ-DONOR-02. |
| NQ-R4-03 | For `s>=23` and `s+c_4<=25`, `rank(H)=3`. | V3 handles `<=24`; equality 25 contradicts NQ-R4-02. | `VERIFIED_CONDITIONAL` | Same V3 and donor premises. |
| NQ-R4-04 | Branches `(23,2)`, `(24,1)`, `(25,0)` in `(s,c_4)` are newly full-rank. | They are exactly the feasible `s>=23` rows on `s+c_4=25`. | `VERIFIED` | Arithmetic plus NQ-R4-03. |
| NQ-R4-05 | Every such residual sequence has a basis contained in the repeated stratum. | A rank-three support contains a three-element basis. | `VERIFIED` | Basis elements have multiplicity at least two by definition of `H`. |
| NQ-R4-06 | Correct boundary arithmetic and the unique low-rank profile pass finite replay. | `verify_five_math_extensions_r4_v2.py`. | `FINITE_REPLAY` | Does not replay Property C. |
| NQ-GATE-01 | `C_0(31)` holds. | No complete proof in the branch. | `UNRESOLVED` | Central exact gate. |
| NQ-GATE-02 | The exact value of `D_4(C_5^3)` is established. | Depends on NQ-GATE-01 or equivalent complete argument. | `UNRESOLVED` | Must not appear as a theorem in title/abstract. |
| NQ-GATE-03 | The support-through-22 computation has an independent complete replay. | Internal artifacts exist; independent replay remains absent. | `UNRESOLVED` | Computational-evidence gate. |
| NQ-GATE-04 | Projective squarefreeness holds for all length-12 or length-13 atoms. | No proof; the branch explicitly warns against this shortcut. | `NOT_CLAIMED` | Requires an independent theorem. |

## 6. Cross-paper verification controls

| ID | Control | Result | Verdict |
|---|---|---|---|
| X-R8-01 | Every new theorem states the model and quantifier boundary before its application interpretation. | Present in all five addenda. | `VERIFIED` |
| X-R8-02 | Generic donor mathematics is separated from paper-specific contribution. | Explicit for minimax, hitting set, cyclic/rank-two zero-sum theory. | `VERIFIED` pending final bibliographic metadata. |
| X-R8-03 | False historical V2 claims are not reintroduced. | D uses least fixed point; NQ uses corrected saturation. | `VERIFIED` |
| X-R8-04 | The first verifier's erroneous expected diagonal is superseded transparently. | V2 verifier documents and corrects it. | `VERIFIED` |
| X-R8-05 | The canonical finite verifier exits with `status: PASS`. | Exact committed V2 script was downloaded and executed after commit. | `FINITE_REPLAY` |
| X-R8-06 | No paper claims production, empirical, legal, physical, or exact-threshold impact beyond proved scope. | Application map lists prohibited overclaims. | `VERIFIED` |

## 7. Load-bearing unresolved gates

These are not cosmetic tasks. They determine whether the associated manuscript can honestly support its most ambitious editorial positioning.

1. **Paper A:** production-faithful grammar or a broader domain-independent theorem application.
2. **Paper B:** a realizing production terminal witness and proof of nonreducibility under every named compiler rule.
3. **Paper C:** independent hostile replay of exact family constructions plus primary-source overlap calibration.
4. **Paper D:** primary-source provenance/resilience comparison plus one domain-faithful worked instance.
5. **Non-quantum:** a complete `C_0(31)` argument, decisive atom-overlap theorem, or independently replayed exhaustive classification.

The branch is therefore theorem-rich and submission-oriented, but its readiness labels remain paper-specific rather than uniformly “top-tier ready.”