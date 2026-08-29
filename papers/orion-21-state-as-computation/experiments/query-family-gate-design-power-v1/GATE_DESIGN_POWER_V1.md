# What ORION-21's `>=8/10` family gate can detect at n=10

**Terminal unchanged:** `P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET`. This adds no
experiment, reads no outcome, and retunes nothing. It bounds what the miss licenses.

The family-scale phase froze a gate of at least 8 of 10 digit responsibilities
quality-supported, and returned LINEAR `3/10`, RBF `5/10`, KNN `5/10`. The round states
the gate was missed. It does not state what per-responsibility capability a `>=8/10`
rule at `n=10` is able to detect — and without that, **"family-scale capability is
absent"** and **"the gate cannot see it at n=10"** are indistinguishable readings of the
same number, with opposite implications for the paper's scope claim.

All figures are exact binomial arithmetic over the ten registered responsibilities
(`compute_gate_design_power_v1.py`, machine-readable in `GATE_DESIGN_POWER_V1.json`).

## The gate is conservative, and it is blunt

| true per-responsibility capability | P(gate passes) |
|---|---|
| 0.50 | 0.0547 |
| 0.60 | 0.1673 |
| 0.70 | 0.3828 |
| 0.75 | 0.5256 |
| 0.80 | 0.6778 |
| 0.85 | 0.8202 |
| 0.90 | 0.9298 |
| 0.95 | 0.9885 |

- **False-pass rate at p = 0.5: 0.0547.** The gate does not pass coin-flip capability;
  as a guard against false promotion it is sound.
- **80% power only at capability >= 0.8424**; 50% power at `>= 0.7414`. A system whose
  true capability is 0.75 fails this gate about half the time.

So the gate was built to certify near-uniform capability, not to measure moderate
capability. That is a legitimate design for a promotion bar — but it means a miss cannot
be read as an absence without the interval below.

## The observed arms exclude the region the gate was powered to detect

Exact Clopper-Pearson two-sided 95% intervals:

| arm | observed | 95% interval | excludes the >=0.8424 region? |
|---|---|---|---|
| LINEAR | 3/10 | `[0.067, 0.652]` | **yes** |
| RBF | 5/10 | `[0.187, 0.813]` | **yes** |
| KNN | 5/10 | `[0.187, 0.813]` | **yes** |

Every arm's upper bound lies below `0.8424`. **The miss is therefore not an artefact of
small n**: capability at the preregistered level is excluded by the data, not merely
unobserved.

## What the negative does and does not license

- **Licensed:** family-scale compilation capability is **below the registered bar**. The
  strongest arm's interval tops out at `0.813`, under the `0.8424` the gate needs.
- **Not licensed:** that capability is *absent*. Neither interval excludes the
  `0.6`–`0.8` band, and across that band the gate's power is only `17%`–`68%`. A system
  with genuine moderate capability would usually fail this gate, and these data cannot
  distinguish that case from a weaker one.

The registered conclusion — never generalise a single-responsibility compiler result to
a ten-responsibility family — is unaffected and, with the interval, better supported: it
now rests on an exclusion rather than on a bare count.

## Why this was worth stating

The distinction matters because the two readings point opposite ways. Read as "capability
absent", the result closes the direction. Read as "gate underpowered", it argues for a
larger responsibility set. The arithmetic says the first is right at the registered bar
and the second is right below it, and a referee would otherwise have to derive that
themselves to know which claim the paper is making.
