# ORION-04 CR-B replay successor V1

This packet repairs the prerequisite replay path only. It does not execute a
new census, authorize itself, close D2/D3, consume a D4 round, or create
external or journal authority.

The live gate is `AWAITING_NEW_ONE_SHOT_AUTHORIZATION`. Historical job 3544056
and key `741454d7...` remain terminal and consumed. A future attempt requires a
new operator-supplied one-shot execution request and must use the canonical
scripts under `engine_b/slurm/`. The machine validates request bindings only;
the operator label is unverified text and establishes neither externality nor
independence.
