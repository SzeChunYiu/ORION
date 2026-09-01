# Fail-closed publication contract

## 1. Authority precedence

Identify the newest explicit authority that is applicable to the paper and
claim scope. File timestamps and prose confidence are not authority. Prefer a
machine-readable active-claim selector or disposition that names its scope,
predecessor and evidence bindings. A later package note cannot promote science;
a later scientific disposition may narrow an older package.

Create exactly one current closure record per paper. It must bind hashes for:

- active claim authority or explicit scoped disposition;
- reader-facing source;
- rendered PDF;
- claim/evidence/negative-result ledger;
- source and supplement archives;
- package inventory; and
- the verifier version.

Every reader-visible, disagreeing readiness or terminal record must either be
updated or declare `historical: true` / `superseded_by`. A passing checksum only
proves byte integrity; it does not resolve semantic contradiction.

Fetch and inspect the live result authority twice: once before claim review and
once immediately before the merge candidate is frozen. Record the compared
upstream commit. If upstream advanced, reconcile and rebuild; do not carry a
stale closure forward merely because its package verifier passes.

A historical `CANNOT_CHECK` may become checkable when its named prerequisite is
later supplied. Conversely, a later result can refute a historical positive.
When an authority delta says that no claim promotion is licensed, later prose
may clarify or narrow wording but must not upgrade the terminal.

Resolve paper identity independently of directory identity. A superseded split,
appendix, or earlier manuscript variant is not a separate filing object merely
because it still has a buildable directory. Current registries must enumerate
current papers exactly once and point historical variants to the successor.

## 2. Claim coherence

Use the claim as the unit of review. For each claim record wording, status,
population/universe, unit of analysis, evidence object, uncertainty, comparator,
limitations and prohibited promotions. Check the abstract, introduction,
results, tables/figures, discussion and conclusion. Retain adverse outcomes with
their original denominators and gate interpretation.

Distinguish independent units from technical repeats and fixed strata. Never
turn a designed benchmark contrast into population inference. Never describe
missing files, fields or artifact types as failed cases or attempted external
acquisitions unless an immutable acquisition log establishes that denominator.

## 3. Venue and identity routing

Bind four fields together: venue, article type, official requirements source
and access date, and audience. Rules are conditional:

- anonymized double-blind reviewer artifacts exclude author identity and
  self-identifying links;
- editor-private covers and declarations may contain identity;
- named-review or transparent-review routes may require identity;
- supplementary files follow the selected venue's explicit rule.

Do not apply a repository-wide anonymous-string scan to identified packages.
Do not infer that a cover letter's identity leaks into an anonymous reviewer
archive; inspect audience partitions independently.

Represent routing as a matrix with at least these columns: repository paper ID,
current manuscript identity, venue, article type, official requirement URL and
access date, review model, manuscript audience, supplement audience, and portal
only inputs. Validate the current venue instructions at closure time; inherited
or remembered requirements are not sufficient.

Resolve personal metadata from a single canonical record with explicit
precedence. Apply it consistently to all identified artifacts and reject stale
affiliations, emails, ORCIDs, funding statements or conflicts found elsewhere.
An absent ORCID or institutional affiliation remains absent; never synthesize
one. Double-blind artifacts must be checked in their compiled PDF text, editable
source, bibliography, metadata and reviewer supplement archives, not only in
the top-level TeX file.

## 4. Package completeness

A complete controlled filing object contains, when the venue/article type calls
for them: current manuscript PDF; complete editable source; bibliography and
figures; clearly labelled supplement; data/code availability; declarations;
cover or information sheet; licence/third-party notices; manifest and checksums;
and deterministic build/replay instructions. Verify archive member paths,
compiled text, page count, metadata and readable EOF. Reject stale manifests,
absent declared files, undeclared files and multiple competing PDFs.

When TeX source exists, the arXiv route is source-first: provide a safe archive
with a unique top-level `main.tex`, all local dependencies, no absolute or
parent-traversal members, and a clean successful build. Supply a PDF for review
and comparison, but do not substitute PDF-only filing for buildable source.
Normalize the arXiv abstract to plain ASCII and validate it against the live
length limit. Compare the built source with the released PDF by page count and
normalized extracted text.

Journal packages must use the selected venue's current class/template when it
is mandatory and available, and must include every route-specific object
required for the chosen article type (for example, a Springer information
sheet, an Elsevier highlights file and named generative-AI declaration, or a
double-blind OpenReview checklist). Record any portal confirmation that cannot
be represented honestly as `HUMAN_FILING_ONLY`.

Separate repository-controlled completion from portal-controlled facts such as
author approval, affiliations, ORCIDs, account profiles, submission identifiers,
conflicts, funding and live archive DOIs. Supply explicit placeholders or a
human-input checklist; do not invent them.

## 5. Exact mirrors

A mirror receipt names source repository, source commit/tree, source path,
target repository, target commit/branch and target path. Compare all mirrored
bytes after declared target-only overlays. The verifier must fail on additions,
deletions or content drift. A workflow definition, push attempt or source-side
commit is not proof of a completed mirror; record the target commit or leave the
mirror terminal pending.

Treat overlays as an ownership boundary, not as an unchecked copy exception.
Exclude the same declared overlay names from both sides of the source/target
comparison, restore target-owned directories with replace semantics, and test a
source/overlay name collision explicitly. A directory-copy primitive that
assumes the destination is absent can turn a legitimate future source `code/`
directory into a stopped or partially completed mirror.

Do not place a commit identifier inside the same commit/tree whose identity it
claims to bind. Bind file or subtree hashes in the source package. Resolve the
immutable main commit after merge, mirror that tree, and store source/target
commit receipts outside the mirrored paper roots or in external CI evidence.

## 6. Registry-driven verification

Verifiers accept the requested paper set and fail if any requested identifier is
unregistered or skipped. Avoid fixed scoreboards whose success can silently omit
new papers. Emit a per-paper result and a failing aggregate terminal.

Do not infer coverage from only the files a discovery loop happens to return.
Compare discovered identifiers with the expected registry, then verify one
checksum-closed package for every expected paper. Targeted maintenance commands
must validate their requested identifiers before reading or changing state; a
typo or unsupported paper is an error, never a successful no-op.

The registry terminal must match the active machine-readable scientific
disposition when one exists. Where the authority is prose-only, bind its hash
and quote the exact terminal in the package record. Verification must cover
archive safety, clean builds, PDF readability, claim/negative-result retention,
identity partitioning, route-specific requirements and exact manifests.

## 7. Reproducibility-language calibration

Describe what was actually repeated:

- same code and inputs on another host: `same-source off-host replay`;
- independently reimplemented method against the same specification:
  `independent implementation`;
- new data or independently sampled units: `independent empirical replication`.

Do not promote the first category into the second or third. Bind host, command,
input hashes and output hashes for replay claims, and retain disagreements or
environment-dependent failures as results rather than silently normalizing
them away.

Bind derived-PDF provenance per artifact. If one manuscript is later rebuilt in
a targeted CI run, do not replace batch-global provenance constants in a way
that makes unchanged PDFs appear to come from that later artifact. Record the
actual source revision, workflow run, artifact identifier, build date, engine
and digest for each rendered PDF, and regression-test mixed-run reconciliation.
