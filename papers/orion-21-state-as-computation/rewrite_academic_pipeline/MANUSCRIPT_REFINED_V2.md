# State Construction and Decoder Search Are Substitutable Computational Resources

## Abstract

A system can contain the information needed for a query while exposing it in a form that is expensive for a bounded decoder to use. We study state construction as a location of computation rather than as a free preprocessing step. For a query family \(F\), every fixed representation that supports exact linear readout of all queries must have dimension at least \(\operatorname{rank}(F)\). For all size-\(s\) parity queries on \(d\) Boolean variables, this accessible rank is
\[
\binom{d}{s}.
\]
A query-conditioned state can expose only the components needed by the current query, but it pays construction and future-optionality costs.

Controlled parity studies show large state-width and sample-threshold gaps under dense decoders. Hostile decoder substitution narrows the interpretation. A preregistered sparse universal decoder falsifies the claim that compiled state retains at least a fourfold threshold advantage in both difficult cells, leaving residual gaps of 2× and 4×. A named deterministic nonlinear arm retains larger low-sample gaps, but a pooled successor becomes negative in the narrow-state regime. On digits, a frozen 16-of-64 compiler satisfies its family gate for only 3 of 10 responsibilities under linear access and 5 of 10 under RBF or KNN, below the required 8 of 10.

The evidence supports a resource-placement principle, not universal compilation superiority. Upstream state construction and downstream feature discovery can substitute for one another; their comparison must include decoder class, construction cost, state width, recovery, and future-query option debt. A planned production successor executed zero cases and contributes no real-system authority.

## 1. Introduction

Reasoning benchmarks often treat the input state as given and charge only downstream computation. That accounting can hide a large part of the work. Retrieval, compilation, materialization, and feature construction may already have searched for and organized the relevant structure before the learner begins.

A universal state can retain broad future utility, but a bounded decoder must discover which coordinates matter. A query-conditioned state can remove that search burden, but it may need to be rebuilt when the query changes and may discard information needed later.

The scientific question is therefore not whether representation matters. It is where structural-search computation is paid and how the two loci substitute:

\[
\text{raw state}
\longrightarrow
\text{state construction}
\longrightarrow
\text{decoder search}
\longrightarrow
\text{answer}.
\]

A valid comparison must state the decoder access class and count both upstream and downstream resources.

## 2. Accessible-rank lower bound

Let \(F=\{f_1,\ldots,f_N\}\subset L_2(\mu)\) be a family of query functions. A representation
\[
\phi:X\to\mathbb R^m
\]
supports exact linear access when every \(f_q\) lies in the span of the coordinate functions of \(\phi\).

**Theorem 1 (accessible rank).** If
\[
\dim\operatorname{span}(F)=r,
\]
then every fixed representation supporting exact linear readout of all queries has \(m\ge r\).

The proof is direct: at most \(m\) coordinate functions must span an \(r\)-dimensional query space.

This is not an unrestricted information lower bound. A nonlinear decoder may recover the same functions from a different or lower-dimensional state. The theorem describes the representation burden relative to a specified access class.

For an orthonormal query family, the same geometry yields an approximate projection frontier: an \(m\)-dimensional linearly accessible subspace cannot capture all \(N\) directions when \(m<N\).

## 3. Parity-query specialization

On \(\{-1,+1\}^d\) under the uniform measure, distinct parity characters are orthogonal. The family of all size-\(s\) parity queries therefore has accessible rank
\[
\binom{d}{s}.
\]

A fixed linearly accessible representation supporting every query requires at least that many dimensions. A query-conditioned constructor can instead expose only the active parity components for the present query.

The comparison isolates access rather than missing information. The universal representation contains the relevant variables; the question is how much decoder search is needed to select and combine them.

## 4. Dense-decoder evidence

In the controlled parity studies, universal-to-compiled width ratios range from 91× to 1820×. Under the registered dense decoder, compiled states reach the target accuracy at smaller training sizes. In the difficult cells, the universal state does not reach the target inside the frozen grid while the compiled state does.

A direct constructor that emitted the label would trivialize this effect. A no-answer-laundering construction therefore exposes only the latent query components, five or seven depending on the cell, and requires the decoder to infer an odd-cardinality majority. No exposed component equals or negates the final target.

These experiments show that upstream construction can remove structural-search burden under a dense access model. They do not establish that the burden cannot be recovered downstream by a stronger decoder.

## 5. Sparse decoder substitution

A preregistered sparse-decoder attack tests a stronger claim: compiled state should retain at least a fourfold sample-threshold advantage in both difficult cells.

The claim fails. The sparse universal decoder reaches the target at \(n=128\) and \(n=256\); compiled state reaches it at \(n=64\). The residual threshold ratios are therefore 2× and 4×, not at least 4× in both cells. A fresh deterministic replication reproduces those residuals and the corresponding low-sample accuracy differences.

The negative result identifies feature discovery as a substitute for upstream state construction. The original dense-decoder margin was partly a decoder-access effect.

## 6. Nonlinear attacks and arm dependence

A separately frozen deterministic tree-ensemble arm retains substantial low-sample gaps against its named universal-state comparator. In the two difficult cells, the universal arm remains below the 0.95 target through \(n=1024\), whereas compiled state reaches the target by \(n=64\).

That result is arm-specific, not a nonlinear lower bound. When all registered universal arms are pooled in a later gate, the successor becomes negative in the narrow-state regime. The comparison therefore depends jointly on state width, decoder inductive bias, and query structure.

The refined claim is substitution, not domination: moving search upstream can help a restricted decoder, while an appropriate downstream model can absorb part of the apparent representation advantage.

## 7. Non-synthetic transfer boundary

A separate digits experiment asks whether a learned 16-of-64 compiler preserves responsibility-specific quality across ten tasks. The frozen family gate requires at least 8 of 10 supported responsibilities.

The gate fails. Support is obtained for 3 of 10 tasks with linear access and 5 of 10 with RBF or KNN. The adverse result prevents the synthetic mechanism study from being promoted into a broad real-task claim.

The digits result also illustrates why average accuracy is insufficient. A constructor useful for some responsibilities can be inadequate for others, and specialization must be evaluated against the future responsibility distribution.

## 8. Construction cost and option debt

Upstream construction can reduce decoder burden while creating lifecycle costs:

- construction and invalidation work;
- storage and materialization;
- query-specific rebuilds;
- loss of raw recoverability;
- inability to answer unanticipated future queries.

Retaining a specialized state without a recovery route creates option debt. A state that is efficient for the current query can be inferior over a changing workload.

Exact workload laws compare retaining raw state and compiling on demand, maintaining a universal materialization, and retaining specialized state with an explicit recovery policy. Compilation is favorable only when future service savings exceed construction, storage, invalidation, and recovery costs under the declared horizon.

## 9. Resource accounting

A fair comparison should expose a resource vector rather than silently treating preprocessing as free. Relevant coordinates include:

- state-construction operations;
- state size;
- training or inference examples;
- decoder search;
- verifier calls;
- latency;
- cache and recovery work;
- model capacity.

A scalar objective is justified only when its exchange rates are frozen before outcomes. Otherwise the correct output is a Pareto frontier.

## 10. Production boundary

A later production-style successor was designed to test learned construction, stronger decoders, total resource savings, drift, future-query transfer, and recovery. Its required datasets, models, transcripts, and resource receipts were not bound. Zero scientific cases executed.

This is acquisition failure, not a negative performance result. It contributes no evidence of real-system generalization.

## 11. Donor boundary

Sufficient representations, partial evaluation, knowledge compilation, materialized views, feature selection, sparse decoding, and query-conditioned retrieval own the underlying primitives. The paper does not claim them as new.

Its residual contribution is the joint accounting: accessible-rank theory makes one access-class burden explicit, hostile decoders quantify substitution between upstream and downstream search, and optionality laws expose the cost of specializing the state.

## 12. Limitations

The strongest positive evidence is controlled and largely synthetic. The theorem is access-class-relative. A more expressive decoder can reduce or remove a compiled-state advantage. The digits transfer is adverse, and no production case has executed.

The paper does not establish that compiled state is universally smaller, easier to use, cheaper end to end, or superior in deployed agents.

## 13. Conclusion

State construction and decoder search are two places to pay for the same structural work. Accessible rank quantifies one fixed-representation burden, controlled studies show how query-conditioned construction can remove it, and hostile decoders recover part of the margin. The non-synthetic gate remains adverse, and future optionality can reverse a present-query advantage. The durable result is a resource-placement principle: evaluate the state and the decoder together, count construction and recovery, and treat specialization as a lifecycle choice rather than a free improvement.
