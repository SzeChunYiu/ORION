REPO_ROOT ?= ../..
UV ?= uv

.PHONY: reproduce-v3 reproduce-v4
reproduce-v3:
	cd $(REPO_ROOT) && $(UV) sync --frozen --extra dev --extra proofs
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/generate_assumption_countermodels_v2.py --check
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/candidates/checkers/check_negative_null_history_v1.py --paper P6
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_assumption_regressions_v2.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2_1.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_certificate_lifting_scope_smt_v1.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/refutation_audit.py

reproduce-v4: reproduce-v3
	cd $(REPO_ROOT) && $(UV) run --frozen python -m orion.study.p6.certificate_as_dependency_graph --repo-root . --date 2026-08-26 --check-output papers/paper-06-formal-epistemic-structures-and-mechanics/formal/mechanized/P6_CERTIFICATE_AS_DEPENDENCY_GRAPH_V2_2026-08-26.json
