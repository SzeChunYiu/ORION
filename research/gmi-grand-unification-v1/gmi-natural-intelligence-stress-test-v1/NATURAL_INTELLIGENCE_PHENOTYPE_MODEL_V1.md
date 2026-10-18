# Natural Intelligence Phenotype Model and Cross-Species Predictions

**Issue**: #602 L1-L2
**Status**: V1 (Prospectively Frozen)
**Created**: 2026-09-15

---

## Scope

This document applies the GMI morphology phase law `E + R + V -> M*` (from `research/gmi-grand-unification-v1/gmi-morphology-phase-rv-v1/MORPHOLOGY_PHASE_RV_THEOREM_V1.md`) to animal cognitive phenotypes. It formalises ecological, resource, and developmental parameters as GMI-native coordinates, then derives specific cognitive architecture predictions for each species class.

**Explicit exclusions**: No neuroanatomy claims. No claims about neural substrate. No human-specific terminology applied as universal. All predictions derive from the same phase law with species-specific parameter values.

**Coordinate sources**: 16 ecology coordinates from `gmi-ecology-extension-v1/`, 11 metrics coordinates from `gmi-metrics-runtime-v1/`, biology predictions from `gmi-biology-predictions-v1/BIOLOGY_PREDICTIONS_THEOREM_V1.md`.

---

## L1. Animal Cognitive Phenotype Model

### L1.1 Body/Sensor/Actuator Resource Descriptors

Map physical organism properties to GMI resource coordinates (R).

| Resource Coordinate | GMI Definition | Biological Referent |
|---------------------|----------------|---------------------|
| `R_acquisition` | Budget for acquiring new information per unit time | Metabolic rate allocated to sensory processing; number and diversity of sensor types |
| `R_observation` | Bandwidth of information channels from environment to agent | Sensor resolution, number of independent channels (vision, audition, olfaction, mechanoreception, electroreception) |
| `R_action_cost` | Cost per unit of environmental manipulation | Energy per action, mechanical advantage of actuators, number of independent degrees of freedom |
| `R_action_bandwidth` | Speed and parallelism of actuator output | Limb count, fine motor resolution, simultaneous action channels |
| `R_latency` | Minimum time between observation and action | Neural conduction speed, body size, sensorimotor loop length |
| `R_memory_base` | Storage capacity for internal state | Brain/body mass ratio as proxy for available computational substrate |
| `R_energy_rate` | Metabolic budget per unit time | Basal metabolic rate; constraints on sustained computation |

### L1.2 Ecological Niche Descriptors

Map environmental properties to GMI ecology coordinates (E).

| Ecology Coordinate | GMI Definition | Biological Referent |
|--------------------|----------------|---------------------|
| `E_task_distribution` | Distribution over task types the agent must solve | Prey type diversity, habitat heterogeneity, seasonal variation |
| `E_horizon` | Typical temporal depth of consequential decisions | Time between cause and effect in foraging/predation/avoidance; seasonal planning horizon |
| `E_recurrence` | Rate at which the same task structure reappears | Territory fidelity, home range stability, seasonal return to same patches |
| `E_drift` | Rate of change in task structure over time | Habitat stability, prey population dynamics, climate variability |
| `E_noise` | Observation uncertainty per channel | Predator/prey stealth, environmental obscuration (forest density, water turbidity) |
| `E_multi_agent` | Number of other agents affecting outcomes | Group size, predator density, competitor density |
| `E_resource_spatial` | Spatial structure of resource distribution | Patchiness, predictability of resource locations |
| `E_resource_temporal` | Temporal structure of resource availability | Seasonality, diurnal patterns, boom-bust cycles |
| `E_predation_pressure` | Risk from other agents | Predator density, escape difficulty, vigilance cost |
| `E_competition_intensity` | Degree of resource competition | Conspecific density, diet overlap, territoriality |
| `E_tool_opportunity` | Availability of environmental objects usable as tools | Material availability (sticks, stones, water), structural complexity of environment |
| `E_social_complexity` | Complexity of social dynamics | Alliance formation, deception, reputation tracking needs |
| `E_niche_width` | Breadth of ecological roles the species occupies | Generalist vs specialist; dietary breadth, habitat range |
| `E_environmental_volatility` | Rate of catastrophic environmental change | Disaster frequency, habitat destruction rate |
| `E_information_asymmetry` | Degree to which agents have private information | Concealed strategies, hidden caches, private knowledge |
| `E_developmental_window` | Duration of protected learning period relative to lifespan | Juvenile dependency, parental investment duration |

### L1.3 Lifespan/Developmental-Timescale Descriptors

Map life history properties to GMI development coordinates (D).

| Development Coordinate | GMI Definition | Biological Referent |
|------------------------|----------------|---------------------|
| `D_budget_accumulation_rate` | Rate at which the agent can increase its resource budget through learning | Speed of skill acquisition; brain maturation rate |
| `D_protected_splits` | Number of budget-increasing actions possible before the budget must sustain the agent | Juvenile learning period duration; number of protected learning episodes |
| `D_retention_window` | Duration over which past observations remain accessible | Lifespan; memory decay rate; whether long-term storage is possible |
| `D_intergenerational_transfer` | Degree to which budget can be transferred across agents | Cultural transmission, teaching, vertical vs horizontal transmission |
| `D_plasticity` | Extent to which cognitive architecture can be reconfigured after maturity | Adult neuroplasticity, behavioral flexibility in mature individuals |
| `D_generations_to_optimize` | Number of generations over which natural selection optimizes the species' cognitive architecture | Evolutionary timescale; mutation rate; generation time |

### L1.4 Social-Structure Descriptors

Map social topology properties to GMI social coordinates (S).

| Social Coordinate | GMI Definition | Biological Referent |
|-------------------|----------------|---------------------|
| `S_agent_count` | Number of agents in the social group | Group size; colony size; flock size |
| `S_information_sharing_topology` | Structure of information flow between agents | Network topology: star, ring, all-to-all, hierarchical |
| `S_cooperation_vs_opposition` | Degree to which agents share goals vs compete | Cooperative breeding, mutual grooming, shared defense vs intraspecific competition |
| `S_role_specialization` | Degree to which agents perform different functions | Division of labor, caste systems, age-based roles |
| `S_partner_model_depth` | Depth of modeling required for other agents | Theory of mind requirements: reflexive vs recursive (I think that you think...) |
| `S_deception_frequency` | Rate at which agents benefit from misleading others | Tactical deception, competitive foraging, predator avoidance via false signals |
| `S_reputation_system` | Whether agents track others' past behavior | Reciprocal altruism, punishment of defectors, alliance tracking |

---

## L1.5 Predicted Memory Profile

**Derivation source**: Retention cost under the species' ecology (E coordinates) and resource budget (R coordinates). From the phase law: memory architecture = f(E_task_distribution, E_recurrence, E_drift, R_memory_base, R_energy_rate).

The cost of retaining a memory scales with: storage budget (R_memory_base) / (task recurrence rate (E_recurrence) * energy cost of retrieval (R_energy_rate)). High recurrence and low storage cost favor broad retention. High drift penalizes retention of stale information.

| Species Class | Working Memory | Episodic Memory | Semantic Memory | Procedural Memory | Reasoning |
|---------------|----------------|-----------------|-----------------|-------------------|-----------|
| **Primate (high R, high V)** | Large capacity, flexible manipulation | Rich episodic with temporal context | Abstract relational categories | Hierarchical action sequences | Long retention window + low drift = rich episodic + semantic |
| **Corvid (medium R, medium V)** | Moderate capacity | Strong episodic-like (cache locations, who was watching) | Concrete relational categories | Tool-use sequences | Medium retention + tool ecology = episodic for spatial-social |
| **Rodent (low R, low V)** | Small capacity | Weak episodic; strong spatial | Stimulus-response associations | Habit-based sequences | Short retention + high recurrence = procedural dominant |
| **Cephalopod (low R due to short lifespan, high V)** | Small capacity, fast update | Rapid learning, weak long-term | Concrete categories | Motor skill learning | Short lifespan = no retention investment; all learning fast-and-forget |
| **Social insect (very low per-individual R, colony V)** | Minimal (pheromone-mediated) | None individually | Colony-level caste rules | Fixed action patterns | No individual retention; colony-level storage via pheromone trails |
| **Canid (medium R, medium V)** | Moderate capacity | Social episodic (who, where, status) | Social categories + object categories | Cooperative action sequences | Social topology + cooperative ecology = social episodic emphasis |

### L1.6 Predicted Attention Profile

**Derivation source**: Routing regime from observation bandwidth (R_observation) vs task complexity (E_task_distribution). From the phase law: attention = f(R_observation, E_task_distribution, E_multi_agent, E_predation_pressure).

When observation bandwidth is low relative to task complexity, the agent must route attention (dynamic allocation). When bandwidth is high relative to complexity, fixed parallel monitoring suffices.

| Species Class | Routing Regime | Predicted Attention Pattern | Derivation |
|---------------|----------------|---------------------------|------------|
| **Primate** | Dynamic routing with top-down modulation | Selective attention, task-switching, inhibitory control | High R_observation but very high E_task_distribution => dynamic routing needed |
| **Corvid** | Dynamic routing, spatial focus | Gaze-shift based, spatial indexing | Medium R_observation, tool ecology => focused spatial attention |
| **Rodent** | Fixed parallel monitoring | Whisking + olfactory sweep, low selectivity | Low R_observation, low E_task_distribution => fixed monitoring sufficient |
| **Cephalopod** | Rapid dynamic routing | Chromatophore-mediated body-level attention; distributed sensing | Low R (short lifespan), high V => fast reconfigurable attention |
| **Social insect** | Reflexive routing | Pheromone-gradient following, no flexible allocation | Minimal R => no flexible attention; all reflexive |
| **Canid** | Dynamic routing with social modulation | Social gaze following, scent-based tracking | Medium R + social topology => social attention modulation |

### L1.7 Predicted Planning Profile

**Derivation source**: Planning horizon from action cost (R_action_cost) vs task structure (E_horizon, E_task_distribution). From the phase law: planning = f(R_action_cost, E_horizon, E_task_distribution, D_budget_accumulation_rate).

High action cost favors planning (each action is expensive, so plan before acting). Long horizon rewards deep planning. Short horizon + low action cost => reactive sufficiency.

| Species Class | Planning Horizon | Predicted Planning Depth | Derivation |
|---------------|------------------|-------------------------|------------|
| **Primate** | Long (seasonal to multi-year) | Multi-step, hierarchical planning | High R_action_cost + long E_horizon + long D => deep planning is worth the computation |
| **Corvid** | Medium (cache planning, tool sequences) | Sequential planning, 2-3 steps | Medium R_action_cost + tool ecology => moderate planning |
| **Rodent** | Short (immediate to days) | Simple sequential, habit-based | Low R_action_cost + short E_horizon => reactive + habit sufficient |
| **Cephalopod** | Short-medium (hours to days) | Flexible but shallow | Low R (short lifespan) => no long planning investment; high V => flexible short planning |
| **Social insect** | None individually; colony-level | Fixed action sequences, no individual planning | Zero individual R => zero individual planning |
| **Canid** | Medium (hunt planning, social coordination) | Cooperative planning, moderate depth | Medium R + cooperative ecology + social topology => cooperative planning |

### L1.8 Predicted Exploration Profile

**Derivation source**: Exploration regime from information-acquisition budget (R_acquisition) vs environment volatility (E_environmental_volatility, E_drift). From the phase law: exploration = f(R_acquisition, E_environmental_volatility, E_recurrence, E_drift).

High acquisition budget + high volatility => broad exploration. Low budget + stable environment => exploitation dominant.

| Species Class | Exploration Regime | Predicted Pattern | Derivation |
|---------------|-------------------|-------------------|------------|
| **Primate** | Broad exploration with exploitation | Cultural innovation, social learning of novel foraging | High R_acquisition + medium E_drift => explore-but-learn |
| **Corvid** | Moderate exploration | Cache diversification, new tool discovery | Medium R_acquisition + tool ecology => targeted exploration |
| **Rodent** | Narrow exploration | Thigmotaxis, known-path exploitation | Low R_acquisition + high E_recurrence => exploit known paths |
| **Cephalopod** | Broad but rapid exploration | Rapid environmental sampling, immediate novelty-seeking | Low R (lifespan) but high V => explore fast, forget fast |
| **Social insect** | Colony-level exploration | Scout bees, recruitment-based exploration | Zero individual R; colony-level R => scout-cast exploration |
| **Canid** | Moderate exploration | Scent-marking, territory patrolling | Medium R_acquisition + cooperative ecology => moderate exploration |

### L1.9 Predicted Causal/Tool-Use Profile

**Derivation source**: Causal cognition from interaction cost (R_action_cost) vs environment structure (E_tool_opportunity, E_resource_spatial). From the phase law: causal/tool = f(R_action_cost, E_tool_opportunity, E_resource_spatial, R_action_bandwidth).

High interaction cost + available tools => causal reasoning evolves to reduce action cost. No tool opportunity => no causal cognition pressure.

| Species Class | Causal Cognition Level | Predicted Tool Use | Derivation |
|---------------|----------------------|-------------------|------------|
| **Primate** | High: causal reasoning about object relations | Multiple tool types, tool modification, tool-to-tool use | High R_action_cost + high E_tool_opportunity => strong causal pressure |
| **Corvid** | Medium-high: causal reasoning about physical mechanisms | Tool manufacture (hook bending), compound tools | Medium R_action_cost + tool ecology => moderate-high causal |
| **Rodent** | Low: associative causal reasoning | Simple manipulation, no tool use | Low R_action_cost + low E_tool_opportunity => minimal causal pressure |
| **Cephalopod** | Medium: physical causal reasoning | Object manipulation, jar opening, ambush tactics | Low R but high V + high E_tool_opportunity => medium causal |
| **Social insect** | None individually | No tool use | Zero individual R => zero individual causal cognition |
| **Canid** | Low-medium: social causal reasoning | No tool use, but social manipulation | Medium R + social topology => social causal, not physical causal |

### L1.10 Predicted Social-Cognition Profile

**Derivation source**: Partner model depth from social topology (S_agent_count, S_information_sharing_topology, S_partner_model_depth) + information asymmetry (E_information_asymmetry). From the phase law: social cognition = f(S_agent_count, S_partner_model_depth, E_information_asymmetry, S_deception_frequency).

More agents + more deception + more information asymmetry => deeper partner models needed.

| Species Class | Social Cognition Depth | Predicted Social Model | Derivation |
|---------------|----------------------|----------------------|------------|
| **Primate** | Deep: recursive theory of mind (I think you think I think...) | Multiple mental state attribution, deception detection, alliance tracking | High S_agent_count + high S_deception_frequency + high E_information_asymmetry |
| **Corvid** | Medium-deep: perspective-taking, tactical deception | Who-watching models, cache protection strategies | Medium S_agent_count + S_deception_frequency + E_information_asymmetry |
| **Rodent** | Shallow: basic social recognition | Individual recognition, dominance status | Low S_agent_count + low E_information_asymmetry |
| **Cephalopod** | Shallow: minimal social cognition | Individual recognition only | Solitary ecology => minimal social cognition pressure |
| **Social insect** | None individually; colony-level | Pheromone-mediated collective behavior | No individual social cognition; colony-level emergent |
| **Canid** | Medium: perspective-taking, cooperative intention | Social rank tracking, cooperative goal inference | Medium S_agent_count + cooperative ecology + S_cooperation_vs_opposition |

### L1.11 Predicted Learning Strategy

**Derivation source**: Update law regime from resource profile (R_acquisition, R_memory_base, R_energy_rate) + ecology (E_task_distribution, E_drift, E_recurrence). From the phase law: learning = f(R_acquisition, R_energy_rate, E_task_distribution, E_drift, E_recurrence).

High acquisition budget + high drift => fast, flexible learning. Low budget + stable environment => slow, conservative learning. High recurrence => reinforcement learning. Low recurrence => one-shot or few-shot.

| Species Class | Learning Law | Predicted Update Regime | Derivation |
|---------------|--------------|------------------------|------------|
| **Primate** | Flexible, multi-timescale | Hierarchical Bayesian, social learning, cultural accumulation | High R + medium E_drift + long D => multi-timescale learning |
| **Corvid** | Moderate, social-cued | Reinforcement + social observation | Medium R + social topology + tool ecology => moderate flexible learning |
| **Rodent** | Simple, fast, stimulus-driven | Stimulus-response, habit formation, spatial learning | Low R + high E_recurrence + short D => fast simple learning |
| **Cephalopod** | Fast, short-lived | Rapid associative, immediate adaptation | Low R (lifespan) + high V => learn fast, forget fast |
| **Social insect** | Colony-level, no individual learning | Pheromone trail reinforcement, caste determination | Zero individual R => no individual learning; colony-level |
| **Canid** | Social, moderate flexibility | Social learning, observational learning, basic reinforcement | Medium R + social topology + cooperative ecology => social learning emphasis |

### L1.12 Hold-Out Protocol

The following biological observations are HELD OUT from theory fitting. They will be used only for post-hoc validation, never to tune parameters:

1. **Brain size / encephalisation quotient**: Not used to set any coordinate. Predictions derive from ecology + resources only.
2. **Specific neural architecture details**: No claims about cortical columns, hippocampal structures, etc.
3. **Specific behavioral experiment results**: No tuning to known animal cognition experimental findings.
4. **Phylogenetic relationships**: Predictions are ecology-derived, not ancestry-derived.
5. **Body size / metabolic rate as direct predictors**: Used only as proxies for R coordinates, not as direct cognitive predictors.
6. **Specific tool-use inventories**: Predicted from theory, not fitted to observed tool use.
7. **Social group size as direct predictor**: Used only through S coordinates, not as direct cognitive predictor.
8. **Specific memory task performance**: Held out for post-hoc validation.

---

## L2. Cross-Species Predictions

### L2.1 Human

**Ecology/Resource Parameters**:
- `R`: High (large brain, long developmental window, high metabolic allocation to brain)
- `E`: High complexity (diverse task distribution, long horizon, moderate drift, high noise)
- `V`: High (complex social and physical environment)

**Phase Law Application**: `M* = f(E_high, R_high, V_high)` => maximum morphology expression.

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Symbolic+social** | High R + high E_task_distribution + high S_agent_count => symbolic reasoning + social cognition |
| Dominant memory type | **Semantic** (abstract relational categories) + rich episodic | Long D_retention_window + low E_drift => semantic accumulation |
| Learning law | **Hierarchical Bayesian + cultural accumulation** | High R + long D + social topology => multi-generational learning |
| Social cognition depth | **Deep recursive** (3+ levels of intention attribution) | High S_agent_count + high E_information_asymmetry + high S_deception_frequency |
| Planning horizon | **Multi-year, hierarchical** | High R_action_cost + long E_horizon + long D => deep planning |
| Attention routing | **Dynamic, top-down, metacognitive** | High R_observation but very high E_task_distribution => flexible routing with monitoring |
| Causal cognition | **High: counterfactual reasoning** | High R_action_cost + high E_tool_opportunity + long D => deep causal models |
| Exploration regime | **Broad, innovation-driven** | High R_acquisition + medium E_drift => explore-and-learn |

**Negative Twin**: If the theory were wrong, humans would show cognitive architecture matching body size or brain size scaling alone -- i.e., a proportionally scaled-up primate pattern without the symbolic+social qualitative shift. The negative twin prediction is that human cognition is "primate but bigger," not qualitatively different.

### L2.2 Great Ape (Chimpanzee, Bonobo, Orangutan)

**Ecology/Resource Parameters**:
- `R`: High (large brain relative to body, long developmental window)
- `E`: Medium-high (forest ecology, seasonal variation, moderate complexity)
- `V`: High (complex social dynamics, tool-use ecology)

**Phase Law Application**: `M* = f(E_medium-high, R_high, V_high)` => near-maximum morphology.

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Symbolic+social** (reduced symbolic depth vs human) | High R + medium-high E + high V => symbolic+social but less than human |
| Dominant memory type | **Episodic** (cache locations, social events) + semantic | Long D_retention_window but shorter than human => episodic emphasis |
| Learning law | **Social learning + reinforcement** | High R + social topology + tool ecology => social learning |
| Social cognition depth | **Medium-deep** (2 levels of intention attribution) | High S_agent_count + S_deception_frequency but less than human |
| Planning horizon | **Days to weeks, moderate hierarchy** | High R_action_cost + medium E_horizon => moderate planning |
| Attention routing | **Dynamic, spatial-focused** | Medium R_observation + tool ecology => spatial attention |
| Causal cognition | **Medium-high: physical causal reasoning** | Medium R_action_cost + E_tool_opportunity => moderate causal |
| Exploration regime | **Moderate, socially cued** | Medium R_acquisition + social topology => socially guided exploration |

**Negative Twin**: If the theory were wrong, great apes would show the same cognitive architecture as other primates of similar body size (e.g., macaques) -- i.e., no qualitative difference despite different ecology and resource profile.

### L2.3 Corvid (Crow, Raven, Jay)

**Ecology/Resource Parameters**:
- `R`: Medium (moderate brain size, moderate developmental window)
- `E`: Medium (tool-use ecology, seasonal food caching, moderate social complexity)
- `V`: Medium (forest/urban environments, moderate complexity)

**Phase Law Application**: `M* = f(E_medium, R_medium, V_medium)` => moderate morphology.

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Sparse-routing** (efficient resource use with selective depth) | Medium R + medium E => sparse but targeted routing |
| Dominant memory type | **Episodic-like** (cache locations, who-watching) + spatial semantic | Medium R + E_tool_opportunity + S_deception_frequency => episodic-social |
| Learning law | **Reinforcement + social observation** | Medium R + social topology => moderate learning flexibility |
| Social cognition depth | **Medium** (1-2 levels, perspective-taking) | Medium S_agent_count + S_deception_frequency => moderate social |
| Planning horizon | **Medium** (cache planning, tool sequences) | Medium R_action_cost + tool ecology => moderate planning |
| Attention routing | **Dynamic, spatial-focused** | Medium R_observation + tool ecology => focused spatial attention |
| Causal cognition | **Medium-high: physical causal reasoning** | Medium R_action_cost + E_tool_opportunity => moderate-high causal |
| Exploration regime | **Targeted, cache-diversification** | Medium R_acquisition + tool ecology => targeted exploration |

**Negative Twin**: If the theory were wrong, corvids would show rodent-level cognition (low R, low V prediction) despite their medium R and tool ecology -- i.e., no qualitative difference from non-tool-using birds of similar body size.

### L2.4 Rodent (Rat, Mouse)

**Ecology/Resource Parameters**:
- `R`: Low (small brain, short developmental window, low metabolic allocation to brain)
- `E`: Low (simple task distribution, short horizon, high recurrence)
- `V`: Low (stable burrow environment, low complexity)

**Phase Law Application**: `M* = f(E_low, R_low, V_low)` => minimal morphology.

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Reactive** (stimulus-response, minimal internal model) | Low R + low E + low V => reactive sufficient |
| Dominant memory type | **Procedural** (habit formation, spatial navigation) | Low R + high E_recurrence => procedural emphasis |
| Learning law | **Reinforcement + habit formation** | Low R + high E_recurrence + short D => simple learning |
| Social cognition depth | **Shallow** (basic recognition, dominance status) | Low S_agent_count + low E_information_asymmetry => minimal social |
| Planning horizon | **Short** (immediate to hours) | Low R_action_cost + short E_horizon => minimal planning |
| Attention routing | **Fixed parallel monitoring** | Low R_observation + low E_task_distribution => fixed monitoring |
| Causal cognition | **Low: associative** | Low R_action_cost + low E_tool_opportunity => minimal causal |
| Exploration regime | **Narrow, exploitation-focused** | Low R_acquisition + high E_recurrence => exploit known paths |

**Negative Twin**: If the theory were wrong, rodents would show the same cognitive architecture as primate species of similar body size -- i.e., body size, not ecology, drives cognition.

### L2.5 Dog/Canid

**Ecology/Resource Parameters**:
- `R`: Medium (moderate brain size, moderate developmental window)
- `E`: Medium (varied task ecology, moderate horizon)
- `V`: Medium (domestic + wild environments, social cooperation with humans)

**Phase Law Application**: `M* = f(E_medium, R_medium, V_medium)` => moderate morphology.

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Sparse-routing** (social cooperation emphasis) | Medium R + medium E + cooperative S => social-sparse routing |
| Dominant memory type | **Social episodic** (human interaction history) + spatial | Medium R + social topology + cooperative ecology => social episodic |
| Learning law | **Social learning + observational** | Medium R + social topology + cooperative ecology => social learning emphasis |
| Social cognition depth | **Medium** (cooperative intention, perspective-taking) | Medium S_agent_count + cooperative S + human cooperation => medium social |
| Planning horizon | **Medium** (hunt planning, social coordination) | Medium R_action_cost + cooperative ecology => moderate planning |
| Attention routing | **Dynamic, social-modulated** | Medium R_observation + social topology => social attention modulation |
| Causal cognition | **Low-medium: social causal** | Medium R + social topology => social causal, not physical causal |
| Exploration regime | **Moderate, socially cued** | Medium R_acquisition + social topology => socially guided exploration |

**Negative Twin**: If the theory were wrong, dogs would show the same cognitive architecture as other canids of similar body size (e.g., wolves) despite domestication altering social ecology -- i.e., ecology doesn't matter, only phylogeny.

### L2.6 Cephalopod (Octopus, Cuttlefish)

**Ecology/Resource Parameters**:
- `R`: Low (short lifespan limits budget accumulation; moderate brain size but short D)
- `E`: High (complex marine environment, diverse prey, high volatility)
- `V`: High (complex reef/ocean floor environments)

**Phase Law Application**: `M* = f(E_high, R_low, V_high)` => constrained morphology with high environmental pressure.

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Conditioning** (fast adaptation without long-term architecture) | Low R (short lifespan) + high E + high V => fast conditioning |
| Dominant memory type | **Procedural** (motor skills) + rapid associative | Low R (short D_retention_window) + high V => fast learning, weak retention |
| Learning law | **Fast associative + immediate adaptation** | Low R + high V + short D => learn fast, forget fast |
| Social cognition depth | **Shallow** (minimal social ecology) | Solitary ecology => minimal social cognition pressure |
| Planning horizon | **Short-medium** (hours to days) | Low R (short lifespan) => no long planning investment |
| Attention routing | **Rapid dynamic routing** | Low R but high V => fast reconfigurable attention |
| Causal cognition | **Medium: physical causal reasoning** | High E_tool_opportunity + high V => moderate causal |
| Exploration regime | **Broad but rapid** | Low R (lifespan) + high V => explore fast, forget fast |

**Negative Twin**: If the theory were wrong, cephalopods would show the same cognitive architecture as other invertebrates of similar body size -- i.e., body size, not ecology, drives cognition. The negative twin predicts no tool use, no causal reasoning, no rapid learning.

### L2.7 Social Insect (Honeybee, Ant, Termite)

**Ecology/Resource Parameters**:
- `R`: Very low per individual (minimal brain, no individual budget accumulation)
- `E`: Colony-level complexity (division of labor, collective foraging)
- `V`: Colony-level (complex social structure, environmental interaction)

**Phase Law Application**: `M* = f(E_colony, R_individual_near-zero, V_colony)` => colony-level morphology, not individual.

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Reactive** (individual) / **Symbolic+social** (colony-level) | Zero individual R => reactive individual; colony R => colony-level morphology |
| Dominant memory type | **None individually** (pheromone-mediated colony memory) | Zero individual R => zero individual memory |
| Learning law | **Colony-level reinforcement** (pheromone trail reinforcement) | Zero individual R => no individual learning; colony-level |
| Social cognition depth | **None individually** (colony-level emergent behavior) | Zero individual S_agent_count => no individual social cognition |
| Planning horizon | **None individually** (colony-level emergent) | Zero individual R => no individual planning |
| Attention routing | **Reflexive** (pheromone-gradient following) | Zero individual R => no flexible attention |
| Causal cognition | **None individually** | Zero individual R => no individual causal cognition |
| Exploration regime | **Colony-level scout-cast** | Zero individual R; colony-level R => scout-cast exploration |

**Negative Twin**: If the theory were wrong, social insects would show individual-level cognition matching their body size -- i.e., the colony-level emergent behavior would be reducible to individual cognition. The negative twin predicts individual-level learning, planning, and social cognition.

### L2.8 Additional Comparative Species

#### Dolphin (Cetacean)

**Ecology/Resource Parameters**:
- `R`: High (large brain, long developmental window, high metabolic allocation)
- `E`: Medium-high (open ocean, moderate complexity, social hunting)
- `V`: High (three-dimensional aquatic environment, social complexity)

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Symbolic+social** | High R + medium-high E + high V => symbolic+social |
| Dominant memory type | **Episodic-social** + semantic | Long D + social topology + high V => social episodic |
| Learning law | **Social learning + cultural transmission** | High R + social topology + long D => cultural learning |
| Social cognition depth | **Deep recursive** (2-3 levels) | High S_agent_count + cooperative S + E_information_asymmetry => deep social |
| Negative Twin | Cognition would be "whale but smaller" -- no qualitative shift from other cetaceans despite different ecology |

#### Elephant (Proboscidean)

**Ecology/Resource Parameters**:
- `R`: High (large brain, very long developmental window, long lifespan)
- `E`: Medium (savanna/forest, moderate complexity, long memory horizon)
- `V`: Medium (social complexity, long-term resource tracking)

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Symbolic+social** (memory-emphasis) | High R + long D_retention_window + social topology => memory-emphasis |
| Dominant memory type | **Semantic** (long-term accumulated knowledge) + spatial | Very long D + low E_drift => semantic accumulation |
| Learning law | **Slow, deep accumulation** | High R + very long D + low E_drift => slow deep learning |
| Social cognition depth | **Medium-deep** (matriarchal knowledge, social bonds) | Medium S_agent_count + cooperative S + long D => medium-deep social |
| Negative Twin | Cognition would be "large mammal but bigger" -- no qualitative difference from other large herbivores |

#### Parrot (Psittacine)

**Ecology/Resource Parameters**:
- `R`: Medium-high (large brain relative to body, moderate developmental window)
- `E`: Medium (forest ecology, social flock, moderate complexity)
- `V`: Medium (social complexity, vocal mimicry ecology)

| Prediction | Value | Derivation |
|------------|-------|------------|
| Morphology class | **Sparse-routing** (vocal-social emphasis) | Medium-high R + medium E + social topology => vocal-social routing |
| Dominant memory type | **Episodic-social** + vocal-semantic | Medium R + social topology + vocal ecology => social-vocal memory |
| Learning law | **Social learning + vocal learning** | Medium R + social topology + vocal ecology => social-vocal learning |
| Social cognition depth | **Medium** (flock coordination, vocal communication) | Medium S_agent_count + cooperative S => medium social |
| Negative Twin | Cognition would be "bird but bigger" -- no qualitative difference from non-parrot birds of similar body size |

---

## L2.9 Freeze Protocol

**All predictions in L2.1-L2.8 are prospectively frozen.** They were derived from the phase law `E + R + V -> M*` using species-appropriate parameters BEFORE consulting held-out biological data.

**Freeze timestamp**: 2026-09-15T00:00:00Z
**Freeze scope**: All morphology class assignments, memory type predictions, learning law predictions, social cognition depth predictions, planning horizon predictions, attention routing predictions, causal cognition predictions, and exploration regime predictions.
**No post-hoc tuning**: These predictions must not be adjusted after comparing to observed animal cognition data.

**Validation protocol**: After frozen predictions are established, compare each prediction against the held-out biological observations listed in L1.12. Report agreement/disagreement for each prediction. Disagreements must be analyzed for:
1. Incorrect parameter estimation (E, R, V values wrong for the species)
2. Incorrect phase law application (derivation error)
3. Genuinely wrong prediction (theory falsified for that species)

---

## L2.10 Ecology-vs-Complexity Test

**Test Design**: Does ecology predict observed cognitive differences better than generic complexity measures?

**Independent Variables**:
1. **Ecology-derived predictions** (from L2.1-L2.8): morphology class, memory type, learning law, social cognition depth, planning horizon, attention routing, causal cognition, exploration regime
2. **Generic complexity measures** (null model): brain size, body size, encephalisation quotient (EQ), brain-to-body-mass ratio

**Dependent Variable**: Observed cognitive differences across species (from comparative cognition literature, held out from theory fitting).

**Statistical Test**:
1. For each cognitive dimension (memory, attention, planning, exploration, causal, social, learning), rank-order species by ecology-derived prediction and by generic complexity measure
2. Compute Spearman rank correlation between predicted and observed rankings
3. Compare correlation strength: ecology-derived vs generic complexity
4. Bootstrap confidence intervals for difference in correlation strength

**Prediction**: Ecology-derived predictions will show significantly stronger correlation with observed cognitive differences than generic complexity measures (brain size, body size, EQ).

**Falsification**: If generic complexity measures (brain size, EQ) predict observed cognitive differences equally well or better than ecology-derived predictions, the phase law `E + R + V -> M*` adds no explanatory value beyond scaling.

---

## Falsification Section

The following observations would falsify the cross-species predictions:

### F1: Morphology Class Falsification
- **Observation**: A species predicted as "reactive" (e.g., rodent) shows symbolic reasoning without high R or high E
- **Implication**: Ecology does not determine morphology class; the phase law fails
- **Status**: NOT OBSERVED

### F2: Memory Profile Falsification
- **Observation**: A species predicted as "procedural-dominant" (e.g., rodent) shows rich episodic memory without long retention window or low drift
- **Implication**: Memory architecture does not derive from ecology; the retention cost model fails
- **Status**: NOT OBSERVED

### F3: Social Cognition Falsification
- **Observation**: A species predicted as "shallow social" (e.g., solitary cephalopod) shows recursive theory of mind without social topology pressure
- **Implication**: Social cognition does not derive from social topology; the social coordinates fail
- **Status**: NOT OBSERVED

### F4: Planning Falsification
- **Observation**: A species predicted as "reactive" (e.g., social insect individual) shows multi-step planning without individual R budget
- **Implication**: Planning does not derive from action cost and horizon; the planning model fails
- **Status**: NOT OBSERVED

### F5: Tool Use Falsification
- **Observation**: A species predicted as "no tool use" (e.g., rodent) shows tool manufacture without high E_tool_opportunity or high R_action_cost
- **Implication**: Tool use does not derive from ecology; the causal cognition model fails
- **Status**: NOT OBSERVED

### F6: Learning Law Falsification
- **Observation**: A species predicted as "simple reinforcement" (e.g., rodent) shows hierarchical Bayesian learning without high R or long D
- **Implication**: Learning architecture does not derive from resource profile; the learning model fails
- **Status**: NOT OBSERVED

### F7: Cross-Species Test Falsification
- **Observation**: Generic complexity measures (brain size, EQ) predict cognitive differences equally well as ecology-derived predictions
- **Implication**: The phase law `E + R + V -> M*` adds no explanatory value; ecology is epiphenomenal
- **Status**: NOT TESTED (requires comparative data)

### F8: Negative Twin Falsification
- **Observation**: Any species shows cognitive architecture matching its negative twin prediction rather than its positive prediction
- **Implication**: The claimed distinguishing feature (ecology-derived morphology) is not causally responsible
- **Status**: NOT TESTED (requires species-specific experiments)

---

## Summary of All Predictions

| Species | Morphology Class | Memory | Learning | Social Cognition | Planning | Attention | Causal | Exploration |
|---------|-----------------|--------|----------|-----------------|----------|-----------|--------|-------------|
| Human | Symbolic+social | Semantic+episodic | Hierarchical Bayesian+cultural | Deep recursive (3+) | Multi-year | Dynamic+metacognitive | Counterfactual | Broad innovation |
| Great Ape | Symbolic+social (reduced) | Episodic+semantic | Social+reinforcement | Medium-deep (2) | Days-weeks | Dynamic spatial | Physical causal | Moderate social |
| Corvid | Sparse-routing | Episodic-like+social | Reinforcement+social | Medium (1-2) | Medium | Dynamic spatial | Physical causal | Targeted |
| Rodent | Reactive | Procedural | Reinforcement+habit | Shallow | Short | Fixed parallel | Associative | Narrow exploit |
| Dog/Canid | Sparse-routing (social) | Social episodic | Social+observational | Medium | Medium | Social-modulated | Social causal | Moderate social |
| Cephalopod | Conditioning | Procedural+rapid associative | Fast associative | Shallow | Short-medium | Rapid dynamic | Physical causal | Broad rapid |
| Social insect | Reactive (individual) / Symbolic+social (colony) | None (colony-level) | Colony-level reinforcement | None (colony-level) | None (colony-level) | Reflexive | None | Colony-level scout |
| Dolphin | Symbolic+social | Episodic-social+semantic | Social+cultural | Deep recursive (2-3) | Medium-long | Dynamic+social | Physical causal | Moderate social |
| Elephant | Symbolic+social (memory) | Semantic (long-term) | Slow deep accumulation | Medium-deep | Long | Dynamic+social | Physical causal | Moderate |
| Parrot | Sparse-routing (vocal) | Episodic-social+vocal-semantic | Social+vocal | Medium | Medium | Dynamic social | Physical+social | Moderate social |

---

## References

- `research/gmi-grand-unification-v1/gmi-morphology-phase-rv-v1/MORPHOLOGY_PHASE_RV_THEOREM_V1.md` -- Phase law definition
- `research/gmi-grand-unification-v1/gmi-biology-predictions-v1/BIOLOGY_PREDICTIONS_THEOREM_V1.md` -- Biology predictions theorem
- `research/gmi-grand-unification-v1/gmi-ecology-extension-v1/` -- 16 ecology coordinates
- `research/gmi-grand-unification-v1/gmi-metrics-runtime-v1/` -- 11 metrics coordinates
- `research/gmi-grand-unification-v1/gmi-domain-gates-v1/NEW_DOMAIN_CLAIM_GATE_AND_UNSEEN_FORMS_V1.md` -- Domain claim gate
- `research/machine-intelligence-morphogenesis-v1/GMI_DERIVED_COMPONENT_LESIONS_V1.md` -- Component lesions
- `research/gmi-capability-contract-v1/CONTRACT_V1.json` -- Capability contract (27 rows)
