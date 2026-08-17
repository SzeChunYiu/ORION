from __future__ import annotations

from dataclasses import dataclass
from math import log2
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ResponsibilityHypothesis:
    name: str
    prior: float


@dataclass(frozen=True)
class DiagnosticProbe:
    probe_id: str
    positive_probability: Mapping[str, float]
    cost: float = 0.0
    risk: float = 0.0

    def __post_init__(self) -> None:
        if self.cost < 0 or self.risk < 0:
            raise ValueError("cost and risk must be non-negative")
        for probability in self.positive_probability.values():
            if not 0.0 <= probability <= 1.0:
                raise ValueError("probe probabilities must lie in [0,1]")


def _entropy(distribution: Mapping[str, float]) -> float:
    return -sum(p * log2(p) for p in distribution.values() if p > 0)


class ResponsibilityDiagnoser:
    """Checks diagnosability before assigning epistemic responsibility.

    The mechanism is deliberately separate from recovery: a diagnosis can license a
    later mutation, but probes and posteriors themselves never mutate the formulation.
    """

    def __init__(
        self,
        hypotheses: Sequence[ResponsibilityHypothesis],
        *,
        cost_weight: float = 0.0,
        risk_weight: float = 0.0,
    ) -> None:
        if len(hypotheses) < 2:
            raise ValueError("at least two responsibility hypotheses are required")
        if cost_weight < 0 or risk_weight < 0:
            raise ValueError("weights must be non-negative")
        total = sum(h.prior for h in hypotheses)
        if total <= 0:
            raise ValueError("priors must have positive total mass")
        self.posterior = {h.name: h.prior / total for h in hypotheses}
        self.cost_weight = cost_weight
        self.risk_weight = risk_weight

    def information_gain(self, probe: DiagnosticProbe) -> float:
        missing = set(self.posterior) - set(probe.positive_probability)
        if missing:
            raise ValueError(f"probe {probe.probe_id} omits hypotheses: {sorted(missing)}")
        current = _entropy(self.posterior)
        p_positive = sum(
            self.posterior[h] * probe.positive_probability[h] for h in self.posterior
        )
        expected_entropy = 0.0
        for positive, p_outcome in ((True, p_positive), (False, 1.0 - p_positive)):
            if p_outcome <= 0:
                continue
            conditioned = {}
            for name, prior in self.posterior.items():
                likelihood = probe.positive_probability[name]
                likelihood = likelihood if positive else 1.0 - likelihood
                conditioned[name] = prior * likelihood / p_outcome
            expected_entropy += p_outcome * _entropy(conditioned)
        return current - expected_entropy

    def diagnosable(self, probes: Sequence[DiagnosticProbe], tolerance: float = 1e-12) -> bool:
        return any(self.information_gain(probe) > tolerance for probe in probes)

    def choose_probe(self, probes: Sequence[DiagnosticProbe]) -> DiagnosticProbe | None:
        scored = []
        for probe in probes:
            gain = self.information_gain(probe)
            utility = gain - self.cost_weight * probe.cost - self.risk_weight * probe.risk
            scored.append((utility, gain, probe.probe_id, probe))
        if not scored:
            return None
        utility, gain, _, probe = max(scored, key=lambda item: (item[0], item[1], item[2]))
        if gain <= 1e-12 or utility <= 0:
            return None
        return probe

    def observe(self, probe: DiagnosticProbe, *, positive: bool) -> None:
        normalizer = 0.0
        unnormalized: dict[str, float] = {}
        for name, prior in self.posterior.items():
            likelihood = probe.positive_probability[name]
            likelihood = likelihood if positive else 1.0 - likelihood
            value = prior * likelihood
            unnormalized[name] = value
            normalizer += value
        if normalizer <= 0:
            raise ValueError("observation has zero probability under every hypothesis")
        self.posterior = {name: value / normalizer for name, value in unnormalized.items()}

    def best_hypothesis(self) -> tuple[str, float]:
        return max(self.posterior.items(), key=lambda item: (item[1], item[0]))

    def licenses(self, allowed_responsibilities: set[str], *, threshold: float = 0.8) -> bool:
        if not 0.5 <= threshold <= 1.0:
            raise ValueError("threshold must be in [0.5,1]")
        name, probability = self.best_hypothesis()
        return name in allowed_responsibilities and probability >= threshold
