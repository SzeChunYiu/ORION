# ORION-P4 Claim Ledger V1

Each headline claim in Paper IV is mapped to its exact evidence path. Claims marked `CANNOT_CHECK` are not supported by external evidence in this manuscript; they are prospective hypotheses awaiting the protected campaign.

| # | Claim | Evidence Type | Location | Status |
|---|-------|--------------|----------|--------|
| 1 | Citation correctness and factual support do not establish scientific authority | Reasoning | main.tex §1, §2 | Established by argument |
| 2 | Evidence records must resolve through host-owned content/provenance identity | Implementation | Kernel evidence binding | Tested locally (local falsifier in `evidence/FALSIFIER_V1.md`) |
| 3 | Claim correctness, evidence identity, source attribution, semantic support, and content provenance are distinct coordinates | Implementation + related work | main.tex §3 | Established by mechanism (ProvenanceGuard baseline) |
| 4 | A checker is not authoritative solely by returning a score | Implementation | Kernel checker registry | Tested locally (weak checker + same-lane tests) |
| 5 | Evaluation is an attack surface requiring prospective freeze | Threat model + related work | main.tex §4, THREAT_MODEL_V1.md | Established by RewardHackingAgents literature |
| 6 | Search-time contamination inflates benchmark performance | Related work | main.tex §4, §6 | Established by STC literature |
| 7 | Non-escalating authority: promotion requires registered prerequisites; default is CANNOT_CHECK/BLOCK | Implementation + protocol | main.tex §5, PROTOCOL_V1.json | Tested locally (fail-closed kernel) |
| 8 | The full ORION pipeline reduces false scientific-authority promotion under attack | Prospective hypothesis | PROTOCOL_V1.json H1 | **CANNOT_CHECK** — awaiting external campaign |
| 9 | Safety gain does not come from blocking everything | Prospective hypothesis | PROTOCOL_V1.json H2 | **CANNOT_CHECK** — awaiting external campaign |
| 10 | CANNOT_CHECK/BLOCK is selected correctly when evidence is insufficient | Prospective hypothesis | PROTOCOL_V1.json H3 | **CANNOT_CHECK** — awaiting external campaign |
| 11 | 5-percentage-point absolute reduction vs strongest baseline is a feasible design target | Design choice | PROTOCOL_V1.json §statistics.practical_margin | Prospective margin, not a result |
| 12 | Clean authority coverage is non-inferior within 5 percentage points | Design choice | PROTOCOL_V1.json §statistics.practical_margin | Prospective margin, not a result |
| 13 | No finite hostile battery proves universal evaluator security | Limitation | THREAT_MODEL_V1.md, main.tex §9 | Established by argument |
| 14 | The protocol, attack taxonomy, baselines, ablations, and statistical plan are frozen | Protocol artifact | PROTOCOL_V1.json (status: DESIGN_FROZEN) | Verified by test suite (`test_journal_protocol_assets.py`) |
| 15 | External results are not reported in this manuscript | Boundary statement | main.tex §8 | Verified by manuscript text |

## Evidence Paths

- **Local implementation evidence:** Kernel tests in `tests/unit/kernel/` cover identity/content substitution, provenance identity, weak checkers, same-lane checking, and chronology.
- **Local falsifier evidence:** `evidence/FALSIFIER_V1.md` documents the authority-laundering falsifier cases.
- **Protocol evidence:** `protocol/PROTOCOL_V1.json` is the frozen protocol artifact, validated by `research/paper-programme-v1/protocols/publication_manifest.py`.
- **Related work evidence:** Citations in `bibliography.bib` point to external systems that establish baseline capabilities.
- **External campaign evidence:** Issue #59 owns the protected hostile benchmark programme. Evidence is **CANNOT_CHECK** until the campaign completes.

## Negative Claims

- Provenance tracking, claim-level auditability, contamination detection, and evaluator locking are not ORION novelty claims.
- The manuscript does not claim external results. All quantitative claims about false-promotion reduction are prospective hypotheses.