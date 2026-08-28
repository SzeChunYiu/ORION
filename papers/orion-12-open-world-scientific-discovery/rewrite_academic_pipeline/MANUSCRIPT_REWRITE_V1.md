# Open-World Literature Discovery with Route-Aware Stopping and Fail-Closed Coverage Diagnostics

## Abstract

Literature-search systems are commonly evaluated as retrieval engines, yet scientific discovery has an additional difficulty: a search process rarely knows whether all material routes to relevant evidence have been explored. We study open-world scientific literature discovery as a governed retrieval problem in which route coverage, route independence and stopping are explicit rather than inferred from confidence alone. The method separates search from synthesis, records which evidence routes have earned independence, preserves unresolved routes as open coverage obligations, and refuses to convert unavailable or unobserved routes into evidence of absence.

A controlled complete-gold programme establishes the internal mechanics of route-aware stopping and hostile coverage checks. We then evaluate the broader retrieval claim on 50 official TREC-COVID topics under a matched external budget. The result is deliberately mixed. Multi-route exploration improves nDCG@10 by 0.1488 with a bootstrap 95% interval of 0.1010 to 0.1995 and is ahead on 42 of 50 topics. However, the preregistered external gate is not met: recall@100 is lower by 0.0177, with a bootstrap interval of -0.0273 to -0.0091 against a -0.02 non-inferiority margin, and the method requires 175.7% more reads rather than the required 25% reduction. Two of five intended routes are unavailable in this setting, so the route-aware method also declines to declare search completeness on all 50 topics.

The paper therefore does not claim retrieval superiority. Its contribution is a methods and system-design result: scientific discovery benefits from distinguishing ranking quality from coverage authority, and a search system should preserve unresolved route obligations rather than laundering incomplete access into a closed-world answer. The adverse external result is part of the contribution because it shows that better early ranking does not by itself justify a claim of better open-world discovery.

## 1. Introduction

Scientific literature search operates under a structural uncertainty that standard information-retrieval evaluation only partly captures. A system can rank the documents it has seen, but it may not know whether relevant material exists behind an unqueried citation path, an unavailable provider, a restricted source or a search route that has not earned independence from routes already explored.

This distinction matters when retrieval output is used to support scientific claims. High precision near the top of a ranking can be useful even when the search remains incomplete. Conversely, a system can retrieve many documents while still lacking evidence that the remaining unseen population is small enough to justify stopping.

We therefore separate three questions:

1. How well does a search strategy rank useful material among what it reaches?
2. What routes to relevant evidence have actually been explored, and which of those routes are meaningfully independent?
3. What evidence licenses the system to stop searching rather than simply exhausting a budget?

The proposed framework treats the first question as retrieval quality and the latter two as coverage governance. It does not claim that route-aware governance automatically improves recall or cost. Instead, it makes incompleteness explicit and testable.

## 2. Route-aware discovery

### 2.1 Search routes as scientific state

A discovery episode maintains a set of candidate routes rather than a single undifferentiated query stream. A route may correspond to a provider, citation expansion, a restricted collection or another materially distinct acquisition mechanism. Route labels do not automatically imply independence. Independence must be earned by the acquisition mechanism and evidence state rather than assumed from different names applied to the same backend.

Each route can be active, exhausted under its declared rule, unavailable or unresolved. Unavailable and unresolved routes remain visible. They do not contribute a scientific zero.

### 2.2 Question-framed read memory

Retrieved material is stored relative to the scientific question that motivated the read. This is intended to reduce a common failure in iterative discovery: a document is remembered as generally supportive or irrelevant even though its value depends on the current question and search route.

The mechanism is not a claim that structured memory is novel. Its role here is to bind retrieved evidence to the discovery decision being evaluated.

### 2.3 Stopping is not a confidence threshold

The stopping rule separates task progress from route coverage. A system may have enough material to synthesize a provisional answer while still lacking evidence that search is complete. Conversely, a route can be exhausted without implying that the scientific question itself is resolved.

A fail-closed coverage diagnostic returns an unresolved state when material routes remain unavailable, dependence among routes cannot be established, or a stopping estimator lacks the information needed by its assumptions. This prevents a budget limit or provider failure from being silently recoded as evidence that no further relevant literature exists.

## 3. Controlled mechanism tests

Before testing broad external retrieval claims, the method is exercised in complete-gold local worlds and hostile coverage cases. These tests focus on semantics rather than field performance.

The checks require a lexical baseline under the same call budget, reject claimed route independence when two routes share a backend, deduplicate repeated encounters with the same content, and refuse to treat a single retrieved target as a recall estimate for an unseen population. Cases with zero overlap between routes remain indeterminate for overlap-based population inference rather than being assigned a confident unseen count.

These controlled tests establish that the implementation follows the intended route and stopping rules. They do not establish that the method retrieves more useful literature in real open-world search.

## 4. External evaluation on TREC-COVID

We evaluate the broader claim on 50 official TREC-COVID topics. The comparison uses a matched external study with fixed topic identities, retrieval budgets and evaluation labels.

The result separates ranking quality from the preregistered discovery gate.

### 4.1 Top-ranked quality improves

The route-aware method improves nDCG@10 by 0.1488 relative to the matched comparator. A bootstrap 95% interval is 0.1010 to 0.1995, and the method is ahead on 42 of 50 topics. This is evidence that multi-route exploration can improve the quality of the highest-ranked material under the tested configuration.

### 4.2 The registered discovery gate does not pass

The broader hypothesis required recall to remain within a prespecified non-inferiority margin while reducing reading cost. Neither condition is established jointly.

Recall@100 differs by -0.0177, with a bootstrap 95% interval from -0.0273 to -0.0091. Because the lower bound crosses the registered -0.02 margin, recall non-inferiority is not established. The method also increases reads by 175.7%, in the opposite direction from the preregistered 25% cost-reduction requirement.

The favorable nDCG result is not substituted for these failed criteria. It answers a different question.

### 4.3 Route completeness remains unresolved

Two of the five intended route classes cannot be executed in the frozen external setting. One lacks an earned seed and another lacks an available provider. The route-aware method therefore declines to declare completeness on all 50 topics even where simpler baselines return a closed terminal.

This behavior is not counted as retrieval superiority. It is the intended semantic distinction between a search answer and an authorized claim that material routes are exhausted.

## 5. What the mixed result means

The external study rules out the strongest version of the paper. We cannot claim that route-aware open-world discovery improves both recall and cost over the matched comparator. The data instead support a narrower and, for system design, useful conclusion.

First, ranking improvement and discovery completeness are separable. A method can improve early ranking while failing a recall-and-cost gate. Second, missing route access is an evidence limitation rather than a negative observation. Third, an explicit unresolved terminal can prevent an automated discovery system from turning unavailable evidence into an unjustified completeness claim.

These properties are especially relevant for scientific workflows in which downstream synthesis may tempt a system to stop searching once a coherent narrative emerges.

## 6. Relation to neighboring work

Scientific retrieval, retrieval-augmented generation, agentic search, automated systematic review and capture-recapture estimation each address important parts of the discovery problem. The present work does not claim those mechanisms as new.

The residual contribution is their control interface: route identity and independence are explicit; route coverage and task completion are separate; and insufficient evidence for stopping remains unresolved. This makes the paper closer to a methods and critical-system-design study than to a state-of-the-art retrieval paper.

## 7. Limitations

The strongest limitation is empirical. The external study does not support superiority on the registered recall-and-cost objective. The controlled mechanism results do not substitute for that failure. The route set is also incomplete in the external campaign, and the study does not establish that the declared route taxonomy covers all material acquisition mechanisms in open scientific search.

Coverage estimators are assumption-dependent. Route dependence, provider censoring and restricted access can make unseen-population estimates non-identifying. The framework handles such cases by refusing closure, but that safety behavior can increase cost and may be unnecessary in settings with reliable closed collections.

Finally, the current evidence does not show that the method improves end-to-end scientific conclusions. It evaluates discovery mechanics and retrieval outcomes, not the truth of downstream synthesis.

## 8. Reproducibility and availability

The final publication package should include the fixed external topic set, retrieval-arm definitions, outcome tables, bootstrap analysis, controlled hostile cases and a replay path that reproduces the reported metrics from the bound source data. Provider-restricted material should be described through the strongest lawful access route rather than represented as publicly available.

## 9. Conclusion

Open-world literature discovery requires more than ranking documents. It also requires a disciplined account of which evidence routes were searched and what justifies stopping. In the external TREC-COVID study, multi-route search improves top-ranked quality but does not satisfy the preregistered recall-and-cost gate. Preserving that adverse result clarifies the paper's contribution: route-aware stopping and fail-closed coverage diagnostics are useful governance mechanisms for scientific search, but they are not evidence of retrieval superiority by themselves.