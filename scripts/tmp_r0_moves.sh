#!/usr/bin/env bash
# R0 naming-unification: pure `git mv` wave (no content edits in this step).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

ARCH="papers/archive/2026-08-pre-unification"
mkdir -p "$ARCH"

# --- orion-01: theory-A + theory-B merged container (no prose merge) -------
mkdir -p papers/orion-01-certificate-realization
mkdir -p "$ARCH/theory-A-multitag-constraint-rank" "$ARCH/theory-B-certificate-complexity"
for T in A B; do
  SRC="papers/theory-${T}-$( [ "$T" = A ] && echo multitag-constraint-rank || echo certificate-complexity )"
  git mv "$SRC/MANUSCRIPT_V2.md"    "papers/orion-01-certificate-realization/theory-${T}-MANUSCRIPT_V2.md"
  git mv "$SRC/MANUSCRIPT_V1.md"    "$ARCH/theory-${T}-$( [ "$T" = A ] && echo multitag-constraint-rank || echo certificate-complexity )/MANUSCRIPT_V1.md"
  git mv "$SRC/CLAIM_LEDGER.md"     "papers/orion-01-certificate-realization/theory-${T}-CLAIM_LEDGER.md"
  git mv "$SRC/CLAIM_LEDGER_R2.md"  "papers/orion-01-certificate-realization/theory-${T}-CLAIM_LEDGER_R2.md"
  rmdir "$SRC"
done

# --- simple renames: old dir -> new dir ------------------------------------
declare -a RENAMES=(
  "papers/theory-C-low-order-information papers/orion-02-fiberguard-finite-fibre"
  "papers/theory-D-falsification-authority papers/orion-03-typed-merge-falsification"
  "papers/nonquantum-c5cubed-davenport papers/orion-04-rooted-completion-certificates"
  "papers/Q-paper-01-tare-expressivity papers/orion-05-tare-expressivity"
  "papers/Q-paper-02-recursive-recovery papers/orion-06-recursive-recovery"
  "papers/Q-paper-03-dual-instrument papers/orion-07-dual-instrument"
  "papers/Q-paper-04-typed-state papers/orion-08-typed-state"
  "papers/QG-paper-01-compilation-regime-geometry papers/orion-09-compilation-regime-geometry"
  "papers/QG-paper-02-certified-static-forecasting papers/orion-10-certified-static-forecasting"
  "papers/paper-01-recursive-epistemic-reconstruction papers/orion-11-recursive-epistemic-reconstruction"
  "papers/paper-02-open-world-scientific-discovery papers/orion-12-open-world-scientific-discovery"
  "papers/paper-03-global-knowledge-portrait papers/orion-13-global-knowledge-portrait"
  "papers/paper-04-verified-scientific-discovery papers/orion-14-verified-scientific-discovery"
  "papers/paper-05-self-orion papers/orion-15-self-orion"
  "papers/paper-06-formal-epistemic-structures-and-mechanics papers/orion-16-formal-epistemic-structures-and-mechanics"
  "papers/paper-07-epistemic-navigation-open-worlds papers/orion-17-epistemic-navigation-open-worlds"
  "papers/paper-08-epistemic-authority-autonomous-science papers/orion-18-epistemic-authority-autonomous-science"
  "papers/paper-09-structured-epistemic-learning papers/orion-19-structured-epistemic-learning"
  "papers/paper-10-structured-problem-solving papers/orion-20-structured-problem-solving"
  "papers/paper-11-state-as-computation papers/orion-21-state-as-computation"
  "papers/paper-12-adaptive-state-reasoning papers/orion-22-adaptive-state-reasoning"
  "papers/paper-13-responsibility-carrying-state papers/orion-23-responsibility-carrying-state"
  "papers/paper-14-orion-rse papers/orion-24-orion-rse"
  "papers/paper-15-orion-research-harness papers/orion-25-orion-research-harness"
)
for pair in "${RENAMES[@]}"; do
  set -- $pair
  git mv "$1" "$2"
done

# --- QG-paper-03 stub -> candidates ----------------------------------------
git mv papers/QG-paper-03-intrinsic-support-numbers papers/candidates/qg-paper-03-stub

# --- superseded twin dirs + paper-xx stub -> archive -----------------------
for D in paper-02-global-knowledge-portrait paper-03-verified-discovery paper-04-self-orion paper-xx-content-bound-math-evaluation; do
  git mv "papers/$D" "$ARCH/$D"
done

# --- archived root files ----------------------------------------------------
for F in FIVE_PAPER_REVIEW_SYNTHESIS_2026-08-24.md FIVE_THEORY_PAPERS_FIGURE_CONTRACTS_2026-08-24.md \
         Q_QG_VENUE_TARGET_MATRIX_V1.md Q_QG_PUBLICATION_READINESS_V2.md Q_QG_TARGET_PACKAGE_MANIFESTS_V1.json \
         check_q_qg_target_packages.py build_q_qg_figures.py; do
  git mv "papers/$F" "$ARCH/$F"
done

# --- per-dir MANUSCRIPT_V1.md where MANUSCRIPT_V2.md exists ----------------
declare -a V1DIRS=(
  "theory-C-low-order-information orion-02-fiberguard-finite-fibre"
  "theory-D-falsification-authority orion-03-typed-merge-falsification"
  "nonquantum-c5cubed-davenport orion-04-rooted-completion-certificates"
  "Q-paper-03-dual-instrument orion-07-dual-instrument"
  "Q-paper-04-typed-state orion-08-typed-state"
  "QG-paper-01-compilation-regime-geometry orion-09-compilation-regime-geometry"
  "QG-paper-02-certified-static-forecasting orion-10-certified-static-forecasting"
)
for pair in "${V1DIRS[@]}"; do
  set -- $pair
  mkdir -p "$ARCH/$1"
  git mv "papers/$2/MANUSCRIPT_V1.md" "$ARCH/$1/MANUSCRIPT_V1.md"
done

# --- Q-paper-01 (orion-05) manuscript chain: keep V3_REFINED (canonical) ----
mkdir -p "$ARCH/Q-paper-01-tare-expressivity"
for F in MANUSCRIPT_V1.md MANUSCRIPT_V2.md MANUSCRIPT_V3.md MANUSCRIPT_SUBMISSION_DRAFT.md; do
  git mv "papers/orion-05-tare-expressivity/$F" "$ARCH/Q-paper-01-tare-expressivity/$F"
done

echo "MOVES DONE"
git status -sb | head -5
