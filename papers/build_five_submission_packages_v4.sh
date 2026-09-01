#!/usr/bin/env bash
set -euo pipefail

papers_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(dirname "${papers_root}")"

declare -A manuscript=(
  [A]="theory-A-multitag-constraint-rank/MANUSCRIPT_V3_PIPELINE.md"
  [B]="theory-B-certificate-complexity/MANUSCRIPT_V3_PIPELINE.md"
  [C]="theory-C-low-order-information/MANUSCRIPT_V3_PIPELINE.md"
  [D]="theory-D-falsification-authority/MANUSCRIPT_V3_PIPELINE.md"
  [N]="nonquantum-c5cubed-davenport/MANUSCRIPT_V3_PIPELINE.md"
)

declare -A title=(
  [A]="Zero-Sum Deletion Normal Forms for a Multi-Tag Pauli Grammar"
  [B]="Abstract Zero-Sum Deletion Complexity and Support-One Normalization in a Pauli Model"
  [C]="Low-Order Decision Certificates and Value Limits in a Pauli-String Partition Model"
  [D]="Typed Evidence Licenses for Finite Positive Rule Graphs"
  [N]='Conditional Davenport Corridors and Saturated Obstructions in \(C_5^3\)'
)

declare -A stem=(
  [A]="Zero-Sum_Deletion_Normal_Forms_for_a_Multi-Tag_Pauli_Grammar"
  [B]="Abstract_Zero-Sum_Deletion_Complexity_and_Support-One_Normalization_in_a_Pauli_Model"
  [C]="Low-Order_Decision_Certificates_and_Value_Limits_in_a_Pauli-String_Partition_Model"
  [D]="Typed_Evidence_Licenses_for_Finite_Positive_Rule_Graphs"
  [N]="Conditional_Davenport_Corridors_and_Saturated_Obstructions_in_C5_Cubed"
)

declare -A legacy_stem=(
  [A]="Zero-Sum_Deletion_Normal_Forms_for_Multi-Tag_Quantum_Compilation"
  [B]="Zero-Sum_Deletion_Certificates_versus_Intrinsic_Support_in_Pauli_Compiler_Models"
  [C]="Low-Order_Decision_Certificates_and_Value-Estimation_Limits_in_Structured_Quantum_Compilation"
  [D]="Typed_Evidence_Licenses_for_Finite_Positive_Rule_Graphs"
  [N]="Conditional_Width-One_Bounds_for_Generalized_Davenport_Constants_of_C5_Cubed"
)

unlink_if_file() {
  if [[ -f "$1" ]]; then
    unlink "$1"
  fi
}

copy_ancillary_files() {
  local key="$1"
  local destination="$2"
  local package="$3"
  local source
  mkdir -p "${destination}"
  cp "${repo_root}/LICENSE" "${destination}/LICENSE_CODE.txt"

  case "${key}" in
    A|B|C|N)
      source="${package}/anc"
      ;;
    D)
      source="${package}/artifact"
      ;;
    *)
      echo "Unknown ancillary package key: ${key}" >&2
      exit 1
      ;;
  esac

  if [[ ! -d "${source}" ]]; then
    echo "Missing package-local ancillary directory: ${source}" >&2
    exit 1
  fi
  cp -R "${source}/." "${destination}/"
}

for key in A B C D N; do
  input="${papers_root}/${manuscript[$key]}"
  package="$(dirname "${input}")/submission"
  output_tex="${package}/${stem[$key]}.tex"
  output_pdf="${package}/${stem[$key]}.pdf"
  journal_zip="${package}/${stem[$key]}_journal_source.zip"
  arxiv_zip="${package}/${stem[$key]}_arxiv_source.zip"

  unlink_if_file "${package}/main.pdf"
  unlink_if_file "${package}/main.tex"
  unlink_if_file "${package}/source.zip"
  unlink_if_file "${package}/artifact.zip"
  latexmk -C -outdir="${package}" "${output_tex}" >/dev/null 2>&1 || true

  sed '1d' "${input}" | pandoc \
    --from=markdown+tex_math_single_backslash \
    --to=latex \
    --standalone \
    --shift-heading-level-by=-1 \
    --metadata="title:${title[$key]}" \
    --variable="title:${title[$key]}" \
    --metadata="author:Sze Chun Yiu" \
    --variable='author:Sze Chun Yiu\\\texttt{sze-chun.yiu@fysik.su.se}' \
    --metadata="date:25 August 2026" \
    --variable='header-includes:\DeclareUnicodeCharacter{220E}{\ensuremath{\square}}' \
    --variable=documentclass:article \
    --variable=fontsize:11pt \
    --variable=geometry:margin=1in \
    --variable=colorlinks:true \
    --output="${output_tex}"

  python3 "${papers_root}/postprocess_submission_tex_v5.py" "${output_tex}"

  latexmk -silent -pdf -interaction=nonstopmode -halt-on-error \
    -outdir="${package}" "${output_tex}"
  latexmk -silent -c -outdir="${package}" "${output_tex}"
  find "${package}" -maxdepth 1 -type f \
    \( -name "${stem[$key]}.aux" -o -name "${stem[$key]}.fdb_latexmk" \
       -o -name "${stem[$key]}.fls" -o -name "${stem[$key]}.log" \
       -o -name "${stem[$key]}.out" -o -name "${stem[$key]}.synctex.gz" \) \
    -delete
  for suffix in aux fdb_latexmk fls log out synctex.gz; do
    unlink_if_file "${package}/${stem[$key]}.${suffix}"
  done

  pdfinfo "${output_pdf}" >/dev/null
  pdftotext "${output_pdf}" /dev/null
  if ! tail -c 1024 "${output_pdf}" | grep -a -q '%%EOF'; then
    echo "PDF integrity check failed: ${output_pdf}" >&2
    exit 1
  fi

  staging="$(mktemp -d)"
  mkdir -p "${staging}/journal" "${staging}/arxiv/anc"
  cp "${output_tex}" "${staging}/journal/main.tex"
  cp "${output_tex}" "${staging}/arxiv/main.tex"
  cp "${package}/README.md" "${staging}/journal/README.md"
  cp "${package}/cover_letter.md" "${staging}/journal/cover_letter.md"
  cp "${package}/submission_checklist.md" "${staging}/journal/submission_checklist.md"
  copy_ancillary_files "${key}" "${staging}/arxiv/anc" "${package}"
  cp -R "${staging}/arxiv/anc" "${staging}/journal/anc"

  unlink_if_file "${journal_zip}"
  unlink_if_file "${arxiv_zip}"

  (
    cd "${staging}/journal"
    zip -q -r "${journal_zip}" .
  )
  (
    cd "${staging}/arxiv"
    zip -q -r "${arxiv_zip}" .
  )

  if [[ "${legacy_stem[$key]}" != "${stem[$key]}" ]]; then
    unlink_if_file "${package}/${legacy_stem[$key]}.tex"
    unlink_if_file "${package}/${legacy_stem[$key]}.pdf"
    unlink_if_file "${package}/${legacy_stem[$key]}_journal_source.zip"
    unlink_if_file "${package}/${legacy_stem[$key]}_arxiv_source.zip"
  fi
  for suffix in aux fdb_latexmk fls log out synctex.gz; do
    unlink_if_file "${package}/${stem[$key]}.${suffix}"
  done
  rm -rf "${staging}"
done

echo "Built five title-named PDFs plus journal and arXiv source packages."
