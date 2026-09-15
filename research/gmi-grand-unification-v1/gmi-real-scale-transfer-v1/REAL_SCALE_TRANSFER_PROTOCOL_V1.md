# Real-Scale Transfer Protocol

**Issue**: #602 T  
**Status**: V1  
**Created**: 2026-09-15  
**Scope**: Transfer GMI morphology phase law predictions from tiny-world experiments to real-scale task benchmarks

---

## T.0 Protocol Overview

### Purpose

This protocol specifies how to test whether GMI morphology phase law predictions, derived from exact finite-scope tiny-world experiments, transfer to real-scale task categories. Each of the 10 unchecked T items receives a complete specification: benchmark selection, GMI prediction, ecology mapping, morphology prediction, comparison protocol, freeze protocol, scaling protocol, and falsification criteria.

### Core GMI Claims Under Test

1. **Morphology Phase Law** (Theorem T-MPL-01): Task morphology determines optimal architecture class; morphology transitions occur at ecology boundaries.
2. **Ecology-Coordinate Prediction** (Theorem T-ECP-01): Four coordinates (E: environment, R: resource, V: variation, H: history) determine morphology phase.
3. **Capability Contract** (Theorem T-CC-01): Each morphology has bounded capability regions; exceeding bounds triggers phase transition.
4. **Resource Lifecycle Ledger** (Theorem T-RLL-01): Resource allocation follows ecology-dependent lifecycle; over/under-allocation produces measurable degradation.

### Transfer Claim

If GMI predictions transfer, then:
- Tasks with ecology coordinates within the same phase as tiny-world experiments will exhibit the predicted morphology advantage
- Tasks at phase boundaries will exhibit predicted transition behavior
- Tasks outside predicted phases will exhibit predicted degradation

---

## T.1 Real Code Tasks

### T.1.1 Task Selection

| Benchmark | Task Type | Scale | Difficulty |
|-----------|-----------|-------|------------|
| HumanEval | Function-level code generation | 164 problems | Medium |
| MBPP | Function-level code generation | 974 problems | Medium |
| SWE-bench | Repository-level bug fixing | 2,294 instances | Hard |
| CodeContests | Competitive programming | 10,000+ problems | Very Hard |
| APPS | Introductory to competition-level | 10,000 problems | Variable |
| DS-1000 | Data science code generation | 1,000 tasks | Medium-Hard |

### T.1.2 GMI Prediction

**Theorem Reference**: T-MPL-01 (Morphology Phase Law)

**Prediction**: 
- Code generation tasks with high sequential dependency (function-level, I/O spec → code) will favor **D4 (symbolic/program)** morphology
- Code generation tasks with high compositional structure (repository-level, multi-function) will favor **D5 (search/frontier)** morphology
- Code generation tasks requiring causal reasoning (debugging) will favor **D6 (dynamical-state)** morphology

### T.1.3 Ecology Mapping

| Coordinate | Function-level (HumanEval/MBPP) | Repository-level (SWE-bench) | Competitive (CodeContests) |
|------------|--------------------------------|------------------------------|----------------------------|
| E (Environment) | Deterministic I/O, single function | Multi-file, git context | Dynamic test cases, hidden |
| R (Resource) | Low: ~100 tokens per problem | High: ~10K tokens per instance | Medium: ~1K tokens per problem |
| V (Variation) | Low: fixed signature | Medium: varying patterns | High: novel algorithms |
| H (History) | None: fresh context | Long: full repository | None: fresh per problem |

### T.1.4 Morphology Prediction

| Task Type | Predicted Morphology | Confidence | Tiny-world Analog |
|-----------|---------------------|------------|-------------------|
| Function generation (with spec) | D4 (symbolic) | High | Symbolic rewriting in tiny formal grammar |
| Function generation (without spec) | D5 (search) | Medium | Combinatorial search in tiny DSL |
| Repository bug fixing | D5 (search) + D6 (dynamical) | Medium | Multi-step reasoning in tiny world |
| Debugging | D6 (dynamical) | High | Causal chain tracing in tiny dynamics |

### T.1.5 Comparison Protocol

**Baselines**:
1. **D1 Baseline**: Codex/CodeGen (function-field neural code model)
2. **D3 Baseline**: CodeRL (probabilistic belief over code tokens)
3. **D4 Baseline**: Codex with symbolic constraint verification
4. **D5 Baseline**: AlphaCode (search over code samples)
5. **D6 Baseline**: GPT-4 with chain-of-thought debugging

**Metrics**:
- Pass@k (percentage of problems solved with k samples)
- Pass@1 (single-sample accuracy)
- Computational cost (tokens, time, memory)
- Sample efficiency (problems solved per 1K tokens)

### T.1.6 Freeze Protocol

**Preregistration Requirements**:
1. Hash of benchmark subset selection (before running)
2. Hash of GMI morphology predictions (before running)
3. Hash of baseline implementations (before running)
4. Hash of evaluation metrics (before running)

**Freeze Artifacts**:
```
research/gmi-grand-unification-v1/gmi-real-scale-transfer-v1/artifacts/t1-code-freeze/
  BENCHMARK_SELECTION_V1.json
  GMI_PREDICTIONS_V1.json
  BASELINE_CONFIGURATIONS_V1.json
  EVALUATION_PROTOCOL_V1.json
```

### T.1.7 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| Problem size (lines) | 1-10 | 10-1000 | 10-100x |
| Token count | 50-200 | 500-10K | 10-50x |
| Search space | 10^3 | 10^6-10^9 | 10^3-10^6x |
| D4 advantage | 2-5x over D1 | 1.5-3x over D1 | Moderate reduction |

**Scaling Prediction**: D4 advantage will diminish by 30-50% from tiny-world due to:
- Increased search space for symbolic verification
- Compositional complexity exceeding D4 capacity
- Emergence of D5/D6 advantages at scale

### T.1.8 Falsification

**Falsification Criteria**:
1. D1 (neural) outperforms D4 (symbolic) on function-level tasks → morphology prediction wrong
2. D5 (search) outperforms D4 on simple function-level tasks → phase boundary wrong
3. No morphology shows advantage → ecology mapping wrong
4. Advantage appears only in one benchmark → transfer claim weak

---

## T.2 Formal Theorem Proving

### T.2.1 Task Selection

| Benchmark | Prover | Domain | Scale |
|-----------|--------|--------|-------|
| Lean4 Mathlib | Lean 4 | Mathematics | ~300K lemmas |
| Isabelle/HOL | Isabelle | Mathematics | ~200K theorems |
| Coq | Coq | Mathematics | ~100K lemmas |
| miniF2F | Multi | Olympiad problems | 488 problems |
| ProofNet | Multi | Undergraduate math | 343 problems |
| LeanDojo | Lean 4 | Interactive proving | Variable |

### T.2.2 GMI Prediction

**Theorem Reference**: T-MPL-01 (Morphology Phase Law)

**Prediction**:
- Formal theorem proving requires **D4 (symbolic/program)** morphology as primary
- Search over proof tactics favors **D5 (search/frontier)** morphology
- Interactive proving with state tracking favors **D6 (dynamical-state)** morphology

### T.2.3 Ecology Mapping

| Coordinate | Automated Proving | Interactive Proving | Olympiad Problems |
|------------|-------------------|--------------------|--------------------|
| E (Environment) | Formal proof system | Formal proof system + hints | Formal proof system |
| R (Resource) | High: proof search | Medium: guided | Low: time-limited |
| V (Variation) | Low: tactic library | Medium: user strategies | High: novel techniques |
| H ( History) | None: from axioms | Long: proof state | Short: per problem |

### T.2.4 Morphology Prediction

| Task Type | Predicted Morphology | Confidence | Tiny-world Analog |
|-----------|---------------------|------------|-------------------|
| Tactic selection | D4 (symbolic) | Very High | Symbolic rewriting |
| Proof search | D5 (search) | High | Combinatorial search |
| Interactive proving | D4 + D6 (symbolic + dynamical) | Medium | Multi-step reasoning |

### T.2.5 Comparison Protocol

**Baselines**:
1. **D1 Baseline**: GPT-f (neural tactic prediction)
2. **D4 Baseline**: Lean + auto tactic (symbolic search)
3. **D5 Baseline**: AlphaZero-style proof search
4. **D6 Baseline**: LeanCop (neural + symbolic hybrid)

**Metrics**:
- Proof success rate
- Proof length (number of tactics)
- Time to proof
- Generalization to unseen theorems

### T.2.6 Freeze Protocol

**Preregistration Requirements**:
1. Hash of theorem subset selection
2. Hash of tactic library definition
3. Hash of morphology predictions
4. Hash of baseline configurations

### T.2.7 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| Proof depth | 1-5 tactics | 10-100 tactics | 10-20x |
| Tactic library size | 5-10 | 50-100 | 5-10x |
| Search space | 10^2 | 10^4-10^6 | 10^2-10^4x |
| D4 advantage | 3-10x over D1 | 2-5x over D1 | Moderate reduction |

### T.2.8 Falsification

**Falsification Criteria**:
1. D1 (neural) outperforms D4 on simple tactic selection → morphology prediction wrong
2. D5 outperforms D4 on proof search → phase boundary wrong
3. No morphology generalizes beyond training theorems → transfer claim weak

---

## T.3 Factual/Scientific Knowledge Tasks

### T.3.1 Task Selection

| Benchmark | Domain | Scale | Difficulty |
|-----------|--------|-------|------------|
| MMLU | Broad knowledge | 57 subjects, 14K questions | Medium |
| ARC (AI2) | Science reasoning | 7.7K questions | Medium |
| SciQ | Science | 13.7K questions | Medium |
| GPQA | Graduate-level science | 448 questions | Hard |
| ARC-Challenge | Science (hard subset) | 2.5K questions | Hard |
| TruthfulQA | Factual accuracy | 817 questions | Medium |

### T.3.2 GMI Prediction

**Theorem Reference**: T-CC-01 (Capability Contract)

**Prediction**:
- Factual recall favors **D2 (exemplar/memory-indexed)** morphology
- Scientific reasoning favors **D3 (probabilistic-belief)** morphology
- Multi-step scientific reasoning favors **D6 (dynamical-state)** morphology

### T.3.3 Ecology Mapping

| Coordinate | Factual Recall (MMLU) | Science Reasoning (ARC) | Graduate Science (GPQA) |
|------------|----------------------|------------------------|------------------------|
| E (Environment) | Static facts | Causal reasoning | Domain expertise |
| R (Resource) | Low: single retrieval | Medium: multi-step | High: deep reasoning |
| V (Variation) | Low: fixed facts | Medium: problem types | High: novel applications |
| H (History) | None: per question | Short: chain of reasoning | Long: background knowledge |

### T.3.4 Morphology Prediction

| Task Type | Predicted Morphology | Confidence | Tiny-world Analog |
|-----------|---------------------|------------|-------------------|
| Simple factual recall | D2 (memory) | Very High | Nearest-neighbor in tiny fact base |
| Multi-hop reasoning | D3 (probabilistic) | High | Bayesian inference in tiny graph |
| Scientific reasoning | D3 + D6 | Medium | Causal chain in tiny dynamics |

### T.3.5 Comparison Protocol

**Baselines**:
1. **D1 Baseline**: BERT/GPT retrieval (neural similarity)
2. **D2 Baseline**: kNN over knowledge base
3. **D3 Baseline**: Bayesian reasoning over facts
4. **D4 Baseline**: Symbolic rule application

**Metrics**:
- Accuracy (top-1, top-5)
- Calibration (expected calibration error)
- Sample efficiency (accuracy vs. number of facts)
- Reasoning depth (multi-hop accuracy)

### T.3.6 Freeze Protocol

**Preregistration Requirements**:
1. Hash of subject/topic selection
2. Hash of fact base construction
3. Hash of morphology predictions
4. Hash of evaluation protocol

### T.3.7 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| Fact base size | 10-100 | 10K-1M | 10^2-10^4x |
| Question complexity | 1-hop | 3-5 hops | 3-5x |
| D2 advantage | 2-5x over D1 | 1.2-2x over D1 | Significant reduction |
| D3 advantage | 3-10x over D1 | 1.5-3x over D1 | Moderate reduction |

### T.3.8 Falsification

**Falsification Criteria**:
1. D1 outperforms D2 on factual recall → memory morphology wrong
2. D4 outperforms D3 on scientific reasoning → probabilistic morphology wrong
3. No morphology handles knowledge updates → continual learning claim weak

---

## T.4 Continual-Changing Knowledge

### T.4.1 Task Selection

| Benchmark | Domain | Scale | Change Type |
|-----------|--------|-------|-------------|
| Split-MNIST | Vision | 10 tasks | Sequential classes |
| Permuted-MNIST | Vision | 10 tasks | Feature permutation |
| Split-CIFAR-10 | Vision | 5 tasks | Sequential classes |
| Split-CIFAR-100 | Vision | 20 tasks | Sequential classes |
| Continual Language Modeling | NLP | Variable | Distribution shift |
| Online Learning Benchmarks | Various | Variable | Streaming data |

### T.4.2 GMI Prediction

**Theorem Reference**: T-ECP-01 (Ecology-Coordinate Prediction)

**Prediction**:
- Continual learning with stable features favors **D2 (memory)** morphology with exemplar replay
- Continual learning with distribution shift favors **D3 (probabilistic)** morphology
- Continual learning with task relationships favors **D6 (dynamical)** morphology

### T.4.3 Ecology Mapping

| Coordinate | Class Incremental | Feature Incremental | Online Learning |
|------------|-------------------|--------------------|--------------------|
| E (Environment) | Discrete tasks | Continuous shift | Streaming |
| R (Resource) | Medium: replay buffer | High: adaptation | Low: single pass |
| V (Variation) | Low: same features | High: new features | Variable |
| H (History) | Long: all past tasks | Medium: recent | Short: window |

### T.4.4 Morphology Prediction

| Task Type | Predicted Morphology | Confidence | Tiny-world Analog |
|-----------|---------------------|------------|-------------------|
| Class incremental | D2 (memory) + replay | High | Exemplar storage in tiny memory |
| Feature incremental | D3 (probabilistic) | Medium | Bayesian adaptation |
| Online learning | D6 (dynamical) | Medium | Dynamic state tracking |

### T.4.5 Comparison Protocol

**Baselines**:
1. **D1 Baseline**: Fine-tuning (no replay)
2. **D2 Baseline**: Experience replay (naive)
3. **D3 Baseline**: Bayesian neural network
4. **D4 Baseline**: Task-specific symbolic rules

**Metrics**:
- Average accuracy across all tasks
- Forgetting measure (accuracy drop on old tasks)
- Forward transfer (accuracy on new tasks before training)
- Computational cost

### T.4.6 Freeze Protocol

**Preregistration Requirements**:
1. Hash of task sequence
2. Hash of replay buffer size
3. Hash of morphology predictions
4. Hash of evaluation protocol

### T.4.7 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| Number of tasks | 2-5 | 10-100 | 5-20x |
| Task complexity | 10 classes | 100-1000 classes | 10-100x |
| D2 advantage | 2-5x over D1 | 1.5-3x over D1 | Moderate reduction |

### T.4.8 Falsification

**Falsification Criteria**:
1. D1 (fine-tuning) outperforms D2 (memory) → memory morphology wrong
2. No morphology handles task interference → continual learning claim weak
3. Advantage disappears with more tasks → scaling claim wrong

---

## T.5 Multimodal Perception/Control

### T.5.1 Task Selection

| Benchmark | Domain | Scale | Modality |
|-----------|--------|-------|----------|
| Atari 57 | Game playing | 57 games | Visual-motor |
| DMLab | 3D navigation | 9 tasks | Visual-spatial |
| RoboSuite | Robotic manipulation | 18 tasks | Visual-motor-tactile |
| Meta-World | Robotic manipulation | 50 tasks | Visual-motor |
| Habitat | Visual navigation | Multiple | Visual-spatial |
| OpenAI Gym MuJoCo | Continuous control | Multiple | Proprioceptive-motor |

### T.5.2 GMI Prediction

**Theorem Reference**: T-MPL-01 (Morphology Phase Law)

**Prediction**:
- Perception-only tasks favor **D1 (coefficient/function-field)** morphology
- Perception-action coupling favors **D6 (dynamical-state)** morphology
- Multi-step planning in perception-action favors **D5 (search/frontier)** morphology

### T.5.3 Ecology Mapping

| Coordinate | Atari (Discrete) | DMLab (3D) | RoboSuite (Manipulation) |
|------------|-----------------|------------|-------------------------|
| E (Environment) | 2D discrete | 3D continuous | 3D continuous + contact |
| R (Resource) | Low: image | Medium: 3D scan | High: multi-sensor |
| V (Variation) | Medium: game variety | High: level variety | High: object variety |
| H (History) | Short: episodic | Medium: navigation | Long: task sequence |

### T.5.4 Morphology Prediction

| Task Type | Predicted Morphology | Confidence | Tiny-world Analog |
|-----------|---------------------|------------|-------------------|
| Discrete control | D1 (neural) | High | Function approximation in tiny MDP |
| Continuous control | D6 (dynamical) | High | Dynamic system in tiny environment |
| Multi-step manipulation | D5 (search) + D6 | Medium | Search in tiny action space |

### T.5.5 Comparison Protocol

**Baselines**:
1. **D1 Baseline**: DQN/PPO (neural policy)
2. **D5 Baseline**: MCTS (search-based)
3. **D6 Baseline**: Model-based RL (dynamic model)

**Metrics**:
- Average return
- Sample efficiency (return vs. environment steps)
- Computational cost (training time, inference time)
- Generalization to unseen levels/objects

### T.5.6 Freeze Protocol

**Preregistration Requirements**:
1. Hash of game/task selection
2. Hash of hyperparameters
3. Hash of morphology predictions
4. Hash of evaluation protocol

### T.5.7 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| State dimension | 10-50 | 100-10000 | 10-200x |
| Action dimension | 1-4 | 4-20 | 4-5x |
| D6 advantage | 2-5x over D1 | 1.3-2.5x over D1 | Moderate reduction |

### T.5.8 Falsification

**Falsification Criteria**:
1. D1 outperforms D6 on continuous control → dynamical morphology wrong
2. D5 outperforms D6 on multi-step tasks → search morphology wrong
3. No morphology generalizes across games → ecology mapping wrong

---

## T.6 Long-Horizon Planning/Control

### T.6.1 Task Selection

| Benchmark | Domain | Scale | Horizon |
|-----------|--------|-------|---------|
| Game of 20 Questions | Information gathering | 1M+ concepts | 20 questions |
| Planning Bench | Classical planning | Variable | 10-1000 steps |
| MiniGrid | Grid-world navigation | Variable | 10-500 steps |
| Sokoban | Puzzle solving | Variable | 10-1000 steps |
| Blocksworld | Planning | Variable | 10-100 steps |
| Logistics | Planning | Variable | 10-100 steps |

### T.6.2 GMI Prediction

**Theorem Reference**: T-CC-01 (Capability Contract)

**Prediction**:
- Short-horizon planning favors **D4 (symbolic)** morphology
- Long-horizon planning favors **D5 (search/frontier)** morphology
- Planning with uncertainty favors **D3 (probabilistic)** morphology

### T.6.3 Ecology Mapping

| Coordinate | Short-horizon (<20) | Medium (20-100) | Long-horizon (>100) |
|------------|---------------------|-----------------|---------------------|
| E (Environment) | Deterministic | Partially observable | Stochastic |
| R (Resource) | Low: few steps | Medium: moderate | High: many steps |
| V (Variation) | Low: fixed goals | Medium: variable goals | High: adaptive goals |
| H ( History) | None: fresh | Short: recent | Long: full trajectory |

### T.6.4 Morphology Prediction

| Task Type | Predicted Morphology | Confidence | Tiny-world Analog |
|-----------|---------------------|------------|-------------------|
| Short deterministic | D4 (symbolic) | Very High | Symbolic planning in tiny world |
| Long deterministic | D5 (search) | High | Search in tiny graph |
| Uncertain | D3 (probabilistic) | Medium | Bayesian planning |

### T.6.5 Comparison Protocol

**Baselines**:
1. **D3 Baseline**: POMCP (probabilistic search)
2. **D4 Baseline**: Fast Downward (symbolic planner)
3. **D5 Baseline**: MCTS (search-based)
4. **D6 Baseline**: Model-based RL

**Metrics**:
- Success rate
- Plan length (optimality)
- Planning time
- Generalization to new problem instances

### T.6.6 Freeze Protocol

**Preregistration Requirements**:
1. Hash of problem selection
2. Hash of horizon cutoff
3. Hash of morphology predictions
4. Hash of evaluation protocol

### T.6.7 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| Problem size | 3-5 objects | 10-100 objects | 2-20x |
| Plan length | 2-5 steps | 20-100 steps | 10-20x |
| D5 advantage | 2-10x over D4 | 1.5-5x over D4 | Moderate reduction |

### T.6.8 Falsification

**Falsification Criteria**:
1. D4 outperforms D5 on long-horizon planning → search morphology wrong
2. D3 outperforms D5 on uncertain planning → probabilistic morphology wrong
3. Advantage disappears with horizon → scaling claim wrong

---

## T.7 Tool-Use/Solver-Routing Tasks

### T.7.1 Task Selection

| Benchmark | Domain | Scale | Tool Type |
|-----------|--------|-------|-----------|
| ToolBench | API usage | 16K+ tasks | API calls |
| API-Bank | API usage | 735 tasks | API calls |
| Sudoku | Constraint solving | Variable | Constraint solver |
| MATH | Mathematical reasoning | 12.5K problems | Calculator/symbolic |
| HotPotQA | Multi-hop QA | 113K questions | Search/retrieval |
| MUSER | Tool use for math | Variable | Multiple tools |

### T.7.2 GMI Prediction

**Theorem Reference**: T-MPL-01 (Morphology Phase Law)

**Prediction**:
- Tool selection favors **D3 (probabilistic)** morphology (belief over tool efficacy)
- Tool sequencing favors **D4 (symbolic)** morphology (rule-based sequencing)
- Complex tool chains favor **D5 (search/frontier)** morphology (search over tool plans)

### T.7.3 Ecology Mapping

| Coordinate | Single-tool | Multi-tool | Complex chains |
|------------|-------------|------------|----------------|
| E (Environment) | Deterministic output | Compositional | Conditional |
| R (Resource) | Low: one call | Medium: few calls | High: many calls |
| V (Variation) | Low: fixed tools | Medium: tool selection | High: tool composition |
| H (History) | None | Short: recent results | Long: full chain |

### T.7.4 Morphology Prediction

| Task Type | Predicted Morphology | Confidence | Tiny-world Analog |
|-----------|---------------------|------------|-------------------|
| Tool selection | D3 (probabilistic) | High | Bayesian selection |
| Tool sequencing | D4 (symbolic) | High | Rule-based sequencing |
| Complex planning | D5 (search) | Medium | Search in tool graph |

### T.7.5 Comparison Protocol

**Baselines**:
1. **D1 Baseline**: LLM with tool descriptions (neural)
2. **D3 Baseline**: Bayesian tool selection
3. **D4 Baseline**: Rule-based tool sequencing
4. **D5 Baseline**: MCTS over tool plans

**Metrics**:
- Task success rate
- Tool call efficiency (calls per success)
- Planning time
- Generalization to new tool combinations

### T.7.6 Freeze Protocol

**Preregistration Requirements**:
1. Hash of tool set definition
2. Hash of task selection
3. Hash of morphology predictions
4. Hash of evaluation protocol

### T.7.7 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| Tool count | 3-5 | 10-50 | 2-10x |
| Chain length | 1-3 | 3-20 | 3-7x |
| D5 advantage | 2-5x over D4 | 1.3-2.5x over D4 | Moderate reduction |

### T.7.8 Falsification

**Falsification Criteria**:
1. D4 outperforms D5 on complex tool chains → search morphology wrong
2. D1 outperforms D3 on tool selection → probabilistic morphology wrong
3. No morphology handles tool failure → robustness claim weak

---

## T.8 Multi-Agent/Social Tasks

### T.8.1 Task Selection

| Benchmark | Domain | Scale | Agents |
|-----------|--------|-------|--------|
| Melting Pot | Social dilemmas | 25+ scenarios | 2-8 |
| Hanabi | Cooperative card game | Variable | 2-5 |
| Negotiation datasets | Bargaining | Variable | 2 |
| Sockeye | Dialogue | Variable | 2 |
| Overcooked | Cooperative cooking | Variable | 2-4 |
| Predator-Prey | Competitive pursuit | Variable | 4+ |

### T.8.2 GMI Prediction

**Theorem Reference**: T-ECP-01 (Ecology-Coordinate Prediction)

**Prediction**:
- Two-agent cooperation favors **D3 (probabilistic)** morphology (belief about partner)
- Multi-agent coordination favors **D7 (collective/distributed)** morphology
- Competitive interaction favors **D5 (search/frontier)** morphology (game tree search)

### T.8.3 Ecology Mapping

| Coordinate | Two-agent | Multi-agent | Competitive |
|------------|-----------|-------------|-------------|
| E (Environment) | Shared | Distributed | Adversarial |
| R (Resource) | Medium: communication | High: coordination | Low: independent |
| V (Variation) | Low: partner fixed | High: partner variety | High: opponent variety |
| H (History) | Medium: partner history | Long: group history | Short: per round |

### T.8.4 Morphology Prediction

| Task Type | Predicted Morphology | Confidence | Tiny-world Analog |
|-----------|---------------------|------------|-------------------|
| Cooperation | D3 (probabilistic) | High | Bayesian partner model |
| Coordination | D7 (collective) | Medium | Distributed consensus |
| Competition | D5 (search) | Medium | Game tree search |

### T.8.5 Comparison Protocol

**Baselines**:
1. **D1 Baseline**: Independent learners
2. **D3 Baseline**: Bayesian opponent modeling
3. **D5 Baseline**: Game-theoretic search
4. **D7 Baseline**: Communication-based coordination

**Metrics**:
- Collective reward
- Fairness (reward distribution)
- Communication efficiency
- Generalization to new partners

### T.8.6 Freeze Protocol

**Preregistration Requirements**:
1. Hash of scenario selection
2. Hash of agent count
3. Hash of morphology predictions
4. Hash of evaluation protocol

### T.8.7 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| Agent count | 2-3 | 4-10 | 2-5x |
| Interaction rounds | 10-20 | 100-1000 | 10-50x |
| D7 advantage | 2-5x over D3 | 1.3-2.5x over D3 | Moderate reduction |

### T.8.8 Falsification

**Falsification Criteria**:
1. D3 outperforms D7 on multi-agent coordination → collective morphology wrong
2. D1 outperforms D3 on cooperation → probabilistic morphology wrong
3. No morphology handles partner variability → social cognition claim weak

---

## T.9 Cross-Domain Transfer

### T.9.1 Protocol Design

**Transfer Definition**: Train on domain A, test on domain B with same ecology coordinates.

**Ecology Coordinate Matching**:
- Same E (environment type): e.g., both are games, both are text
- Same R (resource): e.g., similar compute budget
- Different V (variation): different specific tasks
- Different H (history): different task histories

### T.9.2 Transfer Pairs

| Source Domain | Target Domain | Shared Coordinates | Different Coordinates |
|---------------|---------------|-------------------|----------------------|
| HumanEval (code) | MBPP (code) | E: deterministic I/O | V: different problems |
| Atari (game) | DMLab (navigation) | E: visual-motor | R: 2D vs 3D |
| MMLU (factual) | GPQA (scientific) | R: single query | V: difficulty |
| MiniGrid (navigation) | Sokoban (puzzle) | E: grid-world | V: objective |

### T.9.3 GMI Prediction

**Theorem Reference**: T-CC-01 (Capability Contract)

**Prediction**:
- Positive transfer when source and target share morphology
- Negative transfer when source and target require different morphologies
- Transfer magnitude depends on ecology coordinate overlap

### T.9.4 Comparison Protocol

**Baselines**:
1. **No-transfer**: Train and test on target domain only
2. **Full transfer**: Train on source, test on target
3. **Partial transfer**: Fine-tune source model on target data

**Metrics**:
- Transfer benefit: (target accuracy with transfer) - (target accuracy without)
- Negative transfer: cases where transfer hurts
- Sample efficiency: target accuracy vs. target data size

### T.9.5 Freeze Protocol

**Preregistration Requirements**:
1. Hash of source-target pairs
2. Hash of training protocol
3. Hash of morphology predictions
4. Hash of evaluation protocol

### T.9.6 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| Source data size | 100-1K | 10K-1M | 10-1000x |
| Target data size | 10-100 | 1K-100K | 100-1000x |
| Transfer benefit | 2-10x | 1.2-3x | Significant reduction |

### T.9.7 Falsification

**Falsification Criteria**:
1. Negative transfer appears where positive was predicted → morphology prediction wrong
2. No transfer benefit in any pair → transfer claim weak
3. Transfer depends on specific tasks, not ecology coordinates → coordinate mapping wrong

---

## T.10 Strongest-Parent Baselines

### T.10.1 Protocol Design

**Strongest-Parent Definition**: For each task category, identify the strongest baseline from existing literature and compare GMI-predicted morphology against it.

### T.10.2 Baseline Selection

| Task Category | Strongest Parent | Reference | Metric |
|---------------|------------------|-----------|--------|
| Code generation | GPT-4/Codex | OpenAI 2023 | HumanEval pass@1 |
| Theorem proving | AlphaProof | DeepMind 2024 | miniF2F accuracy |
| Factual knowledge | GPT-4 | OpenAI 2023 | MMLU accuracy |
| Continual learning | DER++ | Buzzega et al. 2020 | Split-CIFAR-100 avg acc |
| Multimodal control | DreamerV3 | Hafner et al. 2023 | Atari 100K return |
| Long-horizon planning | AlphaZero | Silver et al. 2017 | Go/Chess rating |
| Tool use | Toolformer | Schick et al. 2023 | API task success |
| Multi-agent | MAPPO | Yu et al. 2022 | StarCraft win rate |

### T.10.3 GMI Prediction

**Theorem Reference**: T-CC-01 (Capability Contract)

**Prediction**:
- GMI-predicted morphology will match or exceed strongest parent when:
  - Task ecology matches predicted morphology's capability region
  - Task complexity is within morphology's capacity bounds
- GMI-predicted morphology will underperform when:
  - Task exceeds morphology's capability bounds
  - Strongest parent is specifically optimized for the task

### T.10.4 Comparison Protocol

**Method**:
1. Run GMI-predicted morphology on each task category
2. Compare to strongest parent baseline
3. Measure performance, compute cost, and sample efficiency
4. Attribute gaps to specific capability differences

**Metrics**:
- Performance gap: (morphology score) - (strongest parent score)
- Cost ratio: (morphology cost) / (strongest parent cost)
- Efficiency ratio: (morphology score per unit cost) / (parent score per unit cost)

### T.10.5 Freeze Protocol

**Preregistration Requirements**:
1. Hash of baseline implementations
2. Hash of GMI morphology implementations
3. Hash of comparison metrics
4. Hash of evaluation protocol

### T.10.6 Scaling Protocol

| Metric | Tiny-world Value | Real-scale Prediction | Transfer Ratio |
|--------|------------------|----------------------|----------------|
| Task difficulty | Easy | Hard | 10-100x |
| Parent optimization | Generic | Task-specific | Variable |
| GMI advantage | 2-10x over parent | 0.8-2x over parent | Significant reduction |

### T.10.7 Falsification

**Falsification Criteria**:
1. Strongest parent outperforms GMI morphology on all tasks → morphology prediction wrong
2. GMI advantage only on easy tasks → capability contract wrong
3. Advantage disappears with task specificity → transfer claim weak

---

## T.11 Frozen Predictions Before Runs

### T.11.1 Preregistration Protocol

**Freeze Requirements**:
1. **Benchmark Selection**: Hash of which benchmarks/tasks to use
2. **Morphology Predictions**: Hash of predicted morphology for each task
3. **Ecology Mapping**: Hash of coordinate assignments
4. **Baseline Configurations**: Hash of baseline implementations
5. **Evaluation Metrics**: Hash of metrics and thresholds
6. **Falsification Criteria**: Hash of what would falsify each claim

**Freeze Artifacts**:
```
research/gmi-grand-unification-v1/gmi-real-scale-transfer-v1/artifacts/
  PREREGISTRATION_V1.json
  PREREGISTRATION_V1.sha256
  FREEZE_LOG_V1.json
```

### T.11.2 Tamper-Evidence

**Method**:
1. Compute SHA-256 hash of each freeze document
2. Store hash in tamper-evident log (e.g., git commit, blockchain, or signed document)
3. After experiments, verify hash matches pre-experiment freeze
4. Any mismatch invalidates the experiment

### T.11.3 Publication Protocol

**Before Experiments**:
1. Publish preregistration document
2. Record freeze hash in public registry
3. Share hash with independent auditor

**After Experiments**:
1. Publish results alongside preregistration
2. Verify hash matches
3. Report any deviations from preregistration

---

## T.12 Scaling-Law Comparison

### T.12.1 Protocol Design

**Goal**: Compare tiny-world morphology phase predictions against real-scale task performance to determine scaling relationships.

### T.12.2 Scaling Dimensions

| Dimension | Tiny-world Range | Real-scale Range | Scaling Factor |
|-----------|------------------|------------------|----------------|
| Problem size | 1-10 | 100-10,000 | 10-1,000x |
| Vocabulary size | 10-100 | 10K-1M | 100-10,000x |
| Action space | 2-10 | 100-10,000 | 10-1,000x |
| Time horizon | 1-5 | 100-1,000 | 20-200x |

### T.12.3 GMI Scaling Prediction

**Theorem Reference**: T-CC-01 (Capability Contract)

**Prediction**:
- Morphology phase boundaries are preserved across scales
- Absolute performance advantages diminish by factor of 1.5-3x
- Phase transition locations shift by < 20% in ecology coordinates

### T.12.4 Measurement Protocol

**For Each Task Category**:
1. Run tiny-world experiments (existing data)
2. Run real-scale experiments (new data)
3. Plot performance vs. scale dimension
4. Fit scaling law: performance(scale) = a * scale^b + c
5. Compare scaling exponents across morphologies

### T.12.5 Freeze Protocol

**Preregistration Requirements**:
1. Hash of scale dimension choices
2. Hash of scaling law functional form
3. Hash of tiny-world results (for comparison)
4. Hash of evaluation protocol

### T.12.6 Falsification

**Falsification Criteria**:
1. Phase boundaries shift by > 50% in ecology coordinates → morphology prediction wrong
2. Scaling exponents differ by > 2x across morphologies → capability contract wrong
3. No consistent scaling relationship → transfer claim weak

---

## T.13 Implementation Roadmap

### Phase 1: Freeze (Week 1-2)

1. Finalize benchmark selection for all 10 categories
2. Implement ecology coordinate mapping for each benchmark
3. Compute morphology predictions for each benchmark
4. Freeze all predictions in tamper-evident log
5. Publish preregistration document

### Phase 2: Tiny-world Baseline (Week 3-4)

1. Compile existing tiny-world experiment results
2. Verify morphology phase boundaries
3. Compute tiny-world performance metrics
4. Document scaling relationships

### Phase 3: Real-scale Experiments (Week 5-10)

1. Implement GMI morphology architectures for each task
2. Run experiments on all 10 benchmark categories
3. Collect performance metrics
4. Document computational costs

### Phase 4: Comparison and Analysis (Week 11-12)

1. Compare real-scale results to frozen predictions
2. Analyze scaling relationships
3. Identify transfer successes and failures
4. Document falsification results

### Phase 5: Publication (Week 13-14)

1. Write transfer analysis report
2. Publish results with preregistration
3. Submit to appropriate venue
4. Archive all artifacts

---

## T.14 Quality Gates

### Gate 1: Freeze Integrity

- [ ] All predictions frozen before experiments
- [ ] Hash verification passes
- [ ] Preregistration published

### Gate 2: Benchmark Coverage

- [ ] All 10 categories have at least 2 benchmarks
- [ ] Benchmarks span difficulty range
- [ ] Benchmarks have established baselines

### Gate 3: Prediction Specificity

- [ ] Each prediction cites specific theorem
- [ ] Each prediction specifies confidence level
- [ ] Each prediction includes falsification criteria

### Gate 4: Comparison Rigor

- [ ] Baselines are strongest existing methods
- [ ] Metrics are standard for each category
- [ ] Statistical tests are appropriate

### Gate 5: Scaling Analysis

- [ ] At least 3 scale points per category
- [ ] Scaling laws are fitted with R^2 > 0.8
- [ ] Phase boundary shifts are quantified

---

## T.15 References

### GMI Theory

- T-MPL-01: Morphology Phase Law (Theorem derivation in `gmi-morphology-phase-rv-v1/`)
- T-ECP-01: Ecology-Coordinate Prediction (Theorem derivation in `gmi-capability-contract-v1/`)
- T-CC-01: Capability Contract (Theorem derivation in `gmi-capability-contract-v1/`)
- T-RLL-01: Resource Lifecycle Ledger (Theorem derivation in `gmi-resource-lifecycle-ledger-v1/`)

### Existing Artifacts

- `gmi-morphology-phase-rv-v1/`: Phase law theorems and proofs
- `gmi-capability-contract-v1/`: 27-row capability contract
- `gmi-metrics-runtime-v1/`: 11 metrics coordinates
- `gmi-resource-lifecycle-ledger-v1/`: 14 resource coordinates

### Related Protocols

- `gmi-domain-gates-v1/NEW_DOMAIN_CLAIM_GATE_AND_UNSEEN_FORMS_V1.md`: J4/K protocols
- `gmi-natural-intelligence-stress-test-v1/`: Natural intelligence comparison

---

**Protocol Version**: V1  
**Last Updated**: 2026-09-15  
**Status**: Ready for execution
