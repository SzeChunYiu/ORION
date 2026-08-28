# ORION-01 V3 build and verification

Run all commands from this directory.

## Required tools

- Python 3.11 or newer (standard library is sufficient for the checker and manifest builder)
- Pandoc 3.x
- XeLaTeX from TeX Live
- `sha256sum`, `pdfinfo`, and `pdftotext`

## Independent theorem checks

```bash
python proof_checker_v3.py --output PROOF_CHECK_RESULT_V3.json
python -m unittest -v test_proof_checker_v3.py
```

The checker intentionally imports no ORION or PyZX production module. Its finite terminal is not an all-size proof and does not regenerate the parent compiler witnesses.

## PDF build

```bash
pandoc theory-A-MANUSCRIPT_V3.md \
  --from=gfm --standalone --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V colorlinks=true \
  -o theory-A-MANUSCRIPT_V3.pdf

pandoc theory-B-MANUSCRIPT_V3.md \
  --from=gfm --standalone --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V colorlinks=true \
  -o theory-B-MANUSCRIPT_V3.pdf
```

## Structural PDF checks

```bash
pdfinfo theory-A-MANUSCRIPT_V3.pdf
pdfinfo theory-B-MANUSCRIPT_V3.pdf
pdftotext theory-A-MANUSCRIPT_V3.pdf - | grep -F 'BOUNDED_PAPER_RETAINED'
pdftotext theory-B-MANUSCRIPT_V3.pdf - | grep -F 'BOUNDED_PAPER_RETAINED'
```

A release operator must also render and visually inspect every page for clipping, malformed equations, broken tables, or missing glyphs. Structural checks do not replace visual inspection.

## Manifest and checksums

```bash
python build_manifest_v3.py
sha256sum \
  README.md PR1602_ADOPTION_RECEIPT.json \
  theory-A-MANUSCRIPT_V3.md theory-A-MANUSCRIPT_V3.pdf \
  theory-B-MANUSCRIPT_V3.md theory-B-MANUSCRIPT_V3.pdf \
  PROOF_REPAIR_DISPOSITION_V3.md NOVELTY_AUDIT_V2.md \
  proof_checker_v3.py test_proof_checker_v3.py PROOF_CHECK_RESULT_V3.json \
  DATA_CODE_AVAILABILITY.md LICENSE.md COVER_LETTER_A.md COVER_LETTER_B.md \
  SUBMISSION_MANIFEST_V3.json > SHA256SUMS
python build_manifest_v3.py --verify
```

The committed workflow performs these steps and may commit the generated PDFs, final manifest, and checksum ledger back to its branch. A generated-artifact commit does not add peer-review or submission authority.

## Freeze rules

- Do not edit the frozen V2 manuscripts in place.
- Do not reinterpret PR #1602's terminal.
- Do not raise the old cap and call it the same experiment.
- Do not mark the package release-ready unless both PDFs exist, all checks pass, the manifest verifies, and every page has been visually inspected.
