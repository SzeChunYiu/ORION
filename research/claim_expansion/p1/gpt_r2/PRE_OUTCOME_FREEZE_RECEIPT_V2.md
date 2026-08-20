# P1-U GPT-R2 pre-outcome freeze receipt V2

Campaign: #711  
Parent: #649  
Freeze time: 2026-08-20, before held-out source acquisition.

## Frozen policy subject

Repaired base: `main@ea7543fc5b6ad14f151215d87dc7ed81253a8269`.

Policy/test commit before this receipt: `2e26d691939049643c85bb65d446d54974b43475`.

Load-bearing frozen files:
- `development/p1-u-gpt-r2-naturalistic/DEVELOPMENT_PACKET.md`;
- `research/claim_expansion/p1/gpt_r2/PROTOCOL_V1.json`;
- `research/claim_expansion/p1/gpt_r2/policy.py`;
- `tests/unit/p1/test_p1_u_r2_naturalistic_policy.py`.

The scientific policy bytes are the same as the abandoned/conflicted #713 lane; only the base identity was advanced to include the process-repair merge #712.

No held-out case dossier, gold responsibility label, evaluator probe outcome, or policy outcome had been acquired or inspected when commit `2e26d691...` was created.

## Development-only source quarantine

Excluded from held-out evaluation because they were inspected before freeze:
- Model Discovery Agent / NeuronBench (`arXiv:2608.09696`);
- Self-Revising Discovery Systems for Science (`arXiv:2606.01444`);
- SCION (`arXiv:2607.03863`);
- Robin (`10.1038/s41586-026-10652-y`);
- RootCauseBench;
- Dapaah & Grabowski 2026 ML-pipeline RCA (`10.1007/s11334-026-00642-8`).

## Frozen promotion rule

Primary comparator: `B3_HORIZON2_DONOR_COMPLETE`.

Primary promotion requires all of:
- paired GRS improvement >= +0.10;
- frozen paired-bootstrap 95% stability lower bound > 0;
- no domain difference < -0.10;
- ORION false/unnecessary high-level reformulation <= B3 and <= 0.05 absolute;
- zero harmful lower-level skip;
- zero false resolution of evaluator-gold `UNRESOLVED`;
- zero evaluator/source/gold leakage.

If primary passes, disjoint-source replication with an independent scorer and independent policy reconstruction is mandatory before #649 may close.

## Mutation rule after acquisition begins

The four frozen policy/protocol/test files above may not change after held-out acquisition begins. An execution-blocking defect discovered after outcome access invalidates this campaign and requires a new successor freeze; it cannot be patched on the same held-out corpus.
