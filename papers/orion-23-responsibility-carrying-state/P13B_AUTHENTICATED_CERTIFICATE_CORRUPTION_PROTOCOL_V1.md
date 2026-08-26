# P13B authenticated-certificate corruption protocol v1

**Frozen before protected execution.**  This protocol authorizes only a
controlled finite-world claim.  Its gold specification is locally authored and
certificate-independent; it is not externally adjudicated evidence.

## Claim

Against the registered finite corruption panel, an authenticated
responsibility-carrying-state policy rejects mutated certificates, makes zero
reuse decisions where certificate-independent gold support is absent, and costs
less than always reopening on the valid-certificate panel.

## Independent gold and panel

`P13B_GOLD_SUPPORT_SPEC_V1.json` defines task requirements and state-form
contents without reading any certificate.  Gold support holds exactly when a
task's required variables are a subset of the state form's available variables.
The full 6 state forms x 5 tasks panel is enumerated; no sampling inference or
population generalization is claimed.

The valid certificate for a state binds:

- issuer `ORION_P13B_TRUST_ROOT_V1`;
- subject state id;
- epoch `2`;
- the complete declared-support mapping;
- the state variable witness;
- a canonical SHA-256 over those fields.

The generic validator checks issuer, subject, epoch, mapping/witness consistency
and digest before the policy can reuse.  The gold scorer independently recomputes
support from the gold specification and never reads `declared_support`.

## Frozen corruption worlds

1. `OMITTED_SUPPORT`: remove one true support declaration and retain the old
   digest.
2. `OVERBROAD_SUPPORT`: add one unsupported declaration and retain the old
   digest.
3. `FORGED_SUPPORT`: add one unsupported declaration, change the issuer and
   recompute a syntactically valid digest.
4. `STALE_EPOCH`: use an epoch-1 certificate whose witness is the fully material
   `Z3` state while presenting it for a current state lacking at least one
   required variable.

Before outcome scoring, every corruption world must have a nonzero mutation
opportunity: a state/task pair whose unverified decision or certificate validity
changes because of that corruption.  A zero denominator blocks adjudication and
cannot pass as zero violations.

## Arms and costs

- `AUTHENTICATED_RCS`: reuse only when the certificate validates and declares
  support; otherwise reopen.
- `UNVERIFIED_RCS`: trust the declared support field without validation.
- `ALWAYS_RAW`: always reopen.

All episodes have recovery available.  `REUSE` costs 1 and `REOPEN` costs 6.
Reopening returns the exact answer in this controlled world.  Reuse is unsafe
exactly when certificate-independent gold support is absent.

## Frozen gates and terminals

All gates must pass:

1. all four corruption worlds have nonzero mutation opportunities;
2. every mutated certificate is rejected by `AUTHENTICATED_RCS`;
3. `AUTHENTICATED_RCS` has zero unsafe reuse in each corruption world;
4. `UNVERIFIED_RCS` has at least one unsafe reuse opportunity and violation in
   each of `OVERBROAD_SUPPORT`, `FORGED_SUPPORT` and `STALE_EPOCH`;
5. valid certificates are accepted and the authenticated arm exactly matches
   gold-supported reuse on the valid panel;
6. valid-panel verified-correct rate is 1.0;
7. valid-panel mean authenticated cost is at most 0.70 times `ALWAYS_RAW` cost;
8. two fresh subprocess executions are byte-identical.

Success terminal:
`P13B_AUTHENTICATED_CERTIFICATE_SAFETY_COST_SUPPORTED_FINITE_WORLD`.

Failure terminal:
`P13B_AUTHENTICATED_CERTIFICATE_SAFETY_COST_GATE_NOT_MET`.

The success terminal must never be described as external validation, empirical
real-agent safety, or population-level superiority.

