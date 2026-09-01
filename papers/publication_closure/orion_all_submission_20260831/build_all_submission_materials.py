#!/usr/bin/env python3
"""Build dual arXiv/journal submission materials for the ORION paper corpus.

The builder is a publication adapter, not scientific authority.  It starts from
current repository sources or already-closed publication sources, applies the
canonical author policy to attributed copies, preserves double-blind journal
copies, compiles both routes, and emits deterministic source/review archives.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAPERS = ROOT / "papers"
DATE = "2026-08-31"
EPOCH = (1980, 1, 1, 0, 0, 0)
AUTHOR = "Sze Chun Yiu"
AFFILIATION = "Stockholm University"
EMAIL = "sze-chun.yiu@fysik.su.se"
ACADEMIC_PAPER_SKILLS_REVISION = "be335c630240cd5e73535e8f813594b227d736a8"
ACADEMIC_PAPER_PIPELINE_VERSION = "1.20.0"
ACADEMIC_WRITING_VERSION = "1.18.0"
NATURE_POLISHING_VERSION = "7.5.0"
NATURE_REVIEWER_VERSION = "3.5.0"
NAMED_AUTHOR_TEX = rf"{AUTHOR}\\{AFFILIATION}\\\texttt{{{EMAIL}}}"
TMLR_STYLE = PAPERS / "orion-14-verified-scientific-discovery/manuscript/tmlr.sty"
TMLR_BST = PAPERS / "orion-14-verified-scientific-discovery/manuscript/tmlr.bst"
JAIR_STYLE = PAPERS / "publication_closure/vendor/jair-author-kit-20260216"


def spec(
    paper: str,
    slug: str,
    title: str,
    venue: str,
    review: str,
    category: str,
    authority: str,
    terminal: str,
    claim: str,
    negatives: list[str],
    *,
    source: str = "generic",
    status: str = "PACKAGE_COMPLETE__PORTAL_INPUTS_PENDING",
    crosslists: list[str] | None = None,
) -> dict:
    return locals()


SPECS = [
    spec("ORION-01", "orion-01-certificate-realization", "Restore-Sensitive Certificate Realization: Normal Forms and Intrinsic Support in Quantum Compilation", "Quantum", "identified", "quant-ph", "CLAIM_LEDGER_V4.md", "PACKAGE_COMPLETE_PENDING_FINAL_AUTHOR_CONFIRMATION_AND_ARXIV_POSTING", "A whole-instance deletion contract gives simultaneous support ceilings in the stated MultiTag grammar; within matched frozen families the same rank-only certificate language is exact at support two and loose by a five-to-one ratio when it omits whole-system Tag reconstruction.", ["The finite production-realization certificate was rejected and production transfer remains unestablished.", "The pinned PyZX attempt stopped after 74 of 4,681 words with CANNOT_CHECK_MOVE_COMPLETENESS; it does not refute scheduled full_reduce, prove move completeness, establish general MultiTag sharpness, or imply runtime, hardware, or quantum advantage."], source="orion01", crosslists=["cs.DS"]),
    spec("ORION-02", "orion-02-fiberguard-finite-fibre", "When a Representation Can Certify: Sharp Fibre-Diameter Limits and Minimal Refinement", "Transactions on Machine Learning Research", "double_blind", "cs.AI", "CLAIM_LEDGER_V3.md", "ORION_02_FINITE_FIBRE_BOUNDED_RELEASE", "Finite representation fibres admit an exact minimax certification radius and a constructive minimum-refinement characterization.", ["Preserved application studies fail at decision value, useful coverage, or held-out validity.", "The analytic joint-profile repair corrects a specification defect but does not establish empirical transfer value."], source="orion02", crosslists=["cs.LG"]),
    spec("ORION-03", "orion-03-typed-merge-falsification", "Typed Evidence Licenses for Fail-Closed Nonpromotion in Finite Rule Systems", "Journal of Automated Reasoning", "identified", "cs.LO", "CLAIM_LEDGER_V3.md", "ORION_03_BOUNDED_TYPED_AUTHORITY_RELEASE", "A finite positive conjunctive rule system propagates only evidence licenses shared by all premises and permitted by rule caps, with fail-closed nonpromotion after refutation.", ["The X.509 policy's zero errors are analytic identities, not learned performance.", "The paper is not a new general provenance theory, security evaluation, or external replication."], source="orion03", crosslists=["cs.AI"]),
    spec("ORION-04", "orion-04-rooted-completion-certificates", "The Fourth Generalized Davenport Constant of C5^3", "Electronic Journal of Combinatorics", "identified", "math.CO", "WAVE3_PUBLICATION_DISPOSITION_V3.json", "ORION04_C0_31_PROVED__IMPLIES_D4_C5CUBED_EXACT_30", "A complete 60-pattern, 78-branch exact obstruction cover proves that no length-31 total-zero sequence over C5^3 is free of zero sums of lengths one through five; hence D_4(C5^3)=30 and D_k(C5^3)=5k+10 for every k>=2.", ["The computation establishes a finite theorem but not novelty, peer review, or venue acceptance.", "The off-host replay uses the same source and is an independent execution, not an independent implementation; generic recurrence, localization, and zero-sum machinery remain donor-owned."], source="orion04"),
    spec("ORION-05", "orion-05-tare-expressivity", "Support-Two Exactness and Regime Geometry of Shared-Tag TARE Compilation", "Quantum", "identified", "quant-ph", "CLAIM_LEDGER_V4.md", "READY_TO_SUBMIT_SECOND_TIER__BOUNDED_EXACT_GRAMMAR", "Under the frozen grammar and unit objective, every instance has an exact support-at-most-two normal form, and a registered instance makes the support-two ceiling sharp.", ["The prespecified direct support-two implementation timed out on all six full-subject cells under 120 seconds.", "The 9,547 agreements and 688,041,472-case local audit do not establish runtime improvement, hardware benefit, full-circuit optimality, or a general block-encoding result."], crosslists=["cs.DS"]),
    spec("ORION-06", "orion-06-recursive-recovery", "Receipted Recursive Recovery of Negative Quantum-Method Results", "Transactions on Machine Learning Research", "double_blind", "cs.AI", "CLAIM_LEDGER_V4.md", "READY_TO_SUBMIT_SECOND_TIER__ONE_PROGRAMME_CASE_STUDY", "A complete one-programme case study shows how receipted recursive recovery can retain negative, absorbed, mixed, bounded-positive, lower-bound, and CANNOT_CHECK outcomes without false promotion.", ["No causal productivity improvement, false-novelty reduction, cross-domain superiority, or general reliability is claimed.", "The optional cross-domain benchmark is unexecuted and unavailable baseline/verifier cases remain CANNOT_CHECK."], source="orion06", crosslists=["cs.LG"]),
    spec("ORION-07", "orion-07-dual-instrument", "Controller--Host Agreement on Live Research Decisions: A Receipted Benchmark and First Measurement", "Transactions on Machine Learning Research", "double_blind", "cs.AI", "CLAIM_LEDGER_V3.md", "READY_TO_SUBMIT_TOP_TIER__HUMAN_FILING_METADATA_ONLY", "A frozen controller and structurally different host instrument can agree on prospective research-frontier decisions while still sharing a wrong diagnosis.", ["Only three valid prospectively frozen questions contribute to the current result; contaminated candidates stay excluded.", "N=3 questions does not establish calibration, reliability, predictive value, statistical independence, or generalization; the finite 53-row and 39,489-case zero-gap checks remain bounded nulls."], source="orion07", crosslists=["cs.LG"]),
    spec(
        "ORION-08",
        "orion-08-typed-state",
        "Typed Epistemic State under Partial Knowledge: Matched-Information Mechanism Studies and Real-Data Boundaries",
        "Transactions on Machine Learning Research",
        "double_blind",
        "cs.AI",
        "CLAIM_LEDGER_V4.md",
        "TIER_B_ORION08_COMPLETE__CONTROLLED_MECHANISMS_AND_BOUNDED_TRANSFER",
        "Six exact-synthetic matched-information families isolate how typed epistemic bindings change decisions, while a corrected finite criterion and three real-data instantiations delimit mixed held-out transfer.",
        [
            "Scoped versus never-reopen intervals cross zero in both registered regimes, and the remint-unnecessary transport regime is an exact tie.",
            "Twelve synthetic mean comparisons are reported without family-wise corrected bootstrap intervals; targeted verification and the deterministic-proxy acquisition contrast are most exposed.",
            "The ideal value-of-information donor absorbs the allocation-policy residual; the model-selection donor ties on the original world and leaves only a bounded misspecification result.",
            "The earlier refinement strictness wording was underspecified and is withdrawn; merely splitting an impure fibre does not guarantee lower risk.",
            "Same-distribution agreement on OpenML-CC18 and Defects4J is an algebraic instantiation, not independent theorem confirmation.",
            "Held-out OpenML transfer is adverse on three of five datasets relative to the attainable gap; Defects4J helps on ten of twelve projects but one genuine failure remains unexplained.",
            "The WorkflowHub study retains CANNOT_CHECK_NO_CONTRAST because every stratum predicts value.",
            "No deployed-agent, language-model, cryptographic-security, minimal-schema, universal-necessity, practical-superiority, or broad real-domain generalization claim is made.",
        ],
        crosslists=["cs.LG"],
    ),
    spec("ORION-09", "orion-09-compilation-regime-geometry", "Compilation Regime Geometry: A Receipted Programme for Mapping Exact Optimization Families", "Quantum", "identified", "quant-ph", "CLAIM_LEDGER_V2.md", "READY_TO_SUBMIT_SECOND_TIER__EXACT_MODEL_SPECIFIC_GEOMETRY", "Three exact model-specific compilation families separate intrinsic support, proof ceilings, objective certificates, and representation identifiability.", ["The TARE closed-form trade basis and a universal low-order state-preparation boundary are refuted.", "The QG15b representation has 43 irreducible errors among 1,146 cases; no generic transfer, hardware advantage, or externally independent proof is claimed."], crosslists=["cs.DS"]),
    spec("ORION-10", "orion-10-certified-static-forecasting", "Theorem-Backed Static Cost Forecasting with Refutable Explanations for Quantum Compilation", "Quantum", "identified", "quant-ph", "CLAIM_LEDGER_V3.md", "READY_TO_SUBMIT_SECOND_TIER__BOUNDED_STATIC_FORECAST", "For the frozen F2 family, a theorem identifies the exact static cost feature for all n, with 9,547 finite agreements and 102 of 102 staged predictions as bounded checks.", ["The original QG5 formula is refuted on a fresh n=3 instance (10 versus 11).", "A full 740-instance census refutes exact explanation by the named B-prime vocabulary: six of seven f_Bprime fibres are cost-mixed; the earlier 64-instance uniform offset was a selection artifact.", "The communication-support-two proof sector remains open, and no runtime, full-circuit, transfer, hardware, or reweighted-objective claim is made."], crosslists=["cs.DS"]),
    spec("ORION-11", "orion-11-recursive-epistemic-reconstruction", "Typed Responsibility Licensing for Scientific Revision: Transition Envelopes and Exact Mechanism Evidence", "Journal of Artificial Intelligence Research", "identified", "cs.AI", "REFRAMED_CONTRIBUTION_V2.md", "ORION11_COMPARATIVE_NECESSITY_AND_ECONOMY_RETIRED__BOUNDED_MECHANISM_RETAINED", "Typed responsibility-to-authority licensing attains the bounded mechanical constraints and 400/400 exact-contract decisions, while an information-equivalent product also ties at 400/400 as required by the factorization theorem.", ["The earlier +0.50625/+0.5167 comparative-necessity reading is withdrawn because ordered search recovers the margin.", "The costed-ordering successor refutes economy: the licensed policy costs about 1.818 times faithful Active-VOI at equal success and safety and 1.20 times the exact DP optimum, missing both preregistered gates.", "The formal costed-ordering terminal is CANNOT_CHECK__CHECKER_DISAGREEMENT on an ambiguous G6 scope; the cost-component attribution is ATTRIBUTION_INCOMPLETE, and neither defect rescues the jointly failed economy gates."], crosslists=["cs.LG"]),
    spec("ORION-12", "orion-12-open-world-scientific-discovery", "Acquisition Is Not Closure: Fail-Closed Control for Open-World Scientific-Literature Discovery", "Information Processing & Management", "identified", "cs.IR", "PUBLICATION_FREEZE_ADDENDUM_V2.md", "CURRENT_BOUNDED_CONTROL_METHOD__EXTERNAL_SUPERIORITY_NOT_SUPPORTED__ESTIMATOR_SIGNAL_INERT", "A fail-closed controller separates route stopping from task closure and retains unavailable material routes as open obligations.", ["The registered TREC-COVID recall/cost gate fails: recall@100 delta -0.01769 with 95% bootstrap interval [-0.02729,-0.00906], while reads increase 175.7%.", "On ArguAna, density normalization and a query-conditional estimator each leave all five decisions unchanged; the rank-overlap marginal is signal-inert there, so the failure is in the measurement rather than its threshold.", "OpenAIRE remains CANNOT_CHECK after provider invalidity; the fresh 48-task campaign was not accessed; favorable nDCG and complete-gold diagnostics do not establish external superiority or open-world completeness."], crosslists=["cs.AI", "cs.DL"]),
    spec("ORION-13", "orion-13-global-knowledge-portrait", "Coordinate-Governed Mapping of Source-Local Scientific Projections", "Semantic Web Journal", "identified", "cs.AI", "SCOPED_PUBLICATION_TRACK_V1.md", "P3_C5_C9_REPLICATED_MAPPING__P3_C10_C11_EXACT_IDENTITY_AUTHORITY", "Coordinate-governed mapping prevents six false merges in a 32-case fixed panel and supports the registered 400-contract decision scope.", ["All six discordances lie in one polarity family and fixed-panel intervals are diagnostics, not population uncertainty.", "An information-equivalent typed product ties 400/400; raw-text extraction and downstream scientific utility remain undetermined."], source="final_zip", crosslists=["cs.DL"]),
    spec("ORION-14", "orion-14-verified-scientific-discovery", "Non-Escalating Scientific Authority under Content-Bound Evidence and Protected Evaluation", "Transactions on Machine Learning Research", "double_blind", "cs.AI", "PUBLICATION_FREEZE_ADDENDUM_V1.md", "P4_PROTECTED_AUTHORITY_V2_BOUNDED__H3_NOT_SUPPORTED", "A content-bound, non-escalating authority pipeline reduces protected false promotion under the frozen family-level analysis.", ["H3 is NOT_SUPPORTED: both arms are correct on 30/30 eligible cases.", "The legacy 39-case live-model arm remains excluded; inference uses 12 attack-family clusters, not 360 case rows as independent replicates."], source="final_zip", crosslists=["cs.LG"]),
    spec("ORION-15", "orion-15-self-orion", "Minimal Method Revision under Observational Equivalence: Failure-Governed Evolution without Self-Promotion", "Transactions on Machine Learning Research", "double_blind", "cs.AI", "WAVE3_PUBLICATION_DISPOSITION_V1.json", "SELF_ORION_PROTECTED_TRANSFER_NOT_ESTABLISHED__GOVERNANCE_THEORY_RETAINED", "The bounded paper formalizes failure-governed method revision under observational equivalence and retains a descriptive 22/24 versus 23/24 case study without claiming protected transfer or autonomous self-improvement.", ["Protected longitudinal transfer, causal treatment superiority, retention and harm gates, anytime-safe promotion, and independent protected-host execution remain unestablished.", "The current disposition grants no novelty, venue, top-tier, or external-reproduction authority; the journal route requires final author filing confirmation."], status="PACKAGE_COMPLETE__JOURNAL_FILING_REQUIRES_AUTHORITY_CONFIRMATION", crosslists=["cs.LG"]),
    spec("ORION-16", "orion-16-formal-epistemic-structures-and-mechanics", "Formal Epistemic Structures and Mechanics", "Artificial Intelligence", "identified", "cs.AI", "P6_ACTIVE_CLAIM_AUTHORITY_V1.json", "P6_CERTIFICATE_LIFTING_SEMANTICS_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT", "A conservative certificate-lifting semantics proves local frame and propagation laws over uninterpreted sorts and recovers the finite star-graph model as a verified instance.", ["Three V4 quantities are withdrawn under the theorem-level scrutiny retained in the manuscript.", "The bounded recovery is not external validation, naturalistic superiority, inherent expressivity, or a claim that donor certificates establish scientific standing by themselves."], crosslists=["cs.LO"]),
    spec("ORION-17", "orion-17-epistemic-navigation-open-worlds", "Epistemic Navigation in Open Worlds", "Artificial Intelligence", "identified", "cs.AI", "P7_ACTIVE_CLAIM_AUTHORITY_V1.json", "P7_CLOSURE_CARRYING_NAVIGATION_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT", "A closure-carrying navigation semantics gives a sound associative composition law with explicit obligation contracts and recovers the bounded five-family model as an instance.", ["The composition rule is provably incomplete against its own obligation semantics when equivalent demanded obligations lack a registered bridge.", "The result is fail-closed rather than exact and establishes neither universal transport nor naturalistic navigation superiority; external validation remains CANNOT_CHECK.", "The current-path substitute-campaign checker fails three seal bindings after the R0 identifier rewrite. The original pre-R0 seal and corpus arithmetic verify as intact, but no repaired current-path seal or additional external authority is claimed."], crosslists=["cs.SE"]),
    spec("ORION-18", "orion-18-epistemic-authority-autonomous-science", "A Compositional Calculus for Cross-Domain Scientific Authority", "Autonomous Agents and Multi-Agent Systems", "identified", "cs.AI", "P8_ACTIVE_CLAIM_AUTHORITY_V1.json", "P8_CROSS_DOMAIN_SCIENTIFIC_AUTHORITY_COMPOSITION_SUPPORTED__13_DONOR_FORMAL_ENVELOPE__IDEAL_PRODUCT_EQUIVALENT", "A typed lifting and composition calculus conserves native authority across thirteen donor families and matches an equally typed decentralized product on the registered 3,072-state finite model.", ["The 39,936 evaluations replay 3,072 states across donor labels; donor family is a replication factor, not a state dimension, and zero donor-dependent verdict changes are the conservativity result.", "The result is not generic authorization novelty, deployed-agent superiority, externally governed semantic authority, or centralized expressive advantage; external validation remains CANNOT_CHECK." ]),
    spec("ORION-19", "orion-19-structured-epistemic-learning", "Diagnosing Learning-System Failures Before Escalating Compute", "Transactions on Machine Learning Research", "double_blind", "cs.LG", "PUBLICATION_FREEZE_ADDENDUM_V1.md", "P9_BOUNDED_CAUSAL_DIAGNOSTIC_PEER_REVIEW_READY", "Five fixed heterogeneous task families support a bounded diagnostic distinction between accessibility, representation, and compute limitations.", ["Wine is null, Qwen2.5 monotone scaling is negative, digit accessibility is indeterminate, symbol reminting withdraws an older serialization contrast, and the redraw follow-up fails stability.", "Five families support descriptive comparison only; no population-level or broad causal generalization is claimed."], source="final_zip", crosslists=["cs.AI"]),
    spec("ORION-20", "orion-20-structured-problem-solving", "Obstruction-Certified Method-Language Expansion: Formal Closure Theory and an Exact Measurement Contract", "Journal of Automated Reasoning", "identified", "cs.AI", "P10_ACTIVE_CLAIM_AUTHORITY_V1.json", "P10_PROSPECTIVE_PROTOCOL_ONLY", "The paper contributes formal closure conditions and a prospectively frozen measurement contract for obstruction-certified method-language expansion; it reports no protected P10 result.", ["All 12,960 planned run cells were unexecuted and all 480 protected cases remain CANNOT_CHECK because the frozen donor/evaluator inputs were absent.", "No verified-solving superiority, outside-closure expansion, autonomous invention, or protected transfer is claimed; execution is not authorized under the current identity."], status="PACKAGE_COMPLETE__PROSPECTIVE_PROTOCOL_ONLY__FILING_AUTHORITY_CONFIRMATION_REQUIRED", crosslists=["cs.LO"]),
    spec("ORION-21", "orion-21-state-as-computation", "State as Computation: Moving Structural Search between Representation Construction and Downstream Reasoning", "Transactions on Machine Learning Research", "double_blind", "cs.LG", "P11_ACTIVE_CLAIM_AUTHORITY_V2.json", "P11_WIDTH_CONDITIONED_AUTHORITY_SUPPORTED", "A width-conditioned controlled result locates when structural search can move between representation construction and downstream reasoning.", ["The sparse-decoder fourfold claim fails in one of two cells; the pooled attack prevails at width three.", "Digits support is below the frozen 8/10 gate under all registered decoders; the independent replication unit is seed n=3, not nine cells."], source="final_zip", crosslists=["cs.AI"]),
    spec("ORION-22", "orion-22-adaptive-state-reasoning", "Adaptive State--Reasoning Co-Design under Matched Total Compute", "Transactions on Machine Learning Research", "double_blind", "cs.LG", "P12_ACTIVE_CLAIM_AUTHORITY_V5.json", "P12_SIGNAL_COMPLEMENTARITY_AUTHORITY_SUPPORTED", "Across 32 independent simulated family blocks, the equal-action two-signal policy improves exact allocation accuracy by 0.253906 over the stronger one-signal policy; the unchanged allocator also has zero regret in nine bounded internal exact-domain cases.", ["The historical P12A comparison is invalid because action capabilities differed; the frozen robustness study breaks both price and distribution-shift axes.", "The price-aware successor is conditional on exact published charge certificates; certificate availability before action, public-data transfer, naturalistic-agent superiority, and external validation remain CANNOT_CHECK."], status="PACKAGE_COMPLETE__BOUNDED_SPECIALIST_ROUTE_ONLY", crosslists=["cs.AI"]),
    spec("ORION-23", "orion-23-responsibility-carrying-state", "Responsibility-Carrying State: Auditable Sufficiency, Reopen Contracts, and Safe State Reuse", "Autonomous Agents and Multi-Agent Systems", "identified", "cs.AI", "P13_ACTIVE_CLAIM_AUTHORITY_V3.json", "P13_CONTROLLED_COMPOSED_SAFETY_EFFICACY_AUTHORITY_SUPPORTED", "Authenticated responsibility-indexed state prevents unsafe reuse in the declared complete authored finite panels and composed world.", ["The earlier self-scored zero has no reachable harm opportunities and carries no empirical safety authority.", "The 12,288-episode result is an authored finite world, not population inference or external validation; predecessor and comparator unsafe-reuse failures remain visible."], source="final_zip"),
    spec("ORION-24", "orion-24-orion-rse", "Fail-Closed Evaluation Contracts for Autonomous Research Software Engineering", "Autonomous Agents and Multi-Agent Systems", "identified", "cs.SE", "WAVE3_PUBLICATION_DISPOSITION_V1.json", "ORION24_EXTERNAL_ACQUISITION_BLOCKED__EXECUTABLE_HANDOFF_COMPLETE", "The viewpoint specifies a fail-closed custody and authority contract for evaluating autonomous research-software agents.", ["Zero of eight denotes missing prerequisite artifact classes, not attempted external cases.", "Execution was unauthorized, external scientific n=0, all efficacy endpoints are CANNOT_CHECK, and the architecture is specified rather than implemented end to end."], source="final_zip", crosslists=["cs.AI"]),
    spec("ORION-25", "orion-25-orion-research-harness", "Fail-Closed Research Execution: Receipt Semantics and Independence Contracts", "Transactions on Machine Learning Research", "double_blind", "cs.SE", "P15_ACTIVE_CLAIM_AUTHORITY_V3.json", "P15_BOUNDED_SEI_PROVENANCE_ATTESTATION_EARNED", "Bounded fault, provenance-interoperability and Ed25519-chain studies separate execution integrity, provenance and attestation from scientific validity and claim authority.", ["Full key-set compromise is a binding negative: signatures detect 0/6 forgeries and an unscoped chain-as-science rule false-promotes all 6/6.", "A valid stale artifact can remain green after the current producer is killed, so artifact integrity does not establish process liveness.", "Key custody, universal correctness, production scale, superiority, external validation and top-tier readiness remain unestablished."], status="PACKAGE_COMPLETE__BOUNDED_SPECIALIST_ROUTE_ONLY", crosslists=["cs.AI"]),
]


def run(*args: str, cwd: Path | None = None, input_text: str | None = None) -> str:
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = "1788134400"
    env["TZ"] = "UTC"
    proc = subprocess.run(args, cwd=cwd or ROOT, env=env, text=True, input=input_text,
                          encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode:
        raise RuntimeError(f"command failed ({proc.returncode}) in {cwd or ROOT}: {' '.join(args)}\n{proc.stdout[-16000:]}")
    return proc.stdout


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def copy_tree(src: Path, dst: Path) -> None:
    generated = {"main.pdf", "main.aux", "main.bbl", "main.blg", "main.fdb_latexmk", "main.fls", "main.log", "main.out", "main.toc", "main.xdv", "main.markdown.lua", "main.markdown.out"}
    for path in sorted(src.rglob("*")):
        if not path.is_file() or path.name in generated or ".git" in path.parts:
            continue
        out = dst / path.relative_to(src)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)


def deterministic_zip(src: Path, dst: Path) -> None:
    with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in src.rglob("*") if p.is_file()):
            info = zipfile.ZipInfo(path.relative_to(src).as_posix(), EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, path.read_bytes())


def command_span(text: str, command: str) -> tuple[int, int] | None:
    match = re.search(rf"\\{re.escape(command)}\*?(?:\[[^\]]*\])?\s*\{{", text)
    if not match:
        return None
    open_at = text.find("{", match.start())
    depth = 0
    for i in range(open_at, len(text)):
        if text[i] == "{" and (i == 0 or text[i - 1] != "\\"):
            depth += 1
        elif text[i] == "}" and (i == 0 or text[i - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return match.start(), i + 1
    raise RuntimeError(f"unterminated \\{command} command")


def replace_command(text: str, command: str, value: str) -> str:
    span = command_span(text, command)
    if span is None:
        raise RuntimeError(f"missing \\{command} command")
    return text[:span[0]] + rf"\{command}{{{value}}}" + text[span[1]:]


def normalize_paths(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".tex", ".md", ".bib"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            text = (
                text.replace("../figures/", "figures/")
                .replace("../tables/", "tables/")
                .replace("../manuscript/", "manuscript/")
            )
            path.write_text(text, encoding="utf-8")


def flatten_source(root: Path) -> Path:
    mains = list(root.rglob("main.tex"))
    if len(mains) != 1:
        raise RuntimeError(f"expected one main.tex in {root}, got {mains}")
    if mains[0].parent == root:
        return root
    out = root.parent / "flat"
    copy_tree(mains[0].parent, out)
    for sibling in root.iterdir():
        if sibling == mains[0].parent or not sibling.is_dir():
            continue
        copy_tree(sibling, out / sibling.name)
    normalize_paths(out)
    return out


def anonymize_tree(root: Path) -> None:
    replacements = {
        AUTHOR: "The author",
        EMAIL: "anonymous@example.invalid",
        AFFILIATION: "Affiliation withheld for double-blind review",
        "Independent Researcher": "Affiliation withheld for double-blind review",
        "SzeChunYiu": "anonymous-author",
        "github.com/SzeChunYiu/ORION": "anonymous review archive",
    }
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".tex", ".md", ".bib", ".txt", ".json", ".yaml", ".yml", ".csv"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            for old, new in replacements.items():
                text = text.replace(old, new)
            path.write_text(text, encoding="utf-8")


def set_identity(root: Path, spec_: dict, variant: str) -> None:
    main = root / "main.tex"
    text = main.read_text(encoding="utf-8")
    title_tex = spec_["title"].replace("&", r"\&")
    # Metadata titles are deliberately plain ASCII. Restore mathematical
    # typesetting only in the TeX title surface.
    title_tex = title_tex.replace("C5^3", r"\(C_5^3\)")
    text = replace_command(text, "title", title_tex)
    anonymous = variant == "journal" and spec_["review"] == "double_blind"
    if spec_["paper"] != "ORION-03" and command_span(text, "author") is not None:
        text = replace_command(text, "author", "Anonymous authors" if anonymous else NAMED_AUTHOR_TEX)
    if spec_["paper"] == "ORION-03":
        text = text.replace(
            r"\affil*[1]{\orgname{Independent Researcher}}",
            rf"\affil*[1]{{\orgname{{{AFFILIATION}}}}}",
        )
    if command_span(text, "date") is not None:
        text = replace_command(text, "date", "31 August 2026")
    text = re.sub(r"pdfauthor\s*=\s*\{[^{}]*\}", "pdfauthor={Anonymous}" if anonymous else f"pdfauthor={{{AUTHOR}}}", text)
    text = re.sub(r"\\shortauthors\{[^{}]*\}", r"\\shortauthors{Anonymous authors}" if anonymous else rf"\\shortauthors{{{AUTHOR}}}", text)
    main.write_text(text, encoding="utf-8")
    if anonymous:
        anonymize_tree(root)
        text = main.read_text(encoding="utf-8")
        if command_span(text, "author") is not None:
            text = replace_command(text, "author", "Anonymous authors")
        text = re.sub(r"pdfauthor\s*=\s*\{[^{}]*\}", "pdfauthor={Anonymous}", text)
        main.write_text(text, encoding="utf-8")
    else:
        # Identity must be coherent across every attributed source surface,
        # including templates and manuscript copies retained beside main.tex.
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".tex", ".md", ".bib", ".txt", ".json", ".yaml", ".yml", ".csv"}:
                source_text = path.read_text(encoding="utf-8", errors="replace")
                source_text = source_text.replace("Independent Researcher", AFFILIATION)
                path.write_text(source_text, encoding="utf-8")


def convert_to_tmlr(root: Path) -> None:
    main = root / "main.tex"
    text = main.read_text(encoding="utf-8")
    if "\\usepackage{tmlr}" not in text and "\\usepackage[preprint]{tmlr}" not in text:
        text = re.sub(r"\\documentclass(?:\[[^\]]*\])?\{article\}", r"\\documentclass[10pt]{article}\n\\usepackage{tmlr}", text, count=1)
        text = re.sub(r"^\\usepackage(?:\[[^\]]*\])?\{geometry\}\s*$", "", text, flags=re.M)
    # tmlr.sty owns natbib; a second explicitly optioned load causes an option
    # clash in otherwise valid manuscript trees.
    text = re.sub(r"^\\usepackage(?:\[[^\]]*\])?\{natbib\}\s*$", "", text, flags=re.M)
    if "\\def\\openreview" not in text:
        marker = "\\begin{document}"
        text = text.replace(marker, "\\def\\month{08}\n\\def\\year{2026}\n\\def\\openreview{\\url{https://openreview.net/}}\n" + marker, 1)
    text = re.sub(
        r"\\bibliographystyle\{(?:unsrt|plain|abbrv)\}",
        r"\\bibliographystyle{tmlr}",
        text,
    )
    main.write_text(text, encoding="utf-8")
    if not (root / "tmlr.sty").exists():
        shutil.copy2(TMLR_STYLE, root / "tmlr.sty")
    if TMLR_BST.exists() and not (root / "tmlr.bst").exists():
        shutil.copy2(TMLR_BST, root / "tmlr.bst")


def convert_from_tmlr(root: Path) -> None:
    """Render the named arXiv route without double-blind TMLR furniture."""
    main = root / "main.tex"
    text = main.read_text(encoding="utf-8")
    text = re.sub(
        r"\\usepackage(?:\[[^\]]*\])?\{tmlr\}",
        r"\\usepackage[margin=1in]{geometry}\n\\usepackage{natbib}",
        text,
        count=1,
    )
    text = re.sub(r"^\\def\\(?:month|year|openreview)\{.*?\}\s*$", "", text, flags=re.M)
    main.write_text(text, encoding="utf-8")


def adapt_ipm(root: Path, spec_: dict) -> None:
    src = root / "ipm_submission.tex"
    text = src.read_text(encoding="utf-8")
    text = re.sub(
        r"\\documentclass(?:\[[^\]]*\])?\{cas-sc\}",
        r"\\documentclass[11pt]{article}\n\\usepackage[margin=1in]{geometry}\n\\usepackage[hidelinks]{hyperref}",
        text,
        count=1,
    )
    text = replace_command(text, "title", spec_["title"])
    text = replace_command(text, "author", NAMED_AUTHOR_TEX)
    text = text.replace(
        r"\usepackage{xurl}",
        "\\usepackage{xurl}\n\\newcommand{\\idt}[1]{\\path{#1}}",
        1,
    )
    text = re.sub(r"^\\shorttitle\{.*?\}\s*$", "", text, flags=re.M)
    text = re.sub(r"^\\shortauthors\{.*?\}\s*$", "", text, flags=re.M)
    text = re.sub(r"pdfauthor\s*=\s*\{[^{}]*\}", f"pdfauthor={{{AUTHOR}}}", text)
    write(root / "main.tex", text)
    src.unlink()


def adapt_jair(root: Path) -> None:
    """Apply JAIR's mandatory post-2025 author kit to the journal route."""
    main = root / "main.tex"
    text = main.read_text(encoding="utf-8")
    text = re.sub(
        r"\\documentclass(?:\[[^\]]*\])?\{article\}",
        r"\\documentclass[manuscript,screen,review]{jair}",
        text,
        count=1,
    )
    # acmart/jair owns page geometry, hyperlinks and caption formatting.
    text = re.sub(r"^\\usepackage(?:\[[^\]]*\])?\{(?:geometry|hyperref|caption)\}\s*$", "", text, flags=re.M)
    # TeX Live 2026's acmart font stack defines \Bbbk through newtxmath before
    # this legacy source loads amssymb.  Clear only that duplicate symbol before
    # amssymb so the official JAIR class and the manuscript can coexist.
    text = text.replace(
        r"\usepackage{amsmath,amssymb}",
        "\\usepackage{amsmath}\n\\let\\Bbbk\\relax\n\\usepackage{amssymb}",
        1,
    )
    text = re.sub(r"^\\author\{.*?\}\s*$", "", text, flags=re.M)
    text = re.sub(r"^\\date\{.*?\}\s*$", "", text, flags=re.M)
    identity = rf"""
\setcopyright{{none}}
\acmDOI{{}}
\JAIRAE{{}}
\JAIRTrack{{}}
\author{{{AUTHOR}}}
\authornote{{{AFFILIATION}. Corresponding author.}}
\email{{{EMAIL}}}
\renewcommand{{\shortauthors}}{{Yiu}}
"""
    text = text.replace("\\begin{document}", identity + "\n\\begin{document}", 1)
    # acmart/JAIR collects title and abstract metadata before \maketitle. Legacy
    # article sources commonly place \maketitle first, so move it immediately
    # after the first abstract environment without changing abstract bytes.
    text = text.replace("\\maketitle", "", 1)
    text = text.replace("\\end{abstract}", "\\end{abstract}\n\\maketitle", 1)
    main.write_text(text, encoding="utf-8")
    for asset in ("acmart.cls", "jair.cls", "acmauthoryear.bbx", "acmauthoryear.cbx", "acmdatamodel.dbx", "ccicons.sty"):
        shutil.copy2(JAIR_STYLE / asset, root / asset)


def adapt_semantic_web(root: Path) -> None:
    """Meet the current SAGE Semantic Web structured-abstract surface."""
    abstract = root / "sections/00-abstract.tex"
    if not abstract.exists():
        raise RuntimeError("ORION-13 journal source lacks sections/00-abstract.tex")
    write(abstract, r"""\textbf{Purpose.} This study tests whether scientific claims can be mapped
without hiding the coordinate that determines agreement.
\textbf{Design/methodology/approach.} A coordinate-governed rule keeps referent,
construct, measurement, context, polarity, modality, and attribution conditions
separate and permits explicit non-merge. Evaluation uses a prospectively frozen,
case-identifier-disjoint 32-case public-reference holdout, a structurally separate
scorer, and a separate 400-contract exact battery.
\textbf{Findings.} The rule makes zero false merges on the holdout, versus 0.1875
for flat predicate canonicalization; the paired difference is -0.1875, with a
fixed-panel bootstrap diagnostic of [-0.34375,-0.0625]. Its false-split difference
from an exact-coordinate conservative control is 0.000. The separate scorer
reproduces every case-level decision. On the contract battery, the rule scores
400/400, versus 250/400 for a donor-complete product and 50/400 for a compensatory
product; an information-equivalent typed product also scores 400/400.
\textbf{Research limitations/implications.} The evidence concerns structured
inputs and fixed panels. Raw-text extraction, expert-atlas generality, population
uncertainty, and downstream scientific utility are untested. All observed errors
are polarity contrasts. The rule is deterministic and each evaluation decision
remains traceable to frozen records.
\textbf{Originality/value.} The contribution is a bounded, auditable mapping
contract that preserves non-merge and undetermined outcomes while showing exactly
when coordinate erasure creates false agreement. It does not claim superiority
over information-equivalent typing.
\endinput
""")
    main = root / "main.tex"
    text = main.read_text(encoding="utf-8")
    if "Semantic interoperability" not in text:
        text = text.replace(
            r"\end{abstract}",
            r"\end{abstract}" + "\n\n" +
            r"\noindent\textbf{Keywords:} Semantic interoperability; knowledge representation; evidence provenance; coordinate systems; knowledge graphs.",
            1,
        )
    main.write_text(text, encoding="utf-8")


def insert_elsevier_ai_declaration(root: Path) -> None:
    """Insert Elsevier's required named disclosure immediately above references."""
    main = root / "main.tex"
    text = main.read_text(encoding="utf-8")
    if "Declaration of generative AI and AI-assisted technologies" in text:
        return
    declaration = r"""
\section*{Declaration of generative AI and AI-assisted technologies in the writing process}
During preparation of this work, the author used OpenAI ChatGPT and Codex for
drafting, editing, source checking, adversarial review, and submission-package
preparation. The author reviewed the output and takes full responsibility for
the publication's content.

"""
    markers = [r"\printbibliography", r"\bibliography{", r"\begin{thebibliography}"]
    positions = [text.find(marker) for marker in markers if text.find(marker) >= 0]
    if not positions:
        raise RuntimeError(f"cannot place Elsevier AI declaration in {main}")
    at = min(positions)
    text = text[:at] + declaration + text[at:]
    main.write_text(text, encoding="utf-8")


def special_source(spec_: dict, variant: str, root: Path) -> Path:
    paper = PAPERS / spec_["slug"]
    mode = spec_["source"]
    if mode == "orion01":
        final = paper / "journal_package_final/submission"
        tex = final / "Restore-Sensitive_Certificate_Realization.tex"
        shutil.copy2(tex, root / "main.tex")
        if (final / "anc").exists():
            copy_tree(final / "anc", root / "anc")
        return root
    if mode == "orion02":
        base = paper / "journal_package_final/submission"
        name = "When_a_Representation_Can_Certify.tex" if variant == "journal" else "When_a_Representation_Can_Certify_arxiv.tex"
        if not (base / name).exists():
            # The final TMLR closure intentionally stores only the anonymous
            # review source. The arXiv adapter starts from those exact
            # scientific bytes and applies the named identity block below.
            name = "When_a_Representation_Can_Certify.tex"
        shutil.copy2(base / name, root / "main.tex")
        for item in ["references.bib", "tmlr.sty", "tmlr.bst"]:
            if (base / item).exists():
                shutil.copy2(base / item, root / item)
        return root
    if mode == "orion03":
        copy_tree(paper / "journal_package_final/submission/source", root)
        # The historical release source remains useful for the exact Springer
        # class, bibliography, template, and build assets, but it is not the
        # current scientific source.  Rebind every new submission build to the
        # designated V3 manuscript before generating LaTeX.  This prevents the
        # upload-facing PDF/source archive from silently preserving an older
        # prose surface after MANUSCRIPT_V3.md has become canonical.
        shutil.copy2(paper / "MANUSCRIPT_V3.md", root / "MANUSCRIPT.md")
        run(
            "pandoc",
            "MANUSCRIPT.md",
            "--from=markdown+yaml_metadata_block",
            "--to=latex",
            "--natbib",
            "--top-level-division=section",
            "--template=jar-pandoc-template.tex",
            "--wrap=preserve",
            "--output=main.tex",
            cwd=root,
        )
        main = root / "main.tex"
        text = main.read_text(encoding="utf-8")
        text = text.replace(
            r"\section*{Statements and Declarations}",
            r"\backmatter" + "\n\n" + r"\section*{Statements and Declarations}",
            1,
        )
        main.write_text(text, encoding="utf-8", newline="\n")
        return root
    if mode == "orion04":
        run("python3", "submission/final-20260831/build_package.py", cwd=paper)
        with zipfile.ZipFile(paper / "submission/final-20260831/source.zip") as zf:
            zf.extractall(root)
        manuscript = root / "manuscript.md"
        publication_text = manuscript.read_text(encoding="utf-8")
        publication_text = re.sub(
            r"\n\*\*Affiliation:\*\*[^\n]*\n\s*\n\*\*Correspondence:\*\*[^\n]*\n\s*\n",
            "\n",
            publication_text,
            count=1,
        )
        manuscript.write_text(publication_text, encoding="utf-8")
        # Match the paper's proven publication builder. The explicit
        # tex_math_single_backslash extension changes how literal underscores
        # in the Markdown evidence ledger are tokenised and can emit invalid
        # LaTeX even though the canonical build succeeds.
        run("pandoc", "manuscript.md", "--standalone", "--to=latex", "-o", "main.tex", cwd=root)
        return root
    if mode == "final_zip":
        with zipfile.ZipFile(paper / "submission/final-20260831/source.zip") as zf:
            zf.extractall(root)
        flattened = flatten_source(root)
        if spec_["paper"] == "ORION-13" and variant == "journal":
            adapt_semantic_web(flattened)
        return flattened
    if mode in {"orion06", "orion07"}:
        copy_tree(paper / "submission_tmlr", root)
        copy_tree(paper / "manuscript", root / "manuscript")
        normalize_paths(root)
        return root
    copy_tree(paper / "manuscript", root)
    for name in ("figures", "tables"):
        if (paper / name).is_dir() and not (root / name).exists():
            copy_tree(paper / name, root / name)
    normalize_paths(root)
    if spec_["paper"] == "ORION-12":
        adapt_ipm(root, spec_)
    if spec_["paper"] in {"ORION-16", "ORION-17", "ORION-18"}:
        adapt_overlay_abstract(root, spec_["paper"])
    return root


def adapt_overlay_abstract(root: Path, paper: str) -> None:
    """Add a filing abstract while retaining successor-overlay body prose."""
    abstracts = {
        "ORION-16": r"""Scientific-work systems often inherit certificates from governance mechanisms, but a certificate need not remain valid after the scientific state changes. We give a conservative lifting semantics with two components. A local frame calculus states when separated changes commute and when a declared frame determines the result. A dependency calculus states which certificates must reopen after change and proves reopening sound, complete, minimal, conservative, and monotone over graphs of arbitrary size, including cycles. Both components are proved over uninterpreted sorts rather than inferred from bounded enumeration. A finite star-graph interpretation recovers the earlier coordinate model and reproduces its valid revalidation counts. The audit also retains three negative results: two historical counts were forced by the generator and a third property had not been evaluated, so none is evidence of discrimination. The contribution is a bounded formal semantics for lifting donor certificates into continued scientific standing. It does not claim a new donor governance mechanism, empirical deployment performance, or an inherent expressive advantage over an information-equivalent product.""",
        "ORION-17": r"""Scientific navigation transforms can preserve a local plan while losing the obligations needed for task-global scientific closure. We give a closure-carrying navigation semantics in which a donor-valid transformation carries closure only through an explicit obligation witness. Over uninterpreted sorts, identity is a unit, composition is associative, and a composite carries closure when both legs carry it and their intermediate obligation contracts match or have a registered bridge. The side conditions are explicit: reflexivity supports the unit law, extensionality supports equational forms, and obligation-totality composition requires containment of demanded obligations. A finite five-family interpretation reproduces 25 composition successes and 25 bridge-mismatch countermodels. A negative result is retained: the rule is provably incomplete against its own obligation semantics because it can refuse extensionally equivalent demands when no bridge is registered. The calculus is therefore sound and fail-closed, not exact. It does not claim a new donor navigation mechanism, external validation, or deployed-agent superiority.""",
        "ORION-18": r"""Local authorization, delegation, verification, and claim-evidence mechanisms do not by themselves establish a different scientific obligation. We introduce a bounded scientific-authority lifting and composition calculus spanning thirteen donor families. Target obligations are typed by domain, kind, scope, content, and epoch. Donor-native authority is conserved, and scientific authority propagates only through type preservation or narrowing, or through an explicit subject- and epoch-bound protected coercion. Blockers remain three-valued: REFUTED, UNDETERMINED, and ESTABLISHED; UNDETERMINED yields CANNOT_CHECK. Alternative complete support families make revocation exact. A finite model contains 3,072 authority states and 39,936 donor-family evaluations; a second implementation reproduces the canonical enumeration. The thirteen families are a replication factor, not a state dimension, and the result is equivalent to an ideal information-matched product. The contribution is a bounded cross-domain authority-composition semantics. It does not claim generic authorization, ownership of donor mechanisms, local scientific verification, deployed-agent performance, centralized expressive superiority, or naturalistic evidence of effectiveness.""",
    }
    main = root / "main.tex"
    text = main.read_text(encoding="utf-8")
    marker = r"\maketitle"
    if marker not in text:
        raise RuntimeError(f"{paper} maketitle cannot be located")
    filing_abstract = "\n\n\\begin{abstract}\n" + abstracts[paper].strip() + "\n\\end{abstract}\n"
    text = text.replace(marker, marker + filing_abstract, 1)
    main.write_text(text, encoding="utf-8")

    section = root / "sections/01-replacement-abstract.tex"
    body = section.read_text(encoding="utf-8")
    body, count = re.subn(
        r"\A\\section\*?\{(?:Replacement abstract for V5|Abstract)\}\s*",
        r"\\section{Overview and result}\n\n",
        body,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"{paper} abstract heading cannot be normalized")
    section.write_text(body, encoding="utf-8")


def compile_source(spec_: dict, variant: str, root: Path) -> Path:
    if variant == "journal" and spec_["review"] == "double_blind":
        convert_to_tmlr(root)
    elif variant == "arxiv":
        convert_from_tmlr(root)
    set_identity(root, spec_, variant)
    # TeX Live 2026 longtable validates the declared caption-counter name even
    # for Pandoc's intentionally unnumbered tables.  Older releases accepted
    # ``LTcaptype=none`` without a counter.  Define that no-op counter so the
    # same source remains portable without changing table content or numbering.
    main = root / "main.tex"
    main_text = main.read_text(encoding="utf-8")
    if r"\def\LTcaptype{none}" in main_text and r"\newcounter{none}" not in main_text:
        main_text = main_text.replace(r"\begin{document}", r"\newcounter{none}" + "\n" + r"\begin{document}", 1)
        main.write_text(main_text, encoding="utf-8")
    if spec_["paper"] == "ORION-11" and variant == "journal":
        adapt_jair(root)
    if variant == "journal" and spec_["venue"] in {"Artificial Intelligence", "Information Processing & Management"}:
        insert_elsevier_ai_declaration(root)
    apply_targeted_layout_guards(root, spec_["paper"], variant)
    args = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error"]
    if spec_["paper"] in {"ORION-21", "ORION-22", "ORION-23"}:
        args.append("-shell-escape")
    if spec_["paper"] == "ORION-24":
        args = ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error"]
    args.append("main.tex")
    run(*args, cwd=root)
    return root / "main.pdf"


def apply_targeted_layout_guards(root: Path, paper: str, variant: str) -> None:
    """Keep known narrow-format paragraphs inside the text block."""
    main = root / "main.tex"
    text = main.read_text(encoding="utf-8")

    def sloppy_input(target: str) -> None:
        nonlocal text
        marker = rf"\input{{{target}}}"
        if marker not in text:
            raise RuntimeError(f"cannot locate layout-guard input {target} for {paper}")
        guarded = "\\begingroup\\sloppy\n" + marker + "\n\\endgroup"
        text = text.replace(marker, guarded, 1)

    if paper == "ORION-11" and variant == "journal":
        sloppy_input("sections/06-related-work-boundary")
    if paper == "ORION-21" and variant == "arxiv":
        sloppy_input("sections/99-references.tex")
    if paper == "ORION-22" and variant == "arxiv":
        sloppy_input("sections/01-introduction.tex")
    if paper == "ORION-23":
        sloppy_input("sections/99-references.tex")
    if paper == "ORION-14":
        text = text.replace(r"\begin{document}", r"\hypersetup{hidelinks}" + "\n" + r"\begin{document}", 1)
    if paper == "ORION-14" and variant == "arxiv":
        text = text.replace(
            r"\paragraph{Abstention and scientific integrity.}",
            r"\paragraph{Abstention and integrity.}",
            1,
        ).replace("SciIntegrity-Bench", "SciIntegrity-\\allowbreak Bench", 1)
        text, count = re.subn(
            r"(\\begin\{abstract\})(.*?)(\\end\{abstract\})",
            lambda match: match.group(1) + "\n\\sloppy\n" + match.group(2) + "\n\\fussy\n" + match.group(3),
            text,
            count=1,
            flags=re.S,
        )
        if count != 1:
            raise RuntimeError("cannot locate ORION-14 abstract for layout guard")
    main.write_text(text, encoding="utf-8")


def clean_build_products(root: Path) -> None:
    suffixes = {".aux", ".bbl", ".blg", ".fdb_latexmk", ".fls", ".log", ".out", ".toc", ".xdv"}
    for path in sorted(root.rglob("*"), reverse=True):
        if path.is_dir() and path.name.startswith("_markdown_"):
            shutil.rmtree(path)
        elif path.is_file() and (path.suffix in suffixes or path.name in {"main.pdf", "main.markdown.lua", "main.markdown.out"}):
            path.unlink()


def abstract_from_source(root: Path, paper: str) -> str:
    text = (root / "main.tex").read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, flags=re.S)
    fragment = match.group(1) if match else ""
    if not fragment:
        span = command_span(text, "abstract")
        if span:
            cmd = text[span[0]:span[1]]
            fragment = cmd[cmd.find("{") + 1:-1]
    if not fragment:
        abstract_input = re.search(r"\\input\{([^{}]*abstract[^{}]*)\}", text, flags=re.I)
        if abstract_input:
            fragment = abstract_input.group(0)
    if not fragment:
        for included in re.findall(r"\\input\{([^{}]+)\}", text):
            target = root / included
            if not target.suffix:
                target = target.with_suffix(".tex")
            if not target.exists():
                continue
            included_text = target.read_text(encoding="utf-8", errors="replace")
            included_abstract = re.search(
                r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
                included_text,
                flags=re.S,
            )
            if included_abstract:
                fragment = included_abstract.group(1)
                break
    if not fragment:
        # Pandoc renders a Markdown ``## Abstract`` heading as a sectioning
        # command rather than an abstract environment. Capture its body up to
        # the next same-or-higher-level heading.
        heading = re.search(
            r"\\(?:sub)*section\*?\{Abstract\}.*?\n(.*?)(?=\\hypertarget|\\(?:sub)*section\*?\{|\\end\{document\})",
            text,
            flags=re.S | re.I,
        )
        if heading:
            fragment = heading.group(1)
    for _ in range(4):
        changed = False
        def repl_input(m: re.Match[str]) -> str:
            nonlocal changed
            target = root / m.group(1)
            if not target.suffix:
                target = target.with_suffix(".tex")
            if target.exists():
                changed = True
                return target.read_text(encoding="utf-8", errors="replace")
            return ""
        fragment = re.sub(r"\\input\{([^{}]+)\}", repl_input, fragment)
        def repl_md(m: re.Match[str]) -> str:
            nonlocal changed
            target = root / m.group(1)
            if target.exists():
                changed = True
                return target.read_text(encoding="utf-8", errors="replace")
            return ""
        fragment = re.sub(r"\\markdownInput\{([^{}]+)\}", repl_md, fragment)
        if not changed:
            break
    macros: dict[str, str] = {}
    for path in root.rglob("*.tex"):
        source = path.read_text(encoding="utf-8", errors="replace")
        for name, value in re.findall(r"\\newcommand\{\\([A-Za-z@]+)\}\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", source):
            macros[name] = value
    for name, value in sorted(macros.items(), key=lambda item: -len(item[0])):
        fragment = re.sub(
            rf"\\{re.escape(name)}(?:\{{\}})?",
            lambda _match, replacement=value: replacement,
            fragment,
        )
    fragment = re.sub(r"\\(?:begin|end)\{abstract\}", "", fragment)
    # Markdown-backed sections may contain a literal percent sign. Once their
    # bytes are expanded into this temporary LaTeX fragment, an unescaped `%`
    # would comment out the rest of the line and silently truncate a confidence
    # interval in filing metadata.
    fragment = re.sub(r"(?m)^[ \t]*%.*(?:\n|$)", "", fragment)
    fragment = re.sub(r"(?<!\\)%", r"\\%", fragment)
    plain = run("pandoc", "--from=latex", "--to=plain", cwd=root, input_text=fragment).strip()
    plain = plain.replace("–", "-").replace("—", "--").replace("−", "-")
    plain = plain.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    for symbol, name in {
        "μ": "mu", "λ": "lambda", "σ": "sigma", "θ": "theta",
        "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta",
        "ε": "epsilon", "φ": "phi", "ψ": "psi", "ω": "omega",
        "Μ": "Mu", "Λ": "Lambda", "Σ": "Sigma", "Θ": "Theta",
        "Α": "Alpha", "Β": "Beta", "Γ": "Gamma", "Δ": "Delta",
        "Ε": "Epsilon", "Φ": "Phi", "Ψ": "Psi", "Ω": "Omega",
    }.items():
        plain = plain.replace(symbol, name)
    plain = plain.replace("≥", ">=").replace("≤", "<=")
    plain = unicodedata.normalize("NFKD", plain).encode("ascii", "ignore").decode("ascii")
    plain = plain.replace("**", "")
    plain = re.sub(r"\A(?:Replacement abstract for V5|Abstract)\s+", "", plain)
    plain = re.sub(r"support-\s*<=\s*2", "support <= 2", plain)
    plain = re.sub(r"(?<=\s)-\s+(?=0\.)", "-", plain)
    plain = re.sub(r"([A-Za-z])_\(([^)]+)\)", r"\1_\2", plain)
    if paper == "ORION-04":
        plain = plain.replace("C53", "C_5^3")
        plain = plain.replace("D4(C_5^3)", "D_4(C_5^3)")
        plain = plain.replace("31 C0(C_5^3)", "31 in C_0(C_5^3)")
    if paper == "ORION-10":
        plain = plain.replace("enlarged-borrow explanation B repairs", "enlarged-borrow explanation B' repairs")
        plain = plain.replace("seven f_B fibres", "seven f_B' fibres")
        plain = plain.replace("an exact -only explanation", "an exact Psi-only explanation")
    plain = re.sub(r"\s+", " ", plain).strip()
    if len(plain) > 1900:
        sentences = re.split(r"(?<=[.!?])\s+", plain)
        kept: list[str] = []
        for sentence in sentences:
            if len(" ".join(kept + [sentence])) > 1880:
                break
            kept.append(sentence)
        plain = " ".join(kept)
    if len(plain) < 80:
        raise RuntimeError(f"abstract extraction failed in {root}")
    return plain


def author_declarations(spec_: dict) -> str:
    if spec_["venue"] in {"Artificial Intelligence", "Information Processing & Management"}:
        ai = "During preparation of this work, the author used OpenAI ChatGPT and Codex for drafting and editing assistance. The author reviewed the output and takes full responsibility for the publication's content."
    else:
        ai = "Generative AI tools were used for drafting and editing assistance. The author is responsible for all scientific content."
    return f"""# Statements and declarations

## Authorship and contributions

{AUTHOR} is the sole author and is responsible for conception, methodology,
implementation or formal analysis as applicable, source verification, writing,
and the final submission decision.

## Affiliation and correspondence

- Affiliation: {AFFILIATION}
- Correspondence: {EMAIL}

## Funding and competing interests

No funding was received for this work. The author declares no competing interests.
Acknowledgements are omitted under `papers/SUBMISSION_POLICY_V1.md`.

## Generative-AI disclosure

{ai}

## Ethics

The manuscript reports formal, computational, controlled synthetic, public-corpus,
or repository evidence as stated in its Methods. No human participants, personal
data, or animals are introduced by this publication package.
"""


def cover_letter(spec_: dict) -> str:
    adverse = " ".join(spec_["negatives"])
    return f"""# Cover letter - {spec_['venue']}

Dear Editors,

Please consider *{spec_['title']}* for {spec_['venue']}.

The manuscript's bounded contribution is: {spec_['claim']}

The submission deliberately retains its adverse boundary. {adverse}

The source, executable review materials, atomic claim inventory, and checksums
are supplied with the package. The manuscript does not treat an in-repository
replay as external replication and does not enlarge the active claim authority.
The work is not being submitted in parallel; the author must confirm that fact
again in the live portal immediately before filing.

Sincerely,

{AUTHOR}

{AFFILIATION}

{EMAIL}
"""


def reviewer_audit(spec_: dict) -> str:
    adverse = " ".join(spec_["negatives"])
    return f"""# Three-reviewer adversarial audit - {spec_['paper']}

## Review setup

- Input scope: current manuscript, active authority `{spec_['authority']}`, and the packaged result-retention ledger.
- Assessment boundary: bounded publication claim only; optional successor science is outside this review.
- Shared claim: {spec_['claim']}

## Reviewer 1 - evidence and inference emphasis

**Overall assessment.** The bounded claim is reviewable if every numeric or
theorem statement remains tied to its declared unit and authority class.

**Concern R1-M1 - claim moderation.** Claim pointer: the shared claim above.
Evidence pointer: `{spec_['authority']}` and `RESULT_RETENTION.md`. Resolution
test: the manuscript and metadata retain the following adverse boundary without
pooling or euphemism: {adverse}

## Reviewer 2 - novelty and scope emphasis

**Overall assessment.** The contribution should be judged as the stated residual,
not as ownership of donor mechanisms or a broad real-world generalization.

**Concern R2-M1 - novelty boundary.** Claim pointer: introduction and related
work. Evidence pointer: active claim ledger plus the package novelty record.
Resolution test: no donor-owned primitive, null, refutation, or open successor is
presented as this paper's positive novelty.

## Reviewer 3 - reproducibility and filing emphasis

**Overall assessment.** The source and review archive make the bounded object
inspectable, subject to the live portal confirmations listed separately.

**Concern R3-M1 - release binding.** Claim pointer: availability and declarations.
Evidence pointer: `PACKAGE_MANIFEST.json`, `SHA256SUMS`, and both source archives.
Resolution test: clean rebuilds match the reader PDFs, double-blind files contain
no author tokens, and portal-only IDs are not fabricated.

## Cross-review synthesis

The reviewers agree that the paper is referee-resistant only at its explicit
bounded ceiling. The consensus technical risk is accidental promotion of a
negative, null, CANNOT_CHECK, or same-programme replay into a stronger claim.
No broader experiment is required to submit the bounded object; a broader claim
would require successor science and a new authority disposition.

## Risk / unsupported claims

{chr(10).join('- ' + item for item in spec_['negatives'])}
"""


VENUE_PROFILES = {
    "Quantum": {
        "article_type": "Research article",
        "sources": ["https://quantum-journal.org/instructions/authors/"],
        "requirements": [
            "File the arXiv identifier, not a separate manuscript upload; the preprint must be posted in or cross-listed with quant-ph.",
            "State the main results and assumptions clearly in the first pages.",
            "A cover letter is not required; editor and referee suggestions are portal inputs.",
            "Confirm the journal's current open-access licence and publication-fee choice in the live portal.",
        ],
    },
    "Transactions on Machine Learning Research": {
        "article_type": "Research article",
        "sources": [
            "https://jmlr.org/tmlr/author-guide.html",
            "https://jmlr.org/tmlr/submissions.html",
            "https://jmlr.org/tmlr/editorial-policies.html",
        ],
        "requirements": [
            "Use the mandatory TMLR LaTeX style without layout-altering changes.",
            "Keep the review PDF and every reviewer-visible supplement double blind.",
            "Upload the PDF through OpenReview; supplementary author-created material may be supplied as anonymized PDF or ZIP up to the stated portal limit.",
            "Complete OpenReview profile, conflicts, funding, ethics and Action Editor suggestions privately in the live system.",
        ],
    },
    "Journal of Automated Reasoning": {
        "article_type": "Original research article",
        "sources": ["https://link.springer.com/journal/10817/submission-guidelines"],
        "requirements": [
            "Single-blind route: keep author identity in the manuscript and title page.",
            "Provide a 150--250 word abstract and 4--6 indexing keywords.",
            "Supply editable source, figures, declarations, data/code availability and any required statements.",
        ],
    },
    "Electronic Journal of Combinatorics": {
        "article_type": "Research article",
        "sources": ["https://www.combinatorics.org/ojs/index.php/eljc/about/submissions"],
        "requirements": [
            "Initial submission supplies a readable PDF, abstract and author-written account of the result.",
            "Retain complete editable source for final E-JC typesetting if accepted.",
            "Confirm originality, permissions and current AI-assistance policy in the portal.",
        ],
    },
    "Journal of Artificial Intelligence Research": {
        "article_type": "Research article",
        "sources": [
            "https://www.jair.org/index.php/jair/formatting",
            "https://www.jair.org/index.php/jair/about/submissions",
        ],
        "requirements": [
            "Use the mandatory post-2025 JAIR author-kit class; non-JAIR formatting can be rejected without review.",
            "Submit the complete class-compatible source and reader PDF.",
            "Confirm topical editor, conflicts, originality and any portal-only declarations at filing.",
        ],
    },
    "Information Processing & Management": {
        "article_type": "Full-length research article",
        "sources": [
            "https://www.elsevier.com/journals/information-processing-and-management/0306-4573/guide-for-authors",
            "https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals",
        ],
        "requirements": [
            "Keep the concise factual abstract at or below 250 words and provide keywords and highlights.",
            "Supply editable source, separate title-page/declaration materials, data/code availability and competing-interest statement.",
            "Place the named generative-AI declaration immediately above the references in the manuscript.",
        ],
    },
    "Semantic Web Journal": {
        "article_type": "Original Research Article",
        "sources": ["https://journals.sagepub.com/author-instructions/swj"],
        "requirements": [
            "Use the current SAGE route and preferred LaTeX source.",
            "Provide the required structured 200-word abstract and at least 4--5 specific keywords.",
            "Confirm preprint DOI, permissions, data/software availability and transparent-review implications in the live portal.",
        ],
    },
    "Artificial Intelligence": {
        "article_type": "Research article",
        "sources": [
            "https://www.journals.elsevier.com/artificial-intelligence",
            "https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals",
        ],
        "requirements": [
            "Supply editable source, title page, keywords, highlights, declarations and data/code availability.",
            "Place the named generative-AI declaration immediately above the references in the manuscript.",
            "Confirm current article-type and portal-specific limits immediately before filing.",
        ],
    },
    "Autonomous Agents and Multi-Agent Systems": {
        "article_type": "Original research article",
        "sources": ["https://link.springer.com/journal/10458/submission-guidelines"],
        "requirements": [
            "Supply the required 1--2 page information sheet addressing the main claim, precise evidence, closest related contributions and prior-publication status.",
            "Provide editable source, a 150--250 word abstract, 4--6 keywords, title information and declarations.",
            "Use the single-blind identified route and confirm all portal classifications and conflicts.",
        ],
    },
}


def venue_keywords(spec_: dict) -> list[str]:
    if spec_["paper"] == "ORION-04":
        return ["generalized Davenport constants", "zero-sum sequences", "finite abelian groups", "exact computation", "computer-assisted proof"]
    if spec_["venue"] == "Quantum":
        return ["quantum compilation", "exact optimization", "support certificates", "formal verification", "negative results"]
    if spec_["venue"] == "Transactions on Machine Learning Research":
        return ["machine learning systems", "controlled evaluation", "epistemic state", "reproducibility", "fail-closed inference"]
    if spec_["venue"] == "Semantic Web Journal":
        return ["semantic interoperability", "knowledge representation", "evidence provenance", "coordinate systems", "knowledge graphs"]
    if spec_["venue"] == "Information Processing & Management":
        return ["scientific literature discovery", "information retrieval", "stopping rules", "open-world search", "fail-closed control"]
    if spec_["venue"] == "Journal of Automated Reasoning":
        return ["automated reasoning", "formal verification", "typed evidence", "proof systems", "fail-closed inference"]
    if spec_["venue"] == "Journal of Artificial Intelligence Research":
        return ["scientific reasoning", "epistemic transitions", "responsibility licensing", "exact evaluation", "reproducibility"]
    if spec_["venue"] == "Autonomous Agents and Multi-Agent Systems":
        return ["autonomous agents", "scientific reasoning", "epistemic authority", "responsibility", "fail-closed systems"]
    return ["artificial intelligence", "scientific reasoning", "formal semantics", "controlled evaluation", "reproducibility"]


def elsevier_highlights(spec_: dict) -> list[str]:
    return {
        "ORION-12": [
            "Fail-closed control separates route stopping from task closure.",
            "TREC-COVID recall fell while candidate reads increased by 175.7%.",
            "Two ArguAna diagnostics expose a signal-inert stopping statistic.",
        ],
        "ORION-16": [
            "Certificate lifting is proved over explicit local and propagation laws.",
            "The bounded star-graph model is recovered as a verified instance.",
            "Donor certificates do not establish scientific standing by themselves.",
        ],
        "ORION-17": [
            "Closure transport requires an explicit intermediate obligation contract.",
            "The composition rule is sound and associative but provably incomplete.",
            "The bounded five-family model is recovered as a theorem instance.",
        ],
    }[spec_["paper"]]


def venue_materials(spec_: dict, journal_dir: Path) -> None:
    profile = dict(VENUE_PROFILES[spec_["venue"]])
    if spec_["paper"] == "ORION-24":
        profile["article_type"] = "Viewpoint / position paper"
    sources = "\n".join(f"- {url} (accessed {DATE})" for url in profile["sources"])
    requirements = "\n".join(f"- [x] {item}" for item in profile["requirements"])
    write(journal_dir / "VENUE_REQUIREMENTS.md", f"""# Venue requirements - {spec_['venue']}

**Article type:** {profile['article_type']}
**Review audience:** {spec_['review']}
**Requirements checked:** {DATE}

## Official sources

{sources}

## Repository-controlled preparation

{requirements}

## Live-portal recheck

- [ ] Reopen the official sources immediately before filing; venue rules can change.
- [ ] Confirm any portal-only word limits, classifications, conflicts, editor/reviewer choices, licences, fees and account assertions.
- [ ] Record the real submission identifier only after the portal issues it.
""")
    if spec_["venue"] == "Transactions on Machine Learning Research":
        write(journal_dir / "TMLR_OPENREVIEW_CHECKLIST.md", """# TMLR / OpenReview checklist

- [x] Manuscript PDF uses the mandatory TMLR style.
- [x] Manuscript source and reviewer-visible review archive are anonymous.
- [x] Supplement is a ZIP and contains only directly supporting author-created material.
- [x] Named title page, declarations and cover text are editor/private filing materials, not reviewer attachments.
- [ ] Author updates the OpenReview profile and institutional history.
- [ ] Author declares conflicts, funding, prior versions and broader-impact/ethics information in the private fields.
- [ ] Author recommends Action Editors only after checking current conflicts.
- [ ] Author confirms CC BY 4.0 and no prohibited dual submission.
""")
    if spec_["venue"] == "Quantum":
        write(journal_dir / "QUANTUM_ARXIV_FILING.md", f"""# Quantum filing through arXiv

- [x] Proposed arXiv primary category: `{spec_['category']}` (must be posted in or cross-listed with `quant-ph`).
- [x] Named arXiv PDF and complete TeX source are prepared.
- [x] Main results, assumptions and adverse boundaries are stated in the first pages.
- [x] No journal cover letter is required; `COVER_LETTER.md` is retained as optional editor text only.
- [ ] File on arXiv, preview the arXiv compile and wait for the assigned identifier.
- [ ] Submit that real arXiv identifier to Quantum and choose handling-editor/referee suggestions.
""")
    if spec_["venue"] == "Journal of Artificial Intelligence Research":
        write(journal_dir / "JAIR_FORMAT_CHECKLIST.md", """# JAIR format checklist

- [x] Journal source uses the official JAIR class downloaded 2026-08-31.
- [x] Official class assets are vendored with provenance and exact hashes.
- [x] The source archive clean-compiles with the local compatibility shim documented beside the official kit.
- [x] Author identity is present without inventing a city, country or postal address.
- [ ] Supply location/postal data only if the live portal requires it.
- [ ] Confirm topical editor, conflicts and article metadata in the portal.
""")
    if spec_["venue"] == "Electronic Journal of Combinatorics":
        write(journal_dir / "EJC_FILING_CHECKLIST.md", """# Electronic Journal of Combinatorics filing checklist

- [x] Reader PDF, abstract, editable source and exact-computation evidence pointers are supplied.
- [x] The author account of the result distinguishes theorem, replay, novelty and editorial authority.
- [x] No first/unique/priority claim is made from an incomplete literature search.
- [ ] Confirm current E-JC author declarations and AI-assistance policy in the portal.
- [ ] If accepted, apply the then-current E-JC final style without changing theorem authority.
""")
    if spec_["venue"] == "Autonomous Agents and Multi-Agent Systems":
        info = f"""# JAAMAS submission information sheet - {spec_['paper']}

## 1. Main contribution and evidence

The paper's bounded main claim is:

> {spec_['claim']}

The exact evidence authority is `{spec_['authority']}`. The manuscript's Methods,
Results and reproducibility sections bind the claim to that authority and to the
packaged review archive. The submission does not use optional broader real-world
experiments as a prerequisite for this bounded claim.

## 2. Relation to existing contributions

The paper treats authorization, provenance, verification, agent review,
responsibility and other donor mechanisms cited in its Related Work section as
prior contributions. Its residual is the composition, contract or evaluation
boundary stated above, not ownership of those primitives. An
information-equivalent donor tie, where present, is an expressivity boundary and
is retained rather than hidden. The closest-work comparison should be read from
the manuscript's Related Work section together with `REVIEWER_AUDIT.md`; no
"first to do X" assertion is used as a substitute for a technical distinction.

## 3. Adverse boundary

{chr(10).join('- ' + item for item in spec_['negatives'])}

These outcomes limit the interpretation and remain part of the contribution.

## 4. Prior publication and overlap

The repository record does not identify a prior journal publication of this
manuscript. The author must disclose any real arXiv posting, conference version,
related submission or reused material in the live portal and update this sheet
with the actual identifier. No identifier or exclusivity assertion is invented
here. The author must also reconfirm that the work is not under simultaneous
journal review at the moment of filing.
"""
        write(journal_dir / "JAAMAS_INFORMATION_SHEET.md", info)
    if spec_["venue"] in {"Artificial Intelligence", "Information Processing & Management"}:
        highlights = elsevier_highlights(spec_)
        if any(len(item) > 85 for item in highlights):
            raise RuntimeError(f"Elsevier highlight exceeds 85 characters for {spec_['paper']}")
        write(journal_dir / "HIGHLIGHTS.txt", "\n".join(f"- {item}" for item in highlights) + "\n")
        write(journal_dir / "ELSEVIER_AI_DECLARATION.txt", """Declaration of generative AI and AI-assisted technologies in the writing process

During preparation of this work, the author used OpenAI ChatGPT and Codex for drafting, editing, source checking, adversarial review, and submission-package preparation. The author reviewed the output and takes full responsibility for the publication's content.
""")


def build_variant(spec_: dict, variant: str, out: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"{spec_['paper'].lower()}-{variant}-") as td:
        source = Path(td) / "source"
        source.mkdir()
        source = special_source(spec_, variant, source)
        pdf = compile_source(spec_, variant, source)
        shutil.copy2(pdf, out / "manuscript.pdf")
        abstract = abstract_from_source(source, spec_["paper"])
        pages = int(re.search(r"Pages:\s+(\d+)", run("pdfinfo", str(out / "manuscript.pdf"))).group(1))
        text = run("pdftotext", "-f", "1", "-l", "2", str(out / "manuscript.pdf"), "-")
        anonymous = variant == "journal" and spec_["review"] == "double_blind"
        if anonymous and any(token.lower() in text.lower() for token in (AUTHOR, EMAIL, AFFILIATION)):
            raise RuntimeError(f"identity leak in {spec_['paper']} journal PDF")
        if not anonymous and not all(token.lower() in text.lower() for token in (AUTHOR, AFFILIATION, EMAIL)):
            raise RuntimeError(f"named identity incomplete in {spec_['paper']} {variant} PDF")
        clean_build_products(source)
        deterministic_zip(source, out / "source.zip")
    return {"pages": pages, "abstract": abstract}


def build_one(spec_: dict) -> dict:
    paper_root = PAPERS / spec_["slug"]
    out = paper_root / "submission/publication-ready-20260831"
    if out.exists():
        shutil.rmtree(out)
    (out / "arxiv").mkdir(parents=True)
    (out / "journal").mkdir()
    arxiv = build_variant(spec_, "arxiv", out / "arxiv")
    journal = build_variant(spec_, "journal", out / "journal")
    if spec_["paper"] == "ORION-03":
        artifact = (
            paper_root
            / "journal_package_final/submission/Typed_Evidence_Licenses_for_Fail_Closed_Nonpromotion_artifact.zip"
        )
        if not artifact.is_file():
            raise RuntimeError("ORION-03 bounded artifact archive is missing")
        shutil.copy2(artifact, out / "journal/artifact.zip")

    arxiv_meta = {
        "schema": "ORION.arxiv-metadata.v1",
        "paper": spec_["paper"],
        "title": spec_["title"],
        "authors": f"{AUTHOR} ({AFFILIATION})",
        "correspondence": EMAIL,
        "abstract": arxiv["abstract"],
        "abstract_characters": len(arxiv["abstract"]),
        "primary_category": spec_["category"],
        "cross_lists": spec_["crosslists"] or [],
        "comments": f"{arxiv['pages']} pages; all null, adverse, refuted and CANNOT_CHECK results retained.",
        "license_recommendation": "CC BY 4.0, subject to final author selection in the arXiv portal and journal compatibility check",
        "report_number": None,
        "journal_reference": None,
        "doi": None,
        "portal_status": "NOT_FILED",
    }
    write(out / "arxiv/metadata.json", json.dumps(arxiv_meta, indent=2, sort_keys=True) + "\n")
    write(out / "arxiv/SUBMISSION_CHECKLIST.md", f"""# arXiv submission checklist

- [x] Named author PDF and source use `{AUTHOR}`, `{AFFILIATION}`, `{EMAIL}`.
- [x] TeX source archive is supplied; PDF-only filing is not intended.
- [x] Abstract is ASCII-oriented and below arXiv's 1,920-character limit.
- [x] Primary category proposed: `{spec_['category']}`.
- [ ] Author confirms endorsement/category eligibility in the live arXiv account.
- [ ] Author selects the final licence in the portal.
- [ ] Author previews arXiv's compiled PDF and confirms title/author/abstract.
- [ ] Record the assigned arXiv identifier after announcement.
""")

    write(out / "journal/COVER_LETTER.md", cover_letter(spec_))
    write(out / "journal/DECLARATIONS.md", author_declarations(spec_))
    write(out / "journal/TITLE_PAGE.md", f"""# Title page

**Title:** {spec_['title']}

**Article type:** {VENUE_PROFILES[spec_['venue']]['article_type']}

**Author:** {AUTHOR}

**Affiliation:** {AFFILIATION}

**Corresponding author:** {AUTHOR}, {EMAIL}

**ORCID:** not supplied in the repository; omit unless the author provides one.
""")
    journal_meta = {
        "schema": "ORION.journal-metadata.v1",
        "paper": spec_["paper"],
        "venue": spec_["venue"],
        "article_type": VENUE_PROFILES[spec_["venue"]]["article_type"],
        "review_model": spec_["review"],
        "title": spec_["title"],
        "author": {"name": AUTHOR, "affiliation": AFFILIATION, "email": EMAIL, "corresponding": True, "sole_author": True},
        "abstract": journal["abstract"],
        "keywords": venue_keywords(spec_),
        "keywords_source": "current bounded claim and manuscript",
        "portal_status": "NOT_FILED",
        "package_status": spec_["status"],
    }
    write(out / "journal/metadata.json", json.dumps(journal_meta, indent=2, sort_keys=True) + "\n")
    write(out / "journal/SUBMISSION_CHECKLIST.md", f"""# Journal submission checklist - {spec_['venue']}

- [x] Reader PDF and complete source archive are supplied.
- [x] Review identity mode is `{spec_['review']}`.
- [x] Cover letter, title page, declarations, availability statement and review archive are supplied.
- [x] Any paper-specific artifact archive named in the manuscript is supplied when applicable.
- [x] Null, adverse, refuted and CANNOT_CHECK results are retained.
- [ ] Author confirms originality and no simultaneous journal review in the live portal.
- [ ] Author supplies ORCID only if desired or mandatory; no identifier is invented.
- [ ] Author confirms suggested/opposed reviewers and portal classifications.
- [ ] Author records the submission identifier after filing.
""")
    venue_materials(spec_, out / "journal")

    write(out / "RESULT_RETENTION.md", "# Result-retention ledger\n\n" + "\n".join(f"- {x}" for x in spec_["negatives"]) + "\n")
    availability = "# Data and code availability\n\nThe source archives and review-material archive in this directory bind the reader-facing manuscript to the repository evidence used for its bounded claims. A public persistent archive identifier must be inserted only after a real deposit; no DOI or submission identifier is synthesized by this package.\n"
    if spec_["paper"] == "ORION-03":
        availability += "\nThe journal directory also contains `artifact.zip`, the checksum-bound executable evaluator and bounded evidence archive named by the manuscript. Native-tool routes that the artifact marks `CANNOT_CHECK` remain unavailable; the archive does not convert them into reproduced outcomes.\n"
    if spec_["paper"] == "ORION-17":
        availability += "\nThe retained substitute-campaign corpus is arithmetically intact and its original pre-R0 seal verifies against the bytes that were signed. The current post-R0 path checker nevertheless fails three bindings because sealed identifiers were rewritten during namespace unification. `ORION17_SEAL_INTEGRITY_DIAGNOSIS_V1.md` records that unresolved current-path integrity boundary; this package does not re-seal the campaign or claim added external authority.\n"
    write(out / "DATA_AND_CODE_AVAILABILITY.md", availability)
    write(out / "HUMAN_INPUTS_REQUIRED.md", """# Human-controlled filing inputs

- [x] Canonical name: Sze Chun Yiu.
- [x] Canonical affiliation: Stockholm University.
- [x] Correspondence email: sze-chun.yiu@fysik.su.se.
- [x] Standing policy: no funding; no competing interests; acknowledgements omitted unless mandatory.
- [ ] ORCID, if the author has and chooses to supply one.
- [ ] Postal address or phone only where a portal makes it mandatory.
- [ ] Live account profile, category/subject classifications, editor/reviewer choices and conflicts.
- [ ] Final arXiv licence selection, repository deposit/PID and actual arXiv/journal identifiers.
""")
    write(out / "NOVELTY_AND_DONOR_BOUNDARY.md", f"""# Novelty and donor boundary

## Admitted residual

{spec_['claim']}

## Donor and priority limits

- Scientific authority is bound to `{spec_['authority']}` and terminal `{spec_['terminal']}`.
- Generic methods, venue conventions, comparator mechanisms, and cited donor results remain donor-owned.
- The paper claims the bounded formal, controlled, or measurement residual above; it does not claim priority for a generic donor primitive.
- No exhaustive first-in-literature, editorial-acceptance, venue-ranking, or independent-replication claim is made by this package.
- An information-equivalent tie, same-source replay, null, refutation, or CANNOT_CHECK outcome is retained at its actual authority level and is never repackaged as positive novelty.

## Adversarial exclusions

{chr(10).join('- ' + item for item in spec_['negatives'])}
""")
    write(out / "REVIEWER_AUDIT.md", reviewer_audit(spec_))
    atomic = {
        "schema": "ORION.atomic-claim-inventory.v1",
        "paper": spec_["paper"],
        "active_authority": spec_["authority"],
        "terminal": spec_["terminal"],
        "admitted_claim": spec_["claim"],
        "retained_negative_null_open_cannot_check": spec_["negatives"],
        "scientific_authority_delta": "NONE",
    }
    write(out / "ATOMIC_CLAIM_INVENTORY.json", json.dumps(atomic, indent=2, sort_keys=True) + "\n")
    integrity = {
        "schema": "ORION.research-integrity-ledger.v1",
        "paper": spec_["paper"],
        "null_negative_retention": True,
        "cannot_check_is_not_success_or_failure": True,
        "same_programme_replay_is_not_external_replication": True,
        "missing_artifact_classes_are_not_attempted_cases": True,
        "package_grants_scientific_authority": False,
        "author_identity_source": "papers/AUTHOR_IDENTITY_V1.json",
        "submission_policy_source": "papers/SUBMISSION_POLICY_V1.md",
    }
    write(out / "RESEARCH_INTEGRITY_LEDGER.json", json.dumps(integrity, indent=2, sort_keys=True) + "\n")

    review_stage = out / "review-materials"
    review_stage.mkdir()
    authority = paper_root / spec_["authority"]
    if not authority.exists():
        raise RuntimeError(f"missing authority {authority}")
    shutil.copy2(authority, review_stage / authority.name)
    for name in (
        "PUBLICATION_FREEZE_ADDENDUM_V1.md",
        "REPLICATION_PARAMETERISED_GATE_DISPOSITION_V1.md",
        "CLAIM_EVIDENCE_LEDGER.md",
        "PEER_REVIEW_READINESS.md",
        "REVIEWER_SUMMARY.md",
    ):
        if (paper_root / name).exists() and (paper_root / name) != authority:
            shutil.copy2(paper_root / name, review_stage / name)
    if spec_["paper"] == "ORION-17":
        diagnosis = PAPERS / "publication_closure/ORION17_SEAL_INTEGRITY_DIAGNOSIS_V1.md"
        if not diagnosis.is_file():
            raise RuntimeError("missing ORION-17 seal-integrity diagnosis")
        shutil.copy2(diagnosis, review_stage / diagnosis.name)
    shutil.copy2(out / "RESULT_RETENTION.md", review_stage / "RESULT_RETENTION.md")
    shutil.copy2(out / "NOVELTY_AND_DONOR_BOUNDARY.md", review_stage / "NOVELTY_AND_DONOR_BOUNDARY.md")
    if spec_["review"] == "double_blind":
        anonymize_tree(review_stage)
    deterministic_zip(review_stage, out / "journal/review-materials.zip")
    shutil.rmtree(review_stage)

    write(out / "README.md", f"""# {spec_['paper']} dual submission package

This directory is the publication adapter for the current bounded manuscript.
`arxiv/` is attributed and source-complete. `journal/` follows the route-specific
identity mode `{spec_['review']}` for {spec_['venue']}. Scientific authority remains
with `{spec_['authority']}`; this package changes no result terminal.
""")
    write(out / "SKILLS_APPLIED.md", f"""# Academic-paper skill application

`skills-applied: academic-paper-pipeline@{ACADEMIC_PAPER_PIPELINE_VERSION}, academic-writing@{ACADEMIC_WRITING_VERSION}, nature-polishing@{NATURE_POLISHING_VERSION}, nature-reviewer@{NATURE_REVIEWER_VERSION}, publication-release-integrity, manuscript-element-justification`

Skill authority: `SzeChunYiu/academic-paper-skills@{ACADEMIC_PAPER_SKILLS_REVISION}`.
The final pass used the latest verified skill revision for targeted hostile
review, route parity, release binding, identity partitioning, and manuscript-
element justification. It did not reopen optional science or widen the active
claim.
""")

    payload = {}
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name not in {"PACKAGE_MANIFEST.json", "SHA256SUMS"}):
        rel = path.relative_to(out).as_posix()
        payload[rel] = {"sha256": sha(path), "bytes": path.stat().st_size}
    manifest = {
        "schema": "ORION.dual-submission-package.v1",
        "date": DATE,
        "paper": spec_["paper"],
        "title": spec_["title"],
        "active_authority": str(authority.relative_to(ROOT)),
        "active_authority_sha256": sha(authority),
        "terminal": spec_["terminal"],
        "status": spec_["status"],
        "arxiv": {"category": spec_["category"], "cross_lists": spec_["crosslists"] or [], "pages": arxiv["pages"]},
        "journal": {
            "venue": spec_["venue"],
            "article_type": VENUE_PROFILES[spec_["venue"]]["article_type"],
            "review_model": spec_["review"],
            "pages": journal["pages"],
        },
        "identity": {"source": "papers/AUTHOR_IDENTITY_V1.json", "name": AUTHOR, "affiliation": AFFILIATION, "email": EMAIL},
        "academic_paper_skills": {
            "repository": "https://github.com/SzeChunYiu/academic-paper-skills",
            "revision": ACADEMIC_PAPER_SKILLS_REVISION,
            "academic_paper_pipeline_version": ACADEMIC_PAPER_PIPELINE_VERSION,
            "academic_writing_version": ACADEMIC_WRITING_VERSION,
            "nature_polishing_version": NATURE_POLISHING_VERSION,
            "nature_reviewer_version": NATURE_REVIEWER_VERSION,
        },
        "scientific_authority_delta": "NONE",
        "payload": payload,
    }
    write(out / "PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    write(out / "SHA256SUMS", "".join(f"{sha(p)}  {p.relative_to(out).as_posix()}\n" for p in files))
    return {"paper": spec_["paper"], "path": str(out.relative_to(ROOT)), "status": spec_["status"], "manifest_sha256": sha(out / "PACKAGE_MANIFEST.json")}


def write_global_filing_materials() -> None:
    route_rows = []
    for item in SPECS:
        profile = VENUE_PROFILES[item["venue"]]
        route_rows.append({
            "paper": item["paper"],
            "title": item["title"],
            "package": f"papers/{item['slug']}/submission/publication-ready-20260831",
            "arxiv_primary_category": item["category"],
            "arxiv_cross_lists": item["crosslists"] or [],
            "journal": item["venue"],
            "article_type": profile["article_type"],
            "review_model": item["review"],
            "official_requirements": profile["sources"],
            "requirements_accessed": "2026-08-31",
            "package_status": item["status"],
            "portal_status": "NOT_FILED",
        })
    route_json = HERE / "SUBMISSION_ROUTE_MATRIX.json"
    write(route_json, json.dumps({
        "schema": "ORION.submission-route-matrix.v1",
        "date": DATE,
        "canonical_identity": {"name": AUTHOR, "affiliation": AFFILIATION, "email": EMAIL, "orcid": None},
        "papers": route_rows,
    }, indent=2, sort_keys=True) + "\n")
    lines = [
        "# ORION-01--25 submission route matrix",
        "",
        f"Canonical identified-route metadata: **{AUTHOR}**, {AFFILIATION}, `{EMAIL}`. No ORCID is supplied or invented.",
        "",
        "| Paper | arXiv | Journal | Article type | Review | Repository state |",
        "|---|---|---|---|---|---|",
    ]
    for row in route_rows:
        lines.append(
            f"| {row['paper']} | {row['arxiv_primary_category']} | {row['journal']} | "
            f"{row['article_type']} | {row['review_model']} | {row['package_status']} |"
        )
    lines.extend([
        "",
        "Every row has attributed arXiv PDF/source/metadata, route-specific journal PDF/source/metadata, cover/title/declaration materials, reviewer archive, claim and negative-result inventories, a manifest, and checksums. Double-blind identity applies only to reviewer-visible journal bytes; editor-private metadata remains canonical.",
    ])
    write(HERE / "SUBMISSION_ROUTE_MATRIX.md", "\n".join(lines) + "\n")
    write(HERE / "GLOBAL_HUMAN_FILING_CHECKLIST.md", f"""# Global human filing checklist

Repository-controlled submission packages cover the current 25 paper identities. The remaining actions are human- or portal-controlled and are not synthesized.

## Canonical personal information

- Name: {AUTHOR}
- Affiliation: {AFFILIATION}
- Correspondence: {EMAIL}
- ORCID: not supplied; enter one only if the author has and chooses to use it
- Funding: none
- Competing interests: none
- Stockholm University: author-confirmed affiliation for every attributed route

## arXiv portal

- Confirm account/endorsement and each proposed primary category or cross-list.
- Select the final licence after checking journal compatibility.
- Upload the provided source archive, inspect arXiv's compilation, and confirm title, author, abstract, and comments.
- Record the assigned arXiv identifier only after announcement.

## Journal portals

- Confirm originality, no simultaneous journal review, article type, conflicts, editor/reviewer choices, and any mandatory account-profile fields.
- For TMLR, keep the supplied review PDF/source/supplement anonymous and complete the private OpenReview profile/conflict forms.
- For Quantum, post or cross-list the preprint in quant-ph before filing its arXiv identifier.
- For every venue, preview uploaded files and record the real submission identifier only after the portal creates it.

`PACKAGE_COMPLETE__PORTAL_INPUTS_PENDING` means repository preparation is complete, not that an arXiv or journal submission has already been made.
""")


def merge_incremental_records(registry_path: Path, new_records: list[dict]) -> list[dict]:
    """Replace selected records without weakening exact 25-paper coverage."""
    if not registry_path.is_file():
        raise RuntimeError("incremental build requires the existing 25-paper closure registry")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    existing = {record["paper"]: record for record in registry["papers"]}
    expected = {item["paper"] for item in SPECS}
    if set(existing) != expected:
        raise RuntimeError("incremental build refuses a non-25-paper closure registry")
    replacements = {record["paper"]: record for record in new_records}
    if not replacements or not set(replacements) <= expected:
        raise RuntimeError("incremental build contains no valid registered replacement")
    existing.update(replacements)
    return [existing[item["paper"]] for item in SPECS]


def main() -> int:
    records = []
    selected = set(os.environ.get("ORION_PAPERS", "").split(",")) - {""}
    for item in SPECS:
        if selected and item["paper"] not in selected:
            continue
        print(f"BUILD {item['paper']}", flush=True)
        records.append(build_one(item))
    out = PAPERS / "publication_closure/orion_all_submission_20260831/CLOSURE_REGISTRY.json"
    if selected:
        records = merge_incremental_records(out, records)
    write(out, json.dumps({"schema": "ORION.all-dual-submission-registry.v1", "date": DATE, "papers": records, "mirror_phase": "PENDING_POST_MERGE"}, indent=2, sort_keys=True) + "\n")
    if not selected:
        write_global_filing_materials()
    print(f"BUILT {len(records)} publication objects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
