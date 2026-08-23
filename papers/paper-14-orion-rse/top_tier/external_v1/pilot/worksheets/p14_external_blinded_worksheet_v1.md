# External blinded adjudication worksheet (v1)

- Suite: 67 protected packets, 3 domains, 8 scientific-state families.
- Gold record file digest (sha256 of file bytes): 4b1acff51a333c44433e6c6cfae367c1513f3a0b2aa2e33a5120a32cdc5f8b1e
- Instructions: adjudicate each row from the packet evidence alone; never consult
  the gold partition; record agreement/disagreement with System-A and System-B.

| packet | domain | question (truncated) | System-A | System-B | adjudicator |
|---|---|---|---|---|---|
| PKT-FC-0001 | FORMAL | A quasivariety-style fragment Q is claimed to satisfy a dichotomy: either every failure of the fragment's pres... | PROMOTE | PROMOTE | |
| PKT-FC-0002 | FORMAL | An exact value 2n-3 (n>=7) is claimed for a combinatorial width parameter W, improving the known general bound... | PROMOTE | PROMOTE | |
| PKT-FC-0003 | FORMAL | A preservation theorem is claimed: a definable class closed under substructures and ultraproducts is claimed t... | PROMOTE | PROMOTE | |
| PKT-FC-0004 | FORMAL | A duality is claimed between two failure coordinates of a decision fragment: failure-by-nondefinability and fa... | PROMOTE | PROMOTE | |
| PKT-FC-0005 | FORMAL | Membership in a class C defined by a mixed quantifier fragment is claimed NL-complete (previously only the P u... | PROMOTE | PROMOTE | |
| PKT-FC-0006 | FORMAL | A 'novel modular compactness transfer' is claimed: satisfiability of a finite module-theoretic signature set t... | PROMOTE | SUBSUMED | |
| PKT-FC-0007 | FORMAL | A claimed-new lattice characterisation of a closure system is proposed: closed sets are exactly the sets close... | PROMOTE | SUBSUMED | |
| PKT-FC-0008 | FORMAL | A new invariant I(G) for a class of rewriting systems is proposed with a claimed novel monotonicity property u... | PROMOTE | SUBSUMED | |
| PKT-FC-0009 | FORMAL | A 'new' closure operator is proposed for separating two definable classes, built by composing two known operat... | PROMOTE | SUBSUMED | |
| PKT-FC-0010 | FORMAL | A quantitative interpolation bound c*n is claimed as new for a modal fragment, with experiments suggesting c=3... | PROMOTE | SUBSUMED | |
| PKT-FC-0011 | FORMAL | Shorter certificates are claimed for a decision fragment when a normal-form transformation T1 and an ordering ... | PROMOTE | INTERACTION_ONLY | |
| PKT-FC-0012 | FORMAL | A proof-search depth reduction is claimed for a combination of a restart strategy R3 and a lemma-ordering L4. ... | PROMOTE | CANNOT_CHECK | |
| PKT-FC-0013 | FORMAL | A known representation theorem (parent result, reproduced here with a new proof) is claimed to admit an algori... | PROMOTE | NULL_LIVE | |
| PKT-FC-0014 | FORMAL | A live counting formula (parent) is claimed to extend to a two-parameter refinement with a predicted interacti... | PROMOTE | NULL_LIVE | |
| PKT-FC-0015 | FORMAL | Conjecture: every P-definable class closed under substructures admits a finite axiomatisation. Determine the s... | PROMOTE | NEGATIVE | |
| PKT-FC-0016 | FORMAL | A claimed fixed-parameter tractability for a matching parameter k is asserted with a sketch. Determine the str... | PROMOTE | NEGATIVE | |
| PKT-FC-0017 | FORMAL | Decidability is claimed for a mixed first-order fragment with a transitive predicate. Determine the strongest ... | PROMOTE | NEGATIVE | |
| PKT-FC-0018 | FORMAL | A benchmark suite of 300 'hard' algebras is offered as evidence that a new decision method dominates. Determin... | PROMOTE | NEGATIVE | |
| PKT-FC-0019 | FORMAL | A certificate checker is offered as the verification oracle for a family of structural claims; 100% of claims ... | PROMOTE | NEGATIVE | |
| PKT-FC-0020 | FORMAL | A claimed conservation law for a rewriting calculus is offered with a proof that relies on a set-theoretic pri... | PROMOTE | NON_IDENTIFIABLE | |
| PKT-FC-0021 | FORMAL | A structure theorem is submitted whose proof appeals to an external lemma attributed to an out-of-scope manusc... | CANNOT_CHECK | CANNOT_CHECK | |
| PKT-FC-0022 | FORMAL | A search-depth conjecture is evaluated: exhaustive checking to depth 100 over 10^5 generated instances reports... | PROMOTE | PROMOTE | |
| PKT-FC-0023 | FORMAL | Round 2 of the depth conjecture: the preregistered budget escalation to depth 400 is executed. Determine the s... | PROMOTE | REOPEN | |
| PKT-EM-0001 | EMPIRICAL | A same-information representation change (no new data, no new model capacity) is claimed to improve out-of-sam... | PROMOTE | PROMOTE | |
| PKT-EM-0002 | EMPIRICAL | A probe-based steering rule is claimed to move an evaluation pass-rate from 0.9556 (protected baseline, below ... | PROMOTE | PROMOTE | |
| PKT-EM-0003 | EMPIRICAL | A selective-abstention policy is claimed to improve calibrated accuracy on a frozen decision task without redu... | PROMOTE | PROMOTE | |
| PKT-EM-0004 | EMPIRICAL | An 'improved estimator' for tail risk of a bounded scoring rule is proposed, reducing variance by 27% on bench... | PROMOTE | SUBSUMED | |
| PKT-EM-0005 | EMPIRICAL | A 'novel' two-stage resampling scheme for narrow-reliability claims is proposed: subsample, then bias-correct.... | PROMOTE | SUBSUMED | |
| PKT-EM-0006 | EMPIRICAL | A 'new' feature-attribution stability score is proposed, showing 3x more stable rankings than a baseline attri... | PROMOTE | SUBSUMED | |
| PKT-EM-0007 | EMPIRICAL | A 'novel' early-stopping rule for fine-tuning is proposed: stop when the running rank correlation of train and... | PROMOTE | SUBSUMED | |
| PKT-EM-0008 | EMPIRICAL | A calibration gain is claimed for the combination of a temperature schedule and a batch-composition constraint... | PROMOTE | CANNOT_CHECK | |
| PKT-EM-0009 | EMPIRICAL | An accuracy gain is claimed for combining curriculum ordering with a loss-masking rule. Determine the stronges... | PROMOTE | CANNOT_CHECK | |
| PKT-EM-0010 | EMPIRICAL | A sample-efficiency gain is claimed for the combination of a replay buffer and a representation freeze-schedul... | PROMOTE | CANNOT_CHECK | |
| PKT-EM-0011 | EMPIRICAL | A validated parent result (wine-quality transfer, parent effect reproduced) is claimed to extend to a new doma... | PROMOTE | NULL_LIVE | |
| PKT-EM-0012 | EMPIRICAL | A live parent result (representation gain +0.0113, reproduced) is claimed to generalise to a second task famil... | PROMOTE | NULL_LIVE | |
| PKT-EM-0013 | EMPIRICAL | A scaling parent result (log-linear fit, reproduced) is claimed to hold with an added curvature term. Determin... | PROMOTE | NULL_LIVE | |
| PKT-EM-0014 | EMPIRICAL | A live parent result (abstention gain -0.0293 Brier, reproduced) is claimed to survive under a stricter covera... | PROMOTE | NULL_LIVE | |
| PKT-EM-0015 | EMPIRICAL | A capability-scaling claim asserts that a small-model family (0.5B class) improves on a frozen evaluation afte... | PROMOTE | NEGATIVE | |
| PKT-EM-0016 | EMPIRICAL | A selection rule is claimed to beat its own parent selector on a frozen backtest with realistic execution cost... | PROMOTE | NEGATIVE | |
| PKT-EM-0017 | EMPIRICAL | A drift detector is claimed to catch regime shifts at least 2x earlier than a fixed-threshold baseline at equa... | PROMOTE | NEGATIVE | |
| PKT-EM-0018 | EMPIRICAL | A three-defect instrument is retired after a floor-effect diagnosis; a report offers its earlier head-to-head ... | PROMOTE | NEGATIVE | |
| PKT-EM-0019 | EMPIRICAL | A held-out evaluation reports 91% for a method versus 74% for the baseline; the holdout is later found to over... | PROMOTE | NEGATIVE | |
| PKT-EM-0020 | EMPIRICAL | A continuous-integration signal is offered as evidence that a system is green, with a runner-display summary s... | PROMOTE | NEGATIVE | |
| PKT-EM-0021 | EMPIRICAL | Two training pipelines differ in a knob whose effect is claimed to be identifiable from final checkpoints alon... | PROMOTE | NON_IDENTIFIABLE | |
| PKT-EM-0022 | EMPIRICAL | A fairness-improvement claim is submitted where the evaluation artifact references a protected evaluation set ... | PROMOTE | CANNOT_CHECK | |
| PKT-EM-0023 | EMPIRICAL | Round 1 (budget 32) of a search-quality claim: best-found score 0.61 at budget 32, reported as a positive tren... | PROMOTE | CANNOT_CHECK | |
| PKT-EM-0024 | EMPIRICAL | Round 2 (budget 128) of the same search-quality claim: the preregistered escalation reverses the trend. Determ... | PROMOTE | REOPEN | |
| PKT-RI-0001 | RESEARCH | A tamper-evident receipt format is claimed to make evaluation records independently checkable: any post-hoc ed... | PROMOTE | PROMOTE | |
| PKT-RI-0002 | RESEARCH | A deterministic-regeneration gate is claimed to make artifact generation bit-reproducible across machines (no ... | PROMOTE | PROMOTE | |
| PKT-RI-0003 | RESEARCH | A fail-closed contract checker is claimed to prevent evaluation-config drift: schemas must keep additionalProp... | PROMOTE | PROMOTE | |
| PKT-RI-0004 | RESEARCH | A 'novel' artifact-identity scheme is proposed: name artifacts by the SHA-256 of their canonical byte form. De... | PROMOTE | SUBSUMED | |
| PKT-RI-0005 | RESEARCH | A 'novel' staged-evaluation funnel is proposed: candidates pass through frozen gates with ratcheting threshold... | PROMOTE | SUBSUMED | |
| PKT-RI-0006 | RESEARCH | A 'novel' blind-scoring worksheet design is proposed: evaluators receive anonymised systems with identity stri... | PROMOTE | SUBSUMED | |
| PKT-RI-0007 | RESEARCH | A pipeline-latency gain is claimed for the combination of content-addressed caching and a stage-fusion rewrite... | PROMOTE | CANNOT_CHECK | |
| PKT-RI-0008 | RESEARCH | A correctness gain is claimed for combining a lock-free queue with a checkpoint interval change in a verificat... | PROMOTE | NEGATIVE | |
| PKT-RI-0009 | RESEARCH | A validated parent result (artifact-store dedup reclaiming 58 GB, reproduced) is claimed to extend to a second... | PROMOTE | CANNOT_CHECK | |
| PKT-RI-0010 | RESEARCH | A live parent result (CI display-artifact false-failure fix, reproduced) is claimed to reduce operator misclas... | PROMOTE | NULL_LIVE | |
| PKT-RI-0011 | RESEARCH | A live parent result (schema-hash drift detection catching 100% of injected contract drift, reproduced) is cla... | PROMOTE | PROMOTE | |
| PKT-RI-0012 | RESEARCH | A live-deployment widening is claimed: extending a window parameter is asserted to raise daily profit, support... | PROMOTE | NEGATIVE | |
| PKT-RI-0013 | RESEARCH | A shadow monitor is claimed to halve time-to-detection of performance decay. Determine the strongest defensibl... | PROMOTE | NEGATIVE | |
| PKT-RI-0014 | RESEARCH | An auto-configuration agent is claimed to hold evaluation cost within 1.2x of manual configuration while impro... | PROMOTE | NEGATIVE | |
| PKT-RI-0015 | RESEARCH | An aggregate 'system health' score is offered as evidence of improvement (72 -> 81), where the score averages ... | PROMOTE | NEGATIVE | |
| PKT-RI-0016 | RESEARCH | A log-based incident study is offered where 2>/dev/null redirections and `// true` guards are found on 14 of t... | PROMOTE | NEGATIVE | |
| PKT-RI-0017 | RESEARCH | A claim states that an execution gate was 'hard-enforced, not logged' - that the gate blocked actions rather t... | PROMOTE | NON_IDENTIFIABLE | |
| PKT-RI-0018 | RESEARCH | A dependency-isolation claim asserts that two co-deployed systems never shared state, based on a lock-file and... | CANNOT_CHECK | CANNOT_CHECK | |
| PKT-RI-0019 | RESEARCH | Round 1 of a stream-coverage claim: a data stream is declared unarchivable (no reader can be attached without ... | PROMOTE | CANNOT_CHECK | |
| PKT-RI-0020 | RESEARCH | Round 2 of the stream-coverage claim: the preregistered read-only tap protocol recovers the stream. Determine ... | PROMOTE | REOPEN | |
