# Route-Aware Stopping for Open-World Scientific Literature Discovery

## Abstract

Scientific literature discovery is not only a ranking problem. A search system may retrieve useful documents while remaining unable to justify that materially distinct routes to relevant evidence have been explored sufficiently to stop. We study **route-aware stopping**, a governed retrieval framework that represents acquisition routes, route dependence, unavailable access and unresolved coverage obligations explicitly. Search quality and authority to stop are treated as separate scientific objects.

Controlled complete-gold and hostile studies test route identity, deduplication, dependence and fail-closed stopping. These are mechanism-conformance tests, not evidence of retrieval superiority: in several controlled comparisons only the governed rule exposes an explicit unresolved terminal, so a “premature closure” contrast is partly determined by the output contract itself. The broader empirical claim is therefore evaluated separately on all 50 official TREC-COVID topics under a frozen external design.

The external result is mixed and adverse to the preregistered joint claim. Multi-route exploration improves nDCG@10 by 0.1488 (bootstrap 95% interval 0.1010–0.1995) and is ahead on 42 of 50 topics. However, recall@100 is lower by 0.0177, with interval -0.0273 to -0.0091 against a -0.02 non-inferiority margin, so recall non-inferiority is not established. The method uses 175.7% more reads rather than achieving the required 25% reduction. Two of five intended route classes are unavailable in the frozen external setting, and the system therefore declines to declare route completeness on all 50 topics.

The paper makes no retrieval-superiority claim. Its contribution is a methods and critical-system-design result: early ranking quality, route coverage, and evidentiary authority to stop are distinct. The adverse external gate is central because it shows that better top-ranked retrieval can coexist with worse or unresolved broader discovery properties, while unavailable routes should remain unresolved rather than being converted into evidence of absence.

## 1. Ranking quality is not search closure

Literature-search systems typically optimize what they can observe: ranking metrics, recall against a known corpus, user utility, or synthesis quality over retrieved documents. Open scientific discovery adds a harder question. Relevant evidence may remain behind an unavailable provider, unqueried citation path, restricted collection, or route that looks independent but shares the same censoring mechanism as another route.

Once a plausible synthesis appears, an automated system has a strong operational incentive to stop. Confidence in the synthesis, however, is not evidence that remaining evidence routes are exhausted.

We separate three questions:

1. How useful is the material ranked near the top?
2. Which materially distinct acquisition routes have actually been explored, exhausted, unavailable, dependent, or unresolved?
3. What evidence licenses a stopping decision rather than merely recording the end of a budget?

The proposed framework addresses questions 2 and 3 while remaining compatible with ordinary retrieval methods for question 1. Whether this governance improves retrieval quality or cost is an empirical question, not an assumed benefit.

## 2. Route-aware discovery state

A discovery episode maintains explicit acquisition routes. A route may correspond to a database/provider, citation expansion, a restricted corpus, or another materially distinct mechanism. Route names do not create independence: shared backends, shared seeds or common censoring remain part of the state.

Each route can be active, exhausted under a declared rule, unavailable, or unresolved. Unavailable routes do not contribute negative evidence merely because no document was returned.

Retrieved material is stored relative to the scientific question and route under which it was read. This prevents one reading decision from becoming a global statement that a source is supportive, irrelevant or exhausted for every question.

The stopping layer may return an explicit unresolved terminal when a material route is unavailable, dependence is unverified, or an estimator lacks identifying information.

## 3. Controlled studies are conformance tests, not a performance result

Complete-gold and hostile worlds are useful because route truth is known exactly. They test whether the implementation respects four intended semantics:

- nominally different routes that share a backend do not earn independence;
- repeated content is deduplicated rather than counted as independent discovery;
- unavailable routes remain unresolved rather than becoming zero evidence;
- overlap-based unseen-population reasoning fails closed when its assumptions do not identify the required quantity.

These studies also compare closure behavior with simpler baselines. That comparison must be interpreted carefully. Some baselines have only a closed/continue-like terminal while the governed system can emit an explicit `undetermined` state. A difference in “premature closure” is therefore partly **definition-driven by the decision alphabet**: a policy that cannot represent unresolved coverage cannot reproduce that terminal.

Accordingly, the controlled results establish implementation and semantic discrimination. They do not estimate how much better the governed system is at real literature discovery. The external benchmark carries that empirical burden.

## 4. External TREC-COVID study

The broader claim is tested on all 50 official TREC-COVID topics. Topic identities, retrieval arms, read accounting, endpoints and the joint success gate are frozen for the study.

The external evaluation separates a favorable top-ranking result from an adverse recall-and-cost result.

### 4.1 Top-ranked material improves

Route-aware exploration improves nDCG@10 by 0.1488 relative to the matched external comparator. The paired bootstrap 95% interval is 0.1010 to 0.1995, and the route-aware method is ahead on 42 of 50 topics.

This supports a bounded statement about early ranking quality under the tested configuration.

### 4.2 Recall non-inferiority is not established

The preregistered discovery claim required recall to remain within a -0.02 non-inferiority margin while reading effort decreased. The observed recall@100 difference is -0.0177 with a 95% interval from -0.0273 to -0.0091.

Because the lower interval bound crosses below the prespecified -0.02 margin, recall non-inferiority is not established. The favorable nDCG result is a different estimand and is not substituted for the failed recall criterion.

### 4.3 Reading cost moves in the wrong direction

The registered design required a 25% reduction in reads. Instead, the route-aware method uses 175.7% more reads in the external setting.

This is not a threshold miss close to equivalence. The direction is opposite the intended efficiency result. The joint claim of preserved recall plus reduced reading cost is therefore rejected for this implementation and setting.

### 4.4 Coverage authority remains unresolved

Two of the five intended route classes cannot be executed in the external campaign: one lacks an earned seed and another lacks an available provider. Under the registered closure rule, material route obligations remain open.

The system consequently makes no route-completeness declaration on any of the 50 topics. This is not counted as retrieval success. It is the fail-closed governance behavior being evaluated: lack of access is represented as lack of authority, not absence of relevant literature.

## 5. Interpreting the adverse joint gate

The external result rules out the strongest intended story. The tested route-aware strategy is not a demonstrated retrieval-efficiency improvement. It produces better top-ranked material while failing to establish recall non-inferiority and consuming substantially more reads.

That adverse result sharpens the residual contribution in three ways.

First, **ranking and closure are empirically separable**. Better top-ranked material does not imply broader search coverage or lower acquisition cost.

Second, **route availability belongs to the evidence process**. Provider failure cannot be interpreted as a scientific zero.

Third, **fail-closed stopping has a real cost**. Refusing to declare completeness when material routes remain open may require more search. That burden should be measured rather than omitted from a governance paper.

Whether the trade-off is worthwhile depends on the application and is not answered by the current benchmark.

## 6. Route dependence and weak identification

Open-world stopping rules often use route overlap or diminishing discovery to infer unseen evidence. Such reasoning is assumption-dependent. Shared providers, route censoring, duplicated content and zero overlap can make unseen-population quantities weakly identified or non-identifying.

The framework does not repair weak identification through a more confident estimator. It records the dependence and withholds closure when the assumptions required by the estimator are unsupported.

This may be conservative in closed or well-indexed collections. The present contribution is not that fail-closed behavior is universally optimal; it is that the evidence needed to license closure should be visible and falsifiable.

## 7. Relation to information retrieval and scientific search

Information retrieval, automated systematic review, citation expansion, retrieval-augmented generation, agentic search and capture-recapture estimation own substantial parts of the technical landscape. The paper does not claim multi-route search, deduplication, citation expansion or unseen-population estimation as new primitives.

The residual lies in the control interface among them: route identity and dependence are explicit; task completion and coverage closure are separated; stopping claims are typed by their assumptions; and inaccessible routes remain unresolved.

This makes the paper a critical system-design contribution for information science rather than a state-of-the-art ranking paper. The strongest external empirical result is intentionally mixed.

## 8. Limitations

The external study does not support the registered retrieval-superiority objective. Controlled conformance studies cannot substitute for that failure. Two intended route classes are absent from the external campaign, and the current route taxonomy is not proved complete for open scientific search.

Coverage estimators remain assumption-dependent. Fail-closed behavior may be unnecessarily expensive in closed corpora with strong indexing guarantees. The study also stops before downstream synthesis: it does not show that route-aware stopping improves the truth, completeness or calibration of scientific conclusions produced from the retrieved literature.

## 9. Reproducibility and release

The publication package should bind the 50-topic external protocol, retrieval-arm contracts, topic-level outcomes, paired bootstrap analysis, read accounting, controlled hostile cases and replay logic. Provider-restricted material should be described through lawful access conditions rather than falsely represented as publicly redistributable.

The anonymous IP&M surface and the named preprint surface must remain mutually consistent. A compiled PDF is not sufficient while the blind/named release audit remains red.

## 10. Conclusion

Open-world scientific literature discovery requires a stopping theory in addition to a ranking function. In the external TREC-COVID study, multi-route exploration improves nDCG@10 but fails the preregistered recall-and-cost gate and cannot close route coverage because two intended routes are unavailable. Controlled premature-closure contrasts are retained as semantic conformance tests, not inflated into performance evidence. The resulting contribution is a fail-closed discovery methodology that distinguishes useful ranking from authority to stop and treats missing routes as unresolved scientific obligations rather than zeros.