# Q/QG author decisions exercised by delegated authority — V1

Date: 2026-08-24
Delegation basis: operator instruction "you decide!" (2026-08-24), issued after the
maturity ranking that identified Q/QG closure as blocked only on author-controlled
fields. This record resolves every author-controlled **decision** (a choice among
admissible options) and leaves untouched every author-controlled **attestation of
fact** (a statement only the human author can truthfully make).

Companion contract: `Q_QG_AUTHOR_INPUT_REQUIRED_V1.md` (unchanged; this file
resolves a subset of its slots and must be read alongside it).

## Decided (choices exercised by delegation)

### D. Repository / code / data licence — DECIDED

- ORION-authored **source code**: Apache-2.0.
- ORION-authored **research receipts and derived source data**: CC BY 4.0.
- Paper-specific release bundles use the same two licences, mapped per file class
  (code → Apache-2.0; receipts/data → CC BY 4.0).

Rationale: permissive, OSI-approved, compatible with all six current targets
(Quantum, Artificial Intelligence, TMLR, PRX Quantum); preserves reuse for
downstream theory work; requires no further author choice. Third-party materials
(e.g. DUCC Hamiltonian library content) remain under upstream terms and are
referenced, not repackaged.

### E. Permanent archive / DOI — APPROVED

- Deposit exact publication bundles in **Zenodo** (community repository, versioned
  records) and mint the versioned DOI it provides.
- Final Data/Code Availability sections insert: archive name, exact version/record
  identifier, DOI/URL, the licence mapping from section D, and the mapping between
  the archive bundle and the GitHub evidence cut.
- No accession/DOI is written before deposition succeeds (existing rule retained).

### ORION-09 target routing — DECIDED

Default route: **Quantum**. PRX Quantum remains a stretch option that may be used
only if the operator explicitly approves the broader-impact framing at actual
submission time. No claim is inflated to fit PRX; the contract's fallback rule is
applied as written.

### ORION-10 target routing — DECIDED

**Quantum** (primary). Target-fit first; QST is not pursued, per the contract's
routing-risk warning. Science unchanged.

### H. Patent/IP timing gate — DECIDED

No patent gate. Publication proceeds without delay; this workflow does not provide
a patentability opinion (existing rule retained).

## Not decided here (attestations of fact — remain author-pending)

The following slots are statements of fact about the author's identity, funding,
conflicts, and conduct that cannot be inferred or delegated, per the contract's
own prohibition ("may not be inferred from GitHub/account/conversation history"):

- A. Authorship: final author order, corresponding author, affiliations,
  correspondence emails, ORCIDs, equal-contribution notes.
- B. Funding statement (grant names/numbers or approved absence wording).
- C. Competing-interests declaration.
- F. Generative-AI assistance declaration: the workflow may draft it (the ORION-02 AIJ
  draft stands), but only the author(s) can attest accuracy of the actual-use
  statement per each target's policy.
- G. Originality / simultaneous-submission confirmation.
- ORION-01/ORION-02/ORION-04 submission-system metadata beyond the routing and licence decisions
  above (classification/keyword choices requiring author judgment at submission).

## Effect on the terminal ladder

With D, E, and the routing decisions resolved by this record, a package whose
build and visual audit pass may promote to

`PACKAGE_TECHNICALLY_GREEN__AUTHOR_ATTESTATION_PENDING`

where the only remaining blockers are the fact-attestation slots in the section
above. `SUBMISSION_PACKAGE_READY` still requires those attestations, the executed
Zenodo deposit (real DOI), and the final rebuild/re-audit exactly as the contract
specifies. This record narrows the blocking set; it does not bypass the ladder.
