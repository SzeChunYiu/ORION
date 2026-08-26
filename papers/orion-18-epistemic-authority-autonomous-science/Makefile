REPO_ROOT ?= ../..
UV ?= uv

.PHONY: reproduce-v3
reproduce-v3:
	cd $(REPO_ROOT) && $(UV) sync --frozen --extra dev --extra proofs
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/orion-18-epistemic-authority-autonomous-science/benchmark/generate_authority_cases_v2.py --check
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/candidates/checkers/check_negative_null_history_v1.py --paper P8
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/orion-18-epistemic-authority-autonomous-science/formal/check_contract_manifest_v2.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/orion-18-epistemic-authority-autonomous-science/formal/check_theory_closure_v2.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/orion-18-epistemic-authority-autonomous-science/formal/check_theory_closure_v2_1.py
