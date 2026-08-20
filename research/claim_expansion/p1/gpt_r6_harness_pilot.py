from __future__ import annotations

import json
import tempfile
from pathlib import Path

from orion_research_harness.protocol import CapabilityRequest
from orion_research_harness.runner import run_problem
from orion_research_harness.workspace import ResearchWorkspace

DOSSIER = (
    "A random-effects meta-analysis uses study summaries from studies with modest participant "
    "counts. Individual participant records exist, while the inferential model, estimand, and "
    "study collection are otherwise unchanged."
)
SOURCE = (
    "Min & Zhang, Relative Efficiency of Using Summary Versus Individual Data in Random-Effects "
    "Meta-Analysis, Biometrics 2020, DOI 10.1111/biom.13238. The source reports asymptotic "
    "equivalence but appreciable summary-data efficiency loss when sample sizes are not sufficiently large."
)


def service(workspace: ResearchWorkspace, request: CapabilityRequest) -> None:
    p = request.payload
    if request.capability == "LLM_COMPLETE":
        task = p["task"]
        if task == "plan_search":
            content = json.dumps({"queries":[{"query_id":"frozen-search-p1","text":"frozen SEARCH-P1 source","route_id":"frozen-r4","route_kind":"FRESHNESS","domain_hint":"meta_analysis"}]})
        elif task == "interpret":
            content = json.dumps({
                "contribution_id":"p1-r6-search-p1",
                "text":"The fixed source indicates an evidence/information sufficiency limitation without changing the scientific objective or population boundary.",
                "assimilation":"COMPLEMENTARY_FACET",
                "discovered_domain_ids":["meta_analysis"],
                "representation_ids":[],"contradicts_claim_ids":[],"related_claim_ids":[],"context_ids":[],
                "referent_bindings":[],"representation_mappings":[],"assumption_ids":[]
            })
        elif task == "reconstruct":
            content = json.dumps({"summary":"The visible evidence supports a lower-level evidence/information responsibility; high-level objective/boundary reformulation is not supported."})
        elif task == "diagnose":
            content = json.dumps({"responsibilities":["SEARCH"],"rationale":"The fixed source points to evidence/information sufficiency rather than objective or boundary failure."})
        elif task == "propose_reframe":
            content = json.dumps({"add_domain_ids":[],"add_representation_ids":[],"note":"Do not escalate to a high-level reformulation."})
        elif task == "compose_answer":
            content = json.dumps({"answer":"Preserve the scientific objective and boundary; repair evidence/information sufficiency first."})
        else:
            raise AssertionError(f"unexpected LLM task: {task}")
        workspace.ingest_result(request.request_id, success=True, output={"content":content,"model_id":"p1-r6-frozen-pilot"}, executor="p1-r6-pilot")
        return
    if request.capability == "WEB_SEARCH":
        workspace.ingest_result(request.request_id, success=True, output={"items":[{"item_id":"doi:10.1111/biom.13238","content":SOURCE,"source_uri":"https://doi.org/10.1111/biom.13238","domain_ids":["meta_analysis"]}]}, executor="p1-r6-frozen-corpus")
        return
    if request.capability == "VERIFY_EVIDENCE":
        workspace.ingest_result(request.request_id, success=True, output={"passed":True,"certificate_ids":["certificate:p1-r6:search-p1"],"reason":"Contribution is directly supported by the frozen source statement."}, executor="p1-r6-independent-check")
        return
    raise AssertionError(f"unexpected capability: {request.capability}")


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ws = ResearchWorkspace.initialize(root / "ws", project_root=root)
        problem = {
            "problem_id":"p1-r6-search-p1-adverse",
            "question":"What revision level is warranted for this scientific failure?",
            "scope":DOSSIER + " Use only the fixed 2020 R4 source universe. Do not change the objective or boundary unless evidence requires it.",
            "initial_domain_ids":["meta_analysis"],
            "success_criteria":["Preserve uncertainty.","Do not escalate beyond evidence."]
        }
        for _ in range(24):
            outcome = run_problem(ws, problem, max_iterations=2, require_verified_answer=True)
            if outcome["status"] == "COMPLETE":
                break
            if outcome["status"] == "HOST_CAPABILITY_FAILED":
                raise AssertionError(outcome)
            service(ws, CapabilityRequest.from_dict(outcome["request"]))
        else:
            raise AssertionError("harness did not terminate")
        assert outcome["status"] == "COMPLETE"
        assert ws.run_ids(), "completed run was not persisted"
        ops = set(outcome["operator_sequence"])
        assert {"FRAME","SEARCH","ABSORB"}.issubset(ops), outcome
        print("P1_R6_HARNESS_PILOT=" + json.dumps(outcome, sort_keys=True))


if __name__ == "__main__":
    main()
