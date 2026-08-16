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
# See papers/paper-01-recursive-epistemic-reconstruction/REPRODUCE.md.

P1_ARCHIVE ?= papers/paper-01-recursive-epistemic-reconstruction/results/raw
P1_OUT ?= papers/paper-01-recursive-epistemic-reconstruction/results
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
		echo "      lands in $(P1_ARCHIVE). See papers/paper-01-recursive-epistemic-reconstruction/REPRODUCE.md." >&2 ; \
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
