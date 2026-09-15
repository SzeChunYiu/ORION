# ORION repository targets.
#
# Additive by convention: each paper or subsystem owns its own block, so
# parallel lanes extend this file without colliding.

PYTHON ?= python3
SRC ?= src

# --- ORION-P1: recursive epistemic reconstruction (issue #98) ------------------
#
# Regenerates the frozen publication tables from ARCHIVED RAW RECORDS ONLY.
# Nothing here executes a system under test, reads a protected gold label or
# draws a figure: the numbers are the artifact.
#
# Exit codes:
#   0  tables regenerated from records
#   2  the archive exists but is malformed (a record was refused, not skipped)
#   3  CANNOT_CHECK - no archive, an empty archive, or an archive that cannot
#      bind its own numbers. This is the expected result on a clean checkout
#      without a live provider credential. It is deliberately distinct from
#      both success and error.
#
# See papers/orion-11-recursive-epistemic-reconstruction/REPRODUCE.md.

# The scored file, not the raw/ directory. load_records() reads every .json/.jsonl
# under a directory and refuses to skip a record it cannot parse -- deliberately,
# since silently skipping would turn an incomplete archive into confident numbers.
# raw/ also holds test_runs.jsonl, which has no schema_version, so pointing the
# archive at the directory made `make paper01-results` exit 2 on a clean checkout.
# results/INTEGRITY_NOTE.md already recorded this; the Makefile did not agree.
P1_ARCHIVE ?= papers/orion-11-recursive-epistemic-reconstruction/results/raw/test_scored.jsonl
P1_OUT ?= papers/orion-11-recursive-epistemic-reconstruction/results
P1_BOOTSTRAP_SEED ?= 20260815
P1_RESAMPLES ?= 10000
P1_REPEATS ?= 5
P1_MIN_UNITS ?= 0

.PHONY: paper01-results
paper01-results:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.study.p1.tables \
		--archive $(P1_ARCHIVE) \
		--out $(P1_OUT) \
		--expected-repeats $(P1_REPEATS) \
		--bootstrap-seed $(P1_BOOTSTRAP_SEED) \
		--resamples $(P1_RESAMPLES) \
		--min-units $(P1_MIN_UNITS) ; \
	code=$$? ; \
	if [ $$code -eq 3 ]; then \
		echo "" >&2 ; \
		echo "make: paper01-results -> CANNOT_CHECK (exit 3)." >&2 ; \
		echo "      No publishable numbers exist for ORION-P1 yet. This is not a build failure:" >&2 ; \
		echo "      it is the honest state of the external evidence until an archived study run" >&2 ; \
		echo "      lands in $(P1_ARCHIVE). See papers/orion-11-recursive-epistemic-reconstruction/REPRODUCE.md." >&2 ; \
	fi ; \
	exit $$code

.PHONY: paper01-tests
paper01-tests:
	PYTHONPATH=$(SRC) $(PYTHON) -m pytest -q tests/unit/study/p1

.PHONY: paper01-trial paper01-trial-live
## Run the whole P1 trial: systems -> archive -> scores -> tables. Mechanical arm only.
paper01-trial:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.study.p1.run_trial --split $(or $(SPLIT),PILOT)

## Same, plus the live glm-5.2 arm. Requires ANTHROPIC_API_KEY in the environment;
## refuses before running a single case if it is absent, rather than recording
## CANNOT_CHECK on every live cell and wasting the mechanical arm's run too.
paper01-trial-live:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.study.p1.run_trial --split $(or $(SPLIT),PILOT) --live

.PHONY: conformance
## Check every declared protocol quantity against the artifacts on disk.
## Exits 1 on a violation; CANNOT_CHECK does not fail — an unstarted paper is
## unknown, not wrong, and failing on it would get this switched off.
conformance:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.conformance --papers papers

# --- ORION-P3: public-reference mapping route (issue #100) --------------------

P3_PUBLIC_BUILD_OUT ?= papers/orion-13-global-knowledge-portrait/gold/public-reference
P3_PUBLIC_CASES ?= $(P3_PUBLIC_BUILD_OUT)/cases.jsonl
P3_PUBLIC_EVAL_OUT ?= papers/orion-13-global-knowledge-portrait/evaluation/public-reference-summary.json
P3_PUBLIC_TARGET_N ?= 32

.PHONY: paper03-public-reference-build
## Build a pointer/hash-only atlas from pinned external human/expert annotations.
## Optional inputs: P3_MUSE_ROOT, P3_SCIFACT_CLAIMS, P3_SCISCHEMA_ROOT.
## Exit 3 means the authoritative pool cannot yet meet the frozen coverage gate.
paper03-public-reference-build:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.study.p3_public_reference_build \
		$(if $(P3_MUSE_ROOT),--muse-root $(P3_MUSE_ROOT),) \
		$(if $(P3_SCIFACT_CLAIMS),--scifact-claims $(P3_SCIFACT_CLAIMS),) \
		$(if $(P3_SCISCHEMA_ROOT),--scischema-root $(P3_SCISCHEMA_ROOT),) \
		--target-n $(P3_PUBLIC_TARGET_N) \
		--out $(P3_PUBLIC_BUILD_OUT)

.PHONY: paper03-public-reference
## Deterministic mapping-layer evaluation. No model/provider credential required.
paper03-public-reference:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.study.p3_public_reference \
		--cases $(P3_PUBLIC_CASES) \
		--output $(P3_PUBLIC_EVAL_OUT)

P3_PUBLIC_ANALYSIS_OUT ?= papers/orion-13-global-knowledge-portrait/evaluation/public-reference-analysis.json

.PHONY: paper03-public-reference-analysis
## Publication analysis: Wilson intervals, paired bootstrap and coordinate ablations.
paper03-public-reference-analysis:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.study.p3_public_reference_analysis \
		--cases $(P3_PUBLIC_CASES) \
		--output $(P3_PUBLIC_ANALYSIS_OUT)

P3_CONFIRMATORY_ANALYSIS ?= papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1.1-confirmatory/CONFIRMATORY_ANALYSIS.json
P3_PUBLICATION_OUT ?= papers/orion-13-global-knowledge-portrait/evidence/public-reference-v1.1-confirmatory/publication

.PHONY: paper03-public-reference-publication
## Rebuild the narrow public-reference publication tables/SVGs from immutable confirmatory analysis.
paper03-public-reference-publication:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.study.p3_public_reference_publication \
		--analysis $(P3_CONFIRMATORY_ANALYSIS) \
		--out $(P3_PUBLICATION_OUT)

.PHONY: paper03-public-reference-tests
paper03-public-reference-tests:
	PYTHONPATH=$(SRC) $(PYTHON) -m pytest -q \
		tests/unit/study/test_p3_public_reference.py \
		tests/unit/study/test_p3_public_reference_build.py \
		tests/unit/study/test_p3_public_reference_analysis.py \
		tests/unit/study/test_p3_public_reference_publication.py

# --- ORION-P5: self-ORION journal tables (issue #102) -------------------------
#
# Regenerates publication tables from the archived glm-5.2 attribution JSONL.
# Populates P5-3 (21/24 confusion) and the residual-error ledger. Campaign
# plots/tables P5-2/P5-4/P5-5/P5-6/P5-7 and P5-T2/P5-T3 are emitted as
# CANNOT_CHECK stubs with no imputed numbers.
#
# Exit codes:
#   0  tables regenerated; 21/24 verified from raw records
#   2  archive malformed (including a 24-of-24 rewrite or dropped errors)
#   3  CANNOT_CHECK — archive missing

P5_ARCHIVE ?= papers/orion-15-self-orion/evidence/glm-5.2-attribution/results.jsonl
P5_REPORT ?= papers/orion-15-self-orion/evidence/glm-5.2-attribution/report.json
P5_OUT ?= papers/orion-15-self-orion/evidence/tables
P5_TEX ?= papers/orion-15-self-orion/manuscript/tables

.PHONY: paper05-results
paper05-results:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.study.p5.tables \
		--archive $(P5_ARCHIVE) \
		--report $(P5_REPORT) \
		--out $(P5_OUT) \
		--tex-out $(P5_TEX) ; \
	code=$$? ; \
	if [ $$code -eq 3 ]; then \
		echo "" >&2 ; \
		echo "make: paper05-results -> CANNOT_CHECK (exit 3)." >&2 ; \
		echo "      No attribution archive is present. This is not a build failure." >&2 ; \
	fi ; \
	exit $$code

.PHONY: paper05-tests
paper05-tests:
	PYTHONPATH=$(SRC) $(PYTHON) -m pytest -q \
		tests/test_p5_attribution_tables.py \
		tests/test_p5_hidden_cause_freeze.py \
		tests/test_p5_protocol_v2.py

# --- Cross-paper journal packages (issue #160) --------------------------------
#
# Additive Gate 7–9 inventory. Does not compile PDFs or mint
# ScientificResultVerification.v1 (issue #283).

.PHONY: journal-packages
journal-packages:
	$(PYTHON) research/paper-programme-v1/journal_package/check_journal_package.py

.PHONY: journal-package-tests
journal-package-tests:
	PYTHONPATH=$(SRC) $(PYTHON) -m pytest -q tests/unit/publication/test_journal_package.py

# --- Publication closure wave (issue #153) ------------------------------------
#
# Fails closed if any paper *claims* PEER_REVIEW_READY without the required
# manuscript/ledger/protocol/attestation/reproducibility bundle, or if P1 H1 is
# promoted to a confirmatory finding / ready terminal while the frozen 48-case
# arm remains underpowered. An honest non-claim does not fail.
#
# Additive: this target does not rewrite paper terminals. Complements
# research/publication/scoreboard.py (status JSON) and journal-packages (#160).

.PHONY: peer-review-ready-gate
peer-review-ready-gate:
	PYTHONPATH=$(SRC) $(PYTHON) -m orion.publication --papers papers

.PHONY: peer-review-ready-gate-tests
peer-review-ready-gate-tests:
	PYTHONPATH=$(SRC) $(PYTHON) -m pytest -q tests/unit/publication/test_peer_review_ready_gate.py

# --- P1-P10 superiority terminals (issues #649-#656, #662, #663) --------------
#
# Adjudicates every paper's frozen `Done when` list against the evidence ledger
# and runs the eleven-check substitution battery. Additive: it rewrites no paper
# terminal, promotes no claim and grants no issue closure.
#
# Exit codes of the underlying module (make itself reports 2 for any failing
# recipe, as it already does for paper01-results):
#   0  every registered terminal EARNED and the battery clean
#   1  a real negative - some terminal NOT_EARNED, or a battery check FAILed
#   2  the ledger could not be bound to the frozen registry (malformed input)
#   3  CANNOT_CHECK - nothing failed and nothing was established. This is the
#      expected result today: ten open programmes whose superiority terminals
#      have not been attempted. Deliberately distinct from both 0 and 1.
#
# Run the module directly when the exact code matters:
#   PYTHONPATH=src python3 -m orion.programme.superiority_report --ledger ...
#
# See research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_2026-08-21.md.

SUPERIORITY_LEDGER ?= research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_LEDGER_V1.json
SUPERIORITY_REPORT ?= research/paper-programme-v1/P1_P10_SUPERIORITY_TERMINAL_REPORT_2026-08-21.json

.PHONY: p1-p10-superiority-report
p1-p10-superiority-report:
	@PYTHONPATH=$(SRC) $(PYTHON) -m orion.programme.superiority_report \
		--ledger $(SUPERIORITY_LEDGER) \
		--out $(SUPERIORITY_REPORT) ; \
	code=$$? ; \
	if [ $$code -eq 3 ]; then \
		echo "" >&2 ; \
		echo "make: p1-p10-superiority-report -> CANNOT_CHECK (exit 3)." >&2 ; \
		echo "      No P1-P10 superiority terminal is established and none is refuted." >&2 ; \
	fi ; \
	exit $$code

.PHONY: p1-p10-superiority-tests
p1-p10-superiority-tests:
	PYTHONPATH=$(SRC) $(PYTHON) -m pytest -q tests/unit/programme/test_superiority_gates.py
