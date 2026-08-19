from __future__ import annotations

import json
import shutil
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[1]
LEDGER = PAPER / "protocol" / "CLAIM_LEDGER_V1.json"
HUMAN_LEDGER = PAPER / "evidence" / "CLAIM_LEDGER_V1.md"
P2X_DIR = PAPER / "evidence" / "p2x"
RESULT_SRC = ROOT / "research" / "claim_expansion" / "p2" / "P2_X_PROTECTED_RESULT_V1.json"
VERIFY_SRC = ROOT / "research" / "claim_expansion" / "p2" / "P2_X_INDEPENDENT_VERIFICATION_V1.json"
BIB = PAPER / "manuscript" / "novelty_refresh_2026.bib"
FETCHER = PAPER / "evidence" / "literature" / "fetch_literature_evidence.py"
TEST = ROOT / "tests" / "unit" / "p2" / "test_p2_claim_ledger.py"
READINESS = PAPER / "JOURNAL_READINESS.md"

P2X_CLAIMS = [
    {
        "claim_id": "P2-X20",
        "region": "abstract",
        "sentence": "A separate post-saturation exact successor isolates unresolved-route authority after strong stopping mechanisms are granted: on 400 protected heterogeneous acquisition contracts, P2-X attains 400/400 exact scientific closure decisions versus 250/400 for a donor-complete available-route product (paired difference 0.375, 95% CI [0.3275,0.4225]), with zero false task closures; an ideal product supplied identical route-authority semantics ties 400/400.",
        "bindings": ["n", "p2x_correct", "n", "b1_correct", "n", "difference", "ci_percent", "ci_low", "ci_high", "b3_correct", "n"],
        "note": "P2-X abstract headline; bounded exact heterogeneous-acquisition contract only.",
    },
    {
        "claim_id": "P2-X21",
        "region": "conclusion",
        "sentence": "After donor-complete evidence coverage, decision/utility stopping, finite route certificates, deduplication and question-processing state are granted, P2-X obtains 400/400 exact closure decisions versus 250/400 for an available-route donor product, a paired advantage of 0.375 with 95% CI [0.3275,0.4225], while preserving zero false task closures and perfect clean closure.",
        "bindings": ["p2x_correct", "n", "b1_correct", "n", "difference", "ci_percent", "ci_low", "ci_high"],
        "note": "P2-X conclusion headline; does not imply deployed retriever/provider generality.",
    },
    {
        "claim_id": "P2-X22",
        "region": "conclusion",
        "sentence": "The effect is the unresolved-route authority rule: all 150 B1 errors are material unavailable/censored/provider-invalid routes that B1 excludes from the closure denominator.",
        "bindings": ["b1_errors"],
        "note": "Failure localization from the protected P2-X result.",
    },
    {
        "claim_id": "P2-X23",
        "region": "conclusion",
        "sentence": "An ideal typed product supplied the same semantics ties 400/400.",
        "bindings": ["b3_correct", "n"],
        "note": "Ideal-product non-expressivity boundary.",
    },
    {
        "claim_id": "P2-X24",
        "region": "conclusion",
        "sentence": "Thus the contribution is not generic stopping, generic closure certificates, or inherent expressivity; it is bounded evidence that route-local acquisition stop and task-global scientific closure are distinct authority relations when material routes remain unresolved.",
        "bindings": [],
        "note": "Bounded A2 architecture-principle statement; novelty remains donor-subtracted.",
    },
    {
        "claim_id": "P2-X25",
        "region": "conclusion",
        "sentence": "Deployed multi-provider/retrieval-engine generality remains CANNOT_CHECK.",
        "bindings": [],
        "cannot_check": True,
        "note": "A3 remains explicitly unpromoted.",
    },
    {
        "claim_id": "P2-X26",
        "region": "limitations",
        "sentence": "Its 400-case exact battery spans five acquisition settings and includes seed-permuted route order plus non-material unavailable decoys, but route state, route materiality and question-processing state are explicitly supplied rather than inferred from noisy web behavior.",
        "bindings": ["n"],
        "note": "Exact-benchmark scope limitation.",
    },
    {
        "claim_id": "P2-X27",
        "region": "limitations",
        "sentence": "The 1.000 P2-X ESCD ceiling therefore supports the fail-closed authority rule only on the registered exact contracts.",
        "bindings": ["p2x_rate"],
        "note": "Exact-contract-only scope boundary.",
    },
    {
        "claim_id": "P2-X28",
        "region": "limitations",
        "sentence": "No independently implemented lexical/dense/reasoning retrievers or new live provider campaign were used to establish retrieval-engine generality, and B3 shows that an ideal product given identical unresolved-route semantics is extensionally equivalent.",
        "bindings": [],
        "note": "No deployed/retrieval-engine generality and no inherent-expressivity claim.",
    },
]

NEW_LITERATURE = {
    "knowplan2026": (
        "2608.06530",
        "KnowPlan: An Actionable Knowledge Graph for Planning-grounded Retrieval-Augmented Generation",
    ),
    "donotstopearly2026": (
        "2604.24978",
        "Do Not Stop Too Early: An Information-Looking Framework for Adaptive Reliability in Deep Research",
    ),
    "confidencebasedstop2026": (
        "2606.15380",
        "Confidence Based Stopping Criteria for Reinforcement Learning",
    ),
    "icore2026": (
        "2607.27429",
        "iCORE: A Cost Reduction Engine for Computer Use Agents via Internalized Execution",
    ),
    "scienceintent2026": (
        "2604.25000",
        "Intent Modeling for Customer Support with Scientific Computing and NLP",
    ),
}


def write_p2x_evidence() -> None:
    P2X_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(RESULT_SRC, P2X_DIR / RESULT_SRC.name)
    shutil.copyfile(VERIFY_SRC, P2X_DIR / VERIFY_SRC.name)
    result = json.loads(RESULT_SRC.read_text(encoding="utf-8"))
    verification = json.loads(VERIFY_SRC.read_text(encoding="utf-8"))
    if result["terminal"] != "P2_X_BOUNDED_ROUTE_AUTHORITY_RESULT_SUPPORTED":
        raise RuntimeError(f"unexpected P2-X result terminal: {result['terminal']}")
    if not verification.get("ok") or verification.get("terminal") != "P2_X_INDEPENDENT_VERIFICATION_PASS":
        raise RuntimeError(f"P2-X independent verification not green: {verification}")
    if verification["arm_correct"] != {
        "P2X_FAIL_CLOSED_ROUTE_AUTHORITY": 400,
        "B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT": 250,
        "B2_GLOBAL_SUFFICIENCY_AGGREGATOR": 100,
        "B3_IDEAL_TYPED_ROUTE_PRODUCT": 400,
    }:
        raise RuntimeError("P2-X verification headline counts changed")
    claim_values = {
        "schema": "P2_X_CLAIM_VALUES_V1",
        "source_result": RESULT_SRC.as_posix().split("/ORION/")[-1],
        "source_verification": VERIFY_SRC.as_posix().split("/ORION/")[-1],
        "n": result["n"],
        "p2x_correct": result["arms"]["P2X_FAIL_CLOSED_ROUTE_AUTHORITY"]["correct"],
        "b1_correct": result["arms"]["B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT"]["correct"],
        "b2_correct": result["arms"]["B2_GLOBAL_SUFFICIENCY_AGGREGATOR"]["correct"],
        "b3_correct": result["arms"]["B3_IDEAL_TYPED_ROUTE_PRODUCT"]["correct"],
        "p2x_rate": result["arms"]["P2X_FAIL_CLOSED_ROUTE_AUTHORITY"]["rate"],
        "b1_rate": result["arms"]["B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT"]["rate"],
        "difference": result["primary"]["difference"],
        "ci_percent": 95,
        "ci_low": result["primary"]["bootstrap_ci95"][0],
        "ci_high": result["primary"]["bootstrap_ci95"][1],
        "b1_errors": result["n"] - result["arms"]["B1_DONOR_COMPLETE_AVAILABLE_ROUTE_PRODUCT"]["correct"],
        "b3_mismatches": result["secondary"]["b3_decision_mismatches"],
        "decoy_cases": result["secondary"]["decoy_cases"],
        "materiality_errors": result["secondary"]["materiality_errors"],
        "authority": "DERIVED_FROM_VERIFIED_P2_X_PROTECTED_RESULT_FOR_CLAIM_BINDING_ONLY",
    }
    (P2X_DIR / "P2_X_CLAIM_VALUES_V1.json").write_text(
        json.dumps(claim_values, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def update_claim_ledger() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    ledger["artifacts"].update(
        {
            "p2x_result": "evidence/p2x/P2_X_PROTECTED_RESULT_V1.json",
            "p2x_verification": "evidence/p2x/P2_X_INDEPENDENT_VERIFICATION_V1.json",
            "p2x_claim_values": "evidence/p2x/P2_X_CLAIM_VALUES_V1.json",
        }
    )
    existing = {claim["claim_id"] for claim in ledger["claims"]}
    for spec in P2X_CLAIMS:
        if spec["claim_id"] in existing:
            continue
        cannot_check = bool(spec.get("cannot_check"))
        claim = {
            "claim_id": spec["claim_id"],
            "region": spec["region"],
            "manuscript_status": "ASSERTED",
            "sentence": spec["sentence"],
            "support_type": "NONE_YET" if cannot_check else "OFFLINE_MECHANISM",
            "strength": "CANNOT_CHECK" if cannot_check else "DESCRIPTIVE",
            "numeric_bindings": [
                {"artifact": "p2x_claim_values", "key": key} for key in spec["bindings"]
            ],
            "support_artifacts": (
                []
                if cannot_check
                else [
                    {"artifact": "p2x_result", "key": "terminal"},
                    {"artifact": "p2x_verification", "key": "ok"},
                ]
            ),
            "note": spec["note"],
        }
        ledger["claims"].append(claim)
    LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


def update_human_ledger() -> None:
    text = HUMAN_LEDGER.read_text(encoding="utf-8")
    marker = "\n## Promotion rule\n"
    if "| P2-X A1 |" in text:
        return
    rows = """
| P2-X A1 | On 400 protected exact heterogeneous acquisition contracts, P2-X achieves 400/400 exact closure decisions versus 250/400 for the donor-complete available-route product; paired difference 0.375, 95% CI [0.3275, 0.4225], zero false task closures. | Protected exact P2-X result + independent verification; bounded contract only | `evidence/p2x/P2_X_PROTECTED_RESULT_V1.json`; `evidence/p2x/P2_X_INDEPENDENT_VERIFICATION_V1.json` | `SUPPORTED` |
| P2-X A2 | Route-local acquisition success and task-global scientific closure are distinct authority relations when material routes remain unresolved; an ideal product given identical semantics ties 400/400. | Protected exact P2-X result; no inherent-expressivity claim | same P2-X result/verification + `research/claim_expansion/p2/P2_X_CLAIM_EXPANSION_LEDGER_V1.md` | `SUPPORTED` |
| P2-X A3 | The same closure-authority layer improves safe stopping across genuinely different retrieval engines/providers/open-ended tasks. | No independent retriever implementations or new live multi-provider campaign | P2-X explicitly leaves deployed/retrieval-engine generality untested | `CANNOT_CHECK` |
"""
    if marker not in text:
        raise RuntimeError("human claim-ledger promotion marker missing")
    HUMAN_LEDGER.write_text(text.replace(marker, "\n" + rows + marker), encoding="utf-8")


def add_bibliography_identifiers() -> None:
    text = BIB.read_text(encoding="utf-8")
    for key, (arxiv_id, _title) in NEW_LITERATURE.items():
        entry_marker = f"@article{{{key},"
        if entry_marker not in text:
            raise RuntimeError(f"missing novelty-refresh bibliography entry: {key}")
        start = text.index(entry_marker)
        end = text.index("\n}\n", start)
        body = text[start:end]
        if "eprint =" in body or "doi =" in body or "url =" in body:
            continue
        insertion = f"\n  eprint = {{{arxiv_id}}},\n  archivePrefix = {{arXiv}},\n  primaryClass = {{cs.AI}},"
        text = text[:end] + insertion + text[end:]
    BIB.write_text(text, encoding="utf-8")


def register_fetcher_entries() -> None:
    text = FETCHER.read_text(encoding="utf-8")
    marker = 'ENTRIES: dict[str, tuple[str, str, str, str]] = {\n'
    if marker not in text:
        raise RuntimeError("literature fetcher ENTRIES marker missing")
    additions = []
    for key, (arxiv_id, title) in NEW_LITERATURE.items():
        if f'"{key}": (' in text:
            continue
        additions.append(
            f'    "{key}": (\n'
            f'        "arxiv", "{arxiv_id}",\n'
            f'        {json.dumps(title)},\n'
            f'        "pre_existing_independent_claim",\n'
            f'    ),\n'
        )
    if additions:
        text = text.replace(marker, marker + "".join(additions), 1)
    FETCHER.write_text(text, encoding="utf-8")


def fix_hostile_test_anchor() -> None:
    text = TEST.read_text(encoding="utf-8")
    old = '    marker = "rather than promoted.\\n"\n'
    new = '    marker = "\\n\\\\bibliographystyle{plain}\\n"\n'
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError("claim-ledger hostile-test insertion marker not found")
    TEST.write_text(text, encoding="utf-8")


def update_readiness() -> None:
    text = READINESS.read_text(encoding="utf-8")
    anchor = "- [x] OpenAIRE structured-identity discriminator and subsequent 400-row matched campaign retained; the latter remains `P2_WIDE_EXTERNAL_CANNOT_CHECK` after 400 DOI-crosswalk HTTP 400 failures, with all Actions artifacts mirrored before expiry.\n"
    line = "- [x] P2-X post-saturation exact successor retained as bounded A1/A2 evidence: 400/400 P2-X versus 250/400 donor-complete available-route product on 400 exact heterogeneous acquisition contracts; independent verification passes, B3 ideal typed product ties 400/400, and deployed/retrieval-engine generality remains `CANNOT_CHECK`.\n"
    if line not in text:
        if anchor not in text:
            raise RuntimeError("JOURNAL_READINESS result-evidence anchor missing")
        text = text.replace(anchor, anchor + line)
    READINESS.write_text(text, encoding="utf-8")


def main() -> None:
    write_p2x_evidence()
    update_claim_ledger()
    update_human_ledger()
    add_bibliography_identifiers()
    register_fetcher_entries()
    fix_hostile_test_anchor()
    update_readiness()
    print("P2-X promotion-integrity static repair complete")


if __name__ == "__main__":
    main()
