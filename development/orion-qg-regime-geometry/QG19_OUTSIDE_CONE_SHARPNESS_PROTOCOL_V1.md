# QG-19 outside-cone sharpness probe — protocol V1

**Frozen after Q3-R1 instruments and before QG19 execution.**  
Scientific parent: QG8 support-two sufficient cone + QG2 weighted exact referee.  
Authority target: bounded exact-panel result only; no all-n sharpness theorem.

## Frozen question

For `O19=(t_nc=4,t_c=3,t_tag=2,t_r=2,rho=0)`, which lies one unit outside the central QG8 sufficient-cone face and exactly on the noncentral face, does a deterministic exact panel contain any instance with

`C_DP < C_Dxx`,

where `C_DP` is the unrestricted exact R6M DP optimum and `C_Dxx` is the exact support-<=2 family optimum under the same objective?

## Frozen panel

1. all committed R6M hostile `n=1` panels;
2. all committed R6M hostile `n=2` panels;
3. deterministic random seed `20260822`;
4. 24 random six-target instances at `n=2`;
5. 24 random six-target instances at `n=3`;
6. every random target is non-identity and is generated before cost evaluation.

No chemistry subject and no protected discriminator may be read.

## Outcome space

- `SUPPORT3_WITNESS_FOUND_ON_FROZEN_PANEL`: at least one exact row satisfies `C_DP < C_Dxx`;
- `ZERO_GAP_ON_FROZEN_PANEL`: all rows satisfy `C_DP == C_Dxx`;
- `REFEREE_OR_EXECUTION_INVALID`.

A zero-gap panel does not enlarge the theorem cone. A witness proves only that support two is not exact at O19 for that instance.

## Required receipt fields

- exact objective;
- panel counts and seed;
- all gap counts by n/source;
- serialized first witnesses up to cap 20;
- unrestricted DP witness for each serialized gap row up to cap;
- max frame support in the unrestricted witness;
- exact analyzer output digest;
- no-Q3-import gate;
- no chemistry/protected access gate.

## Replay

Run the analyzer twice from the same commit. Canonical result JSON excluding runtime must be byte-identical.