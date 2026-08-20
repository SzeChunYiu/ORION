# P1-U GPT-R1 literature Round B — changed-vocabulary / active-diagnosis pressure

Issue: #696  
Date: 2026-08-20  
Status: `MATERIAL_CHANGE`

## Query families

Changed vocabulary was used deliberately to search outside scientific-agent terminology:

- active diagnosis / fault isolation / optimal test design;
- model discrimination / structural model uncertainty;
- intervention-supported error attribution;
- causal tool diagnosis / repair;
- value of computation / value of information;
- theory revision + experiment planning;
- representation change / problem reformulation;
- hostile assumption: `active responsibility discrimination is already solved`.

## Material donors found

### Active diagnosis is established prior art

Classical and modern active fault diagnosis explicitly chooses interventions or measurements to distinguish fault/model hypotheses under cost/uncertainty. Palmer & Bollas (ISA Transactions 2019) optimize diagnostic test designs for information about faults under uncertainty. Earlier and later model-discrimination/control work similarly treats input/test design as a decision-theoretic model-selection problem.

**Disposition:** `ADOPT`. P1-U cannot claim generic active discrimination, experiment selection for diagnosis, or information-gain test design as novel.

### Intervention-supported agent attribution is current prior art

REFLECT (arXiv:2606.09071, 2026) diagnoses a candidate error step, performs a controlled diagnosis-specific intervention/replay, and feeds the outcome flip back into final attribution.

ARCHITECT / Causal Tool Diagnosis (ACL 2026) uses structural causal modeling plus sandbox interventions to distinguish specification, code, and environment causes, with attribution guiding targeted repairs.

AgentTether (arXiv:2607.06273, 2026) localizes failure-critical trajectory regions and uses guided runtime repair with repair memory.

Doctor-RAG (arXiv:2604.00865, 2026) separates trajectory failure localization from tool-conditioned local repair and reuses validated prefixes/evidence.

**Disposition:** `ADOPT/COMPOSE`. Intervention-backed diagnosis and diagnosis-conditioned repair are donor-owned.

### Value of computation / information is donor-owned

Rational metareasoning and active information acquisition already formalize choosing computations/measurements by their expected decision benefit minus cost. Contemporary evidence also shows humans allocate thinking time according to value of computation.

**Disposition:** `ADOPT`. P1-U must compare against cost-aware VoI/VOC policies. A generic `information gain / cost` score is not ORION novelty.

### Theory revision and representation reformulation are older parents

Theory-revision literature explicitly connects diagnosis, revision points/operators, and experiment planning. Problem-reformulation literature shows that representation change can materially alter problem-solving efficiency without changing the scientific objective.

**Disposition:** `ADOPT`. High-level revision and representation change remain donor territory.

## Consequence for #696

Round B changes the proposed mechanism ownership materially.

The phrase **Active Responsibility Discrimination (ARD)** remains a convenient programme label, but its generic active-testing component is donor-owned. The candidate ORION contribution must be evaluated at a higher level:

> **scientific responsibility acquisition across heterogeneous revision levels, integrated with fail-closed minimal revision, exact reopen scope, protected preservation, and proposal/adoption authority separation.**

The runnable donor-complete comparator must therefore receive:

- active fault/model diagnostic test selection;
- one-step and sequential value-of-information/value-of-computation policies;
- intervention-supported error attribution;
- causal diagnosis-conditioned repair;
- objective evolution;
- M-open model-class expansion;
- representation/task reformulation;
- protected generic authorization/revision machinery.

## Strongest baseline pressure

A fully optimal POMDP/decision-theoretic information-acquisition policy supplied the same complete hypothesis/action/observation model is an **analysis ceiling**, not a realistic baseline ORION is expected to outperform mathematically.

The scientific test must instead ask whether ORION's structured scientific-responsibility model and cross-domain learned/acquired mechanics improve over the strongest runnable donor-complete systems when:

- hypothesis structure is partial;
- action usefulness is context-dependent;
- lower-level and higher-level revisions have asymmetric scientific harms;
- responsibility certificates/reopen obligations matter after a decision;
- new failure regimes require adding a discriminator/operator rather than only selecting among a complete known set.

## Reviewer synthesis

- **E1 nearest-work:** generic active diagnosis/VoI novelty is struck.
- **E2 causal methods:** intervention-supported diagnosis must be a baseline; cause-to-repair utility must be measured, not label accuracy alone.
- **E3 ORION architecture:** residual survives only if responsibility acquisition composes with current interface-precedence, minimal-revision and non-authorizing gates.
- **E4 statistics/reproducibility:** discriminator cost and repeated interventions must be fully charged; case, not probe, is the independent unit.

## Round-B terminal

`MATERIAL_DONOR_ABSORPTION__ARD_GENERIC_ACTIVE_DIAGNOSIS_STRUCK__SCIENTIFIC_RESPONSIBILITY_RESIDUAL_SURVIVES`

A new changed-vocabulary Round C is required. It must try to find prior work that already combines cross-level scientific responsibility acquisition with authority/reopen consequences. If Round C finds no such mechanism, it is the first no-material-change round after this correction.
