# Internal adversarial referee pass — ORION-QG quantum-compilation lane
(C1, QG-34, QG-35, QG-35b/32c, QG-36, QG-39). NOT an external expert review.

## VERDICT: REJECT as a top-tier submission.

**Scope of the REJECT.** It attaches to the list of *claimed contributions as
presented for review* — where these are framed as impossibility theorems that
sharpen QG-2 and price information content. It does NOT attach to the atoms as
internal machine-checked notes. Every document carries `novelty_claim: false`,
`proof_authority: false`, `mathematical_result_credit: false`; QG-35 says
outright it was "found by exploration" with no freeze; QG-36 states its
assumption and that the result "does not apply" without it; QG-39 stamps
`NOT_R6` and names the hardware-calibration gap as unclosed. Those authority
blocks are honest. The defect is entirely in the promotion from
"machine-checked proposal" to "contribution".

## 0. Arithmetic: everything reproduces. Zero discrepancies.
Rebuilt from base primitives (p10 / r6s), no cached JSON:
715 reps, 384 probes, bulk 45, spectrum 54, joint 92, histogram
{1:7,2:22,3:6,4:6,6:25,8:2,12:14,24:8,48:2}; C1: 54 = orbits under
S_3 x (S_2 wr S_3), 0 spectrum changes under wreath, 168 bulk changes,
48-coordinate control = 50; QG-35: 646 argmin sets, 85/92, 708/715, 352/384,
existence quantities 0/92; QG-34: D_*=3, {0:7,1:30,2:39,3:16}, 16 worst
(sizes 6/12/24/48), depth-2 infeasibility on all 16, arity tight 80/92;
QG-32c: 168 masks, C(168,4)=32,018,910, F*=4 hist {0:7,1:30,2:33,3:19,4:3},
U*=5 exact (no 4-cover, 5-cover exists); QG-36 witness 3 vs 4; QG-39 regret
5/3/2/0 with 76/45/7/0. All confirmed independently.

## 1. THE FATAL OBJECTION — the headline numbers are null-reproducible.
Null: keep bulk, spectrum, the 92 joint classes and every existence quantity
EXACTLY; randomise only frame-index alignment (shuffle each response row).
This destroys all TARE content in the only place the claims read it.

            classes split  types    D_*  depth dist            F*  U*  regret 0..3
REAL            85/92      708/715    3   {0:7,1:30,2:39,3:16}  4   5   5,3,2,0
NULL seed 1     85/92      708/715    3   {0:7,1:42,2:34,3:9}   4   5   5,3,1,0
NULL seed 2     85/92      708/715    3   {0:7,1:40,2:36,3:9}   4   -   5,3,1,0
NULL seed 3     85/92      708/715    3   {0:7,1:43,2:33,3:9}   4   -   5,3,1,0

QG-35(b)'s 85/92 and 708/715, QG-34's D_*=3, QG-32c's F*=4 and QG-39's
headline magnitude (worst-case regret 5 at budget 0, falling to 0 at 3) all
survive the destruction of the object being studied. So does QG-32c's entire
hierarchy 3 < 4 < 5. The U* null is the sharpest single line in this report:
the shuffled table has 384 distinct coverage masks against the real table's
168, each covering MORE same-class pairs (4299 vs 4173 of 5895) — it is
strictly easier to cover — and it still needs exactly 5, with no 4-cover.

**Pre-empting the obvious defense.** The depth *distributions* do differ: the
real table has 16 classes at depth 3, the null 9. An author will say the real
instance is strictly harder than random. It does not rescue the claim. The
reported quantity is a max, both maxes are 3, and 3 is forced from below (next
paragraph). Extra hardness raises how many classes are tight against a bound
that was already binding; it does not move the number being reported. The same
holds for regret: the real curve is uniformly at or above the null, but the
headline "it loses 5" is exactly what shuffling gives.

Worse, the two counts are identities. Every non-singleton class splits, and
exactly 7 classes are singletons: "85 of 92" IS "92 minus 7 singletons";
"708 of 715" IS "715 minus 7 singleton types". Both are restatements of the
class-size histogram — which the QG-34 freeze prints before any solver ran.
And D_* >= 3 = ceil(log_6 48) follows from that same class-size histogram plus
the computed max arity of 6, so the solver was needed only for achievability.
(Stated carefully: the bound does depend on knowing arity is 6, not the full
11-value range of K — ceil(log_11 48) = 2 — and QG-34's freeze requires arity
bounds be reported rather than pre-stating them. The deflation is that the
lower bound is information-theoretic and the Bellman run, the depth-2
certificate and the independent re-derivation all certify the easy half.)

## 2. Each remaining "theorem" reduces to something standard.
- QG-35(a) is a tautology. Source: `spec = sorted(row)`. The spectrum IS the
  achievable-cost multiset. "Every function of the multiset is determined by
  the multiset." The 0/92 verification is a unit test of `sorted`.
- QG-35(b) qualitative is pigeonhole: 646 distinct optimal-frame sets, 92
  classes, 646 > 92. One line.
- C1's conceptual claim is already KILLED by the programme's OWN prior-art
  audit (QG_DESCRIPTOR_AUDIT_PRIOR_ART_VERDICT.md): Lehmann's maximal
  invariant (1959) Def.9/Thm.4 is verbatim the ceiling theorem; the procedure
  is the standard GNN-expressivity instrument; Derksen-Kemper separating
  invariants own the algebra. That audit asked the team lead to read the
  spectrum's literal definition. I did: `sorted(row)` — a canonical form in
  both factors jointly, i.e. the "by construction" branch the audit named.
- QG-36 is min-of-sum != sum-of-min, under an assumption the document admits
  is not derived and under which the result "does not apply" if false.

## 3. No parameterised family. Ever.
`f3`/`_factor_support_fast` are 3-argument; TARE-3 fixes 6 letters, so the
alphabet is 4^6 for ALL n (that is QG-28's all-n theorem). There is no
parameter in which D_* could grow. This is one 715x384 integer table, and no
argument here survives perturbing one entry.

## 4. The framing claim is a non-sequitur.
"Sharpens QG-2 from a search-negative to an information-negative" is false.
QG-2's target is `donor_exact` — an EXISTENCE predicate, under reweighted
objective O1. QG-35(a) lists "is the donor optimal?" among the quantities
that split 0 of 92, i.e. QG-35 says QG-2's target is information-free.
Different predicate, different objective, opposite sign. QG-35 does not
sharpen QG-2; it is orthogonal to it.

Also: bulk+spectrum is a strawman. C1 establishes it as the symmetry quotient
— index-forgetting BY CONSTRUCTION. QG-35(b)/QG-36 then show an
index-forgetting summary cannot answer index-dependent questions.

## 5. Charter (v) is undischarged, by the atoms' own text.
QG-34's freeze: "No adaptive depth is predicted here." QG-35/36/39: "no
pre-outcome freeze is claimed." Nothing forecasts anything.

## 6. Objective mis-specification (addressable, not fatal).
K = config_cost - baseline(p) while minimising OVER p: improvement measured
against a moving reference. On 168/715 types argmin(K) != argmin(config_cost),
DISJOINT on 108, and the best "optimal" frame costs +1 or +2 more than the
true optimum. Every printed witness frame set is an argmin of the wrong
quantity. It does not overturn the theorems: 85/92, 708/715, 352/384, D_*=3
and regret 5/3/2/0 are identical under true cost.

## 7. WHAT SURVIVES MY ATTACK — stated explicitly.
Only (a) and (b). I tested (c) and (d) hoping they would survive; they did not,
and I report that rather than leaving them as open doubt.
(a) C1(b), completeness. The null does NOT touch it (row-shuffling preserves
    the spectrum by construction), and a genuinely random cost would break it.
    That the sorted-384 descriptor is a COMPLETE (maximal) invariant for
    S_3 x (S_2 wr S_3) — not merely invariant — is a real, table-specific fact
    that could have failed, with an honest falsification control (48
    coordinates -> 50 classes, merging 4 orbits). It is an instance of
    textbook theory, but the instance is genuine and correctly certified.
(b) Witness DISJOINTNESS. Pigeonhole gives "different"; it does not give
    disjoint. All three pairs are disjoint under BOTH objectives. This kills
    an "intersect the candidate sets" fallback, and is the one selection claim
    with content beyond counting.
(c) U* = 5 and the hierarchy 3 < 4 < 5. DOES NOT SURVIVE. I gave this the best
    chance of being the surviving claim and null-tested it exactly: the null
    also gives U* = 5 (and F* = 4, D_* = 3). QG-32c is swallowed whole.
(d) The 45/54/92 partition arithmetic and the ps[:4] choice. I attacked the
    truncation as arbitrary; it is not — bulk over all 8 gives the identical
    45/92 partition. Objection withdrawn.

## 8. Strongest defensible claim.
"For one fixed 715x384 cost table arising from TARE-3, the sorted-response
descriptor is a maximal invariant for S_3 x (S_2 wr S_3); the residual
frame-selection information is position-asymmetric; and three adaptive
indexed probes suffice to recover it, with witnesses whose optimal-frame sets
are disjoint."
That is a verified computational note about one construction. It is not an
impossibility theorem about compilation, and the counts offered as its
evidence are properties of the class-size histogram, not of quantum compiling.
