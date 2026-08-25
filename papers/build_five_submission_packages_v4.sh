#!/usr/bin/env bash
set -euo pipefail

papers_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

declare -A manuscript=(
  [A]="theory-A-multitag-constraint-rank/MANUSCRIPT_V3_PIPELINE.md"
  [B]="theory-B-certificate-complexity/MANUSCRIPT_V3_PIPELINE.md"
  [C]="theory-C-low-order-information/MANUSCRIPT_V3_PIPELINE.md"
  [D]="theory-D-falsification-authority/MANUSCRIPT_V3_PIPELINE.md"
  [N]="nonquantum-c5cubed-davenport/MANUSCRIPT_V3_PIPELINE.md"
)

declare -A title=(
  [A]="Alphabet-Davenport Normal Forms for Multi-Tag Quantum Compilation"
  [B]="Certificate Complexity Can Exceed Intrinsic Support in Quantum Compilation"
  [C]="Low-Order Optimality Certificates and Sharp Value-Estimation Limits in Structured Quantum Compilation"
  [D]="Typed Evidence-License Propagation and Retraction in Positive Scientific Rule Graphs"
  [N]='A Width-One Generalized-Davenport Corridor in \(C_5^3\) and a Rank-Forcing Obstruction Phase'
)

for key in A B C D N; do
  input="${papers_root}/${manuscript[$key]}"
  package="$(dirname "${input}")/submission"

  sed '1d' "${input}" | pandoc \
    --from=markdown+tex_math_single_backslash \
    --to=latex \
    --standalone \
    --shift-heading-level-by=-1 \
    --variable="title:${title[$key]}" \
    --metadata="author:Author information to be supplied before submission" \
    --metadata="date:Review source - 25 August 2026" \
    --variable='header-includes:\DeclareUnicodeCharacter{220E}{\ensuremath{\square}}' \
    --variable=documentclass:article \
    --variable=fontsize:11pt \
    --variable=geometry:margin=1in \
    --variable=colorlinks:true \
    --output="${package}/main.tex"

  latexmk -pdf -interaction=nonstopmode -halt-on-error \
    -outdir="${package}" "${package}/main.tex"
  latexmk -c -outdir="${package}" "${package}/main.tex"
  find "${package}" -maxdepth 1 -type f \
    \( -name 'main.aux' -o -name 'main.fdb_latexmk' -o -name 'main.fls' \
       -o -name 'main.log' -o -name 'main.out' -o -name 'main.synctex.gz' \) \
    -delete

  pdfinfo "${package}/main.pdf" >/dev/null
  pdftotext "${package}/main.pdf" /dev/null
  if ! tail -c 1024 "${package}/main.pdf" | grep -a -q '%%EOF'; then
    echo "PDF integrity check failed: ${package}/main.pdf" >&2
    exit 1
  fi

  (
    cd "${package}"
    zip -q -j source.zip main.tex README.md cover_letter.md submission_checklist.md
  )
done

artifact="${papers_root}/theory-D-falsification-authority/submission/artifact"
mkdir -p "${artifact}/examples"
cp "${papers_root}/theory-D-falsification-authority/evidence_license_evaluator.py" "${artifact}/"
cp "${papers_root}/theory-D-falsification-authority/evidence_license_schema.json" "${artifact}/"
cp "${papers_root}/theory-D-falsification-authority/test_evidence_license_evaluator.py" "${artifact}/"
cp "${papers_root}/theory-D-falsification-authority/examples/"*.json "${artifact}/examples/"
(
  cd "${papers_root}/theory-D-falsification-authority/submission"
  zip -q -r artifact.zip artifact
  zip -q -u source.zip artifact.zip
)

echo "Built five compile-tested submission packages."
