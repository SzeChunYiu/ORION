# Paper 1 hostile Nature Machine Intelligence Article stress test

**Date:** 2026-08-24  
**Status:** internal simulated review, not peer review or an editorial decision  
**Target:** *Nature Machine Intelligence* (NMI), Article, initial submission  
**Independence boundary:** the validity, positioning and reproducibility reports
below are same-context lenses, not mutually blind external reviews.

## Evidence and checks

- Current manuscript, claim ledger, historical package identity and V11--V13
  packets.
- V11, V12 and V13 `SHA256SUMS`: every entry verified from the repository root.
  Manifest-file digests are respectively
  `8ebd874f0b0a7f3a3a7877c698dee1371352ebc4ce5dc3bb1a1bd2a2d0629721`,
  `7a136154d7fbc3c52d51ea2dade7829446842c21381f3c9c912189d47dc29407`
  and `c2ff7a87356559bfce4ea4033aae807a6a5c4ce03b8b43c29782b58c29d33667`.
- Fresh temporary Tectonic build: 45 pages, no undefined reference, undefined
  citation, overfull box or fatal diagnostic. Pages 1, 11, 22, 30, 35, 39 and
  40 were visually inspected with no clipping, overlap, broken display or
  unreadable glyph. The build exists only under `/tmp/p1-nmi-audit-build-20260824/`.
- No pytest or repository CI was run, and no tracked PDF or historical package
  artifact was modified.

## NMI criteria card

| Criterion | NMI Article contract | Current ORION-11 readout |
|---|---|---|
| Abstract | at most 150 words, unreferenced | **Pass: 146 words** |
| Main text | at most 3,500 words, excluding abstract, Methods, references and legends | **Fail: about 14.0k words**. A conservative core-section audit gives 13,992 words after excluding the explicit historical Methods file, availability, references and display environments; exact allocation may change the count but not the fourfold mismatch |
| Displays | at most six figures and tables combined | **Pass mechanically: 5/6** (two figures and three tables currently included) |
| References | typically at most 50 | **One over: 51 rendered bibliography items**; do not delete a necessary source merely to hit a typical rather than absolute limit |
| Sequence | unheaded Introduction, Results, Discussion, Methods | **Fail:** sixteen numbered sections and no unified Discussion; historical Methods and Discussion are embedded inside the chronology |
| Metadata | reviewable title and real author/affiliation metadata | **Fail:** `Working framework draft` is a placeholder, not an author line; author names, affiliations and corresponding-author details require author input |
| Availability | separate Data availability and Code availability; central artifacts accessible to reviewers | Headings are now separate, but the current snapshot has no public archive URL, DOI, immutable submission commit or verified repository-level licence |

## Editorial triage simulation

**Posture:** `central_case_requires_new_decisive_evidence` plus
`scope_or_article_type_mismatch`.

ORION-11 contains a coherent finite mechanism claim: typed
responsibility-to-authority licensing matters on registered mechanical worlds
and authored exact contracts, while an information-equivalent product ties.
The manuscript also preserves the historical failed broad hypothesis. These are
strengths. They do not yet make an NMI Article about scientific revision by AI
systems: no owner-independent naturalistic panel, completed authority bundle,
model-bearing external comparison or independent semantic review exists.

The current manuscript is additionally about four times the NMI main-text
allowance and is not shaped as an NMI Article. A destructive prose cut would be
unsafe. The scientific allocation in
`P1_NMI_MAIN_TEXT_SI_COMPRESSION_MAP_2026-08-24.md` must precede rewriting.

## Reviewer 1: validity and statistics

### Major concerns

#### R1-M1. Generator-world inference is not naturalistic population inference

The primary and disjoint v2.2.4 runs each contain 2,882 mechanically generated
worlds: 480 hidden-shift worlds and 2,402 controls. The registered paired
intervals and exact tests are valid only for those frozen mechanical designs.
They do not estimate prevalence or effect across papers, laboratories, models,
scientific domains or deployed research agents.

**Resolution test:** execute the frozen source-clustered naturalistic successor
with owner-independent gold and scoring, a runnable strongest external
comparator, changed semantic hosts, and cluster-level uncertainty. Keep the
mechanical result as mechanism evidence rather than pooling it with naturalistic
cases.

#### R1-M2. The historical H1 must remain negative and separate

The historical test set has 48 cases (the full authored suite is 18 pilot plus
48 test, hence 66 total). ORION-11.H1 remains `NOT_SUPPORTED`: the subject and
strongest matched baseline each achieve 1/48 root successes, the study is
underpowered, and template/path shortcuts affect 33/66 authored cases. The
v2.2.4 successor is narrower and cannot supersede or pool with H1.

**Resolution test:** retain the 48-case negative terminal in the abstract or
main Results, and retain the 66-case pilot-plus-test diagnostic only with its
correct denominator. Never convert completeness of the historical archive into
support.

#### R1-M3. Exact contracts demonstrate a mechanism, not external science

The 400 authored exact contracts show 400/400 for the licensed policy versus
275/400 for a donor-complete interface lacking the coupling. The
information-equivalent product also obtains 400/400. That tie rules out an
inherent expressivity or centralization advantage and must remain visible.

**Resolution test:** test the licensing residual against interface-fair external
systems on independently authored episodes. Do not treat authored contract
cells as naturalistic replications.

## Reviewer 2: novelty, title and target fit

### Major concerns

#### R2-M1. The residual contribution is narrower than the theoretical apparatus

Factorization, Bayes deficiency, controlled-state planning, transcript
separation and rectangularity are donor-derived or standard specializations.
The residual is the science-specific responsibility-to-authority coupling and
its exact mechanism evidence. Without an external consequence, an NMI editor
can read the paper as a formal synthesis plus constructed-world validation.

**Resolution test:** predeclare a prediction that differs from the nearest donor
interfaces and test it under owner-independent naturalistic authority.

#### R2-M2. The title is intelligible but broader than the empirical authority

“Scientific Revision” names the formal target, whereas current empirical
authority is mechanical and exact-contract only. The abstract states that
boundary, so the title is not false, but it carries editorial overbreadth risk.

**Resolution test:** if the naturalistic authority bridge closes, retain the
broad target. Otherwise use a title that explicitly signals a finite mechanism
study or choose a specialist theory/systems venue.

#### R2-M3. The manuscript is not an NMI Article projection

The roughly 14.0k-versus-3.5k mismatch cannot be fixed by sentence polishing.
The current chronology interleaves formal theory, successive mechanisms,
historical evaluation, owner-algebra preflights, availability and limitations.

**Resolution test:** construct a new projection with one central question, one
decisive evidence chain and one Discussion. Move full proofs, development
chronology, historical detail and secondary diagnostics to Methods/SI while
preserving every claim-changing boundary.

## Reviewer 3: reproducibility, release and package identity

### Major concerns

#### R3-M1. The current source and historical package are different objects

`journal_package/RENDER_CLOSURE_STATE.json` marks the historical package
`SUPERSEDED`. A current checksum audit preserves four expected mismatches:
`manuscript/main.tex`, `manuscript/bibliography.bib`,
`evidence/CLAIM_LEDGER.md` and `REPRODUCE.md`. The historical inspected
`journal_package/manuscript.pdf` still verifies against its manifest and remains
a valid record of the earlier source, not of the current manuscript.

**Resolution test:** after scientific and NMI projection edits are frozen,
create an immutable current submission commit, rebuild from a clean checkout,
visually inspect the new PDF, regenerate package identities and never relabel
the historical PDF.

#### R3-M2. Review access and redistribution authority are absent

There is no current archive URL, DOI, immutable submission commit or verified
repository-level licence. Path lists and hashes provide integrity but not an
access route or redistribution authority.

**Resolution test:** verify repository and third-party rights, deposit the
exact review snapshot, record its DOI/URL, and test editor/reviewer access to
all conclusion-bearing data and code.

#### R3-M3. V11--V13 close packet design, not external authority

The adverse state is exact: 117,649 maps comprise 116,929 rejections, 720
unresolved maps and zero certifications. V13 has received 0/7 signed outputs
and closed 0/4 authority acts. V11's governance provenance and V12's chronology
do not supply R7 ownership, delegation, rights, custody or semantic review.

**Resolution test:** execute V13 with separately verifiable actors, apply the
frozen bundle-acceptance gate, and rerun the map audit only if every
noncompensatory authority act closes.

## Editor synthesis (simulated)

**Current verdict: not ready for NMI Article peer review.** The manuscript has a
defensible analytic and finite-mechanism contribution, but four blockers remain:

1. no owner-independent naturalistic or model-bearing evidence;
2. the external authority packet is unsigned and unexecuted;
3. about 14.0k core words versus 3.5k and a non-NMI structure;
4. no immutable reviewable release or valid current package identity.

The minimum efficient path is external execution of V13/V14, followed by the
source-clustered naturalistic comparison, then an evidence-preserving NMI
projection and new immutable release. More metadata search, pytest, CI or
prose-only claim widening cannot close the scientific bridge.

## Exact retained terminal

`P1_V13_CONTENT_ADDRESSED_EXTERNAL_EXECUTION_PACKET_COMPLETE__ZERO_OF_SEVEN_EXTERNAL_SIGNED_OUTPUTS_RECEIVED__ZERO_OF_FOUR_AUTHORITY_ACTS_CLOSED__720_MAPS_UNCHANGED`

