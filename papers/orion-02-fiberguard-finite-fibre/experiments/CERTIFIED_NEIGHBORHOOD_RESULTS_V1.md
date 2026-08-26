# C-NBR certified neighborhood — results V1

- lane: `PAPER_PORTFOLIO_REFACTOR_PLAN_V1.md` §3, lane C-NBR
- protocol: `experiments/CERTIFIED_NEIGHBORHOOD_PROTOCOL_V1.md` (frozen before
  outcome access; SHA-256 `8d74d09723c3980d55eaaa61cd49a028bd6cb49b0329d3f91153f01547a106a0`)
- executor: `experiments/certified_neighborhood.py`
- execution: LUNARC job **3544034** (hep partition, account hep2023-1-3),
  python 3.11.5, numpy 1.26.4, scikit-learn 1.5.2, git
  `62e46900cf2f0e7dd412735384e090a04f8c8de6`; job 3544033 failed closed at the
  synthetic self-test and exposed an indexing defect in the self-test only
  (fixed before any outcome access; main-path indexing verified elementwise)
- receipts: `experiments/results/CERTIFIED_NEIGHBORHOOD_RESULT_V1.json`
  (SHA-256 `c6a7fa151c53f3e0397fc8351b951967028c5cc4bd08af63435122ddb315f97e`)
  and the generated `.md` (SHA-256
  `3caba0dd7ad154f32047dce4969c2a1fc8a4dc0922ca090118f5c36145032202`)
- subject: ASlib SAT11-HAND-ALGO, 296 instance-repetitions, 115 features,
  15 solvers, PAR10 at cutoff 5000 s, digest-verified in-job by the frozen
  harness loader

## Verdict (frozen-gate, pre-registered)

**`CERTIFICATE_INVALID` on both splits; overall `CERTIFICATE_INVALID`.**

The certificate-validity gate (`held-out violation rate <= 0.10`) fails on
SPLIT_OFFICIAL_FOLD (NBR_FULL 0.1689, Wilson 95% [0.1171, 0.2375]; NBR_PCA10
0.1824) and on SPLIT_FAMILY_DISJOINT (NBR_FULL 0.1719; NBR_PCA10 0.1484).
Because validity is the first-ranked gate, no value claim is made even where
value exists (below). Positive, null and adverse outcomes were all
pre-registered as reportable; this is the invalid-certificate branch.

## Headline numbers

### SPLIT_OFFICIAL_FOLD (DEV folds 1-5, HELD-OUT folds 6-10; 148/148)

| System | Mean PAR10 | Solve rate | Certainty coverage |
|---|---:|---:|---:|
| VBS (ceiling) | 12439 | 0.757 | — |
| RF_ROUTER | 17531 | 0.655 | — |
| KNN16 | 22620 | 0.554 | — |
| NBR_CERT_FULL | 26170 | 0.486 | 0.2095 |
| NBR_CERT_PCA10 | 26105 | 0.486 | 0.3311 |
| SBS (fallback) | 27196 | 0.466 | — |
| EXACT_EQ (control) | 27196 | 0.466 | 0.0000 |

- certificate coverage at eps=5000: NBR_FULL 20.95%, PCA10 coarsening 33.11%,
  exact-equality control **0.00%** (R14's refutation replicates on this
  subject: exact signatures do not transfer at all)
- `SBS - NBR_CERT_FULL = +1026.18` PAR10, paired bootstrap 95%
  `[+13.5, +2376.1]` — the certified policy beats its own fallback with
  interval excluding zero, **but the certificate backing it is invalid**, and
  the policy is dominated by the uncertificate heuristics:
  `KNN16 - NBR_CERT = -3550 [-6583, -572]`,
  `RF_ROUTER - NBR_CERT = -8639 [-11998, -5306]`
- hostile control (constants x0.25) raises violations only 0.169 -> 0.237:
  the audit is sensitive, weakly

### SPLIT_FAMILY_DISJOINT (41 DEV / 11 HELD-OUT families, zero overlap; 168/128)

- certificate coverage at eps=5000: **0.0000** for both relations; the
  certified set on untouched families is empty, the policy degenerates to
  SBS exactly (all arm rows identical to SBS)
- violation rates remain 0.15-0.17 (Wilson upper up to 0.25)
- EXACT_EQ coverage again 0.0000

## Mechanism readout (why the certificate fails)

1. **The calibrated constants are enormous.** `L_a` ~ 4400-5800 PAR10 per
   unit standardized distance (NBR_FULL) and ~5000-9300 (NBR_PCA10): one unit
   of feature distance costs roughly one full cutoff of certified regret.
   In a 115-dimensional standardized space typical anchor distances exceed
   10, so `U_T(a,x)` >> 5000 for anything but near-duplicates. Coverage is
   confined to near-duplicate structure; across families it vanishes.
2. **The q0.95 pairwise-slope quantile is not a 95% per-instance validity
   guarantee.** Even on its own DEV-CALIBRATION set the FULL-space relation
   violates 14.3% of the time (fold split; PCA10 3.6%). Pairwise-slope
   quantiles and per-instance violation probabilities are different
   functionals; the min-form couples them nonlinearly. Held-out rates
   (0.15-0.18) track the calibration rates, so this is a calibration-rule
   failure, not transfer drift.
3. **The value that exists is the neighborhood heuristic's value, not the
   certificate's.** Where coverage is nonzero the certified policy harvests
   real PAR10 over its fallback (+1026 [13.5, 2376]) but is dominated by
   KNN16 and the RF router — consistent with R14/R16 doctrine that the
   learned baselines are strong.

## Answer to the gate question

The successor gate R14 named — freeze a coverage-producing certified
neighborhood relation on disjoint development data and test it on untouched
scenarios — has now been executed. Answer: **the R15 Lipschitz
training-anchor certificate, calibrated as specified, does not survive the
gate**. It is coverage-producing only where instances are near-duplicates of
development data (fold split), invalid at the pre-registered 10% level
everywhere, and produces zero coverage on family-disjoint held-out
scenarios. This is an empirical confirmation of R15's coverage-tax boundary
and R16's `NO_PORTABLE_CERTIFICATE_VALUE` on a fourth mechanism (conformal
marginals were R16's; this is the Lipschitz neighborhood relation).

## Draft-PR adjudication (what was reused vs run new)

Inspected R11-R19 drafts #1457/#1459/#1460/#1461/#1462/#1468/#1471/#1475 (all
drafts, none in origin/main, all in the archived `papers/five-paper-top-tier-r8/C/` path):

- **R14 (#1457)**: exact-equality transfer refuted (SAT12-ALL coverage
  3.22%/5.08%). Reused: the kNN-16 comparator class and the successor-gate
  framing. This study supplies the successor execution.
- **R15 (#1460)**: Theorem C-R15.9 `U_T(a,x)=min_z[R(a,z)+L_a d(Phi(x),Phi(z))]`
  proved (with hostile controls) but never executed on real data. Reused: the
  certificate formula, the training-anchor form, the hostile
  under-estimated-constant control. New: its execution on the in-tree
  digest-verified SAT11-HAND-ALGO subject.
- **R16 (#1461)**: conformal marginal certificate, `NO_PORTABLE_CERTIFICATE_VALUE`
  — different mechanism; its conclusion is corroborated, not duplicated.
- R15b/R16b (#1462/#1468), R18 (#1471), R19 (#1475): tail audits, RF
  comparator dominance, paired routing, joint hulls — none executes the
  certified-neighborhood freeze; the RF router's dominance of the certified
  policy observed here is consistent with R16b.

## Nonclaims

One bounded public scenario; no ASlib-wide, SAT-wide, cross-domain,
algorithm-selection, selective-prediction or LLM-routing superiority claim.
The verdict binds the ORION-02 C-NBR gate only. `paper_authority_delta:
NONE`. A revival path exists (a per-instance validity-calibrated rule, e.g.
conformal calibration of `U` rather than a pairwise-slope quantile, with a
coverage-explicit coarsening chosen on DEV) but is out of scope for this
frozen protocol; any successor must be a new frozen protocol, not a
retuning of this one.
