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

## 4. Package completeness

A complete controlled filing object contains, when the venue/article type calls
for them: current manuscript PDF; complete editable source; bibliography and
figures; clearly labelled supplement; data/code availability; declarations;
cover or information sheet; licence/third-party notices; manifest and checksums;
and deterministic build/replay instructions. Verify archive member paths,
compiled text, page count, metadata and readable EOF. Reject stale manifests,
absent declared files, undeclared files and multiple competing PDFs.

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

Do not place a commit identifier inside the same commit/tree whose identity it
claims to bind. Bind file or subtree hashes in the source package. Resolve the
immutable main commit after merge, mirror that tree, and store source/target
commit receipts outside the mirrored paper roots or in external CI evidence.

## 6. Registry-driven verification

Verifiers accept the requested paper set and fail if any requested identifier is
unregistered or skipped. Avoid fixed scoreboards whose success can silently omit
new papers. Emit a per-paper result and a failing aggregate terminal.
