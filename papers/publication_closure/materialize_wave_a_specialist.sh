#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

export PYTHONPATH="${PYTHONPATH:-}:$ROOT/src"
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'

# Freeze the exact scientific/control subject before any repository-side
# materialization occurs. Wave-A's current-authority checker validates the
# bounded quantum objects at this subject; the guard below then proves that no
# protected science root changes during publication materialization.
SCIENCE_BASE_COMMIT="$(git rev-parse HEAD)"
export ORION_PUBLICATION_SCOPE_BASE="$SCIENCE_BASE_COMMIT"
SCIENCE_ROOTS=(
  research/extensions/orion-q
  research/extensions/orion-qg
  development/orion-q-max-r0
  development/orion-qg-regime-geometry
  development/orion-q-nlane-closure
)
assert_science_unchanged () {
  local changed
  changed="$(git diff --name-only "$SCIENCE_BASE_COMMIT" -- "${SCIENCE_ROOTS[@]}")"
  if [ -n "$changed" ]; then
    echo 'WAVE_A_SCIENCE_IMMUTABILITY_FAIL' >&2
    printf '%s\n' "$changed" >&2
    exit 1
  fi
  echo "WAVE_A_SCIENCE_IMMUTABILITY_PASS base=$SCIENCE_BASE_COMMIT"
}

# ---------------------------------------------------------------------------
# 1. Fail closed on the current scientific/control surfaces.
# ---------------------------------------------------------------------------
python papers/check_wave_a_publication_closure.py --json
python papers/publication_closure/check_wave_a_quantum_authority.py
python papers/check_q_qg_science_manifests.py
python papers/build_q_qg_cited_masters.py --clean

Q_REPLAY_DIR="${RUNNER_TEMP:-/tmp}/wave-a-quantum-replay"
rm -rf "$Q_REPLAY_DIR"
mkdir -p "$Q_REPLAY_DIR"
Q_REPLAY_RECEIPT="$Q_REPLAY_DIR/QUANTUM_REPLAY_RECEIPT_V1.json"
python papers/publication_closure/run_wave_a_quantum_replays.py --out "$Q_REPLAY_RECEIPT"

python papers/orion-17-epistemic-navigation-open-worlds/formal/check_countermodels.py
python papers/candidates/checkers/p7_finite_falsifiers_v1.py

ORION14_TMP="${RUNNER_TEMP:-/tmp}/orion14-filing"
rm -rf "$ORION14_TMP"
mkdir -p "$ORION14_TMP"
python papers/publication_closure/check_orion14_filing_preflight.py \
  --root "$ROOT" \
  --as-of "$(date -u +%F)" \
  --write-json "$ORION14_TMP/REPOSITORY_FILING_PREFLIGHT_V1.json" \
  --write-md "$ORION14_TMP/REPOSITORY_FILING_PREFLIGHT_V1.md"

bash papers/orion-19-structured-epistemic-learning/build_tmlr_pdf.sh
python papers/publication_closure/check_orion22_r0_rebind_equivalence.py
make -C papers/orion-22-adaptive-state-reasoning/manuscript
PYTHONPATH=src python papers/orion-23-responsibility-carrying-state/check_lifecycle_consolidation_binding_v1.py
make -C papers/orion-23-responsibility-carrying-state/manuscript

# Reader-visible citation syntax must be resolved in the actual PDFs, not merely
# present in a sidecar bibliography file.
for pdf in \
  papers/orion-22-adaptive-state-reasoning/manuscript/main.pdf \
  papers/orion-23-responsibility-carrying-state/manuscript/main.pdf; do
  txt="${RUNNER_TEMP:-/tmp}/$(basename "$(dirname "$(dirname "$pdf")")")-citation-audit.txt"
  pdftotext "$pdf" "$txt"
  if grep -Fq '[@' "$txt"; then
    echo "unresolved Markdown citation token in $pdf" >&2
    exit 1
  fi
done
assert_science_unchanged

# ---------------------------------------------------------------------------
# 2. Commit deterministic current-paper render changes, then re-bind manifests
#    to that exact clean subject. Coordination documents live outside paper
#    trees and are therefore not content-bound scientific bytes.
# ---------------------------------------------------------------------------
git add -u \
  papers/orion-19-structured-epistemic-learning \
  papers/orion-22-adaptive-state-reasoning \
  papers/orion-23-responsibility-carrying-state
if ! git diff --cached --quiet; then
  git diff --check --cached
  git commit -m 'papers(publication): refresh current Wave A rendered papers'
fi
RENDER_COMMIT="$(git rev-parse HEAD)"

git clean -fdX \
  papers/orion-19-structured-epistemic-learning \
  papers/orion-22-adaptive-state-reasoning \
  papers/orion-23-responsibility-carrying-state || true
python scripts/regen_paper_manifests.py --papers orion-19,orion-22,orion-23

git add \
  papers/orion-19-structured-epistemic-learning/CONTENT_MANIFEST_V1.json \
  papers/orion-19-structured-epistemic-learning/SHA256SUMS \
  papers/orion-22-adaptive-state-reasoning/CONTENT_MANIFEST_V1.json \
  papers/orion-22-adaptive-state-reasoning/SHA256SUMS \
  papers/orion-23-responsibility-carrying-state/CONTENT_MANIFEST_V1.json \
  papers/orion-23-responsibility-carrying-state/SHA256SUMS
if ! git diff --cached --quiet; then
  git diff --check --cached
  git commit -m 'papers(publication): bind current Wave A paper bytes'
fi
SOURCE_COMMIT="$(git rev-parse HEAD)"

# Re-run result/package gates after binding. They must reproduce without changing
# the content-bound paper trees.
python papers/orion-19-structured-epistemic-learning/reproduce_final.py
python papers/orion-19-structured-epistemic-learning/audit_final_manuscript.py
python papers/publication_closure/check_orion22_r0_rebind_equivalence.py
PYTHONPATH=src python papers/orion-23-responsibility-carrying-state/check_lifecycle_consolidation_binding_v1.py

git diff --exit-code -- \
  papers/orion-19-structured-epistemic-learning \
  papers/orion-22-adaptive-state-reasoning \
  papers/orion-23-responsibility-carrying-state
assert_science_unchanged

# ---------------------------------------------------------------------------
# 3. Target-specific TQE packages for the three bounded quantum papers.
# ---------------------------------------------------------------------------
declare -A IDS=( [Q1]=ORION-05 [QG1]=ORION-09 [QG2]=ORION-10 )
TQE_ABSTRACTS='papers/publication_closure/tqe/TQE_ABSTRACTS_V1.json'
for p in Q1 QG1 QG2; do
  id="${IDS[$p]}"
  out="papers/publication_closure/submissions/${id}/TQE"
  work="${RUNNER_TEMP:-/tmp}/wave-a-tqe/${p}"
  rm -rf "$out" "$work"
  mkdir -p "$out" "$work"

  # First perform the existing citation-only/scientific-master projection and
  # venue abstract compression. Then apply the separate result-bound verifier;
  # only Q1 may receive the R11 algorithmic section.
  python papers/quantum_preprint/build_quantum_source.py \
    --paper "$p" \
    --cited-master "build/q_qg_cited/${p}/MANUSCRIPT_CITED.md" \
    --abstract-overrides-json "$TQE_ABSTRACTS" \
    --out "$work/prepared_base.md"
  python papers/publication_closure/apply_tqe_submission_projection.py \
    --paper "$p" \
    --prepared-in "$work/prepared_base.md" \
    --out "$work/prepared.md" \
    | tee "$work/TQE_PROJECTION_REPORT.txt"

  cp "build/q_qg_cited/${p}/references.bib" "$work/references.bib"
  cp papers/quantum_preprint/tqe_pandoc_template.tex "$work/template.tex"

  python - "$work/prepared.md" "$work/ABSTRACT_WORD_COUNT.txt" <<'PY'
import pathlib, re, sys
src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
m = re.search(r'^abstract: \|\n(?P<body>(?:  .*\n)+?)dataavailability: \|', src, flags=re.M)
if not m:
    raise SystemExit('cannot extract YAML abstract')
text = ' '.join(line.strip() for line in m.group('body').splitlines())
n = len(re.findall(r"\b[\w'-]+\b", text))
pathlib.Path(sys.argv[2]).write_text(f'{n}\n', encoding='utf-8')
if not 150 <= n <= 250:
    raise SystemExit(f'TQE abstract word count {n} outside 150..250')
PY

  pandoc "$work/prepared.md" --from=markdown+citations --to=latex --natbib \
    --template="$work/template.tex" -o "$work/main.tex"
  pushd "$work" >/dev/null
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  bibtex main
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  pdflatex -interaction=nonstopmode -halt-on-error main.tex
  popd >/dev/null

  test -s "$work/main.pdf"
  pdfinfo "$work/main.pdf" >/dev/null
  pdftotext "$work/main.pdf" "$work/text.txt"
  grep -Fq 'AUTHOR METADATA REQUIRED BEFORE SUBMISSION' "$work/text.txt"
  if grep -Eq '\[@[A-Za-z0-9_:-]+' "$work/text.txt"; then
    echo "${id}: unresolved citation token in PDF" >&2
    exit 1
  fi
  if grep -Eq 'LaTeX Warning: (Citation|Reference).*undefined|There were undefined references' "$work/main.log"; then
    echo "${id}: unresolved LaTeX citation/reference" >&2
    exit 1
  fi

  cp "$work/main.pdf" "$out/main.pdf"
  cp "$work/main.tex" "$out/main.tex"
  cp "$work/references.bib" "$out/references.bib"
  cp "build/q_qg_cited/${p}/MANUSCRIPT_CITED.md" "$out/SCIENTIFIC_MASTER_CITED.md"
  cp "$work/prepared.md" "$out/SUBMISSION_PROJECTION.md"
  cp "$work/TQE_PROJECTION_REPORT.txt" "$out/TQE_PROJECTION_REPORT.txt"
  cp "$work/ABSTRACT_WORD_COUNT.txt" "$out/ABSTRACT_WORD_COUNT.txt"
  cp "$TQE_ABSTRACTS" "$out/TQE_ABSTRACTS_V1.json"
  cp "$Q_REPLAY_RECEIPT" "$out/QUANTUM_REPLAY_RECEIPT_V1.json"
  cp -R "$Q_REPLAY_DIR/quantum-replay-raw" "$out/quantum-replay-raw"
  if [ "$p" = 'Q1' ]; then
    cp papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_RESULT_V1.json \
      "$out/Q1_R11_SPARSE_DIRECT_EXECUTABLE_RESULT_V1.json"
    cp papers/orion-05-tare-expressivity/Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md \
      "$out/Q1_R11_SPARSE_DIRECT_EXECUTABLE_PROTOCOL_V1.md"
    cp papers/publication_closure/tqe/ORION-05_R11_ADDENDUM.md \
      "$out/ORION-05_R11_ADDENDUM.md"
  fi
  find "$out" -type f ! -name SHA256SUMS -print0 | sort -z | while IFS= read -r -d '' f; do sha256sum "$f"; done | sed "s#  $out/#  #" > "$out/SHA256SUMS"
done
assert_science_unchanged

# ---------------------------------------------------------------------------
# 4. Existing AIJ/TMLR/JAAMAS specialist objects.
# ---------------------------------------------------------------------------
# ORION-17 has a self-contained bibliography in AIJ_MANUSCRIPT.tex.
out='papers/publication_closure/submissions/ORION-17/AIJ'
work="${RUNNER_TEMP:-/tmp}/wave-a-aij17"
rm -rf "$out" "$work"
mkdir -p "$out" "$work"
cp papers/orion-17-epistemic-navigation-open-worlds/submission/AIJ_MANUSCRIPT.tex "$work/main.tex"
cp papers/orion-17-epistemic-navigation-open-worlds/manuscript/bibliography.bib "$work/bibliography.bib"
pushd "$work" >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
popd >/dev/null
test -s "$work/main.pdf"
pdfinfo "$work/main.pdf" >/dev/null
cp "$work/main.pdf" "$out/main.pdf"
cp "$work/main.tex" "$out/AIJ_MANUSCRIPT.tex"
cp "$work/bibliography.bib" "$out/bibliography.bib"
printf '%s\n' \
  'formal/check_countermodels.py: PASS' \
  'p7_finite_falsifiers_v1.py: PASS' \
  'AIJ LaTeX build: PASS' > "$out/CHECKS.txt"
(cd "$out" && sha256sum main.pdf AIJ_MANUSCRIPT.tex bibliography.bib CHECKS.txt > SHA256SUMS)

# ORION-14: use the current tracked TMLR PDF/source after the green filing preflight.
out='papers/publication_closure/submissions/ORION-14/TMLR'
rm -rf "$out"
mkdir -p "$out/source/manuscript"
cp papers/orion-14-verified-scientific-discovery/manuscript/main.pdf "$out/main.pdf"
cp -R papers/orion-14-verified-scientific-discovery/manuscript/. "$out/source/manuscript/"
if [ -d papers/orion-14-verified-scientific-discovery/journal_package ]; then
  cp -R papers/orion-14-verified-scientific-discovery/journal_package "$out/source/journal_package"
fi
cp "$ORION14_TMP/REPOSITORY_FILING_PREFLIGHT_V1.json" "$out/REPOSITORY_FILING_PREFLIGHT_V1.json"
find "$out" -type f ! -name SHA256SUMS -print0 | sort -z | while IFS= read -r -d '' f; do sha256sum "$f"; done | sed "s#  $out/#  #" > "$out/SHA256SUMS"

materialize_current () {
  local id="$1" paper="$2" venue="$3"
  local out="papers/publication_closure/submissions/${id}/${venue}"
  rm -rf "$out"
  mkdir -p "$out/sections"
  cp "$paper/manuscript/main.pdf" "$out/main.pdf"
  cp "$paper/manuscript/main.tex" "$out/main.tex"
  cp "$paper/manuscript/references.bib" "$out/references.bib"
  find "$paper/manuscript/sections" -maxdepth 1 -type f -print0 | while IFS= read -r -d '' f; do cp "$f" "$out/sections/"; done
  printf '%s\n' \
    'native replay/checkers: PASS' \
    'current manuscript build: PASS' \
    'content manifest: BOUND' > "$out/CHECKS.txt"
}

materialize_current ORION-19 papers/orion-19-structured-epistemic-learning TMLR
materialize_current ORION-22 papers/orion-22-adaptive-state-reasoning TMLR
materialize_current ORION-23 papers/orion-23-responsibility-carrying-state JAAMAS
cp papers/publication_closure/submissions/ORION-23/JAAMAS_INFORMATION_SHEET.md \
  papers/publication_closure/submissions/ORION-23/JAAMAS/JAAMAS_INFORMATION_SHEET.md

for out in \
  papers/publication_closure/submissions/ORION-19/TMLR \
  papers/publication_closure/submissions/ORION-22/TMLR \
  papers/publication_closure/submissions/ORION-23/JAAMAS; do
  find "$out" -type f ! -name SHA256SUMS -print0 | sort -z | while IFS= read -r -d '' f; do sha256sum "$f"; done | sed "s#  $out/#  #" > "$out/SHA256SUMS"
done
assert_science_unchanged

# ---------------------------------------------------------------------------
# 5. Commit exact packages, then make one final fail-closed closure receipt.
# ---------------------------------------------------------------------------
git add papers/publication_closure/submissions
git diff --check --cached
if ! git diff --cached --quiet; then
  git commit -m 'papers(publication): materialize exact Wave A specialist packages'
fi
PACKAGE_COMMIT="$(git rev-parse HEAD)"

receipt='papers/publication_closure/receipts/WAVE_A_SPECIALIST_CLOSURE_V1.json'
python papers/publication_closure/build_wave_a_specialist_receipt.py \
  --source-commit "$SOURCE_COMMIT" \
  --package-commit "$PACKAGE_COMMIT" \
  --out "$receipt"
git add "$receipt"
git diff --check --cached
if ! git diff --cached --quiet; then
  git commit -m 'papers(publication): close Wave A specialist repository packages [wave-a-materialized]'
fi
assert_science_unchanged

git push origin HEAD:chatgpt/orion-publication-closure-wave-a-20260827

printf 'WAVE_A_SCIENCE_BASE_COMMIT=%s\n' "$SCIENCE_BASE_COMMIT"
printf 'WAVE_A_RENDER_COMMIT=%s\n' "$RENDER_COMMIT"
printf 'WAVE_A_SOURCE_COMMIT=%s\n' "$SOURCE_COMMIT"
printf 'WAVE_A_PACKAGE_COMMIT=%s\n' "$PACKAGE_COMMIT"
printf 'WAVE_A_FINAL_COMMIT=%s\n' "$(git rev-parse HEAD)"
