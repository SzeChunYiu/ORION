# ORION submission policy V1

Author-set defaults for every ORION paper. Venue requirements override these
only where a venue **mandates** the section; otherwise the default is omission.

## Author block

Canonical identity lives in `papers/AUTHOR_IDENTITY_V1.json`. Summary:

- **Name:** Sze Chun Yiu
- **Email:** sze-chun.yiu@fysik.su.se
- **Affiliation:** Independent Researcher. Stockholm University is not an
  affiliation for this work and must not appear in submission materials.

**Double-blind review copies keep `\author{Anonymous authors}`.** TMLR review is
double-blind and `q4-tmlr-package.yml` runs an anonymity audit; substituting the
named block into a review PDF breaks review and fails that audit. The named
block belongs on arXiv, camera-ready, and cover letters.

## Sections that are OMITTED by default

| section | default | rationale |
|---|---|---|
| Acknowledgements | **omit** | author instruction |
| Funding statement | **omit** | no funding to declare |
| Conflict of interest | **omit** | none to declare |
| Competing interests | **omit** | none to declare |

Where a venue **mandates** a declaration rather than allowing omission, use the
shortest truthful negative form — e.g. *"The author declares no competing
interests."* / *"No funding was received for this work."* — and nothing more. Do
not invent a funder, a grant number, or an acknowledgee under any circumstance.

## AI-usage disclosure

Where a venue requires disclosure of AI assistance, use a single sentence,
placed where the venue specifies, and **well inside** any stated word limit:

> Generative AI tools were used for drafting and editing assistance. The author
> is responsible for all scientific content.

Rationale: venue policies (e.g. Elsevier, Springer Nature, IEEE, ACM) require
that AI use be disclosed, that AI is **not** listed as an author, and that the
author retains responsibility. The sentence above satisfies all three in ~25
words, comfortably under every limit encountered. Where a venue asks for a named
tool or a specific location (title page vs. a declarations section), adapt
placement and naming; do not expand the substance.

**AI is never an author, is never in the author list, and is never
acknowledged** — the latter both because acknowledgements are omitted by default
and because several venues explicitly forbid acknowledging AI as a contributor.

## Standing author defaults — do not re-ask

These are settled. Apply them without asking:

- **Email:** `sze-chun.yiu@fysik.su.se` on every paper, every venue.
- **Affiliation:** `Independent Researcher`. This research has no institutional
  involvement from Stockholm University, so that institution is never listed.
- **Every optional submission question defaults to NO** — optional sections,
  optional declarations, optional supplementary offers, opt-ins. If a venue
  makes it optional, omit it.
- **AI disclosure:** always the minimal form that satisfies the venue, and
  always comfortably below any stated word limit. Never expand it, never name
  additional tools, never volunteer detail the venue did not ask for.

## Precedence

1. A venue's **mandatory** requirement.
2. This policy.
3. Paper-local convention.

A paper that silently carries an acknowledgements, funding, or COI section
contrary to this policy is a defect to fix, not a local exception.

`grants_authority: NONE`
