# ORION-P4 protected custody policy V1

## Roles

- **Candidate lane:** produces answer/proposal/checker suggestions and may use only declared candidate-visible evidence/tools.
- **Protected evaluator/holdout lane:** owns final labels, protected hostile cases and evaluator artifacts. It is not writable by the candidate.
- **Host verifier:** freezes hashes/epoch, launches the candidate, retains access telemetry, evaluates outputs and records the authority terminal.

Producer and verifier lineages must be distinct for publication-authorizing external evidence.

## Before candidate execution

The host records:

- subject revision hash;
- evaluator artifact hash;
- public and protected split hashes;
- evidence content/provenance hashes;
- attack-case manifest hash;
- candidate-visible tool/search policy;
- baseline configuration hashes;
- evaluation epoch.

Only then may the protocol be marked `EXECUTION_FROZEN`.

## During execution

- Candidate writes occur only in candidate-owned/isolation paths.
- Access to protected evaluator/holdout paths is denied and logged.
- Search/network requests are logged for contamination auditing.
- Patches touching evaluator/guard/holdout definitions are preserved as hostile evidence and cannot become accepted evaluation changes.

## After execution

The protected lane computes verdicts from the frozen evaluator. A new evaluator or label revision creates a new evaluation version; it does not overwrite the old outcome. False positives, false negatives, blocks and `CANNOT_CHECK` cases all remain in the raw artifact.

## Publication release

Release public cases, schemas, hashes and safe telemetry necessary for reproducibility. Protected labels/cases may be delayed or partially withheld if disclosure would destroy future holdout value; the paper must state what remains protected and enable an independent reviewer/host to audit it.
