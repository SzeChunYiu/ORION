# Route-Aware Stopping for Open-World Scientific Literature Discovery

## Abstract

Scientific literature discovery is not only a ranking problem. A search system may retrieve useful documents while remaining unable to justify that material routes to relevant evidence have been explored sufficiently to stop. We study this distinction through **route-aware stopping**, a governed retrieval framework that represents acquisition routes, route dependence, and unresolved coverage obligations explicitly. Search and synthesis are separated; unavailable or unobserved routes are not converted into evidence of absence; and a fail-closed diagnostic withholds completeness when its stopping assumptions are not met.

Controlled complete-gold and hostile cases establish the intended semantics of route identity, deduplication, dependence, and stopping. We then test the broader retrieval claim on all 50 official TREC-COVID topics under a matched external study. The result is mixed and is reported without endpoint substitution. Multi-route exploration improves nDCG@10 by 0.1488, with a bootstrap 95% interval of 0.1010 to 0.1995, and is ahead on 42 of 50 topics. However, the preregistered discovery gate does not pass: recall@100 is lower by 0.0177, with an interval of -0.0273 to -0.0091 against a -0.02 non-inferiority margin, and the method uses 175.7% more reads rather than achieving the required 25% reduction. Two of five intended route classes are unavailable in the frozen external setting, so the method also declines to declare route completeness on all 50 topics.

The paper therefore makes no retrieval-superiority claim. Its contribution is a methods and critical-system-design result: early ranking quality, route coverage, and authority to stop are distinct scientific objects. Preserving the adverse external gate is central to that conclusion because it shows that better top-ranked retrieval does not imply better open-world discovery on recall and cost, while unavailable evidence should remain an unresolved coverage obligation rather than a scientific zero.

## 1. Introduction

A literature-search system can know how well it ranks documents it has reached without knowing whether its search is complete enough to support a scientific conclusion. Relevant material may remain behind an unqueried citation path, an unavailable provider, a restricted collection, or a nominally different route that is actually dependent on a route already explored.

This distinction matters whenever search feeds scientific synthesis. Once a coherent answer begins to emerge, an automated system has a strong operational incentive to stop. A high-confidence synthesis, however, is not evidence that the remaining literature population is negligible.

We separate three questions:

1. How well does the strategy rank useful material among the documents it reaches?
2. Which materially distinct routes to evidence were actually explored, exhausted, unavailable, or left unresolved?
3. What evidence licenses a stopping decision rather than merely marking the end of a budget?

The proposed framework treats the first as retrieval quality and the latter two as coverage governance. It does not assume that explicit governance will improve recall or reduce cost. Those are empirical questions, and the external study in this paper gives an adverse answer to the strongest joint claim.

The contribution is therefore deliberately two-layered. Controlled studies test the semantics of the stopping mechanism; the external benchmark tests whether that mechanism also earns a broad retrieval advantage. The manuscript does not allow the first layer to overwrite failure in the second.

## 2. Route-aware discovery state

### 2.1 Routes are acquisition mechanisms, not labels

A discovery episode maintains several candidate acquisition routes. A route can correspond to a provider, citation expansion, a restricted collection, or another materially distinct acquisition mechanism. Different names do not automatically establish independence. If two nominal routes share a backend, seed, or censoring mechanism that makes their observations dependent, that dependence remains part of the search state.

Each route is assigned a status such as active, exhausted under its declared rule, unavailable, or unresolved. Unavailable and unresolved routes remain visible. They do not contribute a negative observation merely because no document was retrieved from them.

### 2.2 Question-framed evidence memory

Retrieved material is stored relative to the scientific question and route that motivated the read. This prevents a document from becoming globally marked as supportive or irrelevant when its value depends on a particular query, inferential role, or acquisition path.

The paper does not claim structured memory as a new mechanism. Its role is to bind evidence to the search decision whose completeness is being evaluated.

### 2.3 Task completion is different from coverage closure

A system can have enough material to answer provisionally while still lacking evidence that search is complete. Conversely, a route can be exhausted without resolving the scientific question.

The stopping diagnostic therefore returns an unresolved terminal when material routes remain unavailable, route dependence cannot be established, or an estimator lacks the information required by its assumptions. A budget limit or provider failure is never silently recoded as evidence that additional relevant literature does not exist.

## 3. Controlled mechanism tests

Before making an external retrieval claim, we exercise the framework in complete-gold worlds and hostile cases where route truth is known exactly.

The controlled tests enforce four properties. First, lexical and route-aware strategies are compared under matched call budgets where the test requires it. Second, two routes that share a backend cannot earn independence merely through different labels. Third, repeated encounters with the same content are deduplicated rather than counted as independent evidence. Fourth, overlap-based unseen-population reasoning fails closed when the overlap pattern does not identify the required quantity; a zero-overlap case remains indeterminate rather than receiving a confident unseen-count estimate.

These studies establish implementation semantics. They do not establish field performance and are not substituted for the external benchmark.

## 4. External study on 50 TREC-COVID topics

The broader claim is evaluated on the official 50-topic TREC-COVID collection under a frozen matched external design. Topic identities, comparator definitions, budgets, and outcome labels are fixed for the study.

The result separates a favorable ranking endpoint from the preregistered discovery gate.

### 4.1 Early ranking improves

The route-aware strategy improves nDCG@10 by 0.1488 relative to the matched comparator. The bootstrap 95% interval is 0.1010 to 0.1995, and the route-aware method is ahead on 42 of the 50 topics.

This is evidence that multi-route exploration improves the quality of the highest-ranked material under the tested configuration.

### 4.2 Recall non-inferiority is not established

The registered broader claim required recall to remain within a prespecified non-inferiority margin while reading cost decreased. Recall@100 differs by -0.0177, with a bootstrap 95% interval of -0.0273 to -0.0091. Because the lower interval bound falls below the registered -0.02 margin, recall non-inferiority is not established.

The favorable nDCG result answers a different question and is not used as a replacement endpoint.

### 4.3 Reading cost moves in the wrong direction

The registered design also required a 25% reduction in reading effort. Instead, the route-aware strategy uses 175.7% more reads under the frozen external setting.

This is not a small miss around the target. It reverses the direction of the intended efficiency result. The manuscript therefore rejects the joint claim that the tested route-aware method improves open-world discovery by preserving recall while reducing reading cost.

### 4.4 Completeness remains unresolved

Two of the five intended route classes cannot be executed in the external campaign. One lacks an earned seed and another lacks an available provider. Because material route obligations remain open, the route-aware system does not declare completeness on any of the 50 topics under the registered closure rule.

This behavior is not scored as retrieval superiority. It is the governance property under study: missing access remains an evidence limitation rather than becoming evidence of absence.

## 5. Interpreting the mixed result

The external study rules out the strongest version of the paper. The method improves early ranking but does not satisfy the preregistered recall-and-cost gate. This adverse result sharpens rather than erases the residual contribution.

First, ranking quality and coverage authority are empirically separable. A method can retrieve better top-ranked documents while being worse or unproven on broader recall and cost. Second, route availability is a property of the evidence process, not of the scientific world being searched. Third, an unresolved stopping terminal can prevent synthesis confidence from being laundered into a claim that material search routes are exhausted.

The method may therefore be useful in high-assurance discovery settings even if it is not an efficiency improvement in the present benchmark. Whether that tradeoff is worthwhile is a deployment question not answered by these data.

## 6. Route dependence and fail-closed population reasoning

Open-world stopping rules often rely on information about overlap or diminishing discovery across routes. Such estimators are assumption-dependent. Shared providers, duplicated content, route censoring, and zero overlap can make the unseen population weakly identified or non-identifying.

The framework does not solve those identification problems by assertion. Instead, route dependence is recorded explicitly and a closure estimate is withheld when its assumptions are not supported. This policy can increase search cost, as the external study demonstrates. The cost is part of the scientific result rather than an implementation inconvenience to hide.

## 7. Relation to neighboring work

Information retrieval, automated systematic review, retrieval-augmented generation, agentic search, citation expansion, and capture-recapture estimation each address parts of this problem. The paper does not claim these mechanisms as new.

Its residual contribution is the control interface among them: route identity and dependence are explicit; task completion and coverage closure are separate; stopping claims require evidence appropriate to their assumptions; and inaccessible routes remain unresolved. This makes the work closer to an information-science methods and critical system-design paper than to a state-of-the-art ranking paper.

## 8. Limitations

The external study does not support retrieval superiority on the registered recall-and-cost objective. The controlled mechanism studies cannot substitute for that failure. Two intended route classes are unavailable in the external setting, and the current route taxonomy is not proved complete for open scientific search.

The coverage estimators remain assumption-dependent, and fail-closed behavior may be unnecessarily expensive in well-defined closed collections. The study also stops at discovery mechanics: it does not establish that route-aware search improves the truth, completeness, or calibration of downstream scientific synthesis.

## 9. Reproducibility and availability

The release package should bind the 50-topic study definition, retrieval-arm contracts, outcome tables, bootstrap analysis, controlled hostile cases, and replay logic to one versioned archive. Provider-restricted material should be described through lawful access conditions rather than represented as publicly available.

The IP&M reviewer-facing package should keep the adverse preregistered gate prominent and preserve blind/named surface separation. A clean PDF alone is insufficient if the release audit still detects identity or package inconsistencies.

## 10. Conclusion

Open-world literature discovery requires a theory of stopping in addition to a ranking function. In the external TREC-COVID study, multi-route exploration improves top-ranked quality but fails the preregistered recall-and-cost gate and cannot close route coverage because two intended routes are unavailable. The resulting contribution is therefore not retrieval superiority. It is a fail-closed methods framework that distinguishes useful ranking from authority to stop, and treats missing routes as unresolved scientific obligations rather than zeros.