# State Construction as Computation: Accessible Rank, Decoder Substitution, and Width-Conditioned Search Burden

**ORION-21 — recursive academic-paper-pipeline final editorial master**  
**Scientific cut:** exact accessible-rank theory plus width-conditioned controlled evidence and adverse transfer  
**Primary route:** Theoretical Computer Science / AI theory  
**Specialist fallback:** AIJ Research Note or TMLR  
**Authority:** bounded theorem-and-mechanism paper; real-system superiority remains open

## Abstract

Reasoning systems are often evaluated as if the state presented to the downstream learner were a fixed observation. We study a different resource boundary: constructing task-facing state is itself computation, and that computation can substitute for structural search performed downstream. For a query family `F`, any fixed representation supporting exact linear readout of every query requires dimension at least `rank(F)`. For all size-`s` parity queries on `d` Boolean variables this gives an accessible-dimension requirement of `binom(d,s)`, whereas a query-conditioned construction need expose only the components selected by the current query.

Controlled parity studies produce universal/compiled state-width ratios of 91×–1820× and large sample-threshold gaps under dense access. A no-answer-laundering construction exposes five or seven latent query components rather than the final label. Hostile decoder substitution then attacks the mechanism. A preregistered sparse universal decoder falsifies the stronger hypothesis that compilation retains a fourfold threshold advantage in both difficult cells, reducing the residual to 2× and 4×; a fresh deterministically seeded replication reproduces those gaps with compiled-minus-sparse accuracy advantages of 0.2912 and 0.3307 at `n=64`. A replay-gated deterministic tree ensemble retains larger gaps against its named universal arm, but arm-placement analysis prevents promotion to universal-state decoding as such.

A pooled successor makes the boundary explicit. At compiled-state width `r=3`, the strongest registered universal pool reaches the target by `n=128`, and the preregistered advantage is negative. At `r=7`, a separately frozen successor runs three independent execution seeds across three fixed geometry strata. All nine seed×geometry cells pass the non-compensatory gates: pooled universal accuracy below `n=256` lies between 0.8489 and 0.9421, compiled-minus-pooled accuracy at `n=64` lies between 0.2463 and 0.3543, and compiled accuracy at `n=64` lies between 0.9690 and 0.9981. The matched `r=3` controls keep the universal attack live. These are three independent execution replicates, not nine independent random studies.

On non-synthetic digits, a frozen 16-of-64 compiler meets its family-quality gate for only 3/10 responsibilities under linear access and 5/10 under RBF or KNN, below the preregistered 8/10 threshold. Exact workload laws further quantify the option debt incurred when specialized state is retained without raw recoverability. The result is not that compilation universally dominates inference. It is that structural-search computation can be paid upstream during state construction or downstream by the decoder, and the location of that burden depends on accessible rank, decoder family, compiled-state width, construction cost and future optionality.

## 1. Introduction

A system can possess all information required for a task while exposing that information in a form that is expensive for a bounded learner to use. A raw state may contain the decisive coordinates, yet a downstream decoder must discover them among thousands of irrelevant alternatives. A compiler, retrieval procedure or query-conditioned materializer can move some of that discovery upstream by constructing a task-facing state.

This observation has mature parents. Computationally usable information makes accessibility relative to a model class explicit. Partial evaluation, knowledge compilation and materialized views move work upstream. Feature selection and sparse learning discover relevant coordinates downstream. Retrieval and structured memory condition state on the current task.

The unresolved question is not whether representation matters. It is a resource-placement question:

> When task-relevant structure can be discovered during state construction or later by a decoder, where is the computation paid, how much downstream search can be removed, and what future optionality is lost by specialization?

We call this perspective **state construction as computation**. The comparison is meaningful only under an explicit access class and full resource boundary. A compiled representation can appear cheap if construction is treated as free. A universal representation can appear weak if its decoder is artificially denied the feature-search mechanism needed to use it.

The paper therefore combines four evidence types:

1. an exact decoder-relative accessible-rank theorem;
2. controlled state-width and sample-burden studies;
3. hostile decoder substitutions and width-conditioned successor tests;
4. exact future-optionality laws and a preserved adverse non-synthetic transfer study.

## 2. Accessible-rank theory

Let `X` have distribution `mu`, and let `F={f_1,...,f_N}` be query functions in `L_2(mu)`. A fixed representation

`phi:X -> R^m`

supports exact linear access to every query when, for each `q`, there is a vector `w_q` such that

`f_q(x)=<w_q,phi(x)>`

almost surely.

### Theorem 1 — accessible-rank lower bound

If `span(F)` has dimension `r`, every fixed representation supporting exact linear readout of all queries has `m>=r`.

The coordinate functions of `phi` span a space of dimension at most `m`. That space must contain the `r`-dimensional span of the query family. ∎

This is an access-class theorem, not an unrestricted information lower bound. A nonlinear decoder can exploit a representation through a different function class. The theorem's role is to make the declared downstream mechanism part of the scientific object.

For an orthonormal query family, Bessel's inequality also gives the approximate frontier

`(1/N) sum_q ||f_q-P_U f_q||_2^2 >= 1-m/N`

for every `m`-dimensional linearly accessible subspace `U`.

## 3. Parity-query corollary

On `X={-1,+1}^d` under the uniform measure, distinct parity characters are orthogonal. The family of all size-`s` parity queries therefore has accessible rank

`binom(d,s)`.

A fixed representation supporting every such query by exact linear readout needs at least that many accessible coordinates. A query-conditioned construction can expose only the active components required by the current query.

The corollary provides a controlled setting in which the relevant information is present in both arms. The dispute is how much structural search a declared decoder must perform before it can use that information.

## 4. Dense controlled studies

The confirmatory parity study compares raw input, a fixed universal parity bank and query-conditioned compiled state on a frozen training-size grid. Universal/compiled accessible-dimension ratios range from 91× to 1820×. Under the registered dense decoder, compiled state reaches the target at substantially smaller sample sizes; in the hardest cells universal state does not reach the target within the grid.

A direct compiler that emits the target would make the comparison trivial. A no-answer-laundering successor therefore exposes only the five or seven active parity components selected by the query. The downstream learner must infer an odd-cardinality majority target, and every exposed component is checked against the final label and its negation.

Under dense access, compiled state reaches the registered threshold at `n=64`, whereas the high-dimensional universal state needs far more data or remains below threshold. This supports a structural-search interpretation under the declared decoder. It does not establish that the universal representation is intrinsically hard for every decoder.

## 5. Sparse decoder substitution: the permanent negative

The obvious alternative explanation is that the universal state has been paired with the wrong inductive bias. A sparse decoder can search for a small relevant subset inside the universal bank.

The P11D protocol freezes a deliberately strong positive gate: compiled state must retain at least a fourfold sample-threshold advantage in **both** difficult cells. It does not.

In the two registered cells, the sparse universal decoder reaches the target at `n=128` and `n=256`; compiled state reaches it at `n=64`. The residual ratios are 2× and 4×. The terminal remains negative.

The original sparse run also exposes a reproducibility defect: scientific summaries agree but whole-payload bytes differ because a stochastic solver was not explicitly seeded. A fresh P11E protocol fixes the stochastic identity, uses a new data seed and asks only whether a twofold residual survives in both cells. It does. The replicated compiled-minus-sparse advantages at `n=64` are 0.2912 and 0.3307, and two fresh runs are byte-identical.

The negative is mechanistically valuable. Decoder-side feature discovery buys back part of the upstream compilation advantage. The scientific question becomes how burden is divided, not whether one locus always dominates.

## 6. Nonlinear attacks and arm specificity

A later deterministic 96-tree ExtraTrees successor pins every random state, uses one thread and places two-fresh-process replay in the terminal decision path. Against the named tree-based universal arm, compiled state reaches 0.95 by `n=64`, while universal state remains below 0.95 through `n=1024`; low-sample gaps are 0.4624 and 0.3942.

The result is arm-scoped. On the same data, another registered universal arm changes the verdict in one cell. An arm-placement adjudication therefore withdraws the broader “universal-state decoder” reading without changing a frozen byte.

Holding the decoder family fixed attributes 86.7% and 55.4% of the two `n=64` gaps to the change of state rather than the change of decoder. This decomposition supports a state effect for those cells, but it does not make the named tree arm the strongest possible universal decoder.

## 7. Width-conditioned pooled attack

The strongest interpretation requires the best registered universal arm to enter the gate before outcome. P11H freezes that pooled attack and retains the earlier thresholds.

At compiled-state width `r=3`, the pool reaches 0.95 by `n=128` in both protected cells. The compiled-minus-pooled gap at `n=64` is only 0.0506, below the unchanged 0.20 bar. The terminal is negative:

`P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED`.

The decomposition is informative. At the drawn narrow-state regimes, the entire `n=64` gap is caused by the change of state rather than decoder family, but the gap is too small to satisfy the preregistered magnitude claim. Attribution and practical magnitude are different questions.

A six-rung ladder then shows that the pooled verdict changes with compiled-state width `r`, not with the width of the universal bank. The pool reaches the target early at every `r=3` rung and at no `r=7` rung even as universal-bank dimension varies widely within each half.

## 8. High-width replication

P11I is frozen after the narrow-state negative. It tests the narrower high-width mechanism at `r=7` using three independent execution seeds and three fixed bank-geometry strata per seed. A matched `r=3` control is included in every seed×geometry cell so that the pooled attack remains demonstrably capable.

All nine `r=7` cells pass every non-compensatory gate:

- pooled best accuracy below `n=256`: 0.8489–0.9421;
- compiled-minus-pooled accuracy at `n=64`: 0.2463–0.3543;
- compiled accuracy at `n=64`: 0.9690–0.9981.

All matched `r=3` controls allow the pool to reach 1.0000 below `n=256`.

The unit correction is essential. The study contains **three independent execution seeds**, each evaluated at three fixed geometry strata. The nine cells are not described as nine independent random replicates. The result supports a width-conditioned controlled claim: the high-width compiled-state advantage survives the frozen pooled attack in every registered cell, while the same attack wins in the matched narrow-width controls.

## 9. Non-synthetic transfer remains adverse

A separate frozen digits experiment asks whether a learned 16-of-64 compilation is quality-supported across ten responsibilities. The predeclared family gate requires at least 8/10 responsibilities.

The result fails:

- linear access: 3/10;
- RBF: 5/10;
- KNN: 5/10.

The exact resource identities in the study survive, but they do not rescue the failed quality gate. The current paper therefore does not generalize the parity mechanism to a responsibility family in natural data.

## 10. Future optionality

Moving structural search upstream can reduce current decoding burden while creating **option debt**. A query-specialized state may have to be rebuilt when the query changes. If raw state is discarded or expensive to recover, specialization can make future tasks unavailable.

The registered workload model supplies exact laws for future-query coverage. If a compiled state contains `r` of `N` possible query coordinates, one uniformly drawn future query is covered with probability `r/N`, `K` independent queries are all served according to the corresponding product law, and the expected number of distinct future demands follows the standard coupon-style relation.

These identities do not predict a deployment workload. They make the cost of lost optionality explicit once a horizon and query model are declared.

A valid lifecycle comparison must count:

- state-construction operations and bytes;
- downstream training/search burden;
- cache and invalidation cost;
- raw-state recovery;
- future-query service;
- verifier/tool calls and latency;
- model capacity where it changes the access class.

When no scientifically justified scalarization exists, the correct result is a Pareto frontier.

## 11. Relation to prior work

Computationally usable information, sufficient representation theory, partial evaluation, knowledge compilation, feature selection, sparse learning, query-conditioned retrieval and materialized views own the major primitives. The paper does not claim them as new.

The residual is a joint placement account. Accessible rank gives an exact decoder-relative state burden. Hostile decoders demonstrate substitution between upstream and downstream search. The width-conditioned pooled study identifies a regime boundary. Optionality laws price one consequence of moving work upstream.

## 12. Production-style successor boundary

A later successor was prospectively designed to test real learned compilation, stronger decoders, end-to-end resources, drift and future-query recovery. The required datasets, models, transcripts, compiler/decoder artifacts and resource receipts were not content-bound. Zero scientific cases executed.

The correct terminal is acquisition failure with no real-system outcome. It supplies neither positive nor negative evidence about deployment.

## 13. Limitations

The strongest positive evidence is controlled and mostly synthetic. The accessible-rank theorem is relative to linear readout. The high-width result contains three independent seeds, not nine. The digits family gate is adverse. Exact workload laws require an externally justified future-query model.

The paper does not show that compiled state is universally smaller, easier to decode, cheaper end to end or superior in deployed agents.

## 14. Reproducibility and availability

The release should bind the theorem statements, parity generators, universal and compiled states, every decoder protocol and adjudication, independent-unit correction, high-width and narrow-width receipts, digits negative and optionality derivations. Frozen negative terminals and protocol defects must remain reconstructable.

## 15. Conclusion

State construction and downstream decoding are two places to pay for structural search. Accessible-rank theory makes one part of that burden exact. Dense studies show large gaps; sparse and pooled attacks recover part of the burden and falsify broader claims; and a high-width successor survives the strongest frozen universal pool across three independent seeds and three fixed geometry strata while matched narrow-width controls remain negative.

The durable result is conditional rather than universal. Representation construction can move structural search upstream, but the benefit depends on the declared decoder and compiled-state width, and specialization creates a future-query debt that must be priced alongside present performance.

---

## Editorial production note — not manuscript prose

Adoption must reconcile this master with `MANUSCRIPT.md`, `CLAIM_EVIDENCE_LEDGER.md`, the P11H/P11I authority records and the independent-unit amendment. Figures should foreground the sparse negative, narrow-width pooled negative, high-width controlled positive and digits transfer failure. Refresh the state-representation/knowledge-compilation literature, rebuild the target source, PDF, archive and manifests, and keep the zero-execution production successor outside the empirical claim.
