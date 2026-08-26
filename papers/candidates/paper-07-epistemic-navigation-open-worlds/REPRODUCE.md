# Reproduce ORION-17 candidate formal results

**Candidate:** Epistemic Navigation in Open Worlds  
**Status:** deterministic formal-support path; no novelty/benchmark-superiority authority  
**Python dependency:** standard library only for current checkers

## 1. Reproduction subject

Reproduce from an immutable commit containing:

- `manuscript/FORMAL_CORE_V1.md`;
- `formal/check_countermodels.py`;
- shared `papers/candidates/checkers/p7_finite_falsifiers_v1.py`;
- `papers/candidates/CHECK_RESULTS_V2.md`;
- `CLAIM_LEDGER_V1.md`.

The current working synchronization branch is `shadow/p6-p8-wide-sync-2026-08-17`. Archive an exact commit SHA before any result is cited outside the candidate workspace.

## 2. Environment

Current V2 local environment:

```text
CPython 3.13.5
Linux 6.18.35 x86_64
```

No third-party package, network request, model/provider, judge or LLM API is used by the current formal checker.

Suggested clean setup:

```bash
export PYTHONHASHSEED=0
python --version
uname -a
```

## 3. Primary deterministic checker

From repository root:

```bash
python papers/candidates/paper-07-epistemic-navigation-open-worlds/formal/check_countermodels.py
```

Expected V2 semantic signature:

```text
ORION-17 deterministic countermodels: PASS
  extension-ambiguous complete/incomplete pairs: 8
  certificate-absence != extension-ambiguity counterexample: confirmed
  route-stop/task-stop counterexample: confirmed
  overlap/independence counterexamples: confirmed
  topology-change strict-expressivity instance: confirmed
  preservation/reopening fixtures: confirmed
  evidence-preserved / closure-reopened goal-change fixture: confirmed
  fail-closed stopping fixture: confirmed
  unnecessary-reframe negative control: confirmed
```

The eight extension-ambiguous pairs arise from all undirected edge subsets on the three visible fixture nodes. They demonstrate the theorem in a deliberately rich constructed world class; they do not establish that every certificate-free world class is ambiguous.

## 4. Small theorem-boundary falsifier

```bash
python papers/candidates/checkers/p7_finite_falsifiers_v1.py
```

This smaller script makes the theorem-boundary cases easy to inspect, including the negative case where certificate absence does not imply ambiguity and a fixed-chart negative control where reframe is unnecessary.

## 5. Capture an immutable run

```bash
mkdir -p /tmp/orion-p7-repro
python papers/candidates/paper-07-epistemic-navigation-open-worlds/formal/check_countermodels.py \
  | tee /tmp/orion-p7-repro/check_countermodels.stdout.txt
python papers/candidates/checkers/p7_finite_falsifiers_v1.py \
  | tee /tmp/orion-p7-repro/p7_finite_falsifiers_v1.stdout.txt
sha256sum /tmp/orion-p7-repro/*.txt
```

The final archival path should store stdout plus hashes under immutable repository/CI artifacts.

## 6. What the current checks establish

Bounded support exists for:

- extension-ambiguity stopping countermodels in the explicit constructed class;
- the distinction between certificate absence and ambiguity;
- route-stop/task-stop separation;
- output-overlap versus structural-independence counterexamples;
- a fixed-chart unreachable / reframed-chart reachable instance;
- support preservation versus reopening;
- evidence identity surviving a goal change while old closure scope does not;
- fail-closed mandatory obligations;
- an unnecessary-reframe negative control.

They do **not** establish:

- empirical superiority over SoG/POMDP/planning/world-model baselines;
- that real scientific spaces admit faithful atlas charts/maps;
- that orientation/route-independence contracts can be identified reliably;
- donor-faithful planning abstraction/homomorphism embeddings;
- novelty beyond ORION-11+ORION-12 and parent planning/search theory;
- peer-review readiness.

## 7. Next reproducibility layers

### A. Exact ORION-11/ORION-12 embeddings
Freeze native reframe, route-independence, route-stop/task-stop and censored-obligation decision fixtures and require exact decision equivalence under the atlas representation when chart transformations are inactive.

### B. Planning-abstraction donor fixtures
Implement small plan-preserving map/homomorphism cases from formal planning literature and test that ORION-17 adds no new verdict when its support/obligation dimensions are inert.

### C. Atlas generator
Build a versioned generator with explicit seeds/schema for:

- hidden branches;
- censored routes;
- initial-orientation uncertainty;
- chart-changing tasks;
- objective-changing tasks;
- world-model revision without chart change;
- negative fixed-chart controls.

### D. Trace replay
Every generated benchmark instance should emit the hidden world, visible observation trace, route/chart actions, obligation transitions and final stopping authority in a deterministic machine-readable format.

### E. Strong baselines
#338/#353 require strongest relevant fixed-chart/planning/search donors, not only BFS/no-reframe controls.

## 8. Claim authority

Use `CLAIM_LEDGER_V1.md` as the maximum claim boundary. In particular, do not rewrite the stopping theorem as “no closure certificate implies incompleteness”; the current theorem is conditioned on extension ambiguity, with a separate richness corollary.