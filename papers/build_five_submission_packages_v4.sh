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
  [A]="Zero-Sum Deletion Normal Forms for Multi-Tag Quantum Compilation"
  [B]="Zero-Sum Deletion Certificates versus Intrinsic Support in Quantum Compilation"
  [C]="Low-Order Decision Certificates and Value-Estimation Limits in Structured Quantum Compilation"
  [D]="Typed Evidence Licenses for Finite Positive Rule Graphs"
  [N]='Conditional Width-One Bounds for Generalized Davenport Constants of \(C_5^3\)'
)

declare -A stem=(
  [A]="Zero-Sum_Deletion_Normal_Forms_for_Multi-Tag_Quantum_Compilation"
  [B]="Zero-Sum_Deletion_Certificates_versus_Intrinsic_Support_in_Quantum_Compilation"
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
  mkdir -p "${destination}"
  cp "${repo_root}/LICENSE" "${destination}/LICENSE_CODE.txt"

  case "${key}" in
    A)
      cp "${repo_root}/research/extensions/orion-qg/PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json" \
        "${destination}/multitag_normal_form_results.json"
      ;;
    B)
      cp "${repo_root}/research/extensions/orion-qg/QG18_TARE_KAPPA_RESULTS.json" \
        "${destination}/one_tag_three_block_witness_results.json"
      cp "${repo_root}/research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json" \
        "${destination}/dependent_triple_support_one_results.json"
      ;;
    C)
      cp "${repo_root}/research/extensions/orion-qg/paper_c_c1_all_m_decision.py" \
        "${destination}/decision_certificate.py"
      cp "${repo_root}/research/extensions/orion-qg/PAPER_C_C1_ALL_M_DECISION_RESULTS_2026-08-24.json" \
        "${destination}/decision_certificate_results.json"
      cp "${repo_root}/development/orion-qg-regime-geometry/paper_c_c1_generic_verify.py" \
        "${destination}/verify_decision_certificate.py"
      cp "${repo_root}/research/extensions/orion-qg/paper_c_c2_pair_value_separation.py" \
        "${destination}/pair_value_separation.py"
      cp "${repo_root}/research/extensions/orion-qg/PAPER_C_C2_PAIR_GAIN_VALUE_SEPARATION_RESULTS_2026-08-24.json" \
        "${destination}/pair_value_separation_results.json"
      cp "${repo_root}/development/orion-qg-regime-geometry/paper_c_c2_generic_verify.py" \
        "${destination}/verify_pair_value_separation.py"
      cp "${repo_root}/research/extensions/orion-qg/paper_c_c3_rwise_value_separation.py" \
        "${destination}/proper_marginal_separation.py"
      cp "${repo_root}/research/extensions/orion-qg/PAPER_C_C3_RWISE_VALUE_SEPARATION_RESULTS_2026-08-24.json" \
        "${destination}/proper_marginal_separation_results.json"
      cp "${repo_root}/development/orion-qg-regime-geometry/paper_c_c3_generic_verify.py" \
        "${destination}/verify_proper_marginal_separation.py"
      ;;
    D)
      cp "${papers_root}/theory-D-falsification-authority/evidence_license_evaluator.py" \
        "${destination}/evidence_license_evaluator.py"
      cp "${papers_root}/theory-D-falsification-authority/evidence_license_schema.json" \
        "${destination}/evidence_license_schema.json"
      cp "${papers_root}/theory-D-falsification-authority/test_evidence_license_evaluator.py" \
        "${destination}/test_evidence_license_evaluator.py"
      mkdir -p "${destination}/examples"
      cp "${papers_root}/theory-D-falsification-authority/examples/"*.json \
        "${destination}/examples/"
      ;;
    N)
      cp "${repo_root}/research/orion-rg/x1k_property_c_support_check.c" \
        "${destination}/support_eight_search.c"
      cp "${repo_root}/research/orion-rg/x1k_c0_support9_check.c" \
        "${destination}/support_nine_search.c"
      cp "${repo_root}/research/orion-rg/x1k_c0_support10_13_rank3_bytes.c" \
        "${destination}/support_ten_search_bytes.c"
      cp "${repo_root}/research/orion-rg/x1k_c0_support10_13_rank3_u128.c" \
        "${destination}/support_ten_search_u128.c"
      cp "${repo_root}/research/orion-rg/NONQUANTUM_M2_SATURATION_DEFECT_REPLAY_RESULTS_2026-08-24.json" \
        "${destination}/support_eight_to_nine_results.json"
      cp "${repo_root}/research/orion-rg/NONQUANTUM_M3_SUPPORT10_REPLAY_RESULTS_2026-08-24.json" \
        "${destination}/support_ten_results.json"
      cp "${repo_root}/development/orion-rg-davenport/nonquantum_m2_generic_verify.py" \
        "${destination}/verify_support_eight_to_nine.py"
      cp "${repo_root}/development/orion-rg-davenport/nonquantum_m3_generic_verify.py" \
        "${destination}/verify_support_ten.py"
      ;;
  esac
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
  copy_ancillary_files "${key}" "${staging}/arxiv/anc"
  cp -R "${staging}/arxiv/anc" "${staging}/journal/anc"

  (
    cd "${staging}/journal"
    zip -q -r "${journal_zip}" .
  )
  (
    cd "${staging}/arxiv"
    zip -q -r "${arxiv_zip}" .
  )
  rm -rf "${staging}"
done

echo "Built five title-named PDFs plus journal and arXiv source packages."
