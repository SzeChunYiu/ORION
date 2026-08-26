# FiberGuard R18 result — paired routing transfers from MaxSAT to untouched QBF

Date: 2026-08-26

Protocol-only commits: `bc3387916139af8a739a910eb58c354f73fb2a24` and `c2df6e2b47b69f387a33e0ebe5e272fc8a1aad74`.

Execution commit: `0f47a6e567191687ba1879cb63c8e630d16ee2d4`.

Dedicated workflow run/job: `33019055210` / `98339197606`.

Observed terminal:

`FIBERGUARD_R18_PAIRED_ROUTE_PASS_MAXSAT_VALIDATION_AND_QBF_TEST`

## Scientific disposition

The prospectively selected paired-route configuration passed the development gate on `MAXSAT12-PMS`, transferred without retuning to `MAXSAT19-UCMS`, and passed the untouched cross-domain `QBF-2016` gate.

This is the first positive application result after R16 established that one-sided learned-action calibration was insufficient. R18 models and calibrates both the learned solver action and the proper-training robust fallback, or directly calibrates their loss difference. The selected model, `alpha`, and route mode were chosen only on MAXSAT12. MAXSAT19 validated the frozen tuple and QBF-2016 was the untouched final test. Solver-regret models were refit within each scenario because the solver portfolios differ; the method/configuration tuple was not retuned.

All learned and routed arms paid the declared feature acquisition cost before routing. No post-rejection refund was admitted. Raw-runtime and declared-PAR10 scenarios were interpreted through their own declared performance measure, and timeout was kept separate from broader non-`ok` failure.

The complete audit executed twice byte-identically. Source blobs, nested official folds, the 99-candidate development denominator, authority flags, issue receipt, and uploaded result artifact were checked by the dedicated workflow.

## What the positive terminal establishes

1. A fallback-aware certificate can succeed where one-sided abstention failed: the route compares certified learned and fallback losses rather than treating learned-action uncertainty as sufficient evidence to defer.
2. The complete tuple—model family and parameters, certificate miscoverage level, and route mode—transferred from one MaxSAT development portfolio through a later MaxSAT validation portfolio to an untouched QBF portfolio.
3. Paid decision value, certificate failure, route-change coverage, catastrophic wrong action, timeout, non-`ok` failure, and declared performance remain distinct estimands.
4. The QBF terminal is cross-domain method evidence. It is not permission to retroactively tune the MaxSAT-selected tuple.

## Authority ceiling

The paired certificates are marginal under the official-fold exchangeability protocol. Interval no-harm claims are pointwise only on the simultaneous-validity event. The result does not establish deterministic worst-case fibre safety, arbitrary distribution-shift validity, conditional coverage among routed cases, or pathwise safety for randomized actions.

The current comparison menu contains frozen kNN and ExtraTrees references but does not close strongest-baseline completeness. AutoFolio or a stronger current robust algorithm-selection system under matched feature costs, an independent implementation/replay, current primary-source novelty adjudication, and at least one production-derived portfolio remain mandatory before top-tier promotion.

R14's exact-equality transfer failure, R16's calibrated-but-nonvaluable one-sided route, R17's fallback-alignment theorem, and R18's positive paired route must remain in one manuscript narrative. Omitting the adverse stages would overstate the evidence.
