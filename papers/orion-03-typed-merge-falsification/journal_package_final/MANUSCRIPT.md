# Typed Evidence Licenses for Fail-Closed Nonpromotion in Finite Rule Systems

## Abstract

Derivability does not by itself determine the evidential status of a scientific claim. After a counterexample invalidates one support route, a conclusion may remain reachable through another route while losing the license needed to describe it as prospective, theorem-level, or externally reproduced. We formalize this bounded problem for finite positive conjunctive rule systems. Independent seeds carry subsets of a finite evidence-license universe, each rule transmits only licenses shared by all premises and permitted by an explicit cap, and directly refuted claims are fixed to the empty label. The resulting monotone operator has a finite least fixed point. We prove an equivalent finite proof-tree semantics, fail-closed behavior for unsupported cycles, monotone loss of licenses under additional refutations, and exact removal of claim-license pairs whose typed proof trees no longer survive. A deterministic evaluator implements the declared algebra and exercises three scientific-record cases. In a separately frozen OpenSSL 3.6.4 instantiation, flat trust-store union produced 46 hybrid authorizations among 1,962 merge tasks that neither parent store authorized. An origin-witness policy excludes those hybrids by definition and requires both parent evaluations; its zero errors are therefore analytic identities, not learned performance. The result is a scoped evidence-license specialization with executable nonpromotion semantics and a third-party-corpus, native-engine obstruction-and-cost instantiation, not a new general provenance theory or a security evaluation.

**Keywords:** scientific authority; falsification; provenance; least fixed points; evidence licenses

## Introduction

A scientific record can preserve a conclusion after losing the evidence class that once licensed one route to that conclusion. A prospective forecast may be replaced after its outcome is known by a distinct, post-outcome route. A finite exact computation may support a bounded statement without proving a theorem-shaped generalization. An independent derivation may survive a counterexample even when another derivation is withdrawn. Directly refuting the conclusion itself is different: under the algebra below, its label is then empty. In each surviving-route case, ordinary reachability answers only whether some path to the conclusion remains. It does not answer which evidence type is carried by that path.

This distinction matters whenever records are merged, revised, or mechanically propagated. If a post-outcome route inherits the word *prospective* merely because it reaches a conclusion also reached by the original forecast route, the record has promoted weaker evidence. If a rule combines a theorem with an unrelated bounded computation and reports the result as a theorem, it has mixed authorities that no single derivation carries end to end. These are failures of evidence typing rather than failures of Boolean inference.

Truth-maintenance systems, belief revision, positive logic programming, annotated logics, and database provenance already provide substantial parts of the mathematical substrate [@doyle1979; @martins1988; @agm1985; @kifer1992; @green2007; @cheney2009]. We therefore do not claim a new general theory of fixed points, proof trees, provenance, minimal support, or deletion robustness. The contribution is a narrower specialization. A finite set of evidence licenses is attached to claims, every conjunctive rule carries an explicit license cap, and a license can cross a rule only when all premises and the cap admit it. This makes nonpromotion an executable invariant rather than a prose warning.

The paper makes four bounded contributions.

1. It defines a finite positive conjunctive authority system whose synchronous semantics is a least fixed point over powerset labels.
2. It proves a finite typed proof-tree characterization, refutation monotonicity, and exact semantic retraction relative to the declared seeds, rules, caps, and refutations.
3. It provides a deterministic evaluator, schema validation, proof-tree reconstruction, and three scientific-record cases that separate Boolean reachability from licensed use.
4. It reports a third-party-corpus X.509 trust-store instantiation in which hybrid authorizations occur in third-party material and alternative merge policies pay different measured costs.

The last contribution has an important boundary. The origin-witness policy used in the X.509 study returns exactly the disjunction of the two parent-store decisions. Its zero unsafe merges and zero needless rejections are logical consequences of that definition, not evidence that a detector learned or outperformed a comparator. The empirical result is instead that the hybrid obstruction occurs, that flat and conservative merge policies behave differently on the frozen tasks, and that retaining origin distinctions requires additional native-engine work. No attack, deployed incident, whole-public-key-infrastructure guarantee, or human usability claim is made.

## Related work and contribution boundary

### Belief maintenance and revision

Doyle's truth-maintenance system associates conclusions with justifications and revises beliefs when supporting assumptions change [@doyle1979]. Martins and Shapiro develop a belief-revision model that retains multiple support contexts [@martins1988]. The Alchourrón-Gärdenfors-Makinson (AGM) framework characterizes rational contraction and revision at a more abstract level [@agm1985]. These traditions own the general problem of dependency-sensitive update. The present system does not compete with their expressivity. It fixes a small positive rule language and asks a different operational question: which declared evidence license survives every edge of a particular derivation after direct refutation?

### Annotated logic and provenance

Generalized annotated logic programming studies logical atoms carrying values from an annotation domain [@kifer1992]. Provenance semirings describe how alternative and joint derivations compose, and subsequent work extends provenance to recursion and Datalog convergence [@green2007; @bourgaux2022; @abokhamis2022]. Provenance and trust annotations have also been combined in linked-data reasoning [@bonatti2011], while the broader database-provenance literature distinguishes why, how, and where provenance [@cheney2009]. These are direct donors. In particular, the use of an ordered annotation domain, positive fixed-point evaluation, and derivation trees is not novel here.

Deletion propagation and database causality more directly study how removing source facts changes query answers and which inputs explain an answer [@buneman2002; @meliou2010]. Recent work on recursive Datalog organizes minimal supports as a hypergraph that determines actual causes, responsibility, and deletion robustness, while its stratified-negation extension shows where support-based monotonic reasoning ceases to suffice [@thapa2026minimal; @thapa2026stratified]. These broader frameworks are further reason to state the retraction result below only as an exact consequence of the declared evidence-license algebra, not as a new general account of causal responsibility or deletion robustness.

The residual specialization lies in the interpretation and enforcement of licenses. A license denotes a bounded evidential permission such as theorem-level support, prospective support, post-outcome support, bounded computation, or external replay. A rule cap states which such permissions the rule is allowed to transmit. Intersection across conjunctive premises enforces a common end-to-end license, while the cap prevents a rule from upgrading that license. The resulting algebra is intentionally transparent and is not presented as the only reasonable model of scientific authority.

### Authorization and the domain instantiations

Modern authorization languages provide analyzable policy semantics and native decision engines; Cedar is one example [@cutler2024]. X.509 certificate validation has its own detailed path and revocation semantics [@rfc5280]. Neither domain is reduced here to the evidence-license calculus. The first domain-transfer attempt used Cedar's official multi-policy fixtures but found no native evidence-authority, license, or retraction field with which to adjudicate the proposed residual. That attempt was retained as a null result. The second attempt used native OpenSSL decisions as fixed per-store facts and asked only whether erasing store origin during a merge can authorize a result that neither store authorizes alone. The evidence-license layer preserves that origin distinction; it does not replace the native X.509 engine.

## Finite typed authority system

### Claims, licenses, seeds, and capped rules

Let $Q$ be a finite set of claims and let $\Lambda$ be a finite set of evidence licenses. A label is a subset of $\Lambda$, ordered by inclusion. The empty set is the bottom label and union is the join. Each claim $q\in Q$ has an independent seed label $\sigma(q)\subseteq\Lambda$.

A positive conjunctive rule is a triple

$$
r=(A_r\rightarrow h_r, K_r),
$$

where $A_r\subseteq Q$ is a nonempty finite antecedent set, $h_r\in Q$ is the head, and $K_r\subseteq\Lambda$ is the rule's license cap. Let $\mathcal{R}$ be a finite set of such specified rules and let the declared system be $\mathcal{S}=(Q,\Lambda,\sigma,\mathcal{R})$. Rules with empty bodies are represented as seeds. For a label assignment $x\in(2^\Lambda)^Q$, the transfer made by rule $r\in\mathcal{R}$ is

$$
\tau_r(x)=K_r\cap\bigcap_{a\in A_r}x_a.
$$

Thus a license crosses a rule only if every premise carries the license and the cap permits it. Disjunctive support is represented by multiple rules with the same head, whose contributions are joined by union.

Let $R\subseteq Q$ be the set of directly refuted claims. Define the synchronous operator $F_R:(2^\Lambda)^Q\rightarrow(2^\Lambda)^Q$ by

$$
F_R(x)_q=
\begin{cases}
\varnothing, & q\in R,\\[3pt]
\displaystyle \sigma(q)\cup
\bigcup_{r\in\mathcal{R}:h_r=q}\tau_r(x), & q\notin R.
\end{cases}
$$

Starting from the all-empty assignment, iterate $F_R$ to stabilization. The resulting assignment is denoted $\operatorname{Auth}_\Lambda(R)=\operatorname{lfp}(F_R)$. The system $\mathcal{S}$ is held fixed whenever refutation sets are compared. This notation does not assert that every seed or cap is scientifically correct. It denotes only the consequences of the declared policy.

### Finite convergence

**Theorem 1 (finite least fixed point).** Synchronous iteration of $F_R$ from the bottom assignment reaches its least fixed point after at most $|Q||\Lambda|$ strict claim-license additions, followed by a stability check.

**Proof.** The operator is monotone because union and intersection are monotone in each premise label and every refuted claim is fixed to the bottom label. Iteration from bottom can therefore only add claim-license pairs. There are at most $|Q||\Lambda|$ such pairs, so there can be no more than that many strict additions. The first state with no addition is a fixed point. By induction, every iterate is contained in every fixed point of $F_R$, hence the stabilized assignment is the least fixed point. $\square$

The theorem concerns the registered synchronous operator. No separate claim about arbitrary asynchronous schedules is needed for the results below. An implementation using another schedule must independently establish that it computes the same operator.

### Typed proof trees

A finite proof tree for a pair $(q,\lambda)\in Q\times\Lambda$ is valid under $R$ when the following conditions hold.

1. Its root is $q$, and no claim appearing at a node belongs to $R$.
2. Every leaf $a$ satisfies $\lambda\in\sigma(a)$.
3. Every internal node with claim $h_r$ applies a specified rule $r\in\mathcal{R}$, has one child tree for each claim in $A_r$, and satisfies $\lambda\in K_r$.

**Theorem 2 (typed proof-tree equivalence).** A license $\lambda$ belongs to $\operatorname{Auth}_\Lambda(R)_q$ if and only if a finite valid proof tree for $(q,\lambda)$ exists under $R$.

**Proof.** For the forward direction, induct on the first synchronous iteration at which $(q,\lambda)$ appears. A seed appearance gives a leaf. A rule-derived appearance identifies a capped rule whose antecedent pairs appeared earlier, so the induction hypothesis supplies finite child trees. For the reverse direction, induct on tree height. A leaf license is present from its seed. At an internal node, all child licenses are present by the induction hypothesis and the rule cap contains $\lambda$, so the rule transfer adds $\lambda$ to its head. $\square$

The proof-tree view is the intended semantic reading of the fixed point. Derivability and evidence class travel together. Label membership is memberwise: each pair $(q,\lambda)$ has its own witness, and a label containing several licenses does not assert that one proof tree carries the whole set jointly. If all license and cap information is deliberately forgotten, each nonempty seed is replaced by a Boolean fact, and every specified rule is retained as a Boolean rule, the resulting projection is ordinary positive reachability. Because this projection also forgets cap exclusions and the need for a common end-to-end license, it can overapproximate typed authorization.

## Nonpromotion, cycles, and retraction

### Unsupported cycles and license conservation

Consider rules $a\rightarrow b$ and $b\rightarrow a$ with no licensed seed. Their least fixed point is empty. The cycle supplies a derivation shape but no evidence. If $a$ has a seed license and both caps admit that license, the license can propagate to $b$ and around the cycle. If either cap excludes it, propagation stops at that edge.

**Corollary 3 (license conservation).** Every license attached to a conclusion occurs in all leaf seeds and all rule caps along at least one finite valid proof tree for that conclusion.

The system therefore cannot manufacture a license that is absent from every end-to-end derivation. The result is relative to the declared tree semantics; it is not a general theorem about all annotation algebras.

### Compact nonpromotion examples

Suppose an analytic lemma is seeded with $\{\textsf{THEOREM}\}$ and an exact finite search is seeded with $\{\textsf{BOUNDED\_COMPUTATION},\textsf{EXTERNAL\_REPLAY}\}$. A rule that requires both premises and proposes an exact general constant receives the intersection of the two seed labels. That intersection is empty, even if the Boolean dependency graph reaches the proposed constant. The record must therefore leave the exact general claim unlicensed.

A rule cap can impose an additional boundary. If every premise carries both $\textsf{PROSPECTIVE}$ and $\textsf{POST\_OUTCOME}$ but a repair rule is capped at $\{\textsf{POST\_OUTCOME}\}$, the repaired conclusion receives only the post-outcome license. The rule does not deny that the repair may be exact on observed data. It denies the stronger statement that an outcome-informed repair is prospective evidence.

Direct refutation and route withdrawal remain distinct. For example, let the license universe contain the labels $\textsf{PROSPECTIVE}$ and $\textsf{POST\_OUTCOME}$. Seed $p$ with the prospective license and $s$ with the post-outcome license, and register two single-premise rules from $p$ and $s$ to the same conclusion $q$, capped by their respective licenses. Before refutation, $q$ carries both licenses through separate proof trees. Refuting $p$ leaves only the post-outcome route and license. Refuting $q$ itself instead fixes $q$ to the empty label, regardless of either incoming rule.

### Monotone loss under refutation

**Theorem 4 (refutation monotonicity).** If $R\subseteq R'$, then $\operatorname{Auth}_\Lambda(R')_q\subseteq\operatorname{Auth}_\Lambda(R)_q$ for every $q\in Q$.

**Proof.** For every assignment $x$, direct refutation in $R'$ can only replace additional labels by the empty set. Hence $F_{R'}(x)\subseteq F_R(x)$ pointwise. Synchronous iteration from bottom preserves this containment at every round, and the containment therefore holds at the least fixed points. $\square$

Let $A_{\mathrm{pre}}=\operatorname{Auth}_\Lambda(\varnothing)$ and $A_{\mathrm{post}}=\operatorname{Auth}_\Lambda(R)$. Define

$$
\operatorname{Ret}_\Lambda(R)=
\{(q,\lambda):\lambda\in A_{\mathrm{pre}}(q)\setminus A_{\mathrm{post}}(q)\}.
$$

**Corollary 5 (exact retraction within the declared algebra).** The set $\operatorname{Ret}_\Lambda(R)$ contains exactly the claim-license pairs for which every previously valid typed proof tree is destroyed by the specified refutations. A pair with at least one surviving valid typed proof tree remains licensed.

This statement follows directly from Theorem 2. It is an exact characterization for the declared seeds, rules, caps, and refutations. It is not claimed as new generic minimal-support, causality, or belief-contraction theory.

## Executable semantics and evaluation design

### Reference evaluator

The reference implementation accepts a machine-readable problem instance containing the license universe, claims, seed labels, capped rules, refutations, and optional expected outcomes. A JavaScript Object Notation (JSON) Schema checks document shape. Semantic validation then rejects duplicate identifiers and references to undeclared claims or licenses. Empty rule bodies are rejected because independent facts must be represented as seeds.

The evaluator performs deterministic bottom-up iteration of $F_R$. It records the iteration rank at which each claim-license pair first appears. Proof-tree reconstruction descends strictly through those ranks, preventing cyclic output even when the rule graph contains cycles. Retraction is computed by comparing the unrefuted and refuted least fixed points. Canonical ordering makes semantic reports byte stable for equal inputs.

The implementation does not infer scientific policy. It cannot determine whether a license vocabulary is appropriate, whether a seed deserves its label, or whether a rule cap reflects a defensible evidential transition. These remain author-supplied premises. The evaluator's role is narrower: it makes the consequences of those premises reproducible and exposes unlicensed Boolean reachability.

Three committed case families exercise the intended boundary. A forecast case withdraws a falsified equality while retaining independently supported bounds and prevents a post-outcome repair from regaining prospective status. A query-specific case separates decision authority from exact-value and witness authority. A bounded-frontier case prevents finite internal computation from being combined with analytic support to license an unresolved exact theorem. These cases demonstrate behavior of the declared algebra; they do not establish general usability across scientific communities.

### Native-engine study outcome definitions

For each two-origin merge task, let $v_A$ and $v_B$ denote the native engine's decisions for the two parent stores. Let $v_U$ and $v_I$ denote its decisions on textual union and intersection. The parent-authorized reference is $P=v_A\lor v_B$. A *hybrid authorization* satisfies

$$
H=v_U\land\neg v_A\land\neg v_B.
$$

The term identifies an origin-mixing event only. It does not imply a security vulnerability. For a merge method with decision $d$, an unsafe merge is $d\land H$, and a needless rejection is $\neg d\land P$.

Five fixed policies were compared: textual union, set intersection, reject all, prefer side B, and a typed origin witness. The last policy is defined by $d=P$. Its unsafe-merge and needless-rejection counts are therefore identically zero for any task set. This identity is useful as a specification check but cannot be interpreted as empirical accuracy or superiority. Its required native-engine work is two parent evaluations per task, compared with one merged-store evaluation for textual union.

## Empirical instantiations

### A retained null result on Cedar multi-policy fixtures

The first domain-transfer attempt used the complete official Cedar multi-policy fixture family available at the frozen source revision [@cutler2024]. The native engine reproduced all five fixtures and all 15 requests, comprising nine allows and six denies. Decision, reason, error, and validation outputs agreed on all requests, and a typed origin-preserving projection retained the native reason sets without changing any decision.

This result did not adjudicate the intended evidence-license residual. The upstream fixtures exposed no independently authored evidence-authority, license, or retraction field. The typed labels used in hostile controls were added by the study itself and therefore could not establish a real-domain positive. The outcome was recorded as null or adverse rather than being relabeled as validation. A first Rust invocation also failed before parsing any fixture because a pinned source override expected an exact file rather than a directory. That zero-request setup failure is retained separately; the corrected invocation changed the path binding, not the fixtures or expected outcomes.

### X.509 corpus and task construction

The second study used OpenSSL 3.6.4 test materials and the native OpenSSL verification engine [@openssl364; @rfc5280]. The source was bound to the official OpenSSL 3.6.4 tag and published tarball digest. A content rule selected 252 public certificate- or revocation-list-bearing files and excluded private-key and auxiliary material. The upstream verification table contained 192 parsed rows, of which 191 were statically usable; one row depended on setup-time generated material and was excluded before task construction.

Two task families were frozen before merge evaluation. The upstream-pair family paired distinct upstream-authored store states that shared a leaf, purpose, and option set, producing 1,858 tasks. A parity-partition family split the selected certificate material into two deterministic stores and produced 104 further tasks. All evaluations used row-specific times when supplied and a fixed timestamp otherwise, so host time could not change verdicts. The resulting task population contained 1,962 merge tasks.

A diagnostic execution before the result commit found that the independent structural control omitted OpenSSL's depth-zero same-subject, same-public-key anchor case under partial-chain evaluation. The control model was amended before results while the corpus, task manifest, and expected method definitions remained unchanged. This repair is part of the provenance record rather than being hidden as implementation cleanup.

### Method outcomes

Table 1 gives the independently reproduced overall counts. There were 1,143 parent-authorized tasks and 810 union-authorized tasks. Textual union authorized 46 hybrid tasks that neither parent store authorized. Intersection and reject-all avoided those hybrids but rejected many parent-authorized tasks. Side-B preference also avoided the hybrids while rejecting 444 parent-authorized tasks. The origin-witness row equals the parent-authorized reference by definition.

| Policy | Allows | Unsafe hybrids | Needless rejections |
|:--|--:|--:|--:|
| Textual union | 810 | 46 | 379 |
| Intersection | 250 | 0 | 970 |
| Reject all | 0 | 0 | 1,143 |
| Prefer side B | 699 | 0 | 444 |
| Typed origin witness, $v_A\lor v_B$ | 1,143 | 0 | 0 |

: Policy outcomes over the 1,962 frozen merge tasks. Unsafe hybrids are union-authorized tasks that neither parent authorizes; needless rejections are parent-authorized tasks rejected by the policy. The origin-witness row equals $v_A\lor v_B$ by definition and is not a performance estimate.

The 46 hybrids comprised 42 upstream-pair tasks and four parity-partition tasks. Forty-five were classified as policy cases: the structural issuance graph could be derived within at least one origin, but native policy conditions such as purpose, extended-key usage, or trust admission still caused both parent decisions to deny. One case was structurally mixed. Consequently, the general evaluator can represent the 45 policy cases only by treating the native per-origin decisions as fixed oracle facts. The paper does not claim to reproduce X.509 policy semantics inside the evidence-license algebra.

The typed origin witness requires 3,924 parent-store verification requests across the 1,962 tasks, exactly twice the 1,962 merged-store requests required by textual union. The complete ground-truth basis evaluated both parents, union, and intersection. Caching reduced the number of unique engine invocations in the full run, but that implementation detail does not alter the per-policy requirement.

### Controls and adverse observations

The result packet retains checks that did not pass perfectly. Re-execution of the upstream verification table agreed on 186 of 191 usable rows. The five disagreements were Federal Information Processing Standards (FIPS) provider rows containing a runtime token that was not statically executable in the frozen harness; they remain counted as disagreements rather than being excluded after inspection. The 97.38% agreement exceeded the prospectively registered 95% anchoring gate but is not reported as full reproduction.

Two complete runs produced byte-identical result receipts. After the documented anchor-model repair, a one-directional structural control had no violations across the 1,962 tasks. Three upstream revocation adjudications retained their expected failures, their positive control authorized without revocation checking, and no tested merge resurrected a revoked chain. A complete-alternative-origin control produced no false flags. A deliberately split chain was detected and localized, but that hostile case was authored by the study and is treated only as a mechanics check.

An independent in-repository implementation re-derived the per-task parent, union, and intersection decisions and the aggregate counts without importing the primary evaluator. This is implementation-level reproduction, not external human peer review or cross-institution replication.

## Discussion

### What the formal result establishes

The formal contribution is small enough to state precisely. In a finite positive conjunctive system, a license is authorized exactly when a finite unrefuted proof tree carries it through every seed and rule cap. Unsupported cycles add nothing. Adding direct refutations cannot add licenses. Retraction removes exactly the claim-license pairs that lose all such proof trees. A cap can therefore make nonpromotion fail closed even when the untyped dependency graph still reaches a conclusion.

These properties are useful because the evidence boundary becomes executable. A report can distinguish “the conclusion remains reachable” from “the conclusion remains licensed as prospective” without assigning probabilistic confidence or resolving arbitrary inconsistency. The same restriction is also a limitation. The algebra is not a general logic of science, and a mechanically consistent policy can still encode indefensible seeds or caps.

### What the X.509 instantiation establishes

The X.509 study supplies a non-vacuity and cost instantiation. Hybrid authorizations appeared in upstream-authored certificate material under the pinned native engine. Textual union, intersection, reject-all, and side preference paid different measured costs on the same frozen tasks. Preserving origin by evaluating both parents required twice the per-task engine calls of evaluating the merged store once.

The origin-witness result should not be described as a detector win. Once the policy is defined as $v_A\lor v_B$, perfect agreement with the parent-authorized set is tautological. The study does not estimate generalization, calibration, or predictive performance. Its empirical burden is met by the occurrence of 46 hybrids, the comparator trade-offs, the native-engine bindings, the controls that could have failed, and the recorded adverse observations.

Nor is the study a security evaluation. No adversary, deployed system, operational incident, or threat model was studied. The X.509 engine remains authoritative for certificate semantics once a store is fixed. The evidence-license layer contributes only the origin distinction that is erased by a flat merge. Whether that distinction should control a production workflow is a separate policy and usability question.

### Why the negative first attempt matters

The Cedar result shows that a plausible domain transfer can be non-informative even when every native test passes. Native reason identifiers preserved policy provenance, but the corpus did not contain independently adjudicated evidence-license or retraction fields. Treating study-authored labels as a real-domain positive would have made the experiment self-authorizing. Preserving the null result clarifies the evidence required by the successful X.509 study: upstream material, a native adjudicator, and a measurable origin-mixing event defined before outcomes.

## Limitations

The system handles finite positive conjunctive rules only. It does not model negation, defaults, probabilistic evidence, inconsistency, or arbitrary scientific disagreement. The powerset/intersection transfer algebra is one policy design rather than a universal authority algebra. License vocabularies, seeds, caps, and direct refutations are curated inputs and can be wrong even when evaluation is mechanically correct.

The three scientific-record cases are bounded mechanism demonstrations. They do not establish cross-institution usability, human interpretability, or improved scientific decision making. Repeated execution by the same repository is not external replication.

The X.509 task population is derived from one pinned OpenSSL test corpus and one native engine version. The 46 hybrid tasks are not an estimate of production prevalence. Forty-five depend on native policy decisions that the structural model does not reproduce. The observed policy costs therefore remain conditional on the frozen task construction and engine semantics.

The origin-witness policy is definitionally aligned with the parent-authorized reference. Its zero error counts cannot support a superiority claim, and its two-parent evaluation cost may be unacceptable in settings with different latency or trust requirements. No user study, deployment evaluation, or security assessment was performed.

## Reproducibility

The accompanying artifact contains the complete reference evaluator, schema, tests, case encodings, Cedar null-result records, X.509 protocol, task manifest, source bindings, result receipts, independent reproducer, selected third-party OpenSSL material, and its attribution and license notices. The source archive contains the editable manuscript, bibliography, Springer Nature class and numeric bibliography style used for compilation, and build instructions. A release manifest binds the canonical manuscript, compiled PDF, source archive, artifact archive, and exact archive member sets by SHA-256 cryptographic digest and byte count.

The X.509 protocol identifies the source tag, commit, tarball digest, fixed evaluation time, selection rule, and native-engine version. Missing external tools or source material are treated as unavailable rather than silently substituted. The package-level verifier checks hashes and archive membership; it does not grant scientific authority beyond the claims proved or measured above.

## Conclusion

Boolean reachability is too coarse when conclusions carry different evidential permissions. The finite system developed here attaches evidence licenses to positive conjunctive derivations and prevents a rule from transmitting a license that is absent from any premise or excluded by its cap. Its least-fixed-point and proof-tree views coincide, refutation can only remove licenses, and post-refutation retraction is exact relative to the declared algebra.

The executable cases show how this distinction blocks prospective and theorem-level promotion in bounded scientific records. The third-party-corpus X.509 instantiation shows that origin mixing is not vacuous and that alternative merge policies have different costs. The strongest supported conclusion remains narrow: explicit license caps and origin witnesses make nonpromotion auditable in a finite positive system. They do not create a new general provenance theory, certify a security system, or replace scientific judgment.

## Statements and Declarations {.unnumbered}

### Funding

No funding was received for conducting this study.

### Competing interests

The author has no competing interests to declare that are relevant to the content of this article.

### Ethics approval and consent to participate

Not applicable. The study used no human participants, human data, or animals.

### Consent for publication

Not applicable.

### Author contributions

Sze Chun Yiu is the sole author.

### Use of generative artificial intelligence

Generative AI tools were used for drafting and editing assistance. The author is responsible for all scientific content.

### Data availability

The submission artifact contains the exact protocols, frozen task manifests, source bindings, result receipts, and selected third-party OpenSSL test material used to audit the reported results. Third-party OpenSSL material remains subject to the Apache License 2.0 and its bundled attribution notice.

### Code availability

The editable manuscript source, reference evaluator, schema, case encodings, tests, independent reproducer, and reproduction instructions are included in the submission archives.

### Materials availability

The selected OpenSSL test materials required for the reported task construction are included in the submission artifact with their source binding, attribution, and licence.

## Tool-use disclosure

A generative language model assisted manuscript organization, language revision,
adversarial review, and submission-package preparation. The listed author remains
responsible for the mathematical statements, proofs, references, executable claims,
and final text.

## Data and code availability

The source archive includes the JSON schema, deterministic Python evaluator, unit
tests, and bounded case fixtures required to reproduce the executable claims. The
external X.509 measurements remain bound to the committed corpus records; analytic
policy identities are not re-labelled as empirical detector performance.

## References

1. J. Doyle, “A Truth Maintenance System,” *Artificial Intelligence* **12**,
   231–272 (1979). DOI: 10.1016/0004-3702(79)90008-0.
2. J. P. Martins and S. C. Shapiro, “A Model for Belief Revision,”
   *Artificial Intelligence* **35**, 25–79 (1988).
   DOI: 10.1016/0004-3702(88)90031-8.
3. C. Bourgaux, P. Bourhis, L. Peterfreund, and M. Thomazo, “Revisiting
   Semiring Provenance for Datalog,” in *KR 2022* (2022).
   DOI: 10.24963/kr.2022/10.
4. M. Abo Khamis, H. Q. Ngo, R. Pichler, D. Suciu, and Y. R. Wang,
   “Convergence of Datalog over (Pre-)Semirings,” in *PODS 2022*, 105–117
   (2022). DOI: 10.1145/3517804.3524140.
5. T. J. Green, G. Karvounarakis, and V. Tannen, “Provenance Semirings,” in
   *PODS 2007*, 31–40 (2007). DOI: 10.1145/1265530.1265535.
6. P. A. Bonatti, A. Hogan, A. Polleres, and L. Sauro, “Robust and Scalable
   Linked Data Reasoning Incorporating Provenance and Trust Annotations,”
   *Journal of Web Semantics* **9**(2), 165–201 (2011).
   DOI: 10.1016/j.websem.2011.06.003.
