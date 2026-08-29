# ORION-02 — independent algebraic-statistics proof and novelty review V1

**Document ID:** `ORION02.INDEPENDENT_PROOF_REVIEW.V1`
**Date:** 2026-08-28
**Status:** `ADVERSARIAL_REVIEW__NO_SCIENTIFIC_AUTHORITY`
**scientific_authority_delta:** `NONE`

## Independence statement

This review did **not** import or rely on the generating proof or search logic.
No verifier, executor or proof script from the repository was read or run.
Theorem statements were taken from `MANUSCRIPT_V2.md` and attacked from first
principles; every arithmetic claim below was recomputed independently in a
throwaway script from the published formulas alone.

Verdicts are per-theorem. **A precise "this step is not justified" is the
deliverable; approvals are stated only where the check was actually performed.**

---

## 1. Summary of verdicts

| # | Object | Verdict |
|---|---|---|
| 1 | Theorem 1 / C-C1 — four-index decision certificate | **CONDITIONAL — two undeclared assumptions** |
| 2 | C-C2 — sharpness at `m=4` | **CANNOT_CHECK — required cost convention absent from the manuscript** |
| 3 | §4 / C-C3, C-C4 — the `A_t/B_t` fibre | **NOT JUSTIFIED AS WRITTEN — missing cross-gadget lemma (most consequential finding)** |
| 4 | Theorem 2 / C2-C4, C2-C5, C2-C6 — minimax | **ARITHMETIC VERIFIED; donor credit owed; scope defect (corrected separately)** |
| 5 | §6 / C-C5 — order `m-2` separation | **CONDITIONAL — uniqueness asserted; forward reference** |
| 6 | Theorem 4 / C-C6, C-C7 — proper-marginal kernel | **APPROVED — proof complete; verified `q=1..8`; donor credit owed** |
| 7 | Novelty posture | **Largely sound; two donor lineages missing** |

No counterexample to any stated theorem was found.

---

## 2. Findings against the theorems

### 2.1 §4 — cross-gadget blocks are never excluded (highest value finding)

**Statement under review** (`MANUSCRIPT_V2.md:88-94`): "For each `t>=1`, construct
`t` disjoint five-term gadgets... Exact decomposition gives `Delta_A(t)=12t-2`,
`Delta_B(t)=10t-1`."

**The problem.** The optimizer ranges over **all set partitions of all `5t`
terms**, which includes blocks containing terms from two or more different
gadgets. Nothing in §4 argues that such blocks never help. Two distinct issues
hide under the single phrase "exact decomposition":

**(a) The cost function is not additively separable across gadgets.** In the
§2 formula
`C(Pi)=2m+|Pi|-3 + sum_S d(|S|) + max_S b(|S|) + sum_S [2f(S)+(b(|S|)+2)(w(S)-|S|f(S))]`,
the term `max_S b(|S|)` is a **single global maximum over all blocks**, not a sum.
Per-gadget contributions therefore cannot simply be added: once one gadget pays
for a large block, another gadget's large block incurs no further `max`-term cost.

*Partial mitigation, stated in fairness:* `Delta_A = 12t-2` and `Delta_B = 10t-1`
are **not** `t` times a constant — each carries a single `t`-independent
correction (`-2`, `-1`). That is exactly the shape one expects if a single global
term is paid once rather than `t` times, which suggests the authors did account
for (a). **But the argument is not exhibited**, so a reader cannot confirm it.

**(b) Independently of (a), no argument excludes blocks that span gadgets.**
This is not bookkeeping; it is an optimization-domain question, and it is
nowhere addressed. Since `f(S)` counts columns where *every* term of `S` shares a
nonidentity Pauli, a cross-gadget block's `f` is plausibly small — but
"plausibly" is not a proof, and the `max_S b(|S|)` coupling in (a) is precisely a
mechanism that could make one large cross-gadget block cheap at the margin.

**Why this matters most.** Theorem 2 (`C2-C4`, `C2-C5`, `C2-C6`) assumes
`Delta_A` and `Delta_B` are the **exact optima**. If a cross-gadget partition
beats either, the two-point construction collapses and the entire minimax
section fails. C-C3 and C-C4 are `PROVEN-ALL-T` in both ledgers; that status is
not currently supported by the manuscript text.

**Required repair:** an explicit lemma — *no optimal partition of `A_t` or `B_t`
contains a block meeting two distinct gadgets* — plus explicit bookkeeping for
the global `max_S b(|S|)` term.

### 2.2 §2 — two undeclared assumptions in Theorem 1

**(a) Integrality of weights.** The proof sketch (`:80`) argues "integrality
prevents two disjoint pair blocks from simultaneously attaining zero gain", and
the `+1` in clause (ii) `g_ij+g_kl+1<=0` is exactly the integrality-strengthened
form of `g_ij+g_kl<0`. §2 (`:46`) introduces `w_i` only as "term weight" and never
declares it integral.

*Independently checked, and this is the interesting part:* for the registered
`m=4` instance `XXII, XYII, XZII, XIXX`, taking `w_i` = the Pauli Hamming weight
(count of non-identity positions) gives `w = (2,2,2,3)`, `W = 9`, and
`C_U = 2W+3m-3 = 27` — **reproducing the manuscript's stated `C_U=27` exactly.**
So `w_i` is almost certainly the Pauli Hamming weight, which is an integer by
construction, and the integrality assumption would then be automatically
discharged. **But the manuscript never defines `w_i`, so as written the
assumption is used and undischarged.** The repair is one sentence in §2.

**(b) Dominance is asserted, not proved.** "Under the frozen equal-weight
structural objective, factoring and shared width dominate their alternatives"
(`:46`). The reduction to four-index clauses depends on this. If it is an
assumption rather than a lemma, **Theorem 1 is conditional** and should say so.

**(c) Terminological inconsistency.** §2 says "**equal-weight** structural
objective", yet §5 (`:104`) feeds the estimator "**ordered weights**", and the
registered `m=4` instance has unequal weights `(2,2,2,3)`. Either "equal-weight"
refers to equal weighting of the `SELECT`/`PREP`/`WIDTH` components rather than
equal term weights, or the phrase is wrong. It must be disambiguated: as written
the two readings give different theorems.

### 2.3 C-C2 — the sharpness counterexample cannot be verified from the manuscript

**Verdict: `CANNOT_CHECK`, not "wrong".** Recorded as unverifiable, not adverse.

`MANUSCRIPT_V2.md:82-86` claims the `m=4` instance has `C_U=27` and one-block
cost `23`. I verified `C_U=27` independently (§2.2a above).

I **cannot** verify `23`. The §2 cost formula is explicitly introduced with
"For `|Pi|>=2`" (`:48`), and `:62` states "The single-block flag convention is
treated separately" — but **that convention is never given in the manuscript.**
Applying the `|Pi|>=2` formula to the single block anyway yields
`6 + d(4) + b(4) + [2f + (b(4)+2)(W-4f)] = 6+2+2+22 = 32`, with `f=1` (only
column 1 is uniformly non-identity) — not `23`. The discrepancy is expected and
is *not* evidence of an error; it is evidence that the missing convention is
load-bearing.

**Consequence:** C-C2 is `PROVEN-EXACT` in both ledgers, but no reader can check
it from the paper. Theorem 1's proof also invokes "the exceptional one-block
formula is bounded separately" (`:80`), so the same missing convention sits
inside Theorem 1. **The single-block cost convention must be stated explicitly.**

### 2.4 Theorem 2 — arithmetic verified, no counterexample

Recomputed independently from `Delta_A=12t-2`, `Delta_B=10t-1`:

- **Real additive radius.** `min_y max(|y-Delta_A|,|y-Delta_B|) = (Delta_A-Delta_B)/2 = (2t-1)/2`, attained at the midpoint. Confirmed `t=1,2,5,17`. **Correct.**
- **Integer radius.** Midpoint `11t-1.5`; at `y=11t-1` the max is `max(t-1,t)=t`, at `y=11t-2` likewise `t`. Confirmed by exhaustive integer search for `t=1,2,5,17`. **Correct — `t`, exactly as stated.**
- **Symmetric multiplicative factor.** `sqrt(Delta_A Delta_B)` equalizes `Delta_A/y` and `y/Delta_B`, giving `sqrt(Delta_A/Delta_B)=sqrt((12t-2)/(10t-1))`. **Correct.**
- **The `sqrt(6/5)` limit and its phrasing.** The ratio is strictly *increasing* in `t` (`1.111...` at `t=1`, `1.199920` at `t=1000`) with supremum `6/5`, **never attained**. So "no uniform factor **strictly below** `sqrt(6/5)`" (`:19`, `:132`) is the correct form; "at least `sqrt(6/5)` for each `t`" would be **false**. The manuscript uses the correct form. **Confirmed — no correction owed here.**
- **One-sided.** `alpha >= Delta_A/Delta_B -> 6/5`; the manuscript correctly labels this **asymptotic** (`:19`). **Correct.**

Two non-arithmetic points:
- **Scope defect (already corrected).** The abstract and §5 conclusion originally dropped the "deterministic" restriction that `:104` imposes and Limitation 4 concedes. Corrected as LA-01/02/03 in `LANGUAGE_AUDIT_V1.md`.
- **Donor credit owed** — see §3.

### 2.5 §6 — conditional

- **Uniqueness asserted, not proved.** "add identical all-term padding that makes the single block **uniquely** optimal" (`:142`). Uniqueness is distinct from the padding *minimality* that C-C8 openly leaves open, and it is not something C-C8's disclaimer covers. If uniqueness fails, the `Delta(A)-Delta(B)` computation breaks. Nothing in §6 proves it.
- **Forward reference.** §6's premise — that all labeled common-factor counts through order `m-2` agree — is justified by §7's kernel theorem, which appears *after* it. Presentational, but it obscures the actual dependency `C-C5 <- C-C6`.
- **Same single-block dependency** as §2.3: §6 relies on a single block being optimal, and the single-block convention is not stated.

### 2.6 Theorem 4 — approved

**The one unqualified approval in this review.**

`M(T)=sum_{S superset T} delta(S)`. Möbius inversion on the Boolean lattice under
inclusion gives `delta(S)=sum_{T superset S} (-1)^(|T|-|S|) M(T)`. If `M(T)=0` for
every proper `T`, only `T=[q]` survives, so `delta(S)=(-1)^(q-|S|) M([q])` and
`M([q])=delta([q])=c`. Assumptions stated, used, and sufficient.

**Independently verified by brute force for `q=1..8`** with `c=3`: setting
`delta(S)=(-1)^(q-|S|)c` makes every proper upper marginal vanish (0 nonzero in
all eight cases) and yields `M([q])=c`. Consistent with the manuscript's own
"bounded reconstruction checks `q<=8`", reached independently.

**No counterexample exists.** The edge case `T=empty` is consistent:
`sum_S (-1)^(q-|S|)c = 0` for `q>=1`.

C-C7 follows immediately: `|delta(S)|=|c|` for every `S`, so all `2^q` cells are
touched, with `2^(q-1)|c|` signed mass per side.

---

## 3. Novelty and donor ownership

### 3.1 Correctly disclaimed already

`CLAIM_LEDGER.md` C-C10 and `CLAIM_LEDGER_R2.md` C2-C11 mark Markov bases,
marginal fibres, Möbius inversion and generic lower-order insufficiency
`DONOR-OWNED`; `MANUSCRIPT_V2.md:174` names fibres, marginal-preserving moves,
toric ideals and Graver/Markov complexity; Limitation 6 repeats it. C2-C12 marks
the computational-hardness reading `FORBIDDEN`. The five Diaconis-Sturmfels /
Dobra / Hosten-Sullivant / Develin-Sullivant / Kral'-Norine-Pangrac references
are the right algebraic-statistics donors. **This posture is better than typical
and should not be diluted.**

### 3.2 Donor credit owed but currently absent

**(a) Rota — Möbius inversion.** Theorem 4 *is* Möbius inversion on a finite
poset. `:170` calls it "classical" but the reference list contains no Möbius or
poset citation. Owed: G.-C. Rota, *On the foundations of combinatorial theory I:
theory of Möbius functions* (1964). The paper's residual is the *application*, and
that is easier to defend with the citation present than absent.

**(b) Le Cam / Tsybakov — two-point minimax.** Theorem 2 is a textbook two-point
indistinguishability argument: two parameters with identical observable
distributions, risk bounded below by half the separation. The reference list has
no minimax lower-bound lineage at all. Owed: L. Le Cam (asymptotic methods /
two-point method) and A. B. Tsybakov, *Introduction to Nonparametric Estimation*,
§2.2. The compiler-specific *instantiation* is the contribution; the *technique*
is donor-owned and should be labelled as such — the same standard the paper
already applies to Markov bases.

**(c) Not owed here.** The conformal / selective-risk lineage (Vovk et al.,
Lei et al., Chow, El-Yaniv-Wiener, Bates et al.) belongs to the *empirical*
FiberGuard programme and its successor design, and is credited in
`experiments/selective-fibre-risk-v1/THEORY.md` §4. It does not bear on the
theory core.

### 3.3 Residual contribution — my assessment

With (a) and (b) added, the defensible residual is the **conjunction for one
frozen compiler**: a constant-order (four-index) decision certificate coexisting
with unbounded pair-information value ambiguity, forced optimizer-structure
separation, and order-`m-2` insufficiency. I found no primary source combining
these for this compiler, but **this is an author-side overlap conclusion, not an
external priority certification** — `MANUSCRIPT_V2.md:176` already says exactly
this, and it should stay.

`MANUSCRIPT_V2.md:220` carries `..._SUBSTANTIALLY_CLOSED` two lines above an
**External-only gates** list (`:222`) that still includes *independent proof
audit*. **This review is not that audit** — it is a single adversarial pass by a
non-specialist reviewer with no access to the generating proofs. Findings §2.1,
§2.2 and §2.3 should be read as evidence that the external gate is **not**
substantially closed.

---

## 4. What a repair would require

Ordered by consequence:

1. **Prove the cross-gadget lemma** (§2.1). Without it C-C3/C-C4 are not
   `PROVEN-ALL-T`, and Theorem 2's premise is unsupported.
2. **State the single-block cost convention** (§2.3). Without it C-C2 is
   unverifiable and part of Theorem 1's proof is unreadable.
3. **Define `w_i` and declare integrality** (§2.2a). Probably one sentence:
   `w_i` is the Pauli Hamming weight — which the `C_U=27` arithmetic confirms.
4. **Say whether dominance is a lemma or an assumption** (§2.2b). If assumed,
   mark Theorem 1 conditional.
5. **Disambiguate "equal-weight"** (§2.2c).
6. **Prove or weaken the §6 padding-uniqueness claim** (§2.5).
7. **Add Rota and Le Cam/Tsybakov citations** (§3.2).

Items 1-6 are author-side and internal to the manuscript. None of them is
addressed by this worker; all are recorded.

## 5. What this review did not do

- Did not read or execute any verifier, proof script or search code.
- Did not verify the `d(s)`/`b(s)` cost formulas against any physical model;
  they are taken as the frozen definition, per `:64`.
- Did not attempt an exhaustive partition search for small `t` to test §2.1
  empirically. That would need compute and is out of scope here; it is the
  obvious cheap first check for whoever repairs item 1.
- Did not assess the FiberGuard empirical programme, which carries its own
  preserved adverse terminal `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`.
