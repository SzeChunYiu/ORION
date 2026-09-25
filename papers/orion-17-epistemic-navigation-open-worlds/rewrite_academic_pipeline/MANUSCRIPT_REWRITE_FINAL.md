# Dependency Density Predicts When Coarse Evidence Reuse Becomes Unsound

## Abstract

Scientific and software agents often reuse conclusions after a system changes. A coarse reuse policy can be inexpensive, but its validity depends on how widely a changed component can affect the rest of the system. We study this boundary in Python package dependency graphs. A three-domain development campaign suggested a simple mechanism: coarse donor-style closure is adequate on sparse import structure and becomes unsound as dependency density increases. Because the only sound development package was both small and sparse, size and density were initially confounded.

We prospectively freeze the rule “predict coarse reuse unsound when import edges per module are at least 1.5” and evaluate it on five previously held-out packages from five organizations. Predictions are committed before policy outcomes are generated. The rule is correct on all five packages: requests (0.84 edges/module) is sound, whereas networkx (2.14), django (3.68), tornado (5.57), and sympy (8.70) are unsound. The coarse policy produces 91,507, 63,398, 12,773, and 344,352 false retentions on those four packages; exact containment produces none. Tornado is the preregistered disambiguator: it is small relative to the large packages but dense, so a size explanation predicts sound while the density rule predicts unsound. The observed outcome is unsound.

The evidence supports a bounded prospective mechanism claim: within the registered Python import-graph construction, dependency density predicts when coarse closure becomes unsafe better than package size. The threshold was calibrated on three domains and validated on five; it is not established for other ecosystems, and the study does not model the magnitude of failure. Exact containment remains the authority-preserving donor rather than a claimed ORION invention. The paper contributes a forward-tested boundary for selective revalidation, not a universal software-dependency law.

## 1. Introduction

A previous result, certificate, or analysis may remain valid after a system changes, but only if the change leaves every load-bearing premise intact. Recomputing everything after every change is safe but expensive. Reusing everything is cheap but can preserve conclusions whose dependencies have silently changed. Practical systems therefore rely on approximations: reopen nearby components, follow a coarse donor relation, or retain conclusions unless an explicit local trigger fires.

The scientific question is not whether exact dependency closure is safer than a coarse approximation. That is expected. The useful question is whether a pre-outcome structural property predicts when the cheaper approximation is adequate and when it becomes unsound.

An earlier three-domain campaign suggested import-graph density as such a property. The approximation was sound on a sparse package and unsound on denser packages. However, the sound package was also the smallest. The observation therefore did not distinguish a density mechanism from a size mechanism. Post-hoc explanation is insufficient because many simple functions can separate three observed points.

We convert the explanation into a prospective prediction. A density threshold is fixed, five held-out packages are selected, and the prediction for each package is committed before policy outcomes are produced. One package, tornado, is chosen specifically because size and density give opposite predictions. This design makes a single disambiguating case more important than four additional examples that preserve the original confound.

## 2. Scientific object: reuse after dependency change

Consider a system represented by a directed import graph. A stored conclusion is supported by a set of modules or facts. After a change, a revalidation policy determines which conclusions remain reusable, which must be reopened, and which cannot be decided from available dependency information.

The study compares two policy families.

- **Exact containment** follows the registered dependency relation and reuses a conclusion only when its complete support remains outside the affected closure.
- **Donor-coarse reuse** uses a cheaper approximation to the change boundary. It can retain a conclusion even when a transitive support path has been affected.

A false retention occurs when the coarse policy reuses a conclusion that exact dependency truth says must be reopened. The endpoint is semantic safety, not runtime or prediction accuracy alone.

Exact containment is treated as a donor baseline and reference mechanism. The paper does not claim the general idea of dependency closure, selective revalidation, provenance tracking, or change-impact analysis.

## 3. Development observation and unresolved confound

The development campaign used three Python package domains. The cheap policy was adequate on flask, whose graph contains 24 modules and 0.79 import edges per module, and unsafe on larger, denser packages. This pattern suggested that dense dependency structure creates many transitive support paths that a coarse approximation fails to retain.

The same evidence also supported a size story: perhaps large packages are difficult and small packages are safe. With one small sparse package and no small dense package, the two explanations were observationally equivalent.

The manuscript therefore does not treat the development pattern as mechanism evidence. It is hypothesis-generating material used to freeze a threshold and a disambiguating test.

## 4. Prospective protocol

The registered rule is

\[
	ext{predict donor-coarse unsound}
\quad\Longleftrightarrow\quad
rac{\text{import edges}}{\text{modules}}\geq 1.5.
\]

The threshold is fixed before held-out outcomes exist. Density extraction constructs import graphs only; it does not evaluate either reuse policy. The chronology is recorded in three steps:

1. import graphs and density values are produced without policy evaluation;
2. predictions and the 1.5 threshold are committed;
3. exact and coarse policy outcomes are generated.

The five held-out packages are requests, networkx, django, tornado, and sympy. They come from five organizations and exclude the development packages. Every terminal—correct, incorrect, or uncheckable—would remain in the denominator.

Tornado is registered as the mechanism discriminator. With 74 modules it is much smaller than networkx, django, or sympy, but its density is 5.57 edges per module. A size rule predicts that it should behave like the small development package; the density rule predicts unsoundness.

## 5. Prospective results

The frozen rule predicts all five outcomes correctly.

| Package | Modules | Edges/module | Frozen prediction | Observed coarse-policy status | False retentions | Exact-containment false retentions |
|---|---:|---:|---|---|---:|---:|
| requests | 19 | 0.84 | sound | sound | 0 | 0 |
| networkx | 583 | 2.14 | unsound | unsound | 91,507 | 0 |
| django | 906 | 3.68 | unsound | unsound | 63,398 | 0 |
| tornado | 74 | 5.57 | unsound | unsound | 12,773 | 0 |
| sympy | 1,566 | 8.70 | unsound | unsound | 344,352 | 0 |

The prospective accuracy is 5/5. Because the sample is deliberately small and structured, this is reported as exact case-series evidence rather than an estimated population accuracy or calibrated probability.

Exact containment falsely retains nothing in any package. That result is consistent with the registered composition theory and establishes the safety reference for these cases; it does not create a claim that exact closure is cost-free or always the preferred deployed policy.

## 6. The disambiguator supports density rather than size

Tornado carries the mechanism inference. It has 74 modules—three times flask but far below the larger held-out packages—and 5.57 import edges per module. A simple size-based explanation predicts sound reuse; the frozen density rule predicts unsoundness. The coarse policy is unsound and retains 12,773 invalid conclusions.

The result does not prove that density is the only relevant graph property. It shows that package size cannot explain the development contrast once a small dense system is observed. Density is the registered variable that made the correct pre-outcome prediction.

Requests is less discriminating. It is both small and sparse, so it repeats the original sound condition without separating explanations. Networkx, django, and sympy strengthen the high-density pattern but are also large. The paper therefore assigns evidentiary weight by design rather than treating all five rows as exchangeable votes.

## 7. What “density carries the effect” means

The supported claim is conditional and operational. In the registered Python import-graph construction, the scalar density rule predicts whether the donor-coarse policy makes any false retention on the five held-out packages, and the predeclared small-dense case rejects the competing size explanation.

The study does not establish a monotone quantitative law for the number of failures. False-retention counts vary by more than an order of magnitude among the unsound packages and are influenced by graph topology, affected components, support distribution, and package-specific structure. Density predicts the binary safety boundary in this case series; it does not explain failure magnitude.

The threshold 1.5 is likewise not universal. It was calibrated on three packages and validated on five under one graph extraction and one policy definition. Applying it to another language ecosystem, build graph, package manager, or scientific workflow requires a new frozen study.

## 8. Relation to selective revalidation and open-world reasoning

Change-impact analysis, dependency tracking, truth-maintenance, build systems, provenance, incremental computation, and selective revalidation are mature donor areas. The paper does not claim the first use of graph closure or the general observation that coarse approximations fail on rich dependency structure.

The residual contribution is evidentiary. A post-hoc structural explanation is converted into a preregistered threshold; a case is chosen where size and density disagree; predictions are committed before outcome; and the exact donor remains visible as the safety reference. This makes the mechanism claim falsifiable without claiming a new dependency algorithm.

The result also illustrates a broader epistemic-navigation principle. Cheap local rules can be adequate in sparse or shallow structures and unsafe when dependencies compose richly. The present data support that principle only for the registered import graphs.

## 9. Independent verification

A structurally separate checker re-derives each density-side prediction and each observed safety terminal from recorded artifacts without importing the ORION-17 policy implementation. It includes negative controls: an inverted density rule must perform worse, and a size-based rule must fail on at least one held-out package. All registered checks and controls pass.

The independent implementation improves defect detection but remains inside the same research programme. It is not external custodianship or independent scientific replication.

## 10. Claim boundary and retained prior results

This study does not reopen or alter earlier ORION-17 claims. The arbitrary-length composition theorem retains its existing authority, and any earlier contrary framing remains retracted. The new case series is additive evidence about the failure boundary of the coarse policy.

The paper does not claim:

- transfer of the 1.5 threshold beyond Python import graphs;
- a population reliability estimate from five cases;
- prediction of the magnitude of false retention;
- runtime superiority of exact or coarse closure;
- a naturalistic longitudinal agent study;
- that dependency density is the only valid structural discriminator.

These exclusions are part of the scientific result, not release caveats.

## 11. Reproducibility and availability

The release package should include the frozen development densities, held-out package identities, graph-construction code, density-only artifacts, timestamped predictions, policy outcome files, exact-containment results, the independent checker, and chronology receipts. Development data, held-out predictions, and outcome generation must remain separately identifiable so that the forward test cannot be reconstructed retrospectively.

Package versions and source snapshots should be archived because import graphs can change over time. A named release should also document which imports are counted and how modules are identified.

## 12. Limitations and next study

Five successful predictions are strong evidence for the registered case series but weak evidence for an open population. The package set is limited to Python and may share ecosystem-level conventions. The density threshold may depend on graph extraction, and the binary endpoint suppresses important variation in error magnitude and revalidation cost.

A valid extension would freeze a policy and threshold family across materially different ecosystems—such as build graphs, workflow DAGs, or package managers—before outcomes are inspected. A second extension should measure the safety–cost frontier rather than safety alone. Neither is required for the bounded present paper.

## 13. Conclusion

A structural explanation becomes scientifically useful when it predicts a case designed to distinguish it from a plausible alternative. In the registered Python study, a dependency-density threshold fixed before outcome correctly predicts coarse-reuse safety on five held-out packages. The small but dense tornado package is unsound under the coarse policy, rejecting package size as the explanation of the development pattern. Exact containment retains zero invalid conclusions throughout. The result is a bounded prospective boundary for selective revalidation: sparse dependency structure can license a cheap approximation, while dense structure can make the same approximation unsafe.