# P1-U GPT-R2 pre-outcome freeze receipt V1

Campaign: #711  
Parent: #649  
Freeze time: 2026-08-20, before held-out source acquisition.

## Frozen policy subject

Policy/test commit before this receipt: `b3386b42933c0defe6773ae582928c18e4fdf158`.

Load-bearing frozen files:
- `development/p1-u-gpt-r2-naturalistic/DEVELOPMENT_PACKET.md`;
- `research/claim_expansion/p1/gpt_r2/PROTOCOL_V1.json`;
- `research/claim_expansion/p1/gpt_r2/policy.py`;
- `tests/unit/p1/test_p1_u_r2_naturalistic_policy.py`.

No held-out case dossier, gold responsibility label, evaluator probe outcome, or policy outcome had been acquired or inspected when the policy/test commit above was created.

## Development-only source quarantine

The following already inspected sources are excluded from held-out evaluation and may be used only as donor/development material:
- Model Discovery Agent / NeuronBench (`arXiv:2608.09696`);
- Self-Revising Discovery Systems for Science (`arXiv:2606.01444`);
- SCION (`arXiv:2607.03863`);
- Robin / *A multi-agent system for automating scientific discovery* (`10.1038/s41586-026-10652-y`);
- RootCauseBench;
- Dapaah & Grabowski 2026 ML-pipeline RCA (`10.1007/s11334-026-00642-8`).

## Frozen outcome rule

Primary comparator: `B3_HORIZON2_DONOR_COMPLETE`.

Primary promotion requires all of:
- paired GRS improvement >= +0.10;
- frozen paired-bootstrap 95% stability lower bound > 0;
- no domain difference < -0.10;
- ORION false/unnecessary high-level reformulation <= B3 and <= 0.05 absolute;
- zero harmful lower-level skip;
- zero false resolution of evaluator-gold `UNRESOLVED`;
- zero evaluator/source/gold leakage.

If primary passes, a disjoint-source replication with independent scorer and independent policy reconstruction is mandatory before #649 may close.

## Mutation rule after freeze

After held-out acquisition begins, these frozen policy/protocol files may not be altered on this campaign branch. A bug that makes execution impossible terminates this frozen campaign as invalid and requires a new successor issue/protocol; it cannot be patched after seeing held-out outcomes.
