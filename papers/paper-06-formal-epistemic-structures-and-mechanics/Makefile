REPO_ROOT ?= ../..
UV ?= uv

.PHONY: reproduce-v3
reproduce-v3:
	cd $(REPO_ROOT) && $(UV) sync --frozen --extra dev --extra proofs
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/generate_assumption_countermodels_v2.py --check
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/candidates/checkers/check_negative_null_history_v1.py --paper P6
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_assumption_regressions_v2.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2_1.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_certificate_lifting_scope_smt_v1.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/paper-06-formal-epistemic-structures-and-mechanics/formal/refutation_audit.py
