#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-}:$ROOT/src"
SCIENCE_BASE_COMMIT="$(git rev-parse HEAD)"
PAPERS=(
  papers/orion-11-recursive-epistemic-reconstruction
  papers/orion-12-open-world-scientific-discovery
  papers/orion-13-global-knowledge-portrait
)

assert_no_paper_mutation () {
  local changed
  changed="$(git diff --name-only "$SCIENCE_BASE_COMMIT" -- "${PAPERS[@]}")"
  if [ -n "$changed" ]; then
    echo 'WAVE_B1P1_PAPER_MUTATION_FAIL' >&2
    printf '%s\n' "$changed" >&2
    exit 1
  fi
  echo "WAVE_B1P1_PAPER_MUTATION_PASS base=$SCIENCE_BASE_COMMIT"
}

assert_text () {
  local path="$1" needle="$2"
  grep -Fq "$needle" "$path" || { echo "missing required boundary: $path :: $needle" >&2; exit 1; }
}

build_scratch_pdf () {
  local paper="$1" label="$2"
  local work="${RUNNER_TEMP:-/tmp}/${label}-build"
  rm -rf "$work"
  mkdir -p "$work"
  cp -R "$paper/manuscript/." "$work/"
  rm -f "$work/main.pdf" "$work/main.aux" "$work/main.bbl" "$work/main.blg" "$work/main.log" "$work/main.out" "$work/main.fls" "$work/main.fdb_latexmk"
  pushd "$work" >/dev/null
  latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex >&2
  if grep -Eiq 'LaTeX Warning: (Citation|Reference).*undefined|There were undefined references|There were undefined citations' main.log; then
    echo "$label undefined citation/reference" >&2
    exit 1
  fi
  test -s main.pdf
  pdfinfo main.pdf >/dev/null
  pdftotext main.pdf main.txt
  if grep -Eq '\[@[A-Za-z0-9_:-]+' main.txt; then
    echo "$label unresolved Markdown citation token" >&2
    exit 1
  fi
  popd >/dev/null
  python scripts/audit_manuscript_clipping.py "$work/main.pdf" --root "$ROOT" >&2
  printf '%s\n' "$work"
}

write_receipt () {
  local out="$1" id="$2" venue="$3" terminal="$4" boundary="$5"
  python - "$out" "$id" "$venue" "$terminal" "$boundary" "$SCIENCE_BASE_COMMIT" <<'PY'
import hashlib, json, pathlib, sys
out = pathlib.Path(sys.argv[1])
id_, venue, terminal, boundary, base = sys.argv[2:]
files=[]
for p in sorted(x for x in out.rglob('*') if x.is_file() and x.name != 'CLOSURE_RECEIPT.json'):
    files.append({'path':str(p.relative_to(out)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes':p.stat().st_size})
receipt={
 'schema':'ORION.BoundedSpecialistPackageReceipt.v1',
 'paper_id':id_, 'venue':venue,
 'terminal':'BOUNDED_SPECIALIST_SUBMISSION_READY',
 'scientific_terminal_preserved':terminal,
 'claim_boundary':boundary,
 'science_base_commit':base,
 'scientific_authority_delta':'NONE',
 'top_tier_promotion':'NOT_GRANTED_BY_THIS_PACKAGE',
 'human_filing_metadata_required':True,
 'reviewer_access_archive_or_doi':'HUMAN_FILING_STEP_REQUIRED',
 'files':files,
}
(out/'CLOSURE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
PY
}

python papers/check_all25_closure_manifest.py

# ---------------------------------------------------------------------------
# ORION-11 — powered mechanical necessity mechanism, JAIR specialist route.
# ---------------------------------------------------------------------------
(cd research/revival/p1/confirmatory/v2.2/primary && sha256sum -c SHA256SUMS)
(cd research/revival/p1/confirmatory/v2.2/replication && sha256sum -c SHA256SUMS)
python - <<'PY'
import json, pathlib
base=pathlib.Path('research/revival/p1/confirmatory/v2.2')
for name in ('primary','replication'):
    v=json.loads((base/name/'INDEPENDENT_VERIFICATION.json').read_text())
    assert v['verdict']=='PASS'
    assert v['score_mismatch_count']==0
    assert v['analysis_mismatch_count']==0
c=json.loads((base/'PRIMARY_REPLICATION_CONCORDANCE.json').read_text())
assert all(c['required_concordance'].values())
print('ORION11_POWERED_PRIMARY_REPLICATION=PASS')
PY
assert_text papers/orion-11-recursive-epistemic-reconstruction/JOURNAL_READINESS.md 'The bounded mechanical claim is `SUPPORTED`'
python - <<'PY'
import pathlib, re
p=pathlib.Path('papers/orion-11-recursive-epistemic-reconstruction/JOURNAL_READINESS.md')
text=p.read_text(encoding='utf-8')
required=(
    r'runs\s+of\s+a\s+frozen\s+generator',
    r'model-general,\s*naturalistic,\s*and\s*open-ended\s+superiority\s+are\s+not\s+claimed',
    r'not\s+2,882\s+independent\s+observations\s+of\s+scientific\s+practice',
)
missing=[pattern for pattern in required if re.search(pattern,text,re.I|re.S) is None]
assert not missing, missing
print('ORION11_GENERATOR_SCOPE_BOUNDARY=PASS')
PY
work="$(build_scratch_pdf papers/orion-11-recursive-epistemic-reconstruction orion11)"
out='papers/publication_closure/submissions/ORION-11/JAIR'
rm -rf "$out" && mkdir -p "$out/source"
cp "$work/main.pdf" "$out/main.pdf"
cp -R papers/orion-11-recursive-epistemic-reconstruction/manuscript/. "$out/source/"
rm -f "$out/source/main.pdf"
cp papers/orion-11-recursive-epistemic-reconstruction/JOURNAL_READINESS.md "$out/JOURNAL_READINESS.md"
cp papers/orion-11-recursive-epistemic-reconstruction/REPRODUCE.md "$out/REPRODUCE.md"
write_receipt "$out" ORION-11 JAIR 'P1_MUTATION_NECESSITY_SUPPORTED__PRIMARY_AND_DISJOINT_REPLICATION' 'mechanism-level inference inside one frozen generator; no naturalistic/model-general/open-ended superiority'

# ---------------------------------------------------------------------------
# ORION-12 — bounded methods/system-design claim, IP&M route.
# ---------------------------------------------------------------------------
assert_text papers/orion-12-open-world-scientific-discovery/JOURNAL_READINESS.md 'ORION-12 = PEER_REVIEW_READY'
assert_text papers/orion-12-open-world-scientific-discovery/JOURNAL_READINESS.md 'External ORION-vs-baseline superiority remains `CANNOT_CHECK`'
python - <<'PY'
from pathlib import Path
import re
p=Path('papers/orion-12-open-world-scientific-discovery/JOURNAL_READINESS.md')
text=p.read_text(encoding='utf-8')
required=(
    r'Paper 2 is now a \*\*methods\s*/\s*critical system-design paper\*\*',
    r'Primary target:\*\* \*Information Processing\s*&\s*Management\*',
    r'Fallback:\s*JASIST',
    r'proof of open-world completeness',
    r'generic lexical/dense/reasoning-aware/field-aware retrieval novelty',
)
missing=[pattern for pattern in required if re.search(pattern,text,re.I|re.S) is None]
assert not missing, missing
# The scope must retain the adverse external comparison instead of allowing a
# positive bounded/offline result to promote the excluded claim.
assert 'External ORION-vs-baseline superiority remains `CANNOT_CHECK`' in text
assert 'not an externally supported ORION-vs-baseline superiority paper' in text
print('ORION12_BOUNDED_TARGET_BOUNDARY=PASS')
PY
work="$(build_scratch_pdf papers/orion-12-open-world-scientific-discovery orion12)"
out='papers/publication_closure/submissions/ORION-12/IPM'
rm -rf "$out" && mkdir -p "$out/source"
cp "$work/main.pdf" "$out/main.pdf"
cp -R papers/orion-12-open-world-scientific-discovery/manuscript/. "$out/source/"
rm -f "$out/source/main.pdf"
cp papers/orion-12-open-world-scientific-discovery/JOURNAL_READINESS.md "$out/JOURNAL_READINESS.md"
cp papers/orion-12-open-world-scientific-discovery/REPRODUCE.md "$out/REPRODUCE.md"
write_receipt "$out" ORION-12 IPM 'PEER_REVIEW_READY_BOUNDED_METHODS_SYSTEM_DESIGN' 'no external superiority, no open-world closure superiority, no retrieval novelty'

# ---------------------------------------------------------------------------
# ORION-13 — scoped structured-mapping claim, Semantic Web Journal route.
# ---------------------------------------------------------------------------
assert_text papers/orion-13-global-knowledge-portrait/JOURNAL_READINESS.md 'ORION-13 = PEER_REVIEW_READY'
assert_text papers/orion-13-global-knowledge-portrait/JOURNAL_READINESS.md 'Semantic Web Journal'
(cd papers/orion-13-global-knowledge-portrait/evidence/coordinate-obstruction-v2 && sha256sum -c SHA256SUMS)
(cd papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1.1-confirmatory && sha256sum -c SHA256SUMS)
work="$(build_scratch_pdf papers/orion-13-global-knowledge-portrait orion13)"
out='papers/publication_closure/submissions/ORION-13/SWJ'
rm -rf "$out" && mkdir -p "$out/source"
cp "$work/main.pdf" "$out/main.pdf"
cp -R papers/orion-13-global-knowledge-portrait/manuscript/. "$out/source/"
rm -f "$out/source/main.pdf"
cp papers/orion-13-global-knowledge-portrait/JOURNAL_READINESS.md "$out/JOURNAL_READINESS.md"
cp papers/orion-13-global-knowledge-portrait/REPRODUCE.md "$out/REPRODUCE.md"
write_receipt "$out" ORION-13 SWJ 'PEER_REVIEW_READY_SCOPED_ORION13_C5_C9' 'structured-mapping/false-merge scoped claim only; no universal raw-text extraction or downstream answer-quality claim'

assert_no_paper_mutation

git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
git add papers/publication_closure/submissions/ORION-11 \
        papers/publication_closure/submissions/ORION-12 \
        papers/publication_closure/submissions/ORION-13
git diff --check --cached
if ! git diff --cached --quiet; then
  git commit -m 'papers(publication): close Wave B1-P1 bounded specialist packages [wave-b1p1-materialized]'
fi
git push origin HEAD:chatgpt/all25-publication-closure-20260827
printf 'WAVE_B1P1_FINAL_COMMIT=%s\n' "$(git rev-parse HEAD)"
