# Claim disposition — ORION11.COSTED_EPISTEMIC_ORDERING.v1

Protocol frozen in this packet; trace schema frozen at `f9490c97e`. Outcomes read once.

**Formal terminal: `CANNOT_CHECK__CHECKER_DISAGREEMENT`.**

## What both parties agree on

The runner and the independent checker agree on **34 of 36** comparable fields, including
every gate that decides the science:

| gate | both |
|---|---|
| G1 success noninferiority | **pass** |
| G2 zero forbidden mutation | **pass** |
| G3 cost ratio vs faithful Active-VOI < 0.80 | **FAIL** |
| G4 within 1.10x the DP optimum | **FAIL** |
| G5 assumption attribution | pass |
| G7 instrument control on ratio_aligned | pass |

**Both parties independently select an UNFAVOURABLE terminal. The hypothesis is
falsified on either reading.** At equal success and safety ORION costs **1.82x** a
faithful Active-VOI comparator (paired n=1657, CI [1.782, 1.854]) against a gate
requiring **< 0.80**, and **1.20x** the exact DP optimum against a 1.10x ceiling.

I reproduced both ratios on a third independent path directly from the raw traces
(`ORCHESTRATOR_SPOT_CHECK_V1.json`): 1.8184 and 1.6649 against the runner's 1.8183686 and
1.6648972.

## What they disagree on, and why I am not arbitrating it

Two fields: `terminal`, and `gates.G6.passed`.

- The **runner** selects `H_FALSIFIED__PC_BASELINE_MATCHES_OR_BEATS_ORION`, reading G6 on
  the **matched set** — the paired worlds where both arms clear identical gates, where the
  p/c baseline is cheaper at ratio 1.665.
- The **checker** selects `H_FALSIFIED__COST_RATIO_GATE_MISSED`, reading G6 **globally**,
  where `gain_per_cost_greedy` carries a 0.364 forbidden-mutation rate against ORION's
  0.000 and therefore never achieves "safety equal to ORION" at all.

Both readings are defensible from the frozen text. `EXPECTED_TERMINALS.json` states the
condition as *"gain_per_cost_greedy achieves success and safety equal to ORION at cost <=
ORION cost (paired, ...)"* and **does not say whether equal safety is evaluated globally
or on the matched set**. `PROTOCOL.primary_criterion` points toward the matched reading;
the terminal's own wording points toward the global one.

That is an ambiguity in a frozen document, discovered by independent recomputation. The
protocol anticipated exactly this and fixed the outcome in advance:
`disagreement_terminal: CANNOT_CHECK__CHECKER_DISAGREEMENT`.

Choosing between the two readings now, with the numbers in hand, would be post-outcome
discretion over a frozen condition — the specific thing preregistration exists to prevent.
So the formal terminal is the disagreement terminal, and the ambiguity is recorded as a
protocol defect for any successor to resolve **before** it next runs.

## What is nonetheless settled

The **#1608 stop rule** attaches to G3, and G3 failed under both readings:

> If cost is not lower against faithful comparators, retire empirical mechanism-superiority
> claims and keep only the bounded methodological/theoretical result.

So the empirical mechanism-economy claim for ORION-11 is retired. This is robust to the
disagreement, because no reading of G6 can rescue a cost ratio of 1.82 against a 0.80 gate.

The sharpest number is one no gate asked for. Under the same safety constraint:

| arm | mean cost | forbidden rate |
|---|---|---|
| `faithful_active_voi` | **1.1670** | 0.0000 |
| `orion_level_monotone` | **2.1861** | 0.0000 |
| `random_safe_ablation` | **2.2983** | 0.0000 |

Paired against random safe ordering, ORION's cost ratio is **0.9405** over 2420 worlds —
about six percent. Zero forbidden mutation is achieved identically by all three. The
safety property tracks the **constraint**, not the responsibility filtration, and a
faithful comparator reaches the same perfect safety at roughly half the cost.

## Consequence for the manuscript

ORION-11's abstract currently states that *"the surviving comparative residual is
intervention-cost economy at equal success and safety."* That residual is falsified under
both readings and must be narrowed. Handled separately so that a manuscript edit is not
mixed into an evidence packet.

## Defects found, and whose they were

Three trace defects were **mine**, in the schema I froze, and the checker found all three
independently on its first run — refusing with exit 3 rather than certifying: negative
1e-17 costs on `exact_dp_oracle`, a `budget_exceeded` flag defined against `total` when the
protocol's budget constrains build cost, and an A4 stratum spelling divergent from
PROTOCOL. All are repaired and the checker now completes.

The runner also recorded two frozen-document conflicts before outcomes: PROTOCOL declares
8 arms while the schema enumerated 7 (resolved by running all 8 and quarantining the
extra where no gate reads it), and PROTOCOL declares a frozen bootstrap seed while
containing no seed value.

## Authority

`scientific_authority_delta: NONE`. No submission authority. `ORION-11.NECESSITY.V2.2.4`
and the R4 replication `CANNOT_CHECK` are untouched. No terminal from the frozen set is
filed as the study's result; the disagreement terminal is.
