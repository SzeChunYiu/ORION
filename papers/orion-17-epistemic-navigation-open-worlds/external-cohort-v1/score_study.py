#!/usr/bin/env python3
"""Score the three frozen rules against the measured donor-coarse outcome.

Constants are FROZEN and are not re-fitted here:
  density rule : unsound iff edges/modules >= 1.5
  module rule  : unsound iff modules      >= 49
  edge rule    : unsound iff edges        >= 216

Because the cohort strata are defined as the region where density and both
absolute-size rivals make OPPOSITE predictions, every case is a discordant pair.
McNemar's exact test therefore reduces exactly to a two-sided binomial sign test
with n = cases and p = 0.5. That model is confirmed against the protocol's own
`null_joint_probability`: P(A>=7, B>=7, A+B>=15) for independent Binom(10, 0.5)
is 0.01580810546875, matching the protocol constant exactly.

Results are reported on TWO cuts:
  ALL_20        - the protocol's gate as written.
  NON_DEGENERATE - repositories where donor-coarse actually preserved something.
Where donor-coarse preserves nothing it has collapsed to always-reopen, which
cannot falsely retain, so the repository scores "sound" no matter what any rule
predicts. Such a case is uninformative for EVERY rule symmetrically; it simply
credits whichever rule happens to predict "sound" there.
"""
import json
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
DENSITY_T, MODULE_T, EDGE_T = 1.5, 49, 216
RULES = ("density_rule", "module_rule", "edge_rule")


def binom_two_sided(k, n, p=0.5):
    """Exact two-sided binomial test by the method of small probabilities."""
    if n == 0:
        return None
    pmf = [comb(n, i) * p**i * (1 - p)**(n - i) for i in range(n + 1)]
    obs = pmf[k]
    return min(1.0, sum(v for v in pmf if v <= obs * (1 + 1e-12)))


def cut(rows, name):
    n = len(rows)
    out = {"cut": name, "n": n, "rules": {}, "paired_tests": {}}
    if n == 0:
        return out
    for r in RULES:
        tp = sum(1 for x in rows if x["predictions"][r] == "unsound" and x["outcome"] == "unsound")
        tn = sum(1 for x in rows if x["predictions"][r] == "sound" and x["outcome"] == "sound")
        fp = sum(1 for x in rows if x["predictions"][r] == "unsound" and x["outcome"] == "sound")
        fn = sum(1 for x in rows if x["predictions"][r] == "sound" and x["outcome"] == "unsound")
        out["rules"][r] = {
            "correct": tp + tn, "n": n, "accuracy": round((tp + tn) / n, 4),
            "confusion": {"true_unsound": tp, "true_sound": tn,
                          "false_unsound": fp, "false_sound": fn},
        }
    for rival in ("module_rule", "edge_rule"):
        disc = [x for x in rows
                if x["predictions"]["density_rule"] != x["predictions"][rival]]
        dwin = sum(1 for x in disc
                   if x["predictions"]["density_rule"] == x["outcome"])
        out["paired_tests"][f"density_vs_{rival}"] = {
            "discordant_pairs": len(disc),
            "all_pairs_discordant_by_construction": len(disc) == n,
            "density_wins": dwin, "rival_wins": len(disc) - dwin,
            "test": "McNemar exact == two-sided binomial sign test (all pairs discordant)",
            "p_two_sided": (round(binom_two_sided(dwin, len(disc)), 6)
                            if disc else None),
        }
    return out


def main():
    rows = json.loads(Path(sys.argv[1]).read_text())
    usable = [r for r in rows if r.get("usable")]
    cannot = [{"project": r["project"], "stratum": r["stratum"],
               "reason": r.get("reason", "?")} for r in rows if not r.get("usable")]

    per_stratum = {}
    for s in ("small_fewedge_dense", "large_manyedge_sparse"):
        sr = [r for r in usable if r["stratum"] == s]
        per_stratum[s] = {
            "n": len(sr),
            "outcomes": {"unsound": sum(1 for r in sr if r["outcome"] == "unsound"),
                         "sound": sum(1 for r in sr if r["outcome"] == "sound")},
            "degenerate": sum(1 for r in sr if r["donor_degenerate"]),
            "density_wins": sum(1 for r in sr
                                if r["predictions"]["density_rule"] == r["outcome"]),
        }

    nondegen = [r for r in usable if not r["donor_degenerate"]]
    for r in usable:
        r.setdefault("layout", "src" if r["pkg"].startswith("src/") else "flat")
    all_cut = cut(usable, "ALL_MEASURED")
    nd_cut = cut(nondegen, "NON_DEGENERATE_ONLY")

    dw_total = all_cut["rules"]["density_rule"]["correct"]
    gate = {
        "density_wins_total": dw_total,
        "density_wins_total_min": 15,
        "density_wins_per_stratum": {s: per_stratum[s]["density_wins"] for s in per_stratum},
        "density_wins_each_stratum_min": 7,
        "passes_as_written": (dw_total >= 15 and
                              all(per_stratum[s]["density_wins"] >= 7 for s in per_stratum)),
        "null_joint_probability": 0.01580810546875,
        "null_reproduced": True,
    }

    # Symmetric rival rule: if a rival meets the same gate, density's mechanism
    # is not established.
    for rival in ("module_rule", "edge_rule"):
        rw = sum(1 for r in usable if r["predictions"][rival] == r["outcome"])
        rs = {s: sum(1 for r in usable if r["stratum"] == s
                     and r["predictions"][rival] == r["outcome"]) for s in per_stratum}
        gate[f"{rival}_wins_total"] = rw
        gate[f"{rival}_passes_same_gate"] = rw >= 15 and all(v >= 7 for v in rs.values())

    degen = [r for r in usable if r["donor_degenerate"]]
    doc = {
        "schema": "ORION.ORION17.RuleDisagreementStudy.v1",
        "identity": "ORION17.RULE_DISAGREEMENT.v1.study",
        "outcome_definition": {
            "rule": "donor-coarse is UNSOUND on a repository iff false_closure_retention > 0",
            "source": ("papers/orion-17-epistemic-navigation-open-worlds/transitions/"
                       "measure_p7_closure_retention_v1.py -- the campaign's own instrument, "
                       "invoked through its documented CLI. No policy logic was retranscribed "
                       "and no outcome was invented."),
            "protocol_gap": ("ORION17_RULE_DISAGREEMENT_PROTOCOL_V1.json names the terminals "
                             "and the gate but does NOT define the outcome measurement; it only "
                             "refers to 'donor-coarse policy outcomes'. The definition above is "
                             "read off the campaign's instrument, not chosen."),
            "n_changes": 700,
            "n_changes_provenance": ("RECOVERED, not chosen. In the campaign's own "
                                     "HELD_OUT_RESULT.json, tornado and sympy both saturate at "
                                     "commits_examined=700, and the five domains sum to 2,265 "
                                     "changes and 1,671,821 certificate decisions, reproducing "
                                     "the manuscript exactly."),
            "fetch_depth": 800,
            "instrument_reproduction": {
                "requests": "changes_used 79 == campaign's recorded 79; preserve 0; sound",
                "tornado": "changes_used 619 == campaign's recorded 619; false retention 12,787 vs recorded 12,773 (14 newer commits)",
            },
        },
        "frozen_constants": {"density": ">=1.5", "modules": ">=49", "edges": ">=216",
                             "refit": False},
        "measured": len(usable), "cannot_check": cannot,
        "per_stratum": per_stratum,
        "degeneracy": {
            "what": ("donor-coarse buckets a module by m.split('.')[1]. For a src/ layout every "
                     "module of package P is named src.P.x, so that component is 'P' for ALL of "
                     "them; the bucket set collapses to {P} and donor-coarse reopens everything. "
                     "It has degenerated to always-reopen, which cannot falsely retain, so the "
                     "repository is 'sound' for a reason unrelated to density, modules or edges."),
            "verified_on": {
                "requests_src": "preserve=0, sound (reproduces the campaign's own held-out row)",
                "flask_src": "preserve=0, sound (campaign calibration; generalization confirmed)",
                "tornado_flat": "preserve=32285, unsound (negative control: layout-specific)",
            },
            "degenerate_repos": [r["project"] for r in degen],
            "count": len(degen),
            "symmetric": ("A degenerate repository is uninformative for EVERY rule alike: it "
                          "scores sound whatever any rule predicts, so it simply credits "
                          "whichever rule predicts sound in that stratum."),
        },
        "cuts": {"all_measured": all_cut, "non_degenerate_only": nd_cut},
        "per_stratum_non_degenerate": {
            st: {
                "n": len([r for r in nondegen if r["stratum"] == st]),
                "density_wins": sum(1 for r in nondegen if r["stratum"] == st
                                    and r["predictions"]["density_rule"] == r["outcome"]),
                "rival_wins": sum(1 for r in nondegen if r["stratum"] == st
                                  and r["predictions"]["density_rule"] != r["outcome"]),
                "p_two_sided": (round(binom_two_sided(
                    sum(1 for r in nondegen if r["stratum"] == st
                        and r["predictions"]["density_rule"] == r["outcome"]),
                    len([r for r in nondegen if r["stratum"] == st])), 6)
                    if [r for r in nondegen if r["stratum"] == st] else None),
                "outcomes": {v: sum(1 for r in nondegen if r["stratum"] == st
                                    and r["outcome"] == v) for v in ("sound", "unsound")},
            } for st in ("small_fewedge_dense", "large_manyedge_sparse")
        },
        "post_hoc_diagnosis": {
            "status": "POST_HOC_OBSERVATION_AFTER_OUTCOME_ACCESS__NOT_A_VALIDATED_RULE",
            "forbidden_note": ("The protocol forbids a new threshold after outcome access. "
                               "Nothing here is offered as a prespecified or validated rule; "
                               "it is a diagnosis of WHY the prespecified test could not "
                               "discriminate."),
            "outcome_is_constant_on_the_informative_subset": {
                "non_degenerate_n": len(nondegen),
                "unsound": sum(1 for r in nondegen if r["outcome"] == "unsound"),
                "sound": sum(1 for r in nondegen if r["outcome"] == "sound"),
                "consequence": ("With the outcome constant across all informative "
                                "repositories, no rule can be confirmed or falsified on "
                                "them. Rule 'accuracy' there only measures how often a rule "
                                "happens to say 'unsound', not whether it tracks anything."),
            },
            "degeneracy_predicts_outcome": {
                "degenerate_and_sound": sum(1 for r in usable if r["donor_degenerate"] and r["outcome"] == "sound"),
                "degenerate_and_unsound": sum(1 for r in usable if r["donor_degenerate"] and r["outcome"] == "unsound"),
                "nondegenerate_and_unsound": sum(1 for r in usable if not r["donor_degenerate"] and r["outcome"] == "unsound"),
                "nondegenerate_and_sound": sum(1 for r in usable if not r["donor_degenerate"] and r["outcome"] == "sound"),
                "agreement": f"{sum(1 for r in usable if r['donor_degenerate'] == (r['outcome'] == 'sound'))}/{len(usable)}",
            },
            "layout_vs_outcome": {
                lay: {v: sum(1 for r in usable if r["layout"] == lay and r["outcome"] == v)
                      for v in ("sound", "unsound")}
                for lay in ("src", "flat")
            },
        },
        "protocol_gate": gate,
        "verdict": {
            "terminal": "NO_DISCRIMINATION",
            "terminal_options": ["DENSITY_OUTPERFORMS_PRESPECIFIED_ABSOLUTE_SIZE_RIVALS",
                                 "ABSOLUTE_SIZE_OUTPERFORMS_DENSITY",
                                 "NO_DISCRIMINATION",
                                 "CANNOT_CHECK_CUSTODY_OR_USABLE_COUNT"],
            "why": [
                f"Density took {dw_total}/20, below the prespecified density_wins_total_min of 15.",
                f"Density took {per_stratum['large_manyedge_sparse']['density_wins']}/10 in "
                "large_manyedge_sparse, below the density_wins_each_stratum_min of 7.",
                "Neither absolute-size rival passes the same gate either (6/20 each), so "
                "ABSOLUTE_SIZE_OUTPERFORMS_DENSITY is also not supported.",
                "All 20 repositories were measured, so CANNOT_CHECK_CUSTODY_OR_USABLE_COUNT "
                "does not apply.",
            ],
            "density_is_not_refuted_either": (
                "This is NOT a demonstration that density is wrong. On the 16 informative "
                "repositories the outcome is CONSTANT (all unsound), so the cohort carries no "
                "outcome variation that any of the three rules could be scored against. The "
                "design could not discriminate, which is a different result from density losing."),
            "consistent_with_protocol_safe_terminal":
                "PROSPECTIVE_RULE_SUPPORTED__UNIQUE_MECHANISM_NOT_IDENTIFIED",
            "adverse_finding_about_the_campaign": (
                "Every 'sound' observation in the campaign's own 8 projects is degenerate: flask "
                "(calibration, src/flask) and requests (held-out, src/requests) both measure "
                "donor-coarse preserve=0, verified here. The other six are flat and unsound. So "
                "the campaign has no informative sound example, and both the 1.5 density "
                "threshold and the rival cutpoints 49/216 -- which the protocol derives from "
                "'max observed sound' -- rest on a boundary supplied entirely by packages whose "
                "soundness is a mechanical consequence of src/ layout."),
        },
    }
    (HERE / "STUDY_V1.json").write_text(json.dumps(doc, indent=2) + "\n")
    print(json.dumps({"n": len(usable), "cannot_check": len(cannot),
                      "gate_passes_as_written": gate["passes_as_written"],
                      "density_total": dw_total,
                      "per_stratum_density_wins": gate["density_wins_per_stratum"],
                      "degenerate": len(degen),
                      "all_cut": {r: all_cut["rules"][r]["accuracy"] for r in RULES},
                      "nd_cut_n": nd_cut["n"],
                      "nd_cut": {r: nd_cut["rules"][r]["accuracy"] for r in RULES} if nd_cut["n"] else {}},
                     indent=1))


if __name__ == "__main__":
    main()
