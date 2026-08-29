# ORION-01–05 convergence V1 CI successor

The V1 convergence verifier has two different jobs that must not be conflated:

1. on the original frozen-base event, prove that the complete V1 change set is
   exactly the predeclared additive diff; and
2. on later per-paper successor events, revalidate the immutable V1 evidence
   without treating every legitimate successor file as an illegal V1-creation
   path.

The original workflow applied job 1 forever. That caused later ORION-02
successor PR #1550 to fail only with `event base commit mismatch`, after all
bounded V1 theorem/evidence regenerations had passed. This packet makes the
event mode explicit. It changes no scientific status, donor byte, adverse/null
result, retraction, `CANNOT_CHECK` boundary, or protected Task-3/P9 path.

The workflow remains content-bound in `DONOR_MANIFEST_V1.json`; its operational
row points to `STATUS.json` so the correction is additive and inspectable rather
than a silent rewrite of authority.
