# Five-lens review matrix

The packet was reviewed against five non-substitutable roles.

| Role | Background | Assigned question | Public finding |
|---|---|---|---|
| Evidence auditor | reproducible research and provenance | Are every current result, file identity, adverse fact and control-plane reference explicit? | Green for the six-paper tranche; unresolved PR #1722 is excluded from authority. |
| Formal-claim reviewer | formal methods and scientific inference | Do terminals follow from the evidence scope? | Green only with zero scientific-authority delta and ORION-20's order/indispensability distinction enforced. |
| Runtime/trust engineer | software supply-chain security | Is the ORION-25 successor native, pinned and fail-closed? | Green as an outcome-free protocol; organizational independence remains `CANNOT_CHECK`. |
| Reproducibility checker | independent verification and hostile testing | Can common claim-inflation mutations be detected? | Green after ten registered mutation tests, including checksum drift and fake LUNARC success. |
| Integration custodian | Git/branch and programme coordination | Does the change avoid protected branches, manuscript collisions and duplicate programmes? | Green as one additive top-level packet on a `shadow/*` branch; PRs #1698 and #1691 remain canonical. |

Agreement across all roles is limited to the integration result. No role treats an
unexecuted protocol, open pull request or engineering-ready runner as a new scientific
outcome.
