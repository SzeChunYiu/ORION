"""P14 external packet specifications - domain 2/3: EMPIRICAL_ML_METHODOLOGY.

Deterministic data only. Anonymized per the external governance protocol.
Numbers are carried over from preserved internal records with identifiers
renamed to generic codes (datasets, model families, tasks).
"""

DOMAIN = "EMPIRICAL_ML_METHODOLOGY"

SPECS = [
    # ---------------- STRONG_PROMOTABLE (3) ----------------
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="A same-information representation change (no new data, no new model capacity) is claimed to improve "
          "out-of-sample skill from 0.0239 to 0.0352 on a frozen forecasting task, with a causal diagnostic "
          "attributing the gain. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Task, split, metric, and both representations frozen; the same-information constraint "
                         "(byte-identical underlying data) declared the load-bearing condition."),
            ("RESULT", "Held-out skill: baseline representation 0.0239 (95% CI [0.0211, 0.0267]); changed "
                       "representation 0.0352 (CI [0.0318, 0.0386]); paired difference +0.0113 (CI [0.0081, 0.0145], "
                       "excludes 0). 12 seeds, predeclared."),
            ("RESULT", "Causal diagnostic: intervention on the representation component alone moves the mechanism "
                       "probe from 0.2 to 0.8 (preregistered threshold 0.5); the probe is inert under placebo "
                       "intervention (0.2 -> 0.2)."),
            ("CONTROL", "Shuffle-null at matched sample size: difference 0.0001 (CI [-0.0026, +0.0028])."),
            ("DONOR", "Donor E-1 (representation-theorem programme): predicts representational gains are possible "
                      "without new information but gives no task-level construction; the delta here is the "
                      "construction plus the causal diagnostic."),
        ],
        dp=["same-information condition verified byte-level", "causal diagnostic above threshold with placebo control", "donor delta stated"],
        scope="the frozen forecasting task and split",
        forbid=["claiming new information was added", "transfer to unseen task families without new evidence"],
    ),
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="A probe-based steering rule is claimed to move an evaluation pass-rate from 0.9556 (protected baseline, "
          "below the 0.965 requirement) to 0.9721 (above requirement), with the gain shown to come from mechanism "
          "repair rather than metric drift. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "The 0.965 requirement, the protected baseline, and the steering rule frozen before any "
                         "steering run; metric drift declared the falsifier."),
            ("RESULT", "Steered runs: 0.9721 mean over 40 episodes (CI [0.9694, 0.9748], lower bound above 0.965). "
                       "Protected baseline replication: 0.9556 (CI [0.9519, 0.9593], upper bound below 0.965)."),
            ("CONTROL", "Metric-drift audit: a held-out metric battery (7 independent checks) is unchanged "
                        "(max |delta| 0.0009); the probe target itself is not part of the evaluated metric."),
            ("BACKGROUND", "The baseline's shortfall was previously attributed to capacity; the steering result "
                           "refutes that attribution (capacity unchanged between arms)."),
        ],
        dp=["requirement thresholds honored as frozen", "metric-drift audit clean", "mechanism-repair attribution tested"],
        scope="the frozen evaluation suite",
        forbid=["re-lowering the 0.965 requirement", "claiming capacity conclusions"],
    ),
    dict(
        family="STRONG_PROMOTABLE", gold="PROMOTE",
        q="A selective-abstention policy is claimed to improve calibrated accuracy on a frozen decision task "
          "without reducing coverage below a preregistered floor. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Coverage floor (60%), abstention budget, and scoring rule frozen."),
            ("RESULT", "Policy with abstention: Brier 0.0812 at coverage 63.4%; no-abstention baseline: Brier 0.1105 "
                       "at coverage 100%. Difference -0.0293 (bootstrap CI [-0.0361, -0.0227], 10,000 resamples, "
                       "excludes 0)."),
            ("CONTROL", "Random-abstention control at matched coverage 63.4%: Brier 0.1091 (no improvement; "
                        "CI [-0.0041, +0.0033] vs baseline, includes 0) - selectivity, not abstention, carries the gain."),
            ("DONOR", "Donor E-2: abstention frameworks for classification; the delta is the coverage-floor "
                      "calibration accounting and the random-abstention control."),
        ],
        dp=["coverage floor honored", "random-abstention control run at matched coverage", "donor delta stated"],
        scope="the frozen decision task",
        forbid=["claiming gains below the coverage floor", "dropping the matched-coverage control in reporting"],
    ),

    # ---------------- APPARENT_POSITIVE_SUBSUMED (4) ----------------
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="An 'improved estimator' for tail risk of a bounded scoring rule is proposed, reducing variance by 27% "
          "on benchmarks. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Estimator and benchmark frozen; novelty of the mechanism declared the estimand."),
            ("RESULT", "Variance reduction 27.3% (CI [24.1, 30.2]) across 8 benchmark distributions."),
            ("DONOR", "Donor E-3: control-variate estimation with a known bounding-function control achieves the "
                      "same algebra; the proposed estimator is the control-variate estimator with the control "
                      "written in expanded form (identity verified symbolically and on all 8 benchmarks to 1e-12)."),
            ("CONTROL", "Step-by-step algebraic rewrite from the donor form to the proposed form is included and "
                        "machine-checked."),
        ],
        dp=["algebraic identity against donor verified", "residual delta isolated", "decision recorded"],
        scope="bounded scoring rules",
        forbid=["claiming the estimator as new", "claiming the variance reduction as a new result"],
    ),
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A 'novel' two-stage resampling scheme for narrow-reliability claims is proposed: subsample, then "
          "bias-correct. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Scheme frozen with a target coverage of 95% two-sided."),
            ("RESULT", "Empirical coverage 94.8% across 6 simulated families."),
            ("DONOR", "Donor E-4: the double-bootstrap bias-corrected interval (decades old) instantiates exactly; "
                      "the first stage is the calibrated root, the second the correction, with identical tuning "
                      "constants."),
        ],
        dp=["instantiation identity against donor established", "residual delta isolated", "decision recorded"],
        scope="scalar estimands",
        forbid=["claiming the scheme as new"],
    ),
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A 'new' feature-attribution stability score is proposed, showing 3x more stable rankings than a baseline "
          "attribution method. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Score definition and stability comparison frozen."),
            ("RESULT", "Rank-stability 0.81 vs 0.27 for the baseline under resampling (1,000 resamples)."),
            ("DONOR", "Donor E-5: rank-stability under bootstrap resampling is an established measurement; the "
                      "proposed score is Kendall-tau stability with a monotone transform (Spearman footrule "
                      "identity verified on all 1,000 resample pairs)."),
        ],
        dp=["score identity against donor established", "residual delta isolated", "decision recorded"],
        scope="attribution rankings on the frozen model class",
        forbid=["claiming the score as new", "claiming the 3x stability as a new finding"],
    ),
    dict(
        family="APPARENT_POSITIVE_SUBSUMED", gold="SUBSUMED",
        q="A 'novel' early-stopping rule for fine-tuning is proposed: stop when the running rank correlation of "
          "train and dev loss curves exceeds 0.9. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Rule frozen; comparison against fixed-epoch and fixed-patience baselines."),
            ("RESULT", "Mean final dev loss 0.412 vs 0.431 (patience-3) and 0.447 (fixed) over 15 tasks."),
            ("DONOR", "Donor E-6: rank-correlation-based generalisation stopping appears in an established model-"
                      "selection treatment with the same 0.9 trigger; the present rule matches it in all tunable "
                      "constants."),
        ],
        dp=["rule identity against donor established", "residual delta isolated", "decision recorded"],
        scope="the frozen task suite",
        forbid=["claiming the stopping rule as new"],
    ),

    # ---------------- INTERACTION_ONLY (3) ----------------
    dict(
        family="INTERACTION_ONLY", gold="INTERACTION_ONLY",
        q="A calibration gain is claimed for the combination of a temperature schedule and a batch-composition "
          "constraint. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Four-arm factorial frozen; interaction declared the estimand."),
            ("RESULT", "Expected calibration error: none 0.061, schedule-only 0.059 (CI [-0.006,+0.010] vs none), "
                       "constraint-only 0.060 (CI [-0.005,+0.007]), combination 0.038 (CI [-0.028,-0.018])."),
            ("CONTROL", "On single-domain batches the combination's gain vanishes (0.059 vs 0.060), locating the "
                        "interaction in cross-domain mixture structure."),
        ],
        dp=["factorial completed with both marginals", "interaction located", "decision recorded"],
        scope="cross-domain batches as frozen",
        forbid=["recommending either component alone"],
    ),
    dict(
        family="INTERACTION_ONLY", gold="INTERACTION_ONLY",
        q="An accuracy gain is claimed for combining curriculum ordering with a loss-masking rule. Determine the "
          "strongest defensible action.",
        ev=[
            ("PROTOCOL", "Two-by-two design frozen."),
            ("RESULT", "Accuracy: none 71.2, curriculum-only 71.4 (+0.2, CI [-0.9,+1.3]), masking-only 71.3 (+0.1, "
                       "CI [-1.0,+1.2]), combined 74.6 (+3.4, CI [+2.1,+4.7])."),
            ("CONTROL", "Shuffle-null at matched sizes: combined-vs-none difference 0.0 +- 0.8."),
        ],
        dp=["factorial completed", "shuffle control run", "decision recorded"],
        scope="the frozen curriculum and masking definitions",
        forbid=["crediting either component alone"],
    ),
    dict(
        family="INTERACTION_ONLY", gold="INTERACTION_ONLY",
        q="A sample-efficiency gain is claimed for the combination of a replay buffer and a representation "
          "freeze-schedule. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Two-by-two design frozen; sample-to-threshold declared the estimand."),
            ("RESULT", "Episodes to 90% return: none 412, replay-only 401 (p=0.42), freeze-only 408 (p=0.67), "
                       "combined 268 (p<1e-4)."),
            ("CONTROL", "Ablating the freeze-schedule's second phase removes most of the combined gain (361 vs 268, "
                        "p=0.003), identifying the specific co-dependence."),
        ],
        dp=["factorial completed", "phase-level ablation locates the co-dependence", "decision recorded"],
        scope="the frozen environment family",
        forbid=["recommending replay or freeze alone"],
    ),

    # ---------------- NULL_LIVE_PARENT (4) ----------------
    dict(
        family="NULL_LIVE_PARENT", gold="NULL_LIVE",
        q="A validated parent result (wine-quality transfer, parent effect reproduced) is claimed to extend to a "
          "new domain with the same sign and magnitude. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Parent effect and the extension declared separately; minimum detectable effect set at "
                         "one-third of the parent's magnitude."),
            ("RESULT", "Parent replication: -0.0021 (CI [-0.0029,-0.0013]), consistent with the parent record. "
                       "Extension domain: -0.00016 (CI [-0.00031,+0.00002], includes 0); the preregistered "
                       "minimum detectable effect is excluded."),
            ("CONTROL", "Power: 0.91 for the preregistered effect; the null is informative."),
            ("BACKGROUND", "The extension used identical code paths and the same seeds as the parent; only the "
                           "data source changed."),
        ],
        dp=["parent scored separately from extension", "power stated", "null recorded for the extension only"],
        scope="the extension domain",
        forbid=["recording a null against the parent", "claiming the extension"],
    ),
    dict(
        family="NULL_LIVE_PARENT", gold="NULL_LIVE",
        q="A live parent result (representation gain +0.0113, reproduced) is claimed to generalise to a second "
          "task family. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Second-family transfer declared a separate claim with its own threshold (+0.005)."),
            ("RESULT", "Parent reproduction: +0.0110 (CI [+0.0078,+0.0142]). Second family: +0.0004 (CI "
                       "[-0.0034,+0.0042], includes 0); preregistered +0.005 excluded."),
            ("CONTROL", "Diagnostic probe: the mechanism activated by the representation change is absent in the "
                        "second family (probe 0.21 vs 0.79 in the parent domain), giving a mechanism-level "
                        "explanation of the null."),
        ],
        dp=["parent scored separately", "mechanism probe explains the null", "null recorded for the transfer only"],
        scope="the second task family",
        forbid=["recording a null against the parent", "claiming transfer"],
    ),
    dict(
        family="NULL_LIVE_PARENT", gold="NULL_LIVE",
        q="A scaling parent result (log-linear fit, reproduced) is claimed to hold with an added curvature term. "
          "Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Curvature term preregistered with minimum detectable curvature 0.05 per doubling."),
            ("RESULT", "Parent log-linear fit reproduced (slope 0.987 vs parent 0.991, CI overlaps). Curvature: "
                       "0.004 per doubling (CI [-0.009,+0.017], includes 0); preregistered 0.05 excluded."),
            ("CONTROL", "A synthetic positive-control with injected curvature 0.06 is recovered at 0.058 (CI "
                        "[0.041,0.075]), so the null is not a measurement failure."),
        ],
        dp=["parent scored separately", "positive-control for the measurement run", "null recorded for the curvature only"],
        scope="the frozen scaling regime",
        forbid=["recording a null against the parent fit"],
    ),
    dict(
        family="NULL_LIVE_PARENT", gold="NULL_LIVE",
        q="A live parent result (abstention gain -0.0293 Brier, reproduced) is claimed to survive under a stricter "
          "coverage floor of 90%. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "The 90% floor declared a separate regime with the same estimand."),
            ("RESULT", "Parent regime (60% floor) reproduced: -0.0289 (CI [-0.0356,-0.0223]). Strict regime "
                       "(90% floor): -0.0031 (CI [-0.0068,+0.0006], includes 0)."),
            ("CONTROL", "Coverage 91.2% in the strict regime; abstention budget nearly exhausted, so the mechanism "
                        "has no room to act - the null is regime-structural, not noise."),
        ],
        dp=["parent scored separately", "regime-structural explanation given", "null recorded for the strict regime only"],
        scope="coverage floors >=90%",
        forbid=["recording a null against the 60%-floor result"],
    ),

    # ---------------- NEGATIVE_RETAINED (3) ----------------
    dict(
        family="NEGATIVE_RETAINED", gold="NEGATIVE",
        q="A capability-scaling claim asserts that a small-model family (0.5B class) improves on a frozen "
          "evaluation after a proposed training modification. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Three-size sweep (0.5B, 1.5B, 3B) frozen with per-size gates and a family-level "
                         "bootstrap lower-bound requirement."),
            ("RESULT", "0.5B: -0.140625 (large negative, CI [-0.152,-0.129]). 1.5B: 0.0000 (CI [-0.006,+0.006], "
                       "includes 0). 3B: +0.0031 (CI [+0.0002,+0.0060], excludes 0 but below the preregistered "
                       "0.01 gate). Family-level bootstrap lower bound <= 0."),
            ("CONTROL", "Training diagnostics: the modification destabilises the 0.5B runs (loss spikes in 8/10 "
                        "seeds), identified as the mechanism of the negative."),
            ("BACKGROUND", "A revival lever (gradient-clip schedule) is documented as the follow-up, not as a "
                           "reason to withhold the negative."),
        ],
        dp=["all three sizes reported", "family-level bootstrap gate evaluated", "negative retained with mechanism"],
        scope="the frozen sweep and gates",
        forbid=["cherry-picking the 3B point", "suppressing the 0.5B result", "re-running with new seeds to flip the sign"],
    ),
    dict(
        family="NEGATIVE_RETAINED", gold="NEGATIVE",
        q="A selection rule is claimed to beat its own parent selector on a frozen backtest with realistic "
          "execution costs. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Cost model (7% round-trip taker, maker exempt, spread 1 tick, 1-tick slippage per side) "
                         "frozen; the clean-parent comparison declared the only admissible test."),
            ("RESULT", "Claimed (no costs, signal-bar fills): +2.14 per unit. Measured (realistic fills, whole "
                       "chain): -0.31 per unit (CI [-0.44,-0.18]); passive-fill probability 0.62 implies the "
                       "survivorship of the claimed edge is fully explained by fill selection."),
            ("CONTROL", "Shuffle-equal-n null: -0.29 (CI [-0.38,-0.20]) - the rule is indistinguishable from "
                        "random selection at the same trade count."),
        ],
        dp=["whole-chain cost accounting applied", "shuffle-equal-n control run", "negative retained"],
        scope="the frozen cost model and venue rules",
        forbid=["reporting the no-cost variant", "blaming the cost model for the sign"],
    ),
    dict(
        family="NEGATIVE_RETAINED", gold="NEGATIVE",
        q="A drift detector is claimed to catch regime shifts at least 2x earlier than a fixed-threshold "
          "baseline at equal false-alarm rate. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Detection-delay ratio <= 0.5 at matched false-alarm rate frozen as the gate."),
            ("RESULT", "Measured ratio 1.38 (detector is 38% LATER); at every operating point on the ROC the "
                       "detector is dominated or matched (max advantage -4%)."),
            ("CONTROL", "A synthetic injected-shift battery recovers the gate for a known-shift class (ratio 0.41), "
                        "so the negative is specific to the natural-shift corpus, and is retained with that "
                        "boundary stated."),
        ],
        dp=["matched false-alarm operating points used", "synthetic battery run", "negative retained with boundary"],
        scope="the natural-shift corpus",
        forbid=["reporting only the synthetic battery", "claiming the 2x-earlier gate"],
    ),

    # ---------------- LEAKY_OR_CORRUPT_BENCHMARK (3) ----------------
    dict(
        family="LEAKY_OR_CORRUPT_BENCHMARK", gold="NEGATIVE",
        q="A three-defect instrument is retired after a floor-effect diagnosis; a report offers its earlier "
          "head-to-head victory (+9.6 points) as evidence of method superiority. Determine the strongest "
          "defensible action.",
        ev=[
            ("PROTOCOL", "Retirement record with three named defects frozen (task ceiling reached by both arms; "
                         "leaked holdout key in the scoring join; label duplication across folds)."),
            ("RESULT", "Post-repair re-run on a validated instrument: difference +0.1 points (CI [-1.3,+1.5], "
                       "includes 0)."),
            ("CONTROL", "Each defect's contribution is isolated: ceiling alone reduces the gap to +3.1; adding the "
                        "leak repair reduces to +0.4; dedup to +0.1."),
            ("BACKGROUND", "The retirement was recorded before the re-run; the earlier +9.6 remains in the archive "
                           "as evidence about the instrument, not the methods."),
        ],
        dp=["retirement record honored", "defect-isolation re-run complete", "earlier comparison withdrawn"],
        scope="the retired instrument only",
        forbid=["citing the +9.6 comparison as method evidence"],
    ),
    dict(
        family="LEAKY_OR_CORRUPT_BENCHMARK", gold="NEGATIVE",
        q="A held-out evaluation reports 91% for a method versus 74% for the baseline; the holdout is later found "
          "to overlap the tuning set through a preprocessing cache. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Split identities and cache paths frozen; cache-identity audit preregistered."),
            ("RESULT", "Overlap audit: 38% of holdout rows carry tuned preprocessing state. Post-purge re-run "
                       "(fresh cache, no shared state): 76% vs 74% (CI of the difference includes 0)."),
            ("CONTROL", "A deliberately-overlapping positive control reproduces the inflation mechanism exactly "
                        "(91% -> 76% under purge), certifying the diagnosis."),
        ],
        dp=["cache-identity audit executed", "purged re-run complete", "positive control certifies the mechanism"],
        scope="the frozen pipeline",
        forbid=["citing the 91%-vs-74% comparison"],
    ),
    dict(
        family="LEAKY_OR_CORRUPT_BENCHMARK", gold="NEGATIVE",
        q="A continuous-integration signal is offered as evidence that a system is green, with a runner-display "
          "summary showing all required jobs as failures when cancelled mid-run. Determine the strongest "
          "defensible action on evidence drawn from that signal.",
        ev=[
            ("PROTOCOL", "Green defined as conclusion=success on the head commit; display-level summaries declared "
                         "inadmissible at freeze."),
            ("RESULT", "The offered summary lists 6 jobs as failed; the run-level records show those 6 as "
                       "cancelled-by-upstream-restart with conclusion=cancelled, and a later rerun on the same "
                       "head reaches conclusion=success for all 6."),
            ("CONTROL", "A summary-to-record consistency check over 1,000 runs finds display failure labels with "
                        "conclusion=cancelled in 7.1% of rows - the display is a known lossy channel."),
            ("BACKGROUND", "No claim about the system's content is at stake; the question is what the evidence "
                           "channel can support."),
        ],
        dp=["run-level conclusions preferred over display summaries", "rerun-to-green completed", "decision recorded"],
        scope="the named signal channel",
        forbid=["treating display-cancelled as failure evidence", "treating display-green as success evidence"],
    ),

    # ---------------- NON_IDENTIFIABLE (2) ----------------
    dict(
        family="NON_IDENTIFIABLE", gold="NON_IDENTIFIABLE",
        q="Two training pipelines differ in a knob whose effect is claimed to be identifiable from final "
          "checkpoints alone. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Identifiability from checkpoints declared the estimand; run logs sealed."),
            ("PRIMARY", "An explicit construction: two run trajectories from different knob settings produce "
                        "byte-identical final checkpoints (loss curves differ only in removed auxiliary fields)."),
            ("RESULT", "The construction is verified over 50 seeded pairs: 50/50 byte-identical checkpoints from "
                       "different knob values; the checkpoint format provably discards the discriminating trace."),
            ("CONTROL", "With run logs unsealed, the knob is trivially readable - identifiability fails exactly at "
                        "the checkpoint granularity and nowhere else."),
        ],
        dp=["both-directions construction certified", "granularity boundary located", "decision recorded"],
        scope="final checkpoints without run logs",
        forbid=["claiming knob identification from checkpoints"],
    ),
    dict(
        family="NON_IDENTIFIABLE", gold="CANNOT_CHECK",
        q="A fairness-improvement claim is submitted where the evaluation artifact references a protected "
          "evaluation set whose contents are not in the visible evidence and cannot be reconstructed from it. "
          "Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Freeze requires the evaluation set, or its full construction recipe, to be present for "
                         "any claim that depends on it."),
            ("PRIMARY", "The submitted report references set S-protected (digested 4d21...) with construction "
                        "omitted for privacy; no recipe, split, or size is given."),
            ("RESULT", "A reconstruction attempt from the visible corpus yields 3 candidate sets with fairness "
                       "deltas of +0.011, -0.004, and +0.019 - the claim's sign is not stable across candidates."),
            ("CONTROL", "The digest is verifiable once an authorized party reveals the set; the channel for that "
                        "is external to this evidence."),
        ],
        dp=["protected-set reconstruction attempted", "sign instability across candidates documented", "external disclosure channel identified"],
        scope="as submitted, on set S-protected",
        forbid=["scoring the claim on a substitute set", "averaging across candidate sets"],
    ),

    # ---------------- REGIME_CHANGE_REOPEN (2, longitudinal pair) ----------------
    dict(
        family="REGIME_CHANGE_REOPEN", gold="REOPEN", round_no=1,
        q="Round 1 (budget 32) of a search-quality claim: best-found score 0.61 at budget 32, reported as a "
          "positive trend. Determine the strongest defensible action at this round.",
        ev=[
            ("PROTOCOL", "Longitudinal design frozen: rounds at budgets 32 and 128 preregistered; no terminal "
                         "action permitted on round-1 evidence alone."),
            ("RESULT", "Round 1 (budget 32): best score 0.61 (CI [0.57,0.65]); trend versus budget-16 pilot "
                       "(0.55) is positive but the pilot was not preregistered."),
            ("CONTROL", "Instrumentation check: budget accounting verified (32.0 +- 0.0 units consumed)."),
            ("BACKGROUND", "The round-2 budget escalation is scheduled and its protocol is already frozen."),
        ],
        dp=["round-1 scope respected", "scheduled escalation acknowledged", "no terminal action on round 1"],
        scope="budget 32",
        forbid=["closing the claim positive on round 1"],
    ),
    dict(
        family="REGIME_CHANGE_REOPEN", gold="REOPEN", round_no=2,
        q="Round 2 (budget 128) of the same search-quality claim: the preregistered escalation reverses the "
          "trend. Determine the strongest defensible action.",
        ev=[
            ("PROTOCOL", "Round-2 budget 128 frozen with round 1; same seeds, same scoring, preregistered "
                         "success gate (>= 0.70 at budget 128)."),
            ("RESULT", "Round 2: best score 0.58 (CI [0.55,0.61]); the 0.70 gate is excluded. Budget-accounting "
                       "verified (128.0 +- 0.0). The budget-32 optimum is not revisited - the search collapses "
                       "to a different basin (trace attached)."),
            ("CONTROL", "A held-out basin classifier confirms the round-2 basin differs from round-1 "
                        "(assignment 0.94 posterior)."),
            ("BACKGROUND", "The trend reversal is a regime change under the frozen longitudinal protocol; the "
                           "claim's record must be amended with both rounds, and the mechanism question reopened."),
        ],
        dp=["round-2 gate evaluated", "regime change certified under the frozen protocol", "round-1 record amended, not deleted"],
        scope="budgets 32 and 128",
        forbid=["deleting round 1", "reporting round 2 as a new claim"],
    ),
]

assert len(SPECS) == 24, len(SPECS)
