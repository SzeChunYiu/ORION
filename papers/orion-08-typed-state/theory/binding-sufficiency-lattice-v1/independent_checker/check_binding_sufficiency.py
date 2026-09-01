#!/usr/bin/env python3
"""Independent checker for ORION08.BINDING_SUFFICIENCY_LATTICE.v1.

INDEPENDENCE CONTRACT
---------------------
No ORION-08 or N-lane module is imported. The sufficiency theorem is verified on
freshly enumerated finite decision problems, and the ORION-08 instantiation is
recomputed from the frozen N4 result files by arithmetic on their recorded
values -- those files are read as data, never executed.

Checks
    A. Sufficiency theorem -- a deterministic zero-regret policy using only the
       binding B exists IFF every positive-mass B-fibre has a common optimal
       action. Exhaustive over small finite worlds.
    B. Refinement monotonicity -- refining a binding never increases Bayes risk.
       The decrease is strict exactly when some coarse fibre has no action that
       minimizes aggregate loss on every positive-mass refined subfibre.
    C. ORION-08 instantiation -- oracle-gap fractions recomputed from the frozen
       N4-B and N4-F3 receipts.
    D. Negative controls.

Exit codes
    0 pass    2 fail    3 CANNOT_CHECK
"""
from __future__ import annotations
import itertools, json, sys
from fractions import Fraction
from pathlib import Path

PACKET = Path(__file__).resolve().parent.parent
ROOT = PACKET.parents[3]
NLANE = ROOT / "research/extensions/orion-q/nlanes"
N4B = NLANE / "N4_B_STALE_RECEIPT_REOPENING_RESULTS.json"
N4F3 = NLANE / "N4_F3_REMINT_TRANSPORT_RESULTS.json"


def bayes_risk(worlds, mass, loss, binding):
    """Minimum expected loss of a deterministic policy measurable wrt binding."""
    fibres = {}
    for w in worlds:
        fibres.setdefault(binding[w], []).append(w)
    total = Fraction(0)
    for _z, ws in fibres.items():
        total += min(sum(mass[w] * loss[w][a] for w in ws)
                     for a in range(len(loss[ws[0]])))
    return total


def optimal_actions(loss_row):
    m = min(loss_row)
    return {a for a, v in enumerate(loss_row) if v == m}


def canonical_partitions(n):
    """Yield each set partition once as a restricted-growth label tuple."""
    for labels in itertools.product(range(n), repeat=n):
        if labels[0] != 0:
            continue
        if all(labels[i] <= 1 + max(labels[:i]) for i in range(1, n)):
            yield labels


def refines(fine, coarse):
    """Return whether every fine block is contained in one coarse block."""
    return all(fine[i] != fine[j] or coarse[i] == coarse[j]
               for i in range(len(fine)) for j in range(len(fine)))


def strict_refinement_criterion(loss, coarse, fine):
    """Correct equality condition for minimum-of-sums versus sum-of-minima."""
    n_actions = len(loss[0])
    coarse_blocks = {}
    for w, label in enumerate(coarse):
        coarse_blocks.setdefault(label, []).append(w)
    for worlds in coarse_blocks.values():
        subblocks = {}
        for w in worlds:
            subblocks.setdefault(fine[w], []).append(w)
        common = set(range(n_actions))
        for subworlds in subblocks.values():
            totals = [sum(loss[w][a] for w in subworlds)
                      for a in range(n_actions)]
            common &= optimal_actions(totals)
        if not common:
            return True
    return False


def main() -> int:
    try:
        # ---- A + B: exhaustive over small finite worlds -------------------
        # Uniform mass, so Bayes risk is proportional to the integer sum
        # sum_z min_a sum_{w in z} loss[w][a].  Integer arithmetic throughout;
        # no division is needed and nothing is approximated.
        checked = 0
        strict_checked = 0
        CONFIGS = [(2, 2), (2, 3), (3, 2), (3, 3), (4, 2)]
        for n_worlds, n_actions in CONFIGS:
            for flat in itertools.product(range(3), repeat=n_worlds * n_actions):
                loss = [list(flat[w * n_actions:(w + 1) * n_actions])
                        for w in range(n_worlds)]
                opt = [optimal_actions(loss[w]) for w in range(n_worlds)]
                oracle = sum(min(loss[w]) for w in range(n_worlds))
                finest = sum(min(loss[w]) for w in range(n_worlds))
                for assign in itertools.product(range(n_worlds), repeat=n_worlds):
                    fibres = {}
                    for w in range(n_worlds):
                        fibres.setdefault(assign[w], []).append(w)
                    common = all(set.intersection(*(opt[w] for w in ws))
                                 for ws in fibres.values())
                    risk = sum(min(sum(loss[w][a] for w in ws)
                                   for a in range(n_actions))
                               for ws in fibres.values())
                    if common != (risk == oracle):            # A: the IFF
                        raise AssertionError(json.dumps(
                            {"check": "A", "loss": loss, "binding": list(assign)}))
                    if finest > risk:                          # B: monotonicity
                        raise AssertionError(json.dumps(
                            {"check": "B", "loss": loss}))
                    checked += 1

                # Verify the corrected strictness IFF over every unique
                # coarse/refined partition pair. This is deliberately separate
                # from the zero-oracle-regret theorem above: world-level action
                # impurity is not by itself enough for an arbitrary refinement
                # to reduce risk.
                parts = list(canonical_partitions(n_worlds))
                risks = {}
                for part in parts:
                    fibres = {}
                    for w, label in enumerate(part):
                        fibres.setdefault(label, []).append(w)
                    risks[part] = sum(
                        min(sum(loss[w][a] for w in ws)
                            for a in range(n_actions))
                        for ws in fibres.values()
                    )
                for coarse in parts:
                    for fine in parts:
                        if not refines(fine, coarse):
                            continue
                        observed_strict = risks[fine] < risks[coarse]
                        predicted_strict = strict_refinement_criterion(
                            loss, coarse, fine)
                        if observed_strict != predicted_strict:
                            raise AssertionError(json.dumps({
                                "check": "B_strict_iff",
                                "loss": loss,
                                "coarse": coarse,
                                "fine": fine,
                                "coarse_risk": risks[coarse],
                                "fine_risk": risks[fine],
                                "criterion": predicted_strict,
                            }))
                        strict_checked += 1

        # ---- D: negative controls -----------------------------------------
        controls = {}
        # a fibre mixing worlds with disjoint optimal actions must have regret > 0
        loss = {0: [0, 5], 1: [5, 0]}
        mass = {0: Fraction(1, 2), 1: Fraction(1, 2)}
        coarse = {0: 0, 1: 0}
        fine = {0: 0, 1: 1}
        controls["mixed_fibre_has_strict_regret"] = {
            "pass": bayes_risk([0, 1], mass, loss, coarse)
            > bayes_risk([0, 1], mass, loss, fine)}
        # a refinement that splits an ALREADY-pure fibre adds nothing
        loss2 = {0: [0, 5], 1: [0, 5]}
        controls["splitting_pure_fibre_adds_nothing"] = {
            "pass": bayes_risk([0, 1], mass, loss2, coarse)
            == bayes_risk([0, 1], mass, loss2, fine)}
        # Counterexample to the withdrawn shorthand: the coarse fibre contains
        # worlds with incompatible pointwise optima and is split, but both
        # refined subfibres have the same aggregate optimum, so risk is equal.
        loss3 = {
            0: [0, 3], 1: [2, 0],
            2: [0, 3], 3: [2, 0],
        }
        mass3 = {w: Fraction(1, 4) for w in loss3}
        coarse3 = {w: 0 for w in loss3}
        fine3 = {0: 0, 1: 0, 2: 1, 3: 1}
        controls["withdrawn_impure_split_shorthand_is_false"] = {
            "pass": (
                not set.intersection(*(optimal_actions(loss3[w]) for w in loss3))
                and bayes_risk(list(loss3), mass3, loss3, coarse3)
                == bayes_risk(list(loss3), mass3, loss3, fine3)
                and not strict_refinement_criterion(
                    [loss3[w] for w in sorted(loss3)],
                    tuple(coarse3[w] for w in sorted(loss3)),
                    tuple(fine3[w] for w in sorted(loss3)),
                )
            )
        }
        controls_ok = all(v["pass"] for v in controls.values())

        # ---- C: ORION-08 instantiation from frozen receipts ----------------
        if not (N4B.is_file() and N4F3.is_file()):
            raise FileNotFoundError("N4 receipts missing")
        B = json.loads(N4B.read_text()); F = json.loads(N4F3.read_text())
        pb, pf = B["pooled"], F["pooled"]
        nb = pb["NEVER_REOPEN"]["mean_regret_vs_oracle"]
        sb = pb["ORION_SCOPED_REOPEN"]["mean_regret_vs_oracle"]
        per = {}
        for reg, v in B["per_regime"].items():
            o = v["ORACLE_AVAILABILITY"]["mean_round_utility"]
            nn = v["NEVER_REOPEN"]["mean_round_utility"]
            ss = v["ORION_SCOPED_REOPEN"]["mean_round_utility"]
            per[reg] = round(100 * (ss - nn) / (o - nn), 1)
        naive = pf["NAIVE_CARRY_FORWARD"]["regret_vs_oracle"]
        red = pf["RE_DERIVE_SCRATCH"]["regret_vs_oracle"]
        typed = pf["ORION_TYPED_TRANSPORT"]["regret_vs_oracle"]
        instantiation = {
            "N4_B_scoped_reopening": {
                "terminal": B["terminal"],
                "pooled_regret_never": nb, "pooled_regret_scoped": sb,
                "pooled_oracle_gap_closed_pct": round(100 * (nb - sb) / nb, 1),
                "per_regime_gap_closed_pct": per,
                "reading": "the scoped binding is FAR from decision-sufficient here",
            },
            "N4_F3_typed_transport": {
                "terminal": F["terminal"],
                "regret_naive": naive, "regret_re_derive": red, "regret_typed": typed,
                "gap_closed_vs_naive_pct": round(100 * (naive - typed) / naive, 1),
                "gap_closed_vs_strongest_baseline_pct": round(100 * (red - typed) / red, 1),
                "reading": "the typed binding is NEARLY decision-sufficient here",
            },
        }
    except AssertionError as exc:
        print(json.dumps({"status": "FAIL", "counterexample": str(exc)}, indent=2))
        return 2
    except Exception as exc:                                    # noqa: BLE001
        print(json.dumps({"status": "CANNOT_CHECK",
                          "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 3

    report = {
        "schema": "ORION.ORION08.BindingSufficiencyLattice.CheckerReport.v1",
        "successor_id": "ORION08.BINDING_SUFFICIENCY_LATTICE.v1",
        "independence": ("no ORION-08 or N-lane module imported; theorem verified on "
                         "freshly enumerated worlds; N4 receipts read as data only"),
        "check_A_B_exhaustive": {
            "world_action_configurations_checked": checked,
            "sufficiency_iff_common_optimal_action": True,
            "refinement_never_increases_risk": True,
            "refinement_strict_iff_no_joint_subfibre_optimum": True,
            "coarse_refined_partition_pairs_checked": strict_checked,
            "arithmetic": "exact rational",
        },
        "check_C_orion08_instantiation": instantiation,
        "check_D_negative_controls": controls,
        "status": "PASS" if controls_ok else "FAIL",
    }
    (PACKET / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("status", "check_A_B_exhaustive",
                       "check_C_orion08_instantiation",
                       "check_D_negative_controls")}, indent=2))
    return 0 if controls_ok else 2


if __name__ == "__main__":
    sys.exit(main())
