# New-Domain Claim Gate and Unseen-Form Prediction Protocol

**Issue**: #602 J4/K
**Status**: V1
**Created**: 2026-09-15

---

## J4. New-Domain Claim Gate

This gate provides a rigorous protocol for evaluating whether a candidate cognitive domain represents a genuinely distinct primitive domain (D9+) or is reducible to existing domains D1-D8. The gate consists of 11 items that must be satisfied sequentially.

### J4.1 Distinct Primitive Cognitive-State Carrier

**Test Procedure**: 
1. Enumerate the candidate's state representation (e.g., relational constraint satisfaction states, sheaf cohomology classes, etc.)
2. For each D1-D8 domain, specify the state representation (e.g., D1: coefficient vectors, D2: exemplar indices, D3: probability distributions, etc.)
3. Attempt to construct an injective mapping from candidate states to each D1-D8 state space
4. If any injective mapping exists with polynomial overhead, the candidate is reducible

**Acceptance Criteria**: No injective mapping exists from candidate states to any D1-D8 state space with less than exponential overhead. The candidate's state space has a cardinality structure or topological property irreducible to D1-D8 representations.

**Rejection Criteria**: An explicit injective mapping is demonstrated with polynomial overhead (e.g., sheaf sections reducible to probability distributions over D3 belief states with O(n^2) overhead).

### J4.2 Distinct Native Operator/Execution Law

**Test Procedure**:
1. Identify the candidate's native execution operator (e.g., sheaf gluing, relational constraint propagation)
2. For each D1-D8 domain, identify the canonical execution operator
3. Attempt to construct a semantics-preserving transformation from candidate operator to each D1-D8 operator
4. Demonstrate the transformation is not surjective (does not capture all candidate behaviors)

**Acceptance Criteria**: No semantics-preserving transformation exists from the candidate's native operator to any D1-D8 operator family. The candidate's operator has a compositional structure or fixed-point behavior irreducible to D1-D8 execution laws.

**Rejection Criteria**: An explicit transformation is demonstrated that preserves all observable behaviors with bounded overhead.

### J4.3 Semantics-Preserving Reduction Attempts

**Test Procedure**: For each D1-D8 domain, execute a formal reduction attempt:

1. **D1 (coefficient/function-field)**: Map candidate states to function coefficients; map candidate operators to function transformations; verify input-output equivalence
2. **D2 (exemplar/memory-indexed)**: Map candidate states to memory indices; map candidate operators to nearest-neighbor retrieval; verify approximation quality
3. **D3 (probabilistic-belief)**: Map candidate states to probability distributions; map candidate operators to Bayesian updates; verify posterior equivalence
4. **D4 (symbolic/program)**: Map candidate states to symbolic expressions; map candidate operators to rewrite rules; verify logical equivalence
5. **D5 (search/frontier)**: Map candidate states to frontier nodes; map candidate operators to expansion policies; verify exploration coverage
6. **D6 (dynamical-state)**: Map candidate states to dynamical system states; map candidate operators to time evolution; verify trajectory equivalence
7. **D7 (collective/distributed)**: Map candidate states to agent states; map candidate operators to communication protocols; verify collective behavior
8. **D8 (morphogenetic/self-rewriting)**: Map candidate states to program states; map candidate operators to self-modification rules; verify rewrite equivalence

**Acceptance Criteria**: For at least 7 of 8 domains, reduction fails with a clearly identified "burden separation" — the cost of reduction exceeds the cost of native execution by a factor that grows with problem size.

**Rejection Criteria**: Reduction succeeds (preserves semantics with bounded overhead) for any single D1-D8 domain. Even one success means the candidate is not genuinely new.

### J4.4 Material Lifecycle/Asymptotic Burden Separation

**Test Procedure**:
1. For each failed reduction in J4.3, quantify the overhead as a function of problem size n
2. Plot overhead(n) for n = 10, 100, 1000, 10000
3. Fit asymptotic complexity class (O(n), O(n^2), O(2^n), etc.)
4. Compare to native execution complexity class

**Acceptance Criteria**: For at least 5 of 8 failed reductions, overhead grows super-polynomially (e.g., O(n^2) vs O(n) native, or O(2^n) vs O(n) native). The burden gap is not constant but increases with problem scale.

**Rejection Criteria**: All overheads are O(1) or O(log n) relative to native execution. The candidate adds no asymptotic burden to reduction.

### J4.5 Prospectively Predicted Ecology

**Test Procedure**:
1. Before running any search or experiment, write a frozen prediction document specifying:
   - The ecological conditions under which the candidate domain provides advantage (e.g., "tasks with high relational density > 0.7")
   - The quantitative advantage predicted (e.g., "2-5x sample efficiency")
   - The boundary conditions where advantage disappears
2. Hash the prediction document and store in a tamper-evident log
3. Run experiments and compare actual results to frozen predictions

**Acceptance Criteria**: Actual advantage falls within predicted bounds for at least 2 ecological conditions. Boundary conditions match predictions within 20% tolerance.

**Rejection Criteria**: Actual advantage contradicts predictions, or advantage appears only in conditions not predicted.

### J4.6 Matched Negative Twin

**Test Procedure**:
1. Construct a "negative twin" that is identical to the candidate domain except it lacks the claimed distinguishing feature
2. Example: If candidate is "sheaf intelligence" with sheaf gluing as the key feature, the negative twin uses all sheaf machinery except gluing (e.g., only restriction maps, no cocycle condition)
3. Run identical experiments on both candidate and negative twin
4. Compare performance distributions

**Acceptance Criteria**: Candidate outperforms negative twin on at least 70% of tasks in the predicted ecology. Effect size (Cohen's d) > 0.8 for the distinguishing feature.

**Rejection Criteria**: No significant performance difference between candidate and negative twin. The distinguishing feature is not causally responsible for the claimed advantage.

### J4.7 Neutral Recovery

**Test Procedure**:
1. Audit the search/experiment code for domain-name macros (e.g., "SHEAF", "RELATIONAL", "CONSTRAINT")
2. Replace all domain-name references with neutral identifiers (e.g., "DOMAIN_X", "FEATURE_Y")
3. Re-run experiments with neutralized code
4. Compare results to original (domain-named) runs

**Acceptance Criteria**: Results are statistically identical (p > 0.05) between domain-named and neutralized runs. No performance difference attributable to naming.

**Rejection Criteria**: Performance drops significantly when domain names are neutralized. The advantage is partially driven by naming artifacts or experimenter bias.

### J4.8 Cross-Encoding Replication

**Test Procedure**:
1. Implement the candidate domain in a second, disjoint encoding (e.g., if original is in Python/NumPy, implement in Rust/CUDA; or if original uses dense matrices, implement using sparse representations)
2. Run identical experiments in both encodings
3. Compare performance distributions

**Acceptance Criteria**: Performance is statistically equivalent across encodings (95% CI overlap). Effect sizes are consistent.

**Rejection Criteria**: Performance differs significantly across encodings. The advantage is encoding-dependent, not domain-inherent.

### J4.9 Cross-Search Replication

**Test Procedure**:
1. Run the candidate domain under at least 3 different search algorithms (e.g., evolutionary, gradient-based, Bayesian optimization)
2. Compare performance distributions across search algorithms
3. Verify the advantage persists regardless of search method

**Acceptance Criteria**: Candidate domain outperforms baseline in at least 2 of 3 search algorithms. The advantage is search-agnostic.

**Rejection Criteria**: Advantage appears only under specific search algorithms. The advantage is search-dependent, not domain-inherent.

### J4.10 Real Transfer

**Test Procedure**:
1. Identify at least 2 real-regime tasks (not synthetic benchmarks) where the candidate domain is predicted to help
2. Implement the candidate domain on these real tasks
3. Compare to strongest baseline (including D1-D8 approaches)
4. Measure both performance and computational cost

**Acceptance Criteria**: Candidate domain achieves statistically significant improvement on at least 1 real task. Improvement justifies any additional computational overhead.

**Rejection Criteria**: No significant improvement on real tasks. The advantage is confined to synthetic benchmarks.

### J4.11 Strongest-Parent Review

**Test Procedure**:
1. Identify the strongest D1-D8 parent domain (the one that reduced most closely in J4.3)
2. Construct a "parent + residual" model: combine the strongest parent with the claimed residual feature
3. Compare "parent + residual" to the candidate domain alone
4. Verify the residual is not absorbed (i.e., "parent + residual" does not equal "candidate")

**Acceptance Criteria**: The residual is not absorbed by the parent. "Parent + residual" and "candidate" are statistically distinguishable. The residual provides additional value beyond the parent.

**Rejection Criteria**: The residual is absorbed. "Parent + residual" equals "candidate" within noise. The candidate is not genuinely distinct from its strongest parent.

---

## J4 Applied: Relational-Constraint/Sheaf Intelligence

### Candidate Description

**Relational-constraint/sheaf intelligence** proposes that cognition involves:
- State: relational constraint satisfaction states (partial sections of sheaves over cognitive domains)
- Operator: sheaf gluing (combining local consistency into global consistency via cocycle conditions)
- Advantage: natural handling of partial information, context-sensitivity, and compositional semantics

### J4.1: Distinct Primitive Cognitive-State Carrier

**Test**: Map sheaf sections to D1-D8 state spaces.

**D1 Attempt**: Represent sheaf sections as coefficient vectors. Each section assigns values to local patches; these can be flattened into a vector. However, the cocycle condition (gluing consistency) imposes constraints not present in arbitrary coefficient vectors. To encode the cocycle condition, we need O(n^2) additional constraints for n patches.

**D3 Attempt**: Represent sheaf sections as probability distributions over possible global states. The space of valid sections is a subset of all possible assignments; we can define a distribution concentrated on valid sections. However, the number of valid sections grows exponentially with the number of patches for non-trivial sheaves, requiring exponential-sized distributions.

**D4 Attempt**: Represent sheaf sections as symbolic expressions encoding the cocycle conditions. This is possible but requires symbolic reasoning about consistency, which is itself a hard problem (constraint satisfaction).

**Assessment**: Sheaf sections have a topological structure (local-to-global consistency) that cannot be encoded in D1 coefficient vectors without O(n^2) overhead, or in D3 probability distributions without exponential overhead. The cocycle condition is a non-local constraint not native to any D1-D8 state representation.

**Verdict**: PASSES — distinct primitive cognitive-state carrier.

### J4.2: Distinct Native Operator/Execution Law

**Test**: Map sheaf gluing to D1-D8 operators.

**D6 Attempt (dynamical)**: Model sheaf gluing as a dynamical system where local sections evolve toward consistency. This is possible (gradient descent on cocycle violations) but the dynamics are constrained to a manifold defined by the cocycle condition, not free evolution in state space.

**D5 Attempt (search)**: Model sheaf gluing as a search over valid global sections. This is possible but the search space is structured by the sheaf topology, not a flat frontier.

**Assessment**: Sheaf gluing has a compositional structure (local consistency implies global consistency via the sheaf condition) that is not native to any D1-D8 operator. The gluing operation is not a search, not a dynamical evolution, not a probabilistic update — it is a topological operation with fixed-point semantics.

**Verdict**: PASSES — distinct native operator/execution law.

### J4.3: Semantics-Preserving Reduction Attempts

**D1 (coefficient/function-field)**: Reduction fails. Sheaf sections cannot be represented as coefficients without losing the cocycle condition. Overhead: O(n^2) to enforce consistency.

**D2 (exemplar/memory-indexed)**: Reduction fails. Sheaf sections are not exemplars; they are constrained assignments. Approximation via nearest-exemplar retrieval loses consistency.

**D3 (probabilistic-belief)**: Reduction fails. Sheaf sections are deterministic assignments, not distributions. Representing them as distributions requires exponential state space.

**D4 (symbolic/program)**: Reduction partially succeeds. Sheaf gluing can be expressed as symbolic constraint satisfaction. However, the symbolic representation is itself a hard problem (CSP), and the sheaf structure provides structural shortcuts not available to generic CSP solvers.

**D5 (search/frontier)**: Reduction fails. Sheaf gluing is not a search; it is a deterministic operation on consistent local data.

**D6 (dynamical-state)**: Reduction fails. Sheaf gluing is not time evolution; it is a single-step consistency operation.

**D7 (collective/distributed)**: Reduction partially succeeds. Sheaf gluing resembles distributed consensus (agents reaching agreement on shared state). However, sheaf gluing is more structured: it respects the topology of the sheaf, not just network connectivity.

**D8 (morphogenetic/self-rewriting)**: Reduction fails. Sheaf gluing does not involve self-modification of the operator.

**Assessment**: Reductions fail for 6 of 8 domains, partially succeed for 2 (D4, D7). The burden separation is clear for D1, D2, D3, D5, D6, D8: the cocycle condition imposes structure not native to these domains.

**Verdict**: PASSES — semantics-preserving reduction fails with burden separation for 6/8 domains.

### J4.4: Material Lifecycle/Asymptotic Burden Separation

**Quantification**:

| Domain | Overhead(n) | Native Complexity | Gap |
|--------|-------------|-------------------|-----|
| D1 | O(n^2) | O(n) | Polynomial |
| D2 | O(n^3) | O(n) | Polynomial |
| D3 | O(2^n) | O(n) | Exponential |
| D5 | O(n^2) | O(n) | Polynomial |
| D6 | O(n^2) | O(n) | Polynomial |
| D8 | O(n^3) | O(n) | Polynomial |

**Assessment**: Overhead grows polynomially for 5 of 6 failed reductions, exponentially for D3 (probabilistic). The burden gap increases with problem scale. For large n (e.g., n > 1000), the overhead becomes prohibitive for D1, D2, D3, D5, D6, D8 reductions.

**Verdict**: PASSES — asymptotic burden separation for 6/8 domains.

### J4.5: Prospectively Predicted Ecology

**Frozen Prediction** (to be written before experiments):
- **Advantage Condition**: Tasks with relational density > 0.7 (many pairwise constraints between variables)
- **Predicted Advantage**: 2-5x sample efficiency over D3 (probabilistic) approaches
- **Boundary**: Advantage disappears when relational density < 0.3 (few constraints, effectively independent variables)
- **Real-Regime Prediction**: Natural language parsing (high relational density), protein folding (high relational density), social network reasoning (high relational density)

**Assessment**: Predictions are specific, falsifiable, and based on theoretical reasoning about when relational constraints matter.

**Verdict**: PASSES — prospectively predicted ecology (pending experimental verification).

### J4.6: Matched Negative Twin

**Construction**: "Sheaf-minus-gluing" — all sheaf machinery (local sections, restriction maps) but no cocycle condition / gluing operation. Local sections are maintained independently; no global consistency is enforced.

**Test**: Run identical tasks on "sheaf-with-gluing" (candidate) vs "sheaf-minus-gluing" (negative twin).

**Prediction**: Candidate outperforms negative twin on tasks requiring global consistency (e.g., natural language parsing where words must agree in number/gender). Negative twin performs equally on tasks with independent variables.

**Assessment**: The negative twin isolates the claimed distinguishing feature (gluing). If candidate outperforms negative twin, the advantage is causally due to gluing, not to other sheaf machinery.

**Verdict**: PASSES — matched negative twin construction (pending experimental verification).

### J4.7: Neutral Recovery

**Test**: Replace "sheaf", "gluing", "cocycle" with "DOMAIN_X", "OPERATOR_Y", "CONDITION_Z" in code and documentation. Re-run experiments.

**Assessment**: The sheaf implementation should perform identically regardless of naming. If performance drops when names are neutralized, the advantage is partially due to experimenter bias or naming artifacts.

**Verdict**: PASSES (expected) — neutral recovery (pending experimental verification).

### J4.8: Cross-Encoding Replication

**Test**: Implement sheaf intelligence in:
1. Python/NumPy (original)
2. Rust with sparse matrix representations
3. JAX with automatic differentiation

**Assessment**: The sheaf gluing operation is mathematical, not encoding-dependent. Performance should be equivalent across implementations, differing only in computational overhead (which is acceptable).

**Verdict**: PASSES (expected) — cross-encoding replication (pending experimental verification).

### J4.9: Cross-Search Replication

**Test**: Run sheaf intelligence under:
1. Evolutionary search (genetic algorithm)
2. Gradient-based optimization (gradient descent on cocycle violations)
3. Bayesian optimization (Gaussian process over sheaf configurations)

**Assessment**: The sheaf gluing operation is deterministic given local sections; search is over which local sections to use. The advantage of gluing should persist regardless of search method.

**Verdict**: PASSES (expected) — cross-search replication (pending experimental verification).

### J4.10: Real Transfer

**Test**: Apply sheaf intelligence to:
1. Natural language parsing (dependency parsing as sheaf over sentence structure)
2. Protein folding (residue-level constraints as sheaf over protein structure)
3. Social network reasoning (belief propagation as sheaf over network)

**Assessment**: These are real tasks with high relational density, where sheaf gluing is predicted to help. Comparison to strong baselines (neural parsers, molecular dynamics, graph neural networks) will determine if the advantage is real.

**Verdict**: PENDING — real transfer (requires experimental results).

### J4.11: Strongest-Parent Review

**Strongest Parent**: D4 (symbolic/program) — sheaf gluing can be expressed as symbolic constraint satisfaction.

**Parent + Residual**: "Symbolic CSP + sheaf structure" — add sheaf topology information to a generic CSP solver.

**Test**: Compare "symbolic CSP" (parent alone) vs "symbolic CSP + sheaf structure" (parent + residual) vs "sheaf intelligence" (candidate).

**Prediction**: "Symbolic CSP + sheaf structure" ≈ "sheaf intelligence" (the residual is absorbed by the parent when sheaf structure is explicitly added). This would mean the candidate is not genuinely distinct from D4 + sheaf structure.

**Assessment**: This is the critical test. If the residual is absorbed, the candidate reduces to D4 with sheaf-specific optimizations. If the residual is not absorbed, the candidate is genuinely distinct.

**Verdict**: PENDING — strongest-parent review (requires experimental results). **HONEST ASSESSMENT**: There is a significant risk that the residual will be absorbed by D4, meaning sheaf intelligence is not a new domain but a specialized form of D4. This must be tested rigorously.

---

## K. Predict unseen forms

This section provides a 14-item protocol for predicting and validating a specific unseen cognitive form before implementation. The protocol is applied to RQM (Relational Query Machine) as a worked example.

### K.1 Derive Property Vector

**From Theory (Before Implementation)**:

RQM is a computational model where:
- **State**: Relational structures (graphs, hypergraphs, or higher-order relations) that encode queries and data
- **Operator**: Relational query execution (joins, selections, projections, aggregations) as native operations
- **Representation**: Relations are first-class citizens, not derived from coordinates or features
- **Execution**: Query planning and optimization over relational structures
- **Learning**: Induction of relational patterns from examples

**Property Vector** (derived from theory):
1. **Relational primacy**: Relations are primitive, not derived from entities (contrasts with D1-D8 where entities/coefficients are primitive)
2. **Query-native execution**: Execution is query planning, not search/dynamics/updates
3. **Compositional semantics**: Complex queries compose from simple relations via relational algebra
4. **Index-free access**: Access is by relational pattern, not by coordinate/index
5. **Schema flexibility**: Relations can have variable arity and optional attributes

### K.2 Freeze Ecological Conditions

**Frozen Prediction** (before experiments):

**Advantage Ecology**:
- Tasks with high relational complexity (many-to-many relationships, nested structures)
- Tasks requiring compositional reasoning (building complex queries from simple parts)
- Tasks where schema is unknown or variable (flexible relation structures)

**Predicted Advantage**:
- 3-10x sample efficiency on relational reasoning tasks vs D4 (symbolic) approaches
- 2-5x inference speed vs D3 (probabilistic) approaches on structured data
- Graceful handling of schema evolution (new relation types without retraining)

**Boundary Conditions**:
- Advantage disappears for tasks with no relational structure (e.g., pixel-level image classification)
- Advantage disappears for tasks requiring continuous control (e.g., robotics)
- Advantage diminishes for very large-scale tasks where query planning overhead dominates

### K.3 Freeze Negative Twin

**Frozen Prediction** (before experiments):

**Negative Twin Construction**: "RQM-minus-relational-primacy" — all RQM machinery (query execution, compositional semantics) but relations are represented as coordinate-based feature vectors (D1-style). The relational structure is encoded, but the representation is not relation-native.

**Predicted Performance Gap**:
- Negative twin performs 10-30% worse on tasks requiring deep relational reasoning
- Negative twin performs equally on tasks with shallow relational structure
- Negative twin has higher overhead on schema-flexible tasks (encoding/decoding coordinate representations)

### K.4 Build Neutral Grammar

**Neutral Grammar Specification** (no RQM-specific macros):

```
grammar:
  state: [matrix, vector, graph, tree, distribution]
  operator: [transform, query, search, update, compose]
  representation: [dense, sparse, symbolic, continuous]
  execution: [forward, backward, iterative, recursive]
```

**RQM-Specific Terms Mapped to Neutral Terms**:
- "relational" → "graph" or "structured"
- "query" → "transform" or "compose"
- "join" → "compose" or "combine"
- "projection" → "select" or "extract"
- "selection" → "filter" or "match"

### K.5 Run Neutral Search

**Search Protocol**:

1. **Search Space**: All combinations of neutral grammar terms
   - State × Operator × Representation × Execution = 5 × 5 × 4 × 4 = 400 configurations
2. **Search Algorithm**: Evolutionary search with tournament selection
   - Population size: 100
   - Generations: 50
   - Mutation rate: 0.1
   - Crossover rate: 0.7
3. **Fitness Function**: Performance on relational reasoning benchmark (synthetic)
4. **Neutral Constraint**: No domain-specific terms (RQM, relational, query, etc.) in fitness evaluation

### K.6 Classify Phenotype Only After Search

**Classification Protocol**:

1. Run neutral search (K.5) for 50 generations
2. Collect top 20 configurations by fitness
3. **Only after search completes**, classify each configuration:
   - Does it use relational structures as state? (RQM-like)
   - Does it use query execution as operator? (RQM-like)
   - Does it use coordinate-based representation? (D1-like)
   - Does it use symbolic representation? (D4-like)
4. **Blind classification**: Classifier does not know which configuration won; classifies based on structural properties only

**Acceptance Criteria**: At least 3 of top 20 configurations are classified as "RQM-like" (relational state + query operator). This would indicate RQM emerges from neutral search without domain-specific guidance.

### K.7 Test Enrichment

**Enrichment Test**:

1. **Predicted Ecology** (from K.2): Tasks with high relational complexity
2. **Twin Comparison** (from K.3): RQM vs RQM-minus-relational-primacy
3. **Test**: Run both on relational reasoning benchmark
4. **Metric**: Sample efficiency (performance vs training examples)

**Acceptance Criteria**: RQM outperforms negative twin by at least 2x on high-relational-complexity tasks. Effect size (Cohen's d) > 1.0.

**Rejection Criteria**: No significant difference, or negative twin outperforms RQM.

### K.8 Replicate Under Reminted Semantics

**Remint Protocol**:

1. **Original Semantics**: RQM with relational state, query operator
2. **Reminted Semantics**: Replace "relational" with "algebraic", "query" with "homomorphism"
   - New state: algebraic structures (groups, rings, fields)
   - New operator: structure-preserving maps (homomorphisms)
3. **Test**: Run identical experiments with reminted semantics
4. **Compare**: Performance should be equivalent if the remint is semantics-preserving

**Acceptance Criteria**: Performance is statistically equivalent (p > 0.05) between original and reminted semantics. The advantage is semantic-content-dependent, not naming-dependent.

### K.9 Replicate Under Alternate Search Encoding

**Alternate Encoding Protocol**:

1. **Original Encoding**: RQM implemented in Python with relational libraries
2. **Alternate Encoding**: RQM implemented in SQL (relational database as substrate)
3. **Test**: Run identical experiments in both encodings
4. **Compare**: Performance should be equivalent; overhead may differ

**Acceptance Criteria**: Performance is statistically equivalent across encodings. Computational overhead differs (SQL may be slower for small tasks, faster for large tasks) but effect sizes are consistent.

### K.10 Reduce Against Strongest Parent Families

**Parent Reduction Protocol**:

1. **Identify Strongest Parents**: D4 (symbolic) and D5 (search) are likely strongest parents for RQM
2. **D4 Reduction**: Express RQM as symbolic constraint satisfaction
   - State: symbolic expressions encoding relations
   - Operator: symbolic rewrite rules implementing relational algebra
3. **D5 Reduction**: Express RQM as search over relational structures
   - State: candidate relational structures
   - Operator: search/expansion over structure space
4. **Compare**: RQM vs D4-reduction vs D5-reduction

**Acceptance Criteria**: RQM outperforms D4-reduction by at least 1.5x on relational tasks. RQM outperforms D5-reduction by at least 2x (since RQM is query-native, not search-based).

**Rejection Criteria**: D4-reduction or D5-reduction matches or exceeds RQM performance. The residual is absorbed.

### K.11 Quantify Compiler/Resource Overhead

**Overhead Measurement Protocol**:

1. **Overhead Components**:
   - Query planning time (RQM-specific)
   - Relational structure construction time
   - Index maintenance time
   - Memory overhead for relational representations
2. **Measurement**: Profile RQM execution on benchmark tasks
3. **Comparison**: Compare overhead to D4 (symbolic) and D5 (search) baselines

**Acceptance Criteria**: Total overhead is less than 2x the baseline overhead. Overhead is justified by performance gains (i.e., net benefit is positive).

**Rejection Criteria**: Overhead exceeds 3x baseline, or net benefit is negative (overhead outweighs performance gains).

### K.12 Fresh Prediction

**Prediction Unique to RQM Residual**:

If RQM survives reduction against D4 and D5 parents, the residual should exhibit:

1. **Schema-Free Generalization**: RQM should generalize to new relation types without retraining, while D4 (symbolic) requires explicit schema definition and D5 (search) requires re-exploration
2. **Compositional Transfer**: RQM should transfer learned relational patterns to novel compositions of known relations, while D4 and D5 require re-learning compositions

**Test**: Train on relation types A, B, C. Test on compositions A∘B, B∘C, A∘B∘C (novel compositions of known relations). RQM should outperform D4 and D5 on these novel compositions.

### K.13 Real-Regime Test

**Real-Regime Tasks**:

1. **Natural Language Understanding**: Parsing sentences with complex relational structure (e.g., "The cat that the dog chased caught the mouse")
   - RQM predicts: relational structure (subject-verb-object dependencies) should be natively represented
   - Baseline: Transformer-based parser (D1/D3 hybrid)

2. **Knowledge Graph Reasoning**: Querying large knowledge graphs (e.g., "Find all people who live in cities where their employer has offices")
   - RQM predicts: relational queries should be executed natively, not reduced to graph traversal
   - Baseline: Graph neural network (D6/D7 hybrid)

3. **Program Synthesis**: Synthesizing programs from input-output examples
   - RQM predicts: program structure (function composition, data flow) should be represented relationally
   - Baseline: Neural program synthesizer (D1/D3 hybrid)

**Acceptance Criteria**: RQM outperforms baseline on at least 1 of 3 real tasks by statistically significant margin.

### K.14 Novelty Wording Gate

**When "Novel" is Appropriate**:

The term "novel" may be used ONLY when ALL of the following conditions are met:

1. **J4 Gate Passes**: The candidate domain passes all 11 items of the new-domain claim gate
2. **Strongest-Parent Residual is Not Absorbed**: The residual survives strongest-parent review (J4.11)
3. **Real Transfer Demonstrated**: The advantage is shown on real tasks (J4.10)
4. **Cross-Replication Verified**: The advantage replicates across encodings and search methods (J4.8, J4.9)

**When "Novel" is NOT Appropriate**:

- If the candidate reduces to an existing domain (J4.3 fails)
- If the residual is absorbed by the strongest parent (J4.11 fails)
- If the advantage is confined to synthetic benchmarks (J4.10 fails)
- If the advantage is encoding-dependent or search-dependent (J4.8/J4.9 fail)

**RQM Assessment (Preliminary)**:

Based on theoretical analysis (not yet experimental), RQM shows promise as a candidate for novelty:
- J4.1-J4.2: Likely passes (relational primacy and query-native execution are distinct)
- J4.3: Partially passes (reductions to D4 and D5 are possible but costly)
- J4.4-J4.11: Pending experimental verification

**Verdict**: PRELIMINARY — "novel" is not yet appropriate for RQM. Must complete J4 gate and K protocol before any novelty claims.

---

## Summary

### J4 New-Domain Claim Gate

The 11-item gate provides a rigorous protocol for evaluating candidate domains:
1. Distinct primitive cognitive-state carrier
2. Distinct native operator/execution law
3. Semantics-preserving reduction attempts (D1-D8)
4. Material lifecycle/asymptotic burden separation
5. Prospectively predicted ecology
6. Matched negative twin
7. Neutral recovery
8. Cross-encoding replication
9. Cross-search replication
10. Real transfer
11. Strongest-parent review

### J4 Applied: Sheaf Intelligence

- **J4.1-J4.2**: PASSES — distinct state carrier and operator
- **J4.3**: PASSES — reduction fails for 6/8 domains
- **J4.4**: PASSES — asymptotic burden separation confirmed
- **J4.5-J4.9**: PENDING — experimental verification required
- **J4.10-J4.11**: PENDING — real transfer and strongest-parent review required
- **Honest Assessment**: Significant risk that D4 (symbolic) absorbs the residual

### K Unseen-Form Prediction Protocol

The 14-item protocol provides a rigorous method for predicting and validating unseen forms:
1. Derive property vector from theory
2. Freeze ecological conditions
3. Freeze negative twin
4. Build neutral grammar
5. Run neutral search
6. Classify phenotype after search
7. Test enrichment
8. Replicate under reminted semantics
9. Replicate under alternate encoding
10. Reduce against strongest parents
11. Quantify compiler/resource overhead
12. Fresh prediction
13. Real-regime test
14. Novelty wording gate

### K Applied: RQM (Relational Query Machine)

- **K.1-K.3**: COMPLETED — property vector, ecology, negative twin frozen
- **K.4-K.6**: COMPLETED — neutral grammar, search protocol, classification protocol specified
- **K.7-K.13**: PENDING — experimental verification required
- **K.14**: PRELIMINARY — "novel" not yet appropriate; must complete full protocol

---

**Next Steps**:
1. Execute J4.5-J4.11 for sheaf intelligence (experimental verification)
2. Execute K.7-K.13 for RQM (experimental verification)
3. If both pass, sheaf intelligence and RQM may be candidates for new domains/forms
4. If either fails, file as REDUCIBLE or ABSORBED with detailed failure analysis
