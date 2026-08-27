# ORION-23 — JAAMAS information sheet

**Submission object:** responsibility-carrying state / responsibility-relative certified reuse  
**Article type:** Regular Paper  
**Status:** author-attestation draft; scientific claims below are bounded to the current repository authority and do not grant submission authority.

## What is the main claim of the paper, and why is it an important contribution?

The paper's main claim is that the authority to reuse a stored scientific state is **responsibility-relative**. A state can be current, provenance-carrying and supported by a valid certificate yet still be insufficient for a downstream responsibility that asks a stronger or different question. Reuse therefore requires the stored certificate to discharge the active responsibility; when the responsibility changes, the correct operation may be preserve, reopen, revoke, or remain undetermined rather than unconditional reuse.

This matters for autonomous and multi-agent systems because provenance, freshness and confidence do not by themselves specify what a stored result is authorized to support. The paper makes that distinction executable. It represents responsibility as part of the state/certificate contract, defines reopen semantics when the contract changes, and tests the resulting reuse rule against controlled donor policies that ignore responsibility or react only to state signatures.

The contribution is deliberately narrower than generic provenance, schema evolution, memory staleness or policy governance. Those mechanisms are prior work. The residual contribution is the responsibility key and the non-compensatory reuse/reopen decision it induces.

## What evidence is provided to support the claim?

The evidence is a set of bounded, separately interpretable studies rather than a claim of universal workflow safety.

1. **Real-data responsibility shift.** A digits study contains 17,970 registered episodes. Under the frozen responsibility-relative rule, the mechanism preserves the required decision contract while reducing raw reads by 48.4375% in the executed regime. The unit of interpretation is the registered responsibility-shift experiment, not each episode as an independent scientific population.

2. **Verifier-backed exact domain.** A CNF study provides mechanically checkable outcomes. The responsibility-carrying rule is verifier-correct on 24/24 registered cases and reduces raw reads by 44.44% under the frozen accounting. The verifier supplies the outcome authority for those cases; repository replay does not turn this into a claim about arbitrary workflows.

3. **Matched donor comparison.** In the registered 48-case donor comparison, donor arms that omit the responsibility condition achieve 36/48 supported decisions and make 12 unsupported reuses, whereas the responsibility-carrying/composed rule achieves 48/48 under the same controlled contract. The paper treats those donor arms as transparent mechanisms, not as evidence against every provenance or memory system.

4. **Transport stress test.** A 60-case drift study separates two characteristic failure modes. Unconditional transport yields 40 unsound transports, while a signature-only policy produces 20 needless reissues. The responsibility-aware rule is evaluated against both because safety alone is not enough if obtained by reopening everything.

5. **Historical negative retained.** The earlier P13A self-entailed safety endpoint is not used as independent safety authority. It remains a methodological negative in the evidence history, and the later controlled result is presented as a different, repaired evaluation object rather than a retroactive validation of the original endpoint.

The package binds the claim ledger, authority records, deterministic replay/checkers, raw evidence and regenerated manuscript. External, naturally occurring responsibilities in an independently governed real research workflow remain an optional stronger validation route; they are not required for the bounded claim above and are not implied by this information sheet.

## Principal limitations relevant to review

- Responsibilities in the current controlled studies are specified within the experimental contract rather than obtained from an independently governed production workflow.
- Perfect finite-case agreement is contract conformance, not a universal safety guarantee.
- Public provenance and schema-evolution systems already own generic provenance-under-evolution functionality; this paper claims only the responsibility-scoped authority layer above such mechanisms.
- Reproducibility and independent model-based checking establish consistency of the bounded evidence, not human expert adjudication or deployment authority.

## Author attestations still required before portal submission

- final author order and affiliations;
- corresponding author;
- funding, conflicts and acknowledgements;
- CRediT roles if requested by the submission system;
- journal-required AI-use disclosure;
- confirmation that the final PDF/source bytes match the bound submission package.
