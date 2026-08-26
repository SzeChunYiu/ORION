#!/usr/bin/env python3
"""Outcome-blind power and attainability for the frozen P10 H1-H6 protocol.

`P10_H1_H6_PROTOCOL_FREEZE_V1.json` lists eight required inputs, all absent. The
freeze code enforces externality by NAME -- an input must be non-self-authorizing
only when its identifier contains `independent`, `custod` or `gold` -- so three
of the eight are genuinely external and five are the researcher's to produce.

This produces one of the five, and it is the one worth producing first: a gate
whose threshold cannot be reached kills a design before any compute is spent.
P2 froze an IoU threshold of 0.03 against an arm whose routes capped it at
0.0113, and nobody ran this arithmetic. P9's D1 v1.3 opportunity gate turned out
unattainable on every arm that exists. Both were found by counting, not running.

Nothing here reads an outcome. Every number is a property of the registered
design: sample sizes, thresholds and the multiplicity correction.

Exit codes: 0 derived, 2 a registered gate is unattainable or has zero tolerance,
3 CANNOT_CHECK.
"""

from __future__ import annotations

import json
import math
import sys

# From the freeze.
MIN_DOMAINS = 4
MIN_TASKS_PER_DOMAIN = 100
MIN_TOTAL_TASKS = 400
MIN_CONTROLS = 80
FAMILYWISE_ALPHA = 0.05
HOLM_FAMILY = ("H1", "H2", "H3", "H5", "H6")
H1_MARGIN = 0.10
H2_REDUCTION = 0.15
H2_WORST_DOMAIN = -0.05
H3_ABSOLUTE_CEILING = 0.05
H3_REDUCTION = 0.10
H5_UPPER_BOUND_CEILING = 0.05
H6_WORST_DOMAIN = -0.05


def clopper_pearson_upper(successes: int, trials: int, alpha: float) -> float:
    """Exact one-sided upper confidence bound on a binomial proportion.

    Uses the beta quantile identity so the bound is exact rather than normal-
    approximate: at these ceilings the approximation and the exact bound
    disagree about whether the gate passes, which is the whole question.
    """
    if successes >= trials:
        return 1.0
    try:
        from scipy.stats import beta
    except ImportError:
        if successes == 0:
            return 1.0 - alpha ** (1.0 / trials)
        raise
    return float(beta.ppf(1 - alpha, successes + 1, trials - successes))


def normal_quantile(p: float) -> float:
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q, r = p - 0.5, (p - 0.5) ** 2
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def paired_power(n: int, true_margin: float, gate_margin: float, discordance: float, alpha: float) -> float:
    if discordance <= 0:
        return 0.0
    se = math.sqrt(discordance / n)
    return normal_cdf((true_margin - gate_margin) / se - normal_quantile(1 - alpha))


def main() -> int:
    try:
        # H5: how many false expansions can the control set tolerate at all?
        tolerance = None
        h5_bounds = {}
        for failures in range(0, 9):
            bound = clopper_pearson_upper(failures, MIN_CONTROLS, 0.05)
            h5_bounds[failures] = round(bound, 6)
            if bound <= H5_UPPER_BOUND_CEILING and tolerance is None or (
                bound <= H5_UPPER_BOUND_CEILING
            ):
                tolerance = failures
        max_tolerated = max((k for k, v in h5_bounds.items() if v <= H5_UPPER_BOUND_CEILING), default=None)

        # Holm-Bonferroni: the first rejection is tested at alpha/m.
        holm_first = FAMILYWISE_ALPHA / len(HOLM_FAMILY)

        h1_power = {
            f"{d:.2f}": round(paired_power(MIN_TOTAL_TASKS, 0.15, H1_MARGIN, d, holm_first), 4)
            for d in (0.05, 0.10, 0.20, 0.40)
        }
        h1_power_at_uncorrected_alpha = {
            f"{d:.2f}": round(paired_power(MIN_TOTAL_TASKS, 0.15, H1_MARGIN, d, FAMILYWISE_ALPHA), 4)
            for d in (0.05, 0.10, 0.20, 0.40)
        }
        h6_worst_domain_power = {
            f"{d:.2f}": round(paired_power(MIN_TASKS_PER_DOMAIN, 0.0, H6_WORST_DOMAIN, d, holm_first), 4)
            for d in (0.05, 0.10, 0.20, 0.40)
        }
    except Exception as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "error": str(exc)}))
        return 3

    zero_tolerance = max_tolerated == 0
    checks = {
        "h5_ceiling_is_reachable_at_zero_failures": h5_bounds[0] <= H5_UPPER_BOUND_CEILING,
        "h5_has_more_than_zero_tolerance": not zero_tolerance,
        "h1_is_adequately_powered_at_moderate_discordance": h1_power["0.20"] >= 0.80,
    }

    print(
        json.dumps(
            {
                "schema": "orion.p10.prospective-attainability.v1",
                "record": "P10_H1_H6_PROSPECTIVE_ATTAINABILITY",
                "authority_scope": "PROSPECTIVE_OUTCOME_BLIND_ONLY",
                "outcome_accessed": False,
                "grants": "Nothing. P10 remains PROSPECTIVE_FROZEN_NOT_EXECUTED and execution stays unauthorized.",
                "discharges": "required_inputs prospective_power_and_attainability_receipt -- one of the five inputs the freeze does not require an outside party for",
                "design": {
                    "minimum_domains": MIN_DOMAINS,
                    "minimum_tasks_per_domain": MIN_TASKS_PER_DOMAIN,
                    "minimum_total_tasks": MIN_TOTAL_TASKS,
                    "minimum_known_method_controls": MIN_CONTROLS,
                },
                "multiplicity": {
                    "familywise_alpha": FAMILYWISE_ALPHA,
                    "method": "HOLM_BONFERRONI",
                    "family": list(HOLM_FAMILY),
                    "alpha_for_the_first_rejection": holm_first,
                    "note": "Holm tests the smallest p-value at alpha/m, so every power figure below is computed at 0.01 rather than 0.05. Reporting power at the uncorrected alpha would overstate it.",
                },
                "H5_false_expansion_ceiling": {
                    "gate": "one-sided 95% Clopper-Pearson upper bound <= 0.05 over at least 80 controls",
                    "exact_upper_bound_by_number_of_false_expansions": h5_bounds,
                    "maximum_false_expansions_that_still_pass": max_tolerated,
                    "reading": (
                        "The gate is reachable, but only with a perfect control set: a single false "
                        "expansion among the 80 minimum controls pushes the exact bound above the "
                        "ceiling. That is a zero-tolerance gate, and it should be registered as one "
                        "rather than discovered after the run."
                    ),
                    "how_to_buy_tolerance": (
                        "Tolerance comes from more controls, not from a softer ceiling. The minimum "
                        "control count is a design parameter the researcher sets; the ceiling is the "
                        "claim."
                    ),
                },
                "H1_power": {
                    "gate": f"paired margin >= {H1_MARGIN} with a simultaneous 95% lower bound above zero",
                    "n": MIN_TOTAL_TASKS,
                    "power_at_holm_corrected_alpha_if_true_margin_is_0.15": h1_power,
                    "power_at_uncorrected_alpha_for_comparison": h1_power_at_uncorrected_alpha,
                },
                "H6_worst_domain_power": {
                    "gate": f"every domain noninferior at margin {H6_WORST_DOMAIN}",
                    "n_per_domain": MIN_TASKS_PER_DOMAIN,
                    "power_at_holm_corrected_alpha_if_truly_equal": h6_worst_domain_power,
                    "note": (
                        "This gate is noncompensatory and is evaluated once per domain, so the "
                        "chance that at least one domain fails grows with the number of domains "
                        "even when every domain is truly equal."
                    ),
                },
                "not_derivable_without_the_external_inputs": [
                    "H3's absolute false-escalation ceiling, which is defined against blinded obstruction gold that does not exist yet",
                    "H4, which is a certificate conjunction requiring two independently witnessed cases rather than a statistic",
                ],
                "checks": checks,
                "all_checks_pass": all(checks.values()),
            },
            indent=2,
        )
    )
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    sys.exit(main())
