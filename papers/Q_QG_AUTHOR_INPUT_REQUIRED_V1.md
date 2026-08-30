# Q/QG author-input contract V1

Purpose: isolate facts the publication workflow is **not authorized to infer**. All five content-ready papers can continue through scientific/citation/render/target preflight without these values, but final submission authority remains blocked until the applicable fields are explicitly supplied and reviewed by the author(s).

## A. Authorship and affiliations — required for ORION-01/ORION-02/ORION-09/ORION-10 final non-blind packages

> **RESOLVED (operator, 2026-08-30) — applies to every ORION paper.** Sole author
> `Sze Chun Yiu`; contact `sze-chun.yiu@fysik.su.se`; **no institutional
> affiliation** on named arXiv surfaces, `Stockholm University, Stockholm,
> Sweden` only where a venue/portal requires an affiliation; no ORCID; no
> acknowledgements; no funding (`The author received no specific funding for
> this work.`); no competing interests (`The author declares no competing
> interests.`); substantive venue-compliant generative-AI declarations as pinned
> in `papers/top_tier_gap_closure/ARXIV_AUTHOR_INPUT_GATE_2026-08-29.md`
> (AI never listed as author; author responsibility asserted).


For each paper:
- final author list in order;
- corresponding author(s);
- institutional affiliation(s), including department/unit where applicable;
- correspondence email(s);
- ORCID(s), if authors choose/provide them;
- any equal-contribution / joint-supervision notes, if genuinely applicable.

ORION-04/TMLR review package remains anonymous, but the submission system still needs non-public author metadata entered by the submitting author.

**Do not infer authorship from GitHub commits, account identity, conversation history, or prior papers.**

## B. Funding — required if target asks

Provide exact grant/funder names and grant numbers, or an explicit author-approved no-funding statement if accurate.

**Do not infer absence of funding.**

## C. Competing interests — required if target asks

Provide the author-approved declaration.

**Do not infer “no competing interests.”**

## D. Repository/code/data licence decision

Current publication cuts contain no root licence that authorizes the workflow to describe ORION as open source.

Author decision needed for:
- licence for ORION-authored source code;
- licence for ORION-authored research receipts/derived source data;
- whether paper-specific release bundles use the same or different licence(s).

Third-party materials such as DUCC Hamiltonian library content remain under their upstream terms and should normally be referenced rather than repackaged unless redistribution is clearly authorized.

## E. Permanent archive / DOI

Author approval needed to deposit exact publication bundles in a permanent archive (e.g. Zenodo or another suitable repository) and mint a versioned identifier/DOI.

The final Data/Code Availability sections should insert:
- archive/repository name;
- exact version/record identifier;
- DOI/URL;
- licence(s);
- mapping between archive bundle and GitHub evidence cut.

Do not invent an accession/DOI before deposition succeeds.

## F. Generative-AI assistance declaration

A draft disclosure is included in the ORION-02 AIJ package. Each target paper requires the author(s) to confirm:
- which AI systems/tools require disclosure under the current target policy;
- what roles they played (research assistance, coding, literature search, writing/editing, figure/package generation, etc.);
- that the submitted declaration accurately reflects actual use.

The workflow may draft the statement but cannot make the factual attestation for the author.

## G. Originality / simultaneous submission

Before each submission, the submitting author must confirm:
- the manuscript is not under consideration elsewhere in a conflicting form;
- all authors approve the submission;
- any overlapping manuscripts/preprints are disclosed as required.

## H. Optional patent/IP timing check

If the author intends to seek patent protection for any implementation before public preprint/journal disclosure, obtain qualified patent-professional advice **before** final public release. The publication workflow does not provide a patentability or filing opinion and will not delay publication unless the author requests this gate.

## Paper-specific target metadata

### ORION-01 / Quantum
- authors/affiliations;
- archive/licence;
- any Quantum submission-system classification/keyword choices that require author judgment.

### ORION-02 / Artificial Intelligence
- authors/affiliations/correspondence;
- funding/COI;
- confirm generative-AI statement;
- confirm originality/simultaneous-submission statement;
- archive/licence.

### ORION-04 / TMLR
- submission-system author metadata entered separately from anonymous review PDF;
- archive/licence;
- confirm current TMLR policy declarations.

### ORION-09 / PRX Quantum stretch (or Quantum fallback)
- authors/affiliations;
- archive/licence;
- confirm popular-summary/front-matter requirements at actual submission;
- if PRX broad-impact framing is not author-approved, use Quantum fallback rather than inflating the claim.

### ORION-10 / Quantum
- authors/affiliations;
- archive/licence;
- if author prefers QST despite target-fit risk, confirm the routing decision without changing science.

## Final authority rule

The publication workflow may emit:

`PACKAGE_TECHNICALLY_GREEN__AUTHOR_INPUT_PENDING`

when builds, references, figures and visual audits pass but these fields remain unresolved.

It may emit `SUBMISSION_PACKAGE_READY` only after the required author-controlled facts have been supplied, inserted, and the exact final PDF/source bundle has been rebuilt and visually audited.
