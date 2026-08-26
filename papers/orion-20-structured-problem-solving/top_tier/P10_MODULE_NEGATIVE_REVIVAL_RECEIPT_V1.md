# P10 module-negative revival receipt (NR-02) — V1

**Lane:** NR-02 of `research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md`
(negative: per-module Markov-minus-unigram deltas Control −0.033333,
CategoryTheory −0.005780 against a pooled +0.104628).

**Scope note.** The module-robustness analysis and its frozen data belong to the
Mathlib source-transfer P10 technical note,
`papers/paper-xx-content-bound-math-evaluation/` (self-identified P10; the
present `paper-10-structured-problem-solving/` directory is its prospective
successor). This receipt is filed here because the revival backlog registers the
lane against the current P10 slot. Canonical machine artifact and generator:

- `papers/paper-xx-content-bound-math-evaluation/analyze_module_negative_revival_v2.py`
- `papers/paper-xx-content-bound-math-evaluation/results/MATHLIB_MODULE_NEGATIVE_REVIVAL_V2.json`
- frozen inputs: `results/MATHLIB_TRANSFER_V2_1.json`, `benchmark/MATHLIB_CORPUS_V2_MANIFEST.json`,
  in-repo corpus `benchmark/corpus/mathlib4_e72c1e277f31/`

## Faithfulness

The frozen leave-top-module-out evaluation was replayed per transition from the
sha-verified in-repo corpus through the frozen runner's own loader. All 28
frozen block receipts matched exactly (transitions, `markov_correct`,
`unigram_correct`, `held_out_trajectories`). Every number below derives from
that replay.

## One-stage attribution per negative module

**Control — measurement resolution (label over-reading).** Paired concordance
7 wins / 9 losses over 16 discordant transitions. At that discordant count the
minimum detectable |net effect| at two-sided α=0.05 is 10; the observed net is
−2 (p=0.804). The V1 "negative" read a coin flip. Within-module structure is
present but itself sub-resolution (LOO +0.0833 on 60 transitions).

**CategoryTheory — measurement resolution over a genuine mechanism boundary.**
Paired concordance 21/22 over 43 discordant transitions: minimum detectable
|net| is 15, observed −1 (p=1.000). Underneath the noise sits a real, localized
failure: the entire negative net concentrates in the `calculation` context
(5W/17L), where the donor-pooled conditional argmax `rewrite` (514 vs 413
continuations — a 46% *plurality*) inverts the module's own argmax `apply`
(17 vs 8). The module has the strongest internal sequential structure of all
26 modules (within-module LOO +0.3815) and the *smallest* marginal shift to
the donor pool of all 26 modules (JS 0.0265 bits). The missing ingredient is
conditional information that is genuinely absent from the donor pool — not
weak donor evidence (median donor context counts 903/1684, minima 147/148),
not marginal mismatch, and not absence of module structure.

Cross-module corroboration: within-module structure and transfer delta are
essentially uncorrelated (Pearson r=0.037, n=26) — transfer success is decided
by conditional alignment, not by how much structure a module has.

## Levers tested (all donor-side; frozen leakage barrier preserved)

| Arm | Rule | Result | Verdict |
|---|---|---|---|
| A — confidence gate | use donor conditional iff its donor-side 95% lower bound beats the donor marginal share | pooled 0.1046 → 0.0968; CategoryTheory worsens (net −1 → −5) | REJECTED — large context counts make nearly every conditional "confident"; confidence ≠ alignment |
| B — majority gate | use donor conditional only when it is a strict >50% majority of that context's donor continuations | pooled 0.1046 → 0.00025 (mechanism collapses to the unigram baseline) | REJECTED — a 16-family action space almost never yields majority continuations |
| per-module donor matching (backlog's suggested lever) | marginal-similarity donor restriction / conditional-similarity donor restriction | marginal variant cannot repair CategoryTheory by construction (its marginal is the closest of all 26 to the pool, JS 0.0265 → returns ≈ the full pool); conditional variant requires the held-out module's own conditionals and breaches the frozen leakage barrier | DISPOSED — the executable form is provably inert; the effective form is a prospective successor only |

The two rejections in opposite directions are themselves the finding: no
donor-side gating can repair a conditional inversion, because the inversion is
not a donor-side pathology. The repair that could work — target-conditional
transductive adaptation (adapt the transferred chain with the module's own
early trajectories) — is barred by the frozen V2.1 leakage barrier and is
recorded as the prospective successor mechanism, not executed post-hoc.

## Re-test under the V2 claim rule (parameter-free)

Rule: a module-level sign is claimable only when its exact paired sign test
reaches two-sided α=0.05. Sub-resolution modules of either sign are reported
UNRESOLVED with the sign withheld. The rule is uniform and even-handed — it
withholds signs from four V1-positive modules as well.

| Quantity | V1 receipt | V2 after rule |
|---|---|---|
| positive modules | 24 | 20 claimable positive, 0 claimable negative |
| negative modules | 2 | 0 claimable; 6 sign-withheld (Control, CategoryTheory, Condensed, Topology, Order, RepresentationTheory) |
| family sign test | p = 1.049e-5 (24/26) | p = 1.907e-6 (20/20 claimable) — **NOT a comparable improvement**: the V2 set is selected by per-module significance and excludes both adverse modules, so this is a denominator change. Do not cite as a gain. |
| pooled delta | 0.104628 | 0.104628 (estimator unchanged — both repair arms data-rejected) |

Resolution floor for design guidance: detecting the pooled effect (0.105) with
power 0.80 requires 44 discordant pairs; Control has 16, CategoryTheory 43.

## Verdicts

- **Control:** CORRECTED — UNRESOLVED by measurement resolution. The V1
  negative label over-read a coin flip; the sign is withheld, never relabelled
  positive.
- **CategoryTheory:** CORRECTED — UNRESOLVED by resolution, with a documented
  mechanism boundary (plurality conditional inversion on the module-signature
  `calculation` context; strong internal structure not present in the donor
  pool). Stays OUT of the positive claim. This is a first-class bounded
  outcome, not a defect to hide: pooled-donor sequential transfer does not
  reach modules whose signature conditionals diverge from a weak-plurality
  donor consensus.
- **Pooled/breadth claim:** upgraded, not tuned — 20/20 claimable-sign modules
  positive at a stronger family sign test, with the estimator and pooled delta
  untouched.

## Boundary

Post-hoc revival analysis of frozen source-projection artifacts. The V2 claim
rule and both lever arms were selected after inspecting the V1 failures; they
are revival outputs requiring prospective re-freezing before use as endpoints,
not preregistered results. No proof-state, tactic-library, prover-utility,
theorem-correctness or scientific-authority claim. Sub-resolution modules stay
unclaimed; nothing was relabelled positive. Multiple-comparison note: 20
claims at α=0.05 across 26 modules implies ≈1.3 expected false claims under a
global null; all claims are same-signed positive and the family-level sign
test covers the familywise concern.
