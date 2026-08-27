#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-}:$ROOT/src"
TMLR_STYLE_COMMIT='7bf90efe3a0debbba703c05c43f3ff7e4d4a2992'
SCIENCE_BASE_COMMIT="$(git rev-parse HEAD)"

PAPER_DIRS=(
  papers/orion-06-recursive-recovery
  papers/orion-07-dual-instrument
  papers/orion-08-typed-state
)
SCIENCE_ROOTS=(
  research/extensions/orion-q
  research/extensions/orion-qg
  development/orion-q-max-r0
  development/orion-qg-regime-geometry
  development/orion-q-nlane-closure
)

assert_no_science_mutation () {
  local changed
  changed="$(git diff --name-only "$SCIENCE_BASE_COMMIT" -- "${SCIENCE_ROOTS[@]}" "${PAPER_DIRS[@]}")"
  if [ -n "$changed" ]; then
    echo 'WAVE_B1Q_SCIENCE_MUTATION_FAIL' >&2
    printf '%s\n' "$changed" >&2
    exit 1
  fi
  echo "WAVE_B1Q_SCIENCE_MUTATION_PASS base=$SCIENCE_BASE_COMMIT"
}

audit_pdf () {
  local pdf="$1" label="$2"
  local tmp="${RUNNER_TEMP:-/tmp}/${label}-pdf.txt"
  test -s "$pdf"
  pdfinfo "$pdf" >/dev/null
  pdftotext "$pdf" "$tmp"
  if grep -Eq '\[@[A-Za-z0-9_:-]+' "$tmp"; then
    echo "$label unresolved Markdown citation token" >&2
    exit 1
  fi
  if grep -Eq 'Citation.*undefined|Reference.*undefined' "${pdf%.pdf}.log" 2>/dev/null; then
    echo "$label unresolved LaTeX citation/reference" >&2
    exit 1
  fi
}

write_receipt () {
  local out="$1" id="$2" venue="$3" scientific="$4"
  python - "$out" "$id" "$venue" "$scientific" "$SCIENCE_BASE_COMMIT" <<'PY'
import hashlib, json, pathlib, sys
out = pathlib.Path(sys.argv[1])
id_, venue, scientific, base = sys.argv[2:]
files = []
for path in sorted(p for p in out.rglob('*') if p.is_file() and p.name != 'CLOSURE_RECEIPT.json'):
    files.append({
        'path': str(path.relative_to(out)),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'bytes': path.stat().st_size,
    })
receipt = {
    'schema': 'ORION.BoundedSpecialistPackageReceipt.v1',
    'paper_id': id_,
    'venue': venue,
    'terminal': 'BOUNDED_SPECIALIST_SUBMISSION_READY',
    'scientific_terminal_preserved': scientific,
    'science_base_commit': base,
    'scientific_authority_delta': 'NONE',
    'top_tier_promotion': 'NOT_GRANTED_BY_THIS_PACKAGE',
    'human_filing_metadata_required': True,
    'files': files,
}
(out / 'CLOSURE_RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
PY
}

# Current science manifests are evidence identity checks, not wording checks.
python papers/check_q_qg_science_manifests.py
python papers/build_q_qg_cited_masters.py --clean

# ---------------------------------------------------------------------------
# ORION-06 / Q2 — bounded recovery methodology -> AIJ specialist package.
# ---------------------------------------------------------------------------
python papers/orion-06-recursive-recovery/check_transition_graph.py
out='papers/publication_closure/submissions/ORION-06/AIJ'
work="${RUNNER_TEMP:-/tmp}/orion06-aij"
rm -rf "$out" "$work"
mkdir -p "$out" "$work"
python papers/orion-06-recursive-recovery/submission_aij/build_aij_source.py \
  --cited-master build/q_qg_cited/Q2/MANUSCRIPT_CITED.md \
  --highlights papers/orion-06-recursive-recovery/submission_aij/HIGHLIGHTS.txt \
  --out "$work/prepared.md"
cp build/q_qg_cited/Q2/references.bib "$work/references.bib"
cp papers/orion-06-recursive-recovery/submission_aij/aij_pandoc_template.tex "$work/template.tex"
pandoc "$work/prepared.md" --from=markdown+citations --to=latex --natbib \
  --template="$work/template.tex" -o "$work/main.tex"
pushd "$work" >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
popd >/dev/null
audit_pdf "$work/main.pdf" ORION06
cp "$work/main.pdf" "$out/main.pdf"
cp "$work/main.tex" "$out/main.tex"
cp "$work/references.bib" "$out/references.bib"
cp "$work/prepared.md" "$out/SCIENTIFIC_MASTER_CITED.md"
cp papers/orion-06-recursive-recovery/submission_aij/HIGHLIGHTS.txt "$out/HIGHLIGHTS.txt" 2>/dev/null || true
cp papers/orion-06-recursive-recovery/submission_aij/COVER_LETTER_DRAFT.md "$out/COVER_LETTER_DRAFT.md" 2>/dev/null || true
write_receipt "$out" ORION-06 AIJ 'BOUNDED_NEGATIVE_RESULT_RECOVERY_METHOD'

# ---------------------------------------------------------------------------
# ORION-07 / Q3 — completed prospective dual-instrument case series -> TMLR.
# ---------------------------------------------------------------------------
python papers/orion-07-dual-instrument/replay_q3_v0.py
python papers/orion-07-dual-instrument/check_q3_result_bindings.py
python papers/orion-07-dual-instrument/check_q3_completion.py
out='papers/publication_closure/submissions/ORION-07/TMLR'
work="${RUNNER_TEMP:-/tmp}/orion07-tmlr"
rm -rf "$out" "$work"
mkdir -p "$out" "$work"
python papers/orion-07-dual-instrument/submission_tmlr/build_tmlr_source.py \
  --cited-master build/q_qg_cited/Q3/MANUSCRIPT_CITED.md \
  --out "$work/prepared.md"
cp build/q_qg_cited/Q3/references.bib "$work/references.bib"
cp papers/orion-07-dual-instrument/submission_tmlr/tmlr_pandoc_template.tex "$work/template.tex"
base="https://raw.githubusercontent.com/JmlrOrg/tmlr-style-file/${TMLR_STYLE_COMMIT}"
curl --fail --location --silent --show-error "${base}/tmlr.sty" -o "$work/tmlr.sty"
curl --fail --location --silent --show-error "${base}/tmlr.bst" -o "$work/tmlr.bst"
curl --fail --location --silent --show-error "${base}/fancyhdr.sty" -o "$work/fancyhdr.sty"
pandoc "$work/prepared.md" --from=markdown+citations --to=latex --natbib \
  --template="$work/template.tex" -o "$work/main.tex"
pushd "$work" >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
popd >/dev/null
audit_pdf "$work/main.pdf" ORION07
cp "$work/main.pdf" "$out/main.pdf"
cp "$work/main.tex" "$out/main.tex"
cp "$work/references.bib" "$out/references.bib"
cp "$work/prepared.md" "$out/SCIENTIFIC_MASTER_CITED.md"
cp "$work/tmlr.sty" "$work/tmlr.bst" "$work/fancyhdr.sty" "$out/"
printf '%s\n' "$TMLR_STYLE_COMMIT" > "$out/TMLR_STYLE_COMMIT.txt"
write_receipt "$out" ORION-07 TMLR 'THREE_PROSPECTIVE_FRONTIER_QUESTIONS_COMPLETED_BOUNDED'

# ---------------------------------------------------------------------------
# ORION-08 / Q4 — bounded exact-synthetic typed-state mechanism -> TMLR.
# Publication analysis is recomputed from frozen generators but is secondary
# descriptive analysis and grants no new authority.
# ---------------------------------------------------------------------------
python papers/orion-08-typed-state/publication_analysis.py > "${RUNNER_TEMP:-/tmp}/orion08-publication-analysis.txt"
out='papers/publication_closure/submissions/ORION-08/TMLR'
work="${RUNNER_TEMP:-/tmp}/orion08-tmlr"
rm -rf "$out" "$work"
mkdir -p "$out" "$work"
python papers/orion-08-typed-state/submission_tmlr/build_tmlr_source.py \
  --cited-master build/q_qg_cited/Q4/MANUSCRIPT_CITED.md \
  --out "$work/prepared.md"
cp build/q_qg_cited/Q4/references.bib "$work/references.bib"
cp papers/orion-08-typed-state/submission_tmlr/tmlr_pandoc_template.tex "$work/template.tex"
base="https://raw.githubusercontent.com/JmlrOrg/tmlr-style-file/${TMLR_STYLE_COMMIT}"
curl --fail --location --silent --show-error "${base}/tmlr.sty" -o "$work/tmlr.sty"
curl --fail --location --silent --show-error "${base}/tmlr.bst" -o "$work/tmlr.bst"
curl --fail --location --silent --show-error "${base}/fancyhdr.sty" -o "$work/fancyhdr.sty"
pandoc "$work/prepared.md" --from=markdown+citations --to=latex --natbib \
  --template="$work/template.tex" -o "$work/main.tex"
pushd "$work" >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
popd >/dev/null
audit_pdf "$work/main.pdf" ORION08
cp "$work/main.pdf" "$out/main.pdf"
cp "$work/main.tex" "$out/main.tex"
cp "$work/references.bib" "$out/references.bib"
cp "$work/prepared.md" "$out/SCIENTIFIC_MASTER_CITED.md"
cp "$work/tmlr.sty" "$work/tmlr.bst" "$work/fancyhdr.sty" "$out/"
printf '%s\n' "$TMLR_STYLE_COMMIT" > "$out/TMLR_STYLE_COMMIT.txt"
cp "${RUNNER_TEMP:-/tmp}/orion08-publication-analysis.txt" "$out/PUBLICATION_ANALYSIS_REPLAY.txt"
write_receipt "$out" ORION-08 TMLR 'BOUNDED_EXACT_SYNTHETIC_TYPED_STATE_MECHANISM'

assert_no_science_mutation

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add papers/publication_closure/submissions/ORION-06 \
        papers/publication_closure/submissions/ORION-07 \
        papers/publication_closure/submissions/ORION-08
git diff --check --cached
if ! git diff --cached --quiet; then
  git commit -m 'papers(publication): close Wave B1-Q bounded specialist packages [wave-b1q-materialized]'
fi

git push origin HEAD:chatgpt/all25-publication-closure-20260827
printf 'WAVE_B1Q_FINAL_COMMIT=%s\n' "$(git rev-parse HEAD)"
