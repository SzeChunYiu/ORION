# ORION-11 claim ledger V1

> **Record of the pre-rewrite manuscript, 2026-08-22.** The manuscript was
> subsequently rewritten so that its claims are about the mechanism rather than
> about a named system, so that internal status tokens do not appear in its
> prose, and so that repository paths and artifact filenames live only in Data
> and code availability. The claim sentences quoted below are the wording of the
> manuscript as it stood when this ledger was cut. **No number, authority,
> supporting artifact or status in this table changed in that rewrite**, and
> none has been edited here: a ledger is a record of what was allowed and on
> what evidence, so it is annotated rather than restated. Where a row names
> `ORION` as the subject of a claim, the rewritten manuscript states the same
> claim about the mechanism and calls the implementation under test the
> *governed policy*; the artifact each row cites is unchanged. Where a row
> records a `CANNOT_CHECK` status, the manuscript now says that the outcome
> *remains undetermined*, which is the same three-valued state under a
> reader-facing name.

This ledger maps every abstract and conclusion claim to a supporting artifact. A row is `SUPPORTED` only when the cited artifact exists in the repository and the stated authority matches that artifact. External superiority remains `CANNOT_CHECK` until the live campaign completes.

| Claim surface | Claim allowed in this revision | Authority | Supporting artifact | Status |
| --- | --- | --- | --- | --- |
| Abstract | ORION explicitly separates object knowledge $K_t$, relevance/search-universe model $W_t$, and governed method state $M_t$. | IMPLEMENTED CONTRACT | `src/orion/core/`; unit tests | `SUPPORTED` |
| Abstract | Typed residuals are diagnosed before high-impact revision. | IMPLEMENTED CONTRACT | `src/orion/engine/cycle.py` responsibility diagnosis | `SUPPORTED` |
| Abstract | Supported formulation/search-universe changes trigger dependency-directed reopening of stale closure. | IMPLEMENTED CONTRACT | `src/orion/engine/operators/reopen.py`; dependency graph tests | `SUPPORTED` |
| Abstract | The workflow recursively audits through inspectable mechanic cells. | IMPLEMENTED CONTRACT | `src/orion/mechanics/` cell model and questioning | `SUPPORTED` |
| Abstract | A frozen deterministic falsifier suite exercises hidden-domain, hidden-representation, missing-evidence and execution-only worlds. | LOCAL FALSIFIER | `evidence/FALSIFIER_V1.md`; suite at commit `8a8a7feed588363f8e2cd820d3399a33b7af3074` | `SUPPORTED` |
| Abstract | The suite exposed an over-broad reframe gate that was repaired. | LOCAL FALSIFIER REPAIR | `evidence/FALSIFIER_V1.md`; git history of gate fix | `SUPPORTED` |
| Abstract | This establishes an implemented and locally falsified mechanism, not external novelty or superiority. | HONEST BOUNDARY | `protocol/PROTOCOL_V1.json` state `outcome_accessed=false` | `SUPPORTED` |
| Abstract | Matched prospective comparisons on fresh hidden-shift tasks remain CANNOT_CHECK. | EXTERNAL NOT EXECUTED | `protocol/PROTOCOL_V1.json`; execution_bindings frozen but campaign incomplete | `SUPPORTED` |
| Results | Mechanical arm attributes correct responsibility on 62 of 66 cases. | DESCRIPTIVE ONLY | `evidence/MECHANICAL_ARM_LIMITATIONS_V1.md`; 62/66 from audit | `SUPPORTED` |
| Results | Zero of 22 negative controls topped by formulation responsibility. | DESCRIPTIVE ONLY | `evidence/MECHANICAL_ARM_LIMITATIONS_V1.md`; 0/22 control false-flags | `SUPPORTED` |
| Results | Four general relations cover 26 cases. | DESCRIPTIVE ONLY | `evidence/MECHANICAL_ARM_LIMITATIONS_V1.md`; relation case counts | `SUPPORTED` |
| Results | Independent blind audit rates 55 of 66 cases SOLVABLE from public content. | DESCRIPTIVE ONLY | `evidence/MECHANICAL_SOLVABILITY_AUDIT_V1.md`; 55/66 SOLVABLE | `SUPPORTED` |
| Results | Pre-gold family prediction accuracy is 61 of 66. | DESCRIPTIVE ONLY | `evidence/MECHANICAL_SOLVABILITY_AUDIT_V1.md`; 61/66 accuracy | `SUPPORTED` |
| Results | Five arithmetic defects were found and confirmed (c013, c014, c139, c142, c143). | DESCRIPTIVE ONLY | `evidence/MECHANICAL_SOLVABILITY_AUDIT_V1.md` defects section | `SUPPORTED` |
| Results | Achieved tier is BELOW_TIER_D; study is underpowered. | DESCRIPTIVE ONLY | `generated/suite_facts.tex`; `\AchievedTier`, `\Underpowered` | `SUPPORTED` |
| Results | Required N for H1 is 385; for H2 is 2401. | DESCRIPTIVE ONLY | `generated/suite_facts.tex`; `\RequiredNForH1`, `\RequiredNForH2` | `SUPPORTED` |
| Results | Template-level leaks exist (66/66 separation on framing phrase). | DESCRIPTIVE ONLY | `evidence/MECHANICAL_SOLVABILITY_AUDIT_V1.md` Probe 1 | `SUPPORTED` |
| Conclusion | ORION makes K/W/M explicit co-evolving state rather than hidden context. | DEFINITION | `src/orion/core/` state representation | `SUPPORTED` |
| Conclusion | Discoveries/failures target distinct formulation coordinates. | IMPLEMENTED CONTRACT | `src/orion/engine/cycle.py` typed responsibility | `SUPPORTED` |
| Conclusion | Material reframe stales dependent closure. | IMPLEMENTED CONTRACT | `src/orion/engine/operators/reopen.py` dependency tracking | `SUPPORTED` |
| Conclusion | Workflow recursively decomposed into inspectable mechanics. | IMPLEMENTED CONTRACT | `src/orion/mechanics/` cell decomposition | `SUPPORTED` |
| Conclusion | Local falsifier exposed invalid reframe path (singular EVIDENCE/EXECUTION entering reframe). | LOCAL NEGATIVE CONTROL | `evidence/FALSIFIER_V1.md`; gate repair documented | `SUPPORTED` |
| Conclusion | External comparison against matched baselines remains open. | EXTERNAL NOT EXECUTED | `protocol/PROTOCOL_V1.json` execution_bindings frozen but campaign incomplete | `SUPPORTED` |
| Related Work | AREX contributes recursive audit/follow-up; not claimed as novel. | NEAREST WORK ABSORPTION | `evidence/NEAREST_WORK_MATRIX_V2.md` AREX row | `SUPPORTED` |
| Related Work | SCION contributes dependency-aware planning; not claimed as novel. | NEAREST WORK ABSORPTION | `evidence/NEAREST_WORK_MATRIX_V2.md` SCION row | `SUPPORTED` |
| Related Work | Iris contributes evolving information state; not claimed as novel. | NEAREST WORK ABSORPTION | `evidence/NEAREST_WORK_MATRIX_V2.md` Iris row | `SUPPORTED` |
| Related Work | SciAgentArena contributes realistic evaluation; not claimed as novel. | NEAREST WORK ABSORPTION | `evidence/NEAREST_WORK_MATRIX_V2.md` SciAgentArena row | `SUPPORTED` |
| Safety | Paper I cannot authorize $M_t$ to rewrite itself. | IMPLEMENTED BOUNDARY | Paper IV owns method evolution; Paper I only exposes failures | `SUPPORTED` |

## Promotion rule

No row marked `CANNOT_CHECK` may be rewritten as positive evidence. The external superiority comparison requires completion of the live campaign with frozen execution bindings before any H1/H2 claim can be promoted from `CANNOT_CHECK`. The 62/66 mechanical arm attribution and 55/66 solvability results are descriptive-only (n=66 < required inferential n) and are not promoted to H1 support.
