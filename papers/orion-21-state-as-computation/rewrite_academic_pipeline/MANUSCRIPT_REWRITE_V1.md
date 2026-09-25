# State Construction as Computation: Accessible Rank, Decoder Substitution and Future Optionality

## Abstract

Reasoning systems are often evaluated as if the state presented to a downstream learner were a fixed observation. We study a different resource boundary: constructing task-facing state is itself computation, and that computation can substitute for structural search performed downstream. For a query family \(F\), any fixed representation supporting exact linear readout of every query requires dimension at least \(\mathrm{rank}(F)\). For all size-\(s\) parity queries on \(d\) Boolean variables this gives an accessible-dimension requirement of \(inom{d}{s}\), whereas a query-conditioned construction need expose only the coordinates required by the current query.

Controlled parity studies show large state-width and downstream sample-threshold gaps under dense access, while a no-answer-laundering construction exposes only latent query components rather than the final label. Hostile decoder substitution then attacks the mechanism. A preregistered sparse universal decoder falsifies the stronger hypothesis that compilation retains a fourfold threshold advantage in both difficult cells, reducing the residual to 2× and 4×; a fresh deterministic replication reproduces those residuals. A separately frozen replay-gated deterministic tree ensemble retains substantial low-sample gaps against its named universal-state arm, but a pooled successor becomes negative in the narrow-state regime, locating part of the advantage in accessible state width rather than universal-representation size alone. On a non-synthetic digits study, a frozen 16-of-64 compiler meets its family quality gate for only 3/10 responsibilities under linear access and 5/10 under RBF or KNN, below the preregistered 8/10 threshold.

Exact workload laws further quantify the option debt incurred when specialized state is retained without raw recoverability. The result is not that compilation universally dominates inference. It is that structural-search computation can be paid upstream during state construction or downstream by the decoder, and the placement should be evaluated jointly through accessible rank, decoder burden, construction cost and future optionality. A later production-style successor executed zero cases because the required datasets, models and transcripts were not content-bound and contributes no real-system authority.

## 1. Introduction

A system can possess all information required for a decision while exposing that information in a form that is expensive for a bounded learner to use. A raw context may contain the decisive variables, yet a decoder must discover them among thousands of irrelevant coordinates. A compiler or retrieval process can move some of that discovery upstream by constructing a task-facing state.

This idea has many established relatives: sufficient representations, partial evaluation, knowledge compilation, materialized views, feature selection, retrieval and query-conditioned memory. The scientific question here is therefore not whether representation matters. It is a **resource-placement** question:

> When the same structural search can be performed during state construction or later by a decoder, where is the computation paid, what downstream burden is removed, and what future optionality is lost by specialization?

We call this perspective *state construction as computation*. The comparison is meaningful only when the access class and full resource boundary are explicit. A compact compiled representation can appear cheap if compilation is treated as free, and a universal representation can appear weak if the downstream decoder is artificially prevented from searching for the relevant coordinates.

The paper combines an exact accessible-rank result, controlled state-construction studies, hostile decoder substitutions, a non-synthetic negative transfer result and exact optionality laws.

## 2. Accessible-rank theory

Let \(X\) have distribution \(\mu\), and let \(F=\{f_1,\ldots,f_N\}\) be a family of query functions in \(L_2(\mu)\). A fixed representation \(\phi:X	o\mathbb R^m\) supports exact linear access to every query when each \(f_q\) can be written as a linear combination of the coordinate functions of \(\phi\).

**Theorem 1 (accessible-rank lower bound).** If \(\mathrm{span}(F)\) has dimension \(r\), every fixed representation supporting exact linear readout of all queries has \(m\ge r\).

The proof is elementary: the coordinate functions of \(\phi\) span a space of dimension at most \(m\) that must contain the \(r\)-dimensional query span.

This is an access-class theorem, not an unrestricted information lower bound. A more expressive nonlinear decoder may recover structure from fewer or differently organized coordinates. The point is to state the decoder class under which the representation is being judged.

For orthonormal queries, Bessel's inequality also gives an approximate frontier: any \(m\)-dimensional linearly accessible subspace has average squared projection error at least \(1-m/N\).

## 3. Parity-query corollary

On \(X=\{-1,+1\}^d\) under the uniform measure, distinct parity characters are orthogonal. The family of all size-\(s\) parity queries therefore has accessible rank

\[
\binom{d}{s}.
\]

A fixed linearly accessible representation supporting every such query exactly needs at least that many coordinates. A query-conditioned construction can instead expose only the parity components selected by the current query.

The corollary creates a clean controlled setting in which information content is not the disputed variable: the universal representation contains the relevant components, but a bounded decoder must identify which ones matter.

## 4. Dense controlled studies

In the confirmatory parity study, universal/compiled state-width ratios range from 91× to 1820×. Under the registered dense decoder, compiled state reaches the target accuracy threshold at substantially smaller training sizes. In the difficult cells, universal state does not reach the target within the frozen training grid while compiled state does.

A direct compiler that emits the final query answer would make the interpretation trivial. A no-answer-laundering successor therefore exposes only the active parity components—five or seven latent components depending on the case—and requires the downstream learner to infer an odd-cardinality majority target. No exposed component equals or negates the final label. Under the same dense access model, compiled state reaches the registered threshold at \(n=64\), while high-dimensional universal state requires much more data or fails to reach the threshold within the grid.

These results support a structural-search interpretation under the declared decoder. They do not establish a universal advantage of compiled state.

## 5. Sparse decoder substitution falsifies the stronger claim

The obvious alternative explanation is that the universal state is paired with the wrong decoder. If a downstream model can discover sparse relevant coordinates, some upstream compilation advantage should disappear.

A preregistered sparse-decoder attack tests a deliberately strong hypothesis: compiled state should retain at least a fourfold sample-threshold advantage in both difficult cells. The hypothesis fails.

In the two protected cells, the sparse universal decoder reaches the target at \(n=128\) and \(n=256\), while compiled state reaches it at \(n=64\). The residual gaps are therefore 2× and 4× rather than at least 4× in both cells. The negative terminal is retained.

A fresh deterministic replication with explicitly seeded stochastic components reproduces the smaller residual: again 2× and 4×, with compiled-minus-sparse accuracy advantages of approximately 0.291 and 0.331 at \(n=64\).

This result is scientifically useful because it identifies decoder-side feature discovery as a substitute for upstream state construction. The question becomes quantitative—how much burden each locus pays—rather than categorical.

## 6. Nonlinear decoder attacks and arm specificity

A separately frozen deterministic ExtraTrees successor places fresh-process replay in the terminal decision path. Under its registered envelope, the named nonlinear universal-state decoder still does not reach 0.95 accuracy through \(n=1024\) in the two difficult cells, whereas compiled state reaches the target by \(n=64\). Low-sample accuracy gaps are approximately 0.462 and 0.394.

This is not a nonlinear lower bound. The terminal depends on which universal arm is placed in the comparison gate. On the same successor data, the sparse universal arm reaches the threshold earlier in one cell. Holding decoder family fixed attributes a substantial but incomplete fraction of the observed gap to the state change.

A further successor pools all registered universal arms in its own gate and returns a negative where the compiled state is narrow. That negative prevents the paper from claiming that representation size alone determines difficulty. Decoder inductive bias, state width and query structure jointly control where search is paid.

## 7. Non-synthetic transfer is not yet established

A separate frozen experiment on digits asks whether a 16-of-64 learned compiler can preserve responsibility-specific quality across ten tasks. The predeclared family gate requires support for at least 8/10 responsibilities.

The result does not pass. Quality support is obtained for 3/10 responsibilities under linear access and 5/10 under each of RBF and KNN. This adverse result is retained as the current non-synthetic boundary.

The synthetic parity studies therefore support mechanism isolation, not a claim that aggressive query-conditioned compilation generally improves real tasks.

## 8. Construction cost and optionality

Moving search upstream can reduce downstream burden while creating other costs. A compiled state may need to be rebuilt when the query changes, the environment drifts or the representation becomes stale. Discarding raw recoverability can create **option debt**: future queries that were not anticipated at compile time may require expensive reconstruction or may become impossible.

Exact workload laws in the programme compare three strategies: retain raw state and compile on demand, retain a universal materialization, or retain specialized compiled state plus an explicit recovery policy. Compilation is worthwhile only when service savings over the future horizon exceed construction, storage, invalidation and recovery costs.

This turns a single-task accuracy comparison into a lifecycle decision. A state that dominates for the present query can be inferior over a changing query distribution.

## 9. Resource accounting

A valid comparison must count the resources spent at both loci. Relevant coordinates include compiler/retrieval operations, state bytes, downstream training or inference samples, search nodes, verifier calls, latency, cache and recovery work, and model capacity. When these resources cannot be justified by a fixed scalarization, the appropriate output is a Pareto frontier rather than a post-hoc weighted score.

The state-construction question is therefore not “which representation is smaller?” but “which placement of computation is preferable under the declared service horizon and access model?”

## 10. Relation to prior work

Computationally usable information, sufficient representation theory, partial evaluation, knowledge compilation, feature selection, sparse models, query-conditioned retrieval and materialized views all own important parts of the mechanism. The paper does not claim those primitives as new.

The residual is a joint placement account: accessible-rank theory identifies one decoder-relative representation burden; hostile decoders demonstrate substitution between upstream and downstream search; future-optionality laws price the consequences of specialization. This makes the scientific object the **location of structural-search computation** rather than a generic “better representation.”

## 11. Production-style successor boundary

A later real-system successor was prospectively specified to test learned compilation, total resource savings, stronger-decoder robustness, future-query transfer, drift and recovery. None of the required datasets, models, transcripts, compiler/decoder artifacts, resource receipts or future-query objects were content-bound. Zero scientific cases executed.

This acquisition failure is not a negative performance result. It contributes no authority to the mechanism claims above and cannot be used as evidence of real-system generalization.

## 12. Limitations

The strongest positive evidence is controlled and largely synthetic. The accessible-rank theorem is tied to a declared access class. Stronger decoder families can absorb some or all apparent representation advantages. The digits study is adverse under its preregistered family gate. The workload laws require a declared future-query distribution or horizon and do not predict one automatically.

The paper therefore does not establish that compiled state is globally smaller, universally easier to decode or superior in deployed agents.

## 13. Conclusion

State construction and downstream reasoning are two places to pay for structural search. Exact accessible-rank theory makes one part of that burden explicit; controlled studies show large gaps under dense access; sparse and nonlinear attacks recover part of the gap and falsify stronger universal claims; and a non-synthetic transfer study remains below its family gate. The durable result is a resource-placement principle: representation construction should be evaluated together with decoder burden, construction cost and future optionality, because moving computation upstream can simplify the present task while creating debt for the future.
