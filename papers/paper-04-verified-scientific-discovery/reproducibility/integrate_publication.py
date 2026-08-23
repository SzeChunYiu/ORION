#!/usr/bin/env python3
"""Integrate the accepted protected campaign into P4 publication artifacts.

This script is deliberately one-way: it reads only the committed safe aggregate
package, never protected per-case gold.  It replaces stale prospective prose,
adds the protected result/claim ledger, and marks only evidence-backed readiness
items complete.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "protected-campaign-31968809206"
SUMMARY = json.loads((EVIDENCE / "CAMPAIGN_SUMMARY_V1.json").read_text(encoding="utf-8"))
ABLATIONS = json.loads((EVIDENCE / "ABLATION_SUMMARY_V1.json").read_text(encoding="utf-8"))
TELEMETRY = json.loads((EVIDENCE / "ACCESS_TELEMETRY_SUMMARY_V1.json").read_text(encoding="utf-8"))
REPRO = json.loads((EVIDENCE / "INDEPENDENT_REPRODUCTION_V1.json").read_text(encoding="utf-8"))
INDEX = json.loads((EVIDENCE / "ARTIFACT_INDEX_V1.json").read_text(encoding="utf-8"))

assert SUMMARY["typed_panel_status"] == "PASS"
assert SUMMARY["panel_pass"] is True
assert SUMMARY["H1"]["status"] == "PASS"
assert SUMMARY["H2"]["status"] == "PASS"
assert SUMMARY["H3"]["status"] == "NOT_SUPPORTED"
assert REPRO["headline_reproduced"] is True
assert TELEMETRY["candidate_protected_identifier_hits"] == 0
assert TELEMETRY["comparator_protected_identifier_hits"] == 0


def replace_section(text: str, title: str, body: str) -> str:
    pattern = re.compile(
        rf"\\section\{{{re.escape(title)}\}}.*?(?=\\section\{{|\\end\{{document\}})",
        flags=re.S,
    )
    replacement = f"\\section{{{title}}}\n{body.strip()}\n\n"
    updated, count = pattern.subn(lambda _: replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"expected exactly one section {title!r}, found {count}")
    return updated


def replace_abstract(text: str, body: str) -> str:
    pattern = re.compile(r"\\begin\{abstract\}.*?\\end\{abstract\}", flags=re.S)
    updated, count = pattern.subn(
        lambda _: "\\begin{abstract}\n" + body.strip() + "\n\\end{abstract}",
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError(f"expected one abstract, found {count}")
    return updated


def fmt(value: float) -> str:
    return f"{value:.3f}"


def main() -> int:
    manuscript = ROOT / "manuscript" / "main.tex"
    text = manuscript.read_text(encoding="utf-8")
    if "\\usepackage{graphicx}" not in text:
        text = text.replace(
            "\\usepackage{amsmath,amssymb}",
            "\\usepackage{amsmath,amssymb}\n\\usepackage{graphicx}\n\\usepackage{booktabs}",
            1,
        )

    h1, h2, h3 = SUMMARY["H1"], SUMMARY["H2"], SUMMARY["H3"]
    comparator = SUMMARY["strongest_frozen_comparator"]
    orion = SUMMARY["systems"]["ORION"]
    comp = SUMMARY["systems"][comparator]

    abstract = rf"""
Citation correctness and factual support do not by themselves establish scientific authority. We evaluate a non-escalating authority pipeline in which evidence references bind exact content and provenance, source attribution is separated from pooled semantic support, candidate checking mechanisms require admissible lineage and hostile discrimination, evaluator/holdout identity is protected, and unresolved prerequisites produce \texttt{{CANNOT\_CHECK/BLOCK}} rather than compensable confidence. The publication-authorizing campaign was prospectively frozen, generated 420 secret-seeded mechanical-gold cases across 13 clean/hostile families under independent host custody, and compared full ORION with nine matched verification baselines plus eight resource-matched ablations over five repeats. Full ORION produced 0/360 false scientific-authority promotions versus 180/360 for the strongest frozen comparator while promoting 60/60 clean positives in both systems: the false-promotion difference was {fmt(h1['orion_minus_baseline_false_promotion'])} with 95\% CI [{fmt(h1['ci95_low'])}, {fmt(h1['ci95_high'])}], and the clean-coverage difference was {fmt(h2['orion_minus_baseline_clean_coverage'])} with 95\% CI [{fmt(h2['ci95_low'])}, {fmt(h2['ci95_high'])}]. Independent reproduction recovered the same headline counts/effects, and scored-process telemetry recorded zero protected-identifier accesses and zero external IP connections. The secondary H3 comparison of correct \texttt{{CANNOT\_CHECK}} selection tied the strongest comparator and is reported as not supported. The result therefore supports the bounded claim that non-compensatory authority gating reduces false authority promotion under the frozen attack/custody model without a clean-coverage loss; it does not establish universal evaluator security or superiority outside this campaign.
"""
    text = replace_abstract(text, abstract)

    introduction = r"""
Scientific authority---the decision that a claim has earned support rather than merely looking plausible---is increasingly mediated by language-model research systems that retrieve, synthesize and verify evidence. Source-aware factuality, attribution evaluation, claim-level auditability, contamination detection and evaluator protection are already active research areas \cite{provenanceguard2026,attributionbench2024,aar2026,provenai2026,rewardhacking2026,stc2026}. Paper IV therefore does not claim any of those components as standalone novelty. It asks a narrower systems question: whether composing exact content/provenance identity, checker-admissibility lineage, protected evaluator/holdout custody and a non-compensatory fail-closed terminal materially reduces false scientific-authority promotion without winning by refusing clean supported claims.

The experiment was outcome-blind through execution freeze. Protocol \texttt{P4.protected-authority.v1} bound subject commit \texttt{46977ea104162c4cf64da8138a4c4759065fe6d4}, the protected-set/split/evaluator/config hashes, resource policy, five repeats and statistical plan before launch. Independent GitHub-hosted preparation generated a fresh 420-case hidden campaign; candidate/comparator jobs received only opaque case IDs plus candidate-visible material. Protected gold was downloaded only after all scored jobs completed. The accepted result is Actions campaign \texttt{31968809206}; its safe aggregate evidence is committed under \texttt{evidence/protected-campaign-31968809206/}, while protected raw verdicts and syscall traces remain in custody.
"""
    text = replace_section(text, "Introduction", introduction)

    problem = r"""
A proposal can be factually correct while citing the wrong source, semantically supported in a pooled corpus while unsupported by its assigned evidence, checked by a mechanism that shares its authoring lineage, or evaluated after benchmark/evaluator information has leaked. Paper IV therefore distinguishes claim correctness, exact evidence identity, source ownership, semantic support, behavioral influence, checker independence/discrimination, evaluator chronology/integrity, search contamination and protected-access state. Promotion is licensed only when every registered prerequisite passes; a failed prerequisite yields \texttt{BLOCK}, and an unresolved prerequisite yields \texttt{CANNOT\_CHECK}. No coordinate can be averaged upward by confidence on another coordinate.

The tested claim is bounded: under the registered 13-family threat model and custody protocol, does that non-compensatory transition reduce false promotions relative to strong source-aware verification baselines while retaining clean authority coverage? This is an empirical systems/security claim, not a claim that provenance, fact checking, attribution or tamper detection was invented here.
"""
    text = replace_section(text, "Problem and claim boundary", problem)

    protocol_design = rf"""
The final execution freeze used protocol \texttt{{P4.protected-authority.v1}} with \texttt{{outcome\_accessed=false}} at launch. The production subject was commit \texttt{{46977ea104162c4cf64da8138a4c4759065fe6d4}} (archive SHA-256 \texttt{{4605bfd7...09d98c5}}). The independently generated hidden battery contained 420 cases: 60 clean positives and 30 cases for each of 12 hostile families. Custody assigned 30 clean cases and 120 hostile cases to post-run public release, 120 hostile cases to protected custody and 150 cases to protected holdout. All 420 cases were mechanically generated with exact gold; zero cases met the predeclared ambiguity trigger for human adjudication, so no human judgment is claimed where none was required.

The nine comparators covered citation presence/format, pooled evidence support, AttributionBench-style multi-source attribution, ProvenanceGuard-style source routing, FIRE/DeepSciVerify-style retrieve-or-verify, CLAIM-BENCH-style scientific evidence classification, ProvenAI-style citation/influence, RewardHacking/STC-style evaluator/contamination checks and claim-level auditability/provenance. Eight resource-matched ablations independently removed exact content binding, source/provenance distinction, checker-lineage independence, hostile-checker discrimination, behavioral influence, evaluator protection/access telemetry, non-compensatory hard gating (replaced by a frozen 6/9 soft-confidence threshold) and search-contamination blocking.

Before launch, the final hidden-set SHA-256 was \texttt{{23c7732118bf750b4f5b927aab271cf1e7ee1068d8dc1838ca5119d7e436b102}}, the split SHA-256 was \texttt{{747213c60d7a6087a6f6fda5e25546acae5ee70ec1b5b9b7db3868f208213959}}, the comparator/ablation config SHA-256 was \texttt{{efa50d3f4e1d76589f80a813e52805b01940409cf353c4826713935a87d8ca84}}, and the executable-harness SHA-256 was \texttt{{14a4c01442bd5f1d17eb4c7c443d94cbcf198e4e910a62d4126e6f35f27ad0c7}}. The freeze merge was GitHub-signature verified and its exact-main CI passed before the separate launch marker was authored.
"""
    text = replace_section(text, "Protocol Design", protocol_design)

    results = rf"""
The protected campaign completed successfully and the independently implemented reproducer recovered the same headline result. Full ORION produced \textbf{{0 false promotions in 360 hostile promotion opportunities}} (rate 0.000) and promoted \textbf{{60/60 clean positives}} (coverage 1.000; clean false-negative count 0). The strongest frozen comparator selected prospectively by the analysis code was \texttt{{{comparator}}}; it produced 180/360 false promotions (0.500) while also promoting 60/60 clean positives.

For H1, the ORION-minus-comparator false-promotion difference was \textbf{{{fmt(h1['orion_minus_baseline_false_promotion'])}}}, with paired-bootstrap 95\% CI \textbf{{[{fmt(h1['ci95_low'])}, {fmt(h1['ci95_high'])}]}}. The upper confidence bound was below zero and the point estimate exceeded the predeclared 0.05 absolute practical margin, so H1 passed. For H2, the clean-coverage difference was \textbf{{{fmt(h2['orion_minus_baseline_clean_coverage'])}}}, 95\% CI \textbf{{[{fmt(h2['ci95_low'])}, {fmt(h2['ci95_high'])}]}}, satisfying the $-0.05$ non-inferiority guard. Security therefore did not arise from total refusal. H3 was not supported: correct \texttt{{CANNOT\_CHECK}} selection tied the strongest comparator (difference {fmt(h3['orion_minus_baseline_correct_cannot_check'])}, 95\% CI [{fmt(h3['ci95_low'])}, {fmt(h3['ci95_high'])}]). We report that null secondary result rather than treating a tie as evidence for the mechanism.

Full ORION achieved 1.000 claim correctness, source-attribution accuracy, support/contradiction F1, conflation detection, content-substitution detection, tamper/leakage detection and correct-\texttt{{CANNOT\_CHECK}} rate in the frozen battery. Actual scored-process telemetry recorded zero protected-identifier accesses and zero external IP connections for both candidate and comparator/ablation lanes. All raw false positives, false negatives, null cases, per-case transitions and syscall traces were retained in protected Actions custody; the safe aggregate package records {SUMMARY['retained_error_case_count']} retained non-ORION/mismatch records without excluding them from analysis.

The ablation arm supports mechanism localization rather than only aggregate superiority. All eight ablations retained 1.000 clean coverage, while each increased false promotion relative to full ORION on the frozen campaign. The soft-confidence variant was the largest failure mode, showing why compensatory scoring is not interchangeable with the hard authority lattice. Exact per-ablation values are reported in Table~\ref{{tab:p4_t2}} and regenerated from the committed safe summary.

\begin{{figure}}[t]
\centering
\IfFileExists{{../figures/p4_2_false_promotion.pdf}}{{\includegraphics[width=0.96\linewidth]{{../figures/p4_2_false_promotion.pdf}}}}{{}}
\caption{{False scientific-authority promotion by frozen system with Wilson 95\% intervals.}}
\label{{fig:p4_2}}
\end{{figure}}

\begin{{figure}}[t]
\centering
\IfFileExists{{../figures/p4_3_coverage_frontier.pdf}}{{\includegraphics[width=0.96\linewidth]{{../figures/p4_3_coverage_frontier.pdf}}}}{{}}
\caption{{Clean authority coverage versus false-promotion rate. ORION occupies the zero-false-promotion, full-coverage corner on the protected campaign.}}
\label{{fig:p4_3}}
\end{{figure}}

\begin{{figure}}[t]
\centering
\IfFileExists{{../figures/p4_4_detection_by_attack.pdf}}{{\includegraphics[width=0.96\linewidth]{{../figures/p4_4_detection_by_attack.pdf}}}}{{}}
\caption{{Correct terminal rate by hostile attack family for ORION and the strongest frozen comparator.}}
\label{{fig:p4_4}}
\end{{figure}}

\begin{{figure}}[t]
\centering
\IfFileExists{{../figures/p4_5_attribution_vs_support.pdf}}{{\includegraphics[width=0.96\linewidth]{{../figures/p4_5_attribution_vs_support.pdf}}}}{{}}
\caption{{Source-attribution accuracy and semantic-support accuracy remain separately reported coordinates.}}
\label{{fig:p4_5}}
\end{{figure}}

\begin{{figure}}[t]
\centering
\IfFileExists{{../figures/p4_6_cost_false_promotion.pdf}}{{\includegraphics[width=0.96\linewidth]{{../figures/p4_6_cost_false_promotion.pdf}}}}{{}}
\caption{{Frozen resource cost versus false-promotion rate.}}
\label{{fig:p4_6}}
\end{{figure}}

\input{{../tables/p4_t1_attack_custody}}
\input{{../tables/p4_t2_baseline_ablation_results}}
\input{{../tables/p4_t3_cannot_check_errors}}
"""
    text = replace_section(text, "Results", results)

    reproducibility = r"""
The publication-authorizing run is GitHub Actions campaign \texttt{31968809206}. Safe immutable outputs are committed under \texttt{evidence/protected-campaign-31968809206/}: campaign summary, typed authority panel, ablation summary, access-telemetry summary, post-run public attack manifest/verdicts and independent reproduction receipt. \texttt{ARTIFACT\_INDEX\_V1.json} binds those files to the host-preparation run, protected-manifest hash, scored job identities and the Actions safe-bundle artifact. Protected raw scored verdicts, error analysis and candidate/comparator \texttt{strace} remain in protected Actions custody rather than being copied into the public repository.

A clean public replay requires no hidden labels: run \texttt{python reproducibility/replay\_public.py}. It verifies the committed safe-file hashes and aggregate invariants, then deterministically regenerates all releasable figures/tables from \texttt{figures/data/RESULTS\_SUMMARY\_V1.json}. The independent protected reproducer is separate: job \texttt{95218146748} reacquired the protected host artifact after scoring, recomputed the headline counts without importing the evaluator implementation and matched the typed-panel hash/effects exactly. The final release package therefore distinguishes public reproducibility from protected-custody reproduction instead of pretending hidden labels are publicly replayable.
"""
    text = replace_section(text, "Reproducibility", reproducibility)

    conclusion = r"""
Under the prospectively frozen 420-case protected authority campaign, full ORION reduced false scientific-authority promotion from 0.500 for the strongest frozen comparator to 0.000 while preserving 1.000 clean authority coverage. The paired false-promotion effect passed the predeclared practical/statistical gate, all eight mechanism ablations increased false promotion without buying clean coverage, actual process telemetry showed no protected-label/network access during scored execution, and an independent implementation reproduced the headline result. The secondary H3 comparison of correct \texttt{CANNOT\_CHECK} selection was a tie and is not supported.

The defensible conclusion is therefore bounded to the registered attack families, subject revision, resource policy and custody model: exact content/provenance binding plus admissible checker lineage, protected evaluation and a non-compensatory authority terminal can materially reduce false authority promotion without collapsing clean coverage in this setting. Finite attack coverage, synthetic/mechanical gold, evaluator attacks outside the taxonomy and the absence of human adjudication cases limit generalization. Those limitations are reasons to preserve external custody and abstention costs, not reasons to silently promote the result into a universal security claim.
"""
    text = replace_section(text, "Conclusion", conclusion)

    stale = [
        "No external results are reported in this manuscript",
        "all execution bindings remain \\texttt{UNBOUND}",
        "remains externally \\texttt{CANNOT\\_CHECK}",
    ]
    for phrase in stale:
        if phrase in text:
            raise RuntimeError(f"stale prospective result claim survived: {phrase}")
    manuscript.write_text(text, encoding="utf-8")

    protected_ledger = ROOT / "evidence" / "PROTECTED_CLAIM_LEDGER_V1.md"
    protected_ledger.write_text(
        f"""# P4 protected result claim ledger V1

Canonical accepted campaign: **31968809206**.  Protected subject: `{SUMMARY['subject_commit']}`.  Typed panel: `{SUMMARY['typed_panel_hash']}` (`PASS`).

| Claim | State | Exact evidence |
|---|---|---|
| Full ORION false scientific-authority promotion is 0/360 on the frozen hostile opportunities. | **SUPPORTED** | `protected-campaign-31968809206/CAMPAIGN_SUMMARY_V1.json` → `systems.ORION.rates.false_authority_promotion_rate`; raw per-case scored verdicts retained in protected Actions artifact from run 31968809206. |
| Strongest frozen comparator is `{comparator}` at 180/360 false promotions (0.500). | **SUPPORTED** | `CAMPAIGN_SUMMARY_V1.json` → `strongest_frozen_comparator` and comparator system metrics; independently recomputed by `INDEPENDENT_REPRODUCTION_V1.json`. |
| H1 ORION-minus-comparator false-promotion effect is {h1['orion_minus_baseline_false_promotion']:.3f}, 95% CI [{h1['ci95_low']:.3f}, {h1['ci95_high']:.3f}]. | **SUPPORTED / preregistered gate PASS** | `CAMPAIGN_SUMMARY_V1.json` → `H1`; statistical plan `protocol/STATISTICAL_ANALYSIS_PLAN_V1.md`. |
| ORION and strongest comparator both promote 60/60 clean positives; coverage difference is {h2['orion_minus_baseline_clean_coverage']:.3f}, 95% CI [{h2['ci95_low']:.3f}, {h2['ci95_high']:.3f}]. | **SUPPORTED / H2 PASS** | `CAMPAIGN_SUMMARY_V1.json` → `H2`, `systems.*.clean_coverage`; independent receipt. |
| H3 correct-CANNOT_CHECK superiority is supported. | **NOT SUPPORTED** | `CAMPAIGN_SUMMARY_V1.json` → `H3`: difference 0.000, CI [0.000, 0.000]. The manuscript must not promote this tie. |
| The safety result is not total refusal. | **SUPPORTED** | ORION clean coverage 60/60 and clean false-negative count 0 in `CAMPAIGN_SUMMARY_V1.json`. |
| Every frozen ORION ablation increases false promotion while retaining clean coverage. | **SUPPORTED for this campaign** | `ABLATION_SUMMARY_V1.json`; all eight variants are reported, none excluded. |
| Scored candidate/comparator lanes accessed protected identifiers or external IP endpoints. | **REFUTED** | `ACCESS_TELEMETRY_SUMMARY_V1.json`: all four counts are zero; raw syscall traces retained in protected Actions custody. |
| Independent protected reproduction matches the headline result. | **SUPPORTED** | `INDEPENDENT_REPRODUCTION_V1.json`: `headline_reproduced=true`, identical 0/360 vs 180/360 and 60/60 clean counts, matching typed-panel hash. |
| The result establishes universal scientific-authority security. | **REJECTED / out of scope** | Frozen threat model covers 13 families on one bound subject/custody model; limitations remain explicit. |

`ARTIFACT_INDEX_V1.json` content-addresses the public-safe files and records host/campaign job identities. The protected per-case artifact is deliberately not copied into this public ledger.
""",
        encoding="utf-8",
    )

    def append_once(path: Path, marker: str, block: str) -> None:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if marker not in existing:
            path.write_text(existing.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")

    append_once(
        ROOT / "evidence" / "CLAIM_LEDGER_V1.md",
        "## Protected campaign 31968809206",
        """## Protected campaign 31968809206

Publication-level authority claims are now governed by `PROTECTED_CLAIM_LEDGER_V1.md`. The earlier local/mechanism claims remain historical evidence; they cannot override the accepted protected result or its explicit H3 non-result.
""",
    )
    append_once(
        ROOT / "evidence" / "AVAILABILITY_STATEMENT_V1.md",
        "## Accepted protected campaign",
        """## Accepted protected campaign

The accepted safe aggregate package for Actions run `31968809206` is committed under `evidence/protected-campaign-31968809206/`. It includes the typed panel, H1/H2/H3 summary, all eight ablations, public post-run attack/verdict slices, actual access-telemetry summary and independent reproduction receipt. Protected hidden labels, raw scored verdicts, error analysis and raw syscall traces remain in Actions custody and are identified by `ARTIFACT_INDEX_V1.json`; they are not silently reclassified as public data.
""",
    )
    append_once(
        ROOT / "reproducibility" / "README.md",
        "## Accepted campaign replay",
        """## Accepted campaign replay

Canonical protected run: `31968809206`; safe bundle artifact ID: `9269235009`.

Public non-secret replay:

```bash
cd papers/paper-04-verified-scientific-discovery
python reproducibility/replay_public.py
```

The replay verifies content hashes and headline aggregate consistency, checks the accepted telemetry/reproduction receipts, regenerates P4-2…P4-6 and Tables P4-1…P4-3, and writes `reproducibility/PUBLIC_REPLAY_RECEIPT_V1.json`. Hidden labels are not required. Protected headline reproduction already passed independently in Actions job `95218146748`.
""",
    )
    append_once(
        ROOT / "reproducibility" / "SCRIPT_INDEX.md",
        "## Protected campaign scripts",
        """## Protected campaign scripts

- `../host/generate_protected_cases.py` — independently generated final hidden set before launch.
- `../host/run_candidate.py` — production ORION adapter (`resolve_evidence_ref` + `evaluate_hard_gates`).
- `../host/run_baselines.py` — nine gold-blind comparator mechanisms.
- `../host/run_ablations.py` — eight resource-matched ablations.
- `../host/evaluate_campaign.py` — protected typed-panel/H1/H2/H3 scorer.
- `../host/evaluate_ablations.py` — protected ablation scorer.
- `../host/independent_reproduce.py` — independent protected headline reproducer.
- `../figures/generate_protected_results.py` — deterministic safe aggregate → figures/tables renderer.
- `replay_public.py` — clean public hash verification and non-secret replay.
""",
    )

    readiness = ROOT / "JOURNAL_READINESS.md"
    ready = readiness.read_text(encoding="utf-8")
    replacements = {
        "- [ ] add Results only from immutable protected artifacts;": "- [x] add Results only from immutable protected artifacts;",
        "- [ ] frozen attack-case manifest with hidden labels stored under protected custody;": "- [x] frozen attack-case manifest with hidden labels stored under protected custody;",
        "- [ ] exact source/evidence content snapshots/digests;": "- [x] exact source/evidence content snapshots/digests;",
        "- [ ] baseline and checker configs;": "- [x] baseline and checker configs;",
        "- [ ] evaluator/holdout access logs;": "- [x] evaluator/holdout access logs;",
        "- [ ] search trajectories for contamination audit;": "- [x] search trajectories for contamination audit;",
        "- [ ] raw per-claim verdicts and authority transitions;": "- [x] raw per-claim verdicts and authority transitions;",
        "- [ ] scripts regenerating all figures/tables;": "- [x] scripts regenerating all figures/tables;",
        "- [ ] clean-environment replay of non-secret portions;": "- [x] clean-environment replay of non-secret portions;",
        "- [ ] independent reproduction/hostile review of the headline false-promotion result.": "- [x] independent reproduction/hostile review of the headline false-promotion result.",
    }
    for old, new in replacements.items():
        if old in ready:
            ready = ready.replace(old, new, 1)
    readiness.write_text(ready, encoding="utf-8")

    print("integrated accepted protected campaign into manuscript and publication ledgers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
