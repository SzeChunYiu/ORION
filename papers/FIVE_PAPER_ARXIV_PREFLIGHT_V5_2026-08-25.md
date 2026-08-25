# Five-paper arXiv preflight V5

> Historical report. Superseded by `FIVE_PAPER_ARXIV_PREFLIGHT_V7_2026-08-25.md`;
> its titles, targets, package claims, and readiness decisions are not current.

Date: 2026-08-25

Branch: `codex/orion-publication-rewrite-20260825`

Scientific closure: `FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS`

## Verified manuscript identities

| Paper | Source of record | Target after arXiv | Current disposition |
|---|---|---|---|
| A | `theory-A-multitag-constraint-rank/MANUSCRIPT_V3_PIPELINE.md` | Quantum | Corrected and packaged; binary alphabet/rank equality is explicit |
| B | `theory-B-certificate-complexity/MANUSCRIPT_V3_PIPELINE.md` | ACM Transactions on Quantum Computing | Corrected and packaged; production-family proofs are reader-facing |
| C | `theory-C-low-order-information/MANUSCRIPT_V3_PIPELINE.md` | Quantum; QIP fallback | Corrected and packaged; the C1-C3 constructions and proofs are explicit |
| D | `theory-D-falsification-authority/MANUSCRIPT_V3_PIPELINE.md` | Journal of Automated Reasoning | Corrected and packaged; retraction order and proof are defined |
| Non-quantum | `nonquantum-c5cubed-davenport/MANUSCRIPT_V3_PIPELINE.md` | Electronic Journal of Combinatorics | Corrected and packaged; the support-ten computer-assisted proof is exposed |

Each source remains in the shared branch/worktree above. No manuscript was
rewritten from a detached or competing source tree.

## Release-stopping correction

Paper A no longer claims that an alphabet spanning a binary signature group can
have a zero-sum-free threshold below the group's rank. The manuscript now states
and proves that if (H=\langle A\rangle\cong\mathbb F_2^d), then the spanning
alphabet contains a basis and

\[
\operatorname{zsf}(H;A)=\operatorname{rank}(H)=d.
\]

The generated-package verifier contains a dedicated failure gate for this
identity. The obsolete strict-refinement claim cannot pass the pipeline.

## Surface and metadata corrections

- All five abstracts use inline mathematics only and a true LaTeX `abstract`
  environment; no display equation is opened in an abstract.
- The title pages and PDF metadata identify `Sze Chun Yiu` and
  `sze-chun.yiu@fysik.su.se`.
- The five PDFs use precise title-based filenames.
- Development labels such as `R6M`, `R6I`, `QG*`, and `ORION` are absent from
  each manuscript, generated TeX file, and generated PDF.
- The struck unified/universal-calculus novelty claim remains absent.
- The placeholder schema URI was replaced with a relative schema identifier.

## Packaging and QA

For every paper, `submission/` contains:

1. a title-named PDF;
2. a matching self-contained TeX source;
3. a title-named journal source archive; and
4. a title-named arXiv source archive with top-level `main.tex` and an `anc/`
   directory, excluding cover letters and journal checklists.

The final verifier passed all checks, including abstract length, inline-only
abstract math, author identity, PDF parsing and EOF integrity, source-archive
integrity, internal-label absence, the Paper A binary equality gate, inherited
scientific gates, nine Paper D evaluator tests, schema validation, and all V5
checksums. First and last pages of all five PDFs were also rendered and visually
inspected.

Checksums are recorded in `FIVE_PAPER_ARXIV_CHECKSUMS_V5.sha256`.

## Remaining author-controlled actions

The artifacts are prepared but have not been finally submitted to arXiv. arXiv
requires the submitter to select an irrevocable distribution license, certify
the right to grant it, use a registered/endorsed account where required, verify
the compiled preview and metadata, and press the final Submit Article control.
The author's affiliation and any ORCID also remain unconfirmed. Those legal and
identity choices must not be inferred from the email domain.

Recommended primary categories are `quant-ph` for A-C, `cs.LO` for D, and
`math.CO` for the non-quantum paper. Quantum specifically requires A and C to be
posted to or cross-listed with `quant-ph` before journal submission.
