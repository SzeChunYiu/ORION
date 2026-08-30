# ORION-19 failure diagnosis on a formal-reasoning domain — protocol V1

**Committed before the runner exists and before any outcome is computed.**

## Why this domain

#1701 asks, for a new external domain, to *prefer a fresh formal-reasoning domain
with exact gold, e.g. SMT-LIB tasks and native solver proofs*. This uses **z3**
(5.1.0) as the native solver. Its verdicts are the gold: `unsat` is a proof of
unsatisfiability, `sat` a model, `unknown` an exhausted budget.

The instances are **constructed**, not sampled from the SMT-LIB archive, for a
reason that is the whole point of the study: a diagnosis experiment needs to know
the *true* cause of each failure. Sampling a benchmark gives hard instances but no
ground truth about *why* one is hard. Constructing them means the deficiency is
placed deliberately and the oracle is exact by construction. The cost is that
these are not naturally-occurring instances, which is stated in the findings and
is not hidden.

## The three deficiencies, frozen here

Every task has a correct reference form that z3 solves within budget. Each
deficient variant removes exactly one thing:

- **INFORMATION** — a logically necessary constraint is deleted. The instance
  remains well-formed and z3 answers quickly, but with the *wrong* verdict
  (`sat` where the reference is `unsat`). No amount of compute repairs this.
- **ACCESSIBILITY** — the identical logical content is re-encoded adversarially
  (a one-hot cardinality constraint expanded into pairwise form over a padded
  variable set). The verdict is unchanged and reachable in principle; the work
  required is not. Compute helps only by brute force.
- **COMPUTE** — the reference encoding with all information present, run under a
  budget deliberately below what it needs. `unknown`. More compute is exactly the
  right answer here.

Three families, so the result is not an artifact of one problem shape:
**pigeonhole** (n+1 pigeons, n holes), **graph colouring** (a clique needing k+1
colours offered k), and **linear arithmetic** (an integer system with an implied
bound).

## The decision

Given a failed run and a **matched probe budget** the diagnoser must name the
deficiency: `INFORMATION`, `ACCESSIBILITY`, or `COMPUTE`.

Budgets are matched across arms and frozen here: every arm sees the same failure
record and may spend **one** additional solver probe of the same wall-clock budget
as the original run. No arm may spend more than another; that is what "equalize
information and compute budgets" means operationally.

## Arms

- `always_compute` — always answer `COMPUTE`. The naive escalation baseline, and
  the one the primary endpoint is about.
- `verdict_only` — use only the returned verdict.
- `resource_vector` — use the full recorded vector: verdict, wall time, z3
  statistics (conflicts, decisions, propagations), and the one probe.
- `oracle` — knows the injected deficiency. Accuracy 1.0 by construction.

## Endpoints

1. **Correct failure diagnosis** — accuracy over all deficient instances.
2. **False compute escalation** — the fraction of `INFORMATION` or
   `ACCESSIBILITY` instances diagnosed as `COMPUTE`. This is the primary. It is
   the expensive error: it spends a budget that cannot possibly fix the fault.
3. **Vector resource accounting** — solver time and probe count per arm, reported
   whether or not it favours any arm.

## No threshold retuning

Every threshold the `resource_vector` arm uses is fitted on a **development half**
of instances and applied unchanged to the held-out half. #1701 says no threshold
retuning, and a threshold chosen after seeing held-out outcomes would be exactly
that. Split seed `20260830`.

## Terminals

- `RESOURCE_VECTOR_DIAGNOSIS_SUPPORTED` — on held-out instances, `resource_vector`
  has strictly lower false-compute-escalation than **both** `always_compute` and
  `verdict_only`, and accuracy no worse than `verdict_only`.
- `RESOURCE_VECTOR_DIAGNOSIS_NOT_SUPPORTED` — otherwise. Recorded with the
  confusion matrix, and not rescued by re-tuning.
- `CANNOT_CHECK_NO_SEPARATION` — if the three deficiencies produce
  indistinguishable failure records, there is nothing to diagnose and the design
  has no power. Declared here so it cannot later be presented as a negative about
  diagnosis.

A pass says a resource vector diagnoses *constructed* deficiencies in a formal
domain better than escalating compute. It says nothing about naturally-occurring
hard instances, about non-formal domains, or about ORION-19's UT3 grid, which
remains unexecuted and untouched.
