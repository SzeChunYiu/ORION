# ORION-19 failure diagnosis on a formal-reasoning domain — findings V1

**Terminal: `RESOURCE_VECTOR_DIAGNOSIS_SUPPORTED`**, on the held-out half, by the
rule frozen in `PROTOCOL_V1.md`. The terminal is reported first because the
protocol says so; the fragility below is reported at equal length because the
terminal alone would mislead.

## Held-out result

| arm | accuracy | **false compute escalation** |
|---|---|---|
| `always_compute` | 0.4500 | **1.0000** |
| `verdict_only` | 0.9000 | **0.1818** |
| `resource_vector` | 1.0000 | **0.0000** |
| `oracle` | 1.0000 | 0.0000 |

40 instances over three families, 5 excluded because the injected deficiency did
not change the verdict. z3 5.1.0. The conflict threshold was fitted on the
development half (37,361) and applied unchanged.

## The perfect score is a split artifact, and here is the proof

`resource_vector` matching the oracle exactly should not be believed, and it should
not be believed for a specific reason rather than out of caution.

The feature is **conflict count**, a proxy for how much search the solver burned.
It has a blind spot the size of a whole family. In `factoring`, the
accessibility-deficient (integer) encoding burns the **entire 5-second budget** and
accrues **5, 6 and 11 conflicts** — because z3 solves nonlinear integer arithmetic
by a route that is not conflict-driven. Those three instances look exactly like
compute starvation to this feature and would be classified `COMPUTE`.

All three landed in the **development** half. The held-out half never contained a
case the feature cannot see.

Scored on **all 40 rows** rather than the lucky half:

| arm | accuracy | **false compute escalation** |
|---|---|---|
| `always_compute` | 0.3750 | 1.0000 |
| `verdict_only` | 0.7500 | 0.4000 |
| `resource_vector` | **0.9250** | **0.1200** |

By family: pigeonhole **1.000**, colouring **1.000**, factoring **0.727**.

The result survives — a false-escalation rate of 0.12 against 0.40 and 1.00 — but
it is not the 0.0000 the held-out table reports, and the difference is a property
of the split, not of the method.

## A hostile budget, because the easy version proved too little

The main run starves compute at 20% of the reference's own solving time, so a
compute-limited run barely starts and accrues almost no conflicts. That makes the
distinction easier than reality. The control re-runs everything at **90%** — a
budget only one tenth short of sufficient, where a compute-limited run does nearly
all the work the reference does:

| arm | accuracy | **false compute escalation** |
|---|---|---|
| `always_compute` | 0.2941 | 1.0000 |
| `verdict_only` | 0.7647 | 0.3333 |
| `resource_vector` | **0.8824** | **0.1667** |

`resource_vector` still halves the naive verdict rule's false escalation, and this
time the held-out score is **not** perfect, so the blind spot shows through instead
of hiding. 34 rows, 11 excluded — at a 90% budget many compute injections no longer
fail at all, which is itself the expected behaviour.

## What this actually establishes

A resource vector diagnoses *why* a formal-reasoning task failed better than the
verdict alone, and far better than escalating compute by default. `always_compute`
is wrong on **every** non-compute failure by construction; `verdict_only` cannot
separate accessibility from compute at all, because both return `unknown`, and
pays for it at 0.33–0.40.

And the mechanism of its failure is legible: **conflict count measures
conflict-driven search, so it is blind wherever the solver does not use it.** That
is not a tuning problem and no threshold repairs it. A diagnosis feature inherits
the solver's own architecture.

## What it does not establish

These instances are **constructed**, so the oracle is exact and the deficiency is
placed deliberately — which is what makes diagnosis scoreable at all, and also
means these are not naturally-occurring hard instances. Nothing here transfers to
the SMT-LIB archive without being re-run on it.

All three families use a bit-vector reference against an integer adversarial form,
so accessibility is measured along **one** encoding axis.

ORION-19's UT3 grid remains unexecuted and untouched; #1701 forbids running it
before a cell executor exists, and nothing here is that.
