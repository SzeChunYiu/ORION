REPO_ROOT ?= ../..
UV ?= uv

.PHONY: reproduce-v3
reproduce-v3:
	cd $(REPO_ROOT) && $(UV) sync --frozen --extra dev --extra proofs
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/orion-17-epistemic-navigation-open-worlds/benchmark/generate_instances_v2.py --check
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/candidates/checkers/check_negative_null_history_v1.py --paper P7
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/orion-17-epistemic-navigation-open-worlds/formal/check_contract_manifest_v2.py
	cd $(REPO_ROOT) && $(UV) run --frozen python papers/orion-17-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py
	cd $(REPO_ROOT) && $(UV) run --frozen python -m orion.study.p7.premise_audit
