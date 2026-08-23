# P1-U GPT-R2 evaluator freeze receipt V1

Campaign: #711  
Parent: #649

Evaluator/test commit before this receipt: `7e6c707cfea45161671052e7fbf71fece30ecb74`.

Frozen evaluator surfaces:
- `research/claim_expansion/p1/gpt_r2/evaluate.py`;
- `tests/unit/p1/test_p1_u_r2_evaluator.py`;
- `research/claim_expansion/p1/gpt_r2/HELDOUT_ACQUISITION_PLAN_V1.json`.

The evaluator was frozen before execution of any of the 28 acquisition queries.

## Fail-closed boundaries

- Policies receive dossier text plus an evaluator-owned `ProbeGate`; gold class, source identity, source URL, query id and corrective disposition are absent from policy input.
- Probe enumeration is forbidden by the gate.
- Every revealed probe observation must match the policy's declared trace exactly.
- Probe cost equals actual gate reveals and cannot exceed two.
- Duplicate source identities, unexpected/missing query identities, invalid observations and >90-word dossiers fail closed.
- Primary corpus cannot promote if any frozen query is missing.
- Primary promotion cannot occur without the fixed margin, stability, domain, harm, unresolved and leakage guards.

After held-out acquisition begins, evaluator/acquisition-plan files listed above are immutable for this campaign. Any discovered scoring defect after outcome access invalidates this campaign and requires a new successor freeze rather than a same-corpus patch.
