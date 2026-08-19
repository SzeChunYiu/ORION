"""Finite, non-authorizing closure checks for discovery morphology issue #506.

The checker validates a frozen, source-bounded historical atlas and a frozen
cross-domain descriptive morphology.  It deliberately does *not* reconstruct
private cognition, infer causal necessity from historical presence, execute a
Jump, or treat famous historical episodes as protected benchmark gold.

The terminal ``USEFUL_MORPHOLOGY_BASIS_FOUND`` therefore means only that the
registered public-artifact morphology is stable enough to organize future
bounded/prospective studies at this resolution.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest


class DiscoveryMorphologyTerminal(str, Enum):
    USEFUL_MORPHOLOGY_BASIS_FOUND = "USEFUL_MORPHOLOGY_BASIS_FOUND"
    CANNOT_CHECK = "CANNOT_CHECK"


_ALLOWED_DOMAINS = (
    "MATHEMATICS_FORMAL",
    "SCIENCE",
    "ENGINEERING_DESIGN",
    "EVERYDAY_PRACTICAL",
)

_REQUIRED_EPISODE_SOURCE_PREFIX = "PRIMARY_"
_REQUIRED_PRIVATE_COGNITION = "CANNOT_INFER"
_REQUIRED_MORPHOLOGY_ROLE = "STRUCTURAL_INTERPRETATION"
_REQUIRED_HISTORICAL_USE = "MECHANISM_EXTRACTION_ONLY"
_FIXED_REGIME_CONTROL = "FIXED_REGIME_SEARCH_CONTROL"


@dataclass(frozen=True)
class DiscoveryMorphologyClosureReport:
    episode_count: int
    domain_counts: tuple[tuple[str, int], ...]
    no_jump_control_count: int
    dimension_count: int
    dimension_episode_support: tuple[tuple[str, int], ...]
    dimension_domain_support: tuple[tuple[str, int], ...]
    all_four_domain_dimension_ids: tuple[str, ...]
    malformed_episode_ids: tuple[str, ...]
    unknown_dimension_ids: tuple[str, ...]
    basis_support_mismatch_ids: tuple[str, ...]
    invalid_no_jump_control_ids: tuple[str, ...]
    post_basis_round_count: int
    post_basis_primary_source_count: int
    material_change_round_ids: tuple[str, ...]
    saturation_unknown_dimension_ids: tuple[str, ...]
    terminal: DiscoveryMorphologyTerminal
    all_checks_passed: bool
    digest: str

    @property
    def grants_historical_cognition_authority(self) -> bool:
        return False

    @property
    def grants_atom_independence_authority(self) -> bool:
        return False

    @property
    def grants_jump_authority(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_protected_benchmark_authority(self) -> bool:
        return False

    @property
    def grants_issue_closure_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "DiscoveryMorphologyClosureReport.v1",
            "episode_count": self.episode_count,
            "domain_counts": [list(item) for item in self.domain_counts],
            "no_jump_control_count": self.no_jump_control_count,
            "dimension_count": self.dimension_count,
            "dimension_episode_support": [
                list(item) for item in self.dimension_episode_support
            ],
            "dimension_domain_support": [
                list(item) for item in self.dimension_domain_support
            ],
            "all_four_domain_dimension_ids": list(self.all_four_domain_dimension_ids),
            "malformed_episode_ids": list(self.malformed_episode_ids),
            "unknown_dimension_ids": list(self.unknown_dimension_ids),
            "basis_support_mismatch_ids": list(self.basis_support_mismatch_ids),
            "invalid_no_jump_control_ids": list(self.invalid_no_jump_control_ids),
            "post_basis_round_count": self.post_basis_round_count,
            "post_basis_primary_source_count": self.post_basis_primary_source_count,
            "material_change_round_ids": list(self.material_change_round_ids),
            "saturation_unknown_dimension_ids": list(
                self.saturation_unknown_dimension_ids
            ),
            "terminal": self.terminal.value,
            "all_checks_passed": self.all_checks_passed,
            "grants_historical_cognition_authority": False,
            "grants_atom_independence_authority": False,
            "grants_jump_authority": False,
            "grants_novelty_authority": False,
            "grants_protected_benchmark_authority": False,
            "grants_issue_closure_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("discovery morphology closure digest mismatch")


def _require_mapping(value: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _require_sequence(value: object, *, label: str) -> Sequence[object]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{label} must be an array")
    return value


def _basis_dimensions(
    basis: Mapping[str, object],
) -> tuple[tuple[str, ...], dict[str, Mapping[str, object]]]:
    raw_dimensions = _require_sequence(basis.get("dimensions", ()), label="basis dimensions")
    by_id: dict[str, Mapping[str, object]] = {}
    for raw in raw_dimensions:
        row = _require_mapping(raw, label="basis dimension")
        dimension_id = str(row.get("id", ""))
        if not dimension_id:
            raise ValueError("basis dimension id is required")
        if dimension_id in by_id:
            raise ValueError(f"duplicate basis dimension: {dimension_id}")
        if not str(row.get("definition", "")):
            raise ValueError(f"basis dimension lacks definition: {dimension_id}")
        if not str(row.get("explicit_nondefinition", "")):
            raise ValueError(f"basis dimension lacks nondefinition: {dimension_id}")
        parents = _require_sequence(
            row.get("strong_parent_owners", ()),
            label=f"strong parent owners for {dimension_id}",
        )
        if not parents or any(not str(parent) for parent in parents):
            raise ValueError(f"basis dimension lacks strong parents: {dimension_id}")
        by_id[dimension_id] = row
    return tuple(sorted(by_id)), by_id


def _analyze_atlas(
    atlas: Mapping[str, object],
    *,
    registered_dimension_ids: set[str],
    minimum_competing_interpretations: int,
) -> tuple[
    int,
    Counter[str],
    int,
    Counter[str],
    dict[str, set[str]],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    raw_episodes = _require_sequence(atlas.get("episodes", ()), label="atlas episodes")
    seen_episode_ids: set[str] = set()
    domain_counts: Counter[str] = Counter()
    dimension_counts: Counter[str] = Counter()
    dimension_domains: dict[str, set[str]] = defaultdict(set)
    malformed: list[str] = []
    unknown_dimensions: set[str] = set()
    invalid_controls: list[str] = []
    no_jump_controls = 0

    for index, raw in enumerate(raw_episodes):
        row = _require_mapping(raw, label=f"atlas episode {index}")
        episode_id = str(row.get("episode_id", "")) or f"<episode-{index}>"
        if episode_id in seen_episode_ids:
            raise ValueError(f"duplicate atlas episode: {episode_id}")
        seen_episode_ids.add(episode_id)

        domain = str(row.get("domain_bucket", ""))
        source_kind = str(row.get("source_kind", ""))
        source_locator = str(row.get("source_locator", ""))
        documented_claim = str(row.get("documented_artifact_claim", ""))
        private_cognition = str(row.get("private_cognitive_sequence", ""))
        morphology_role = str(row.get("structural_interpretation_role", ""))
        historical_use = str(row.get("historical_use", ""))
        protected_gold = row.get("protected_confirmatory_gold")
        jump_status = str(row.get("jump_status", ""))

        raw_tags = _require_sequence(
            row.get("candidate_morphology_ids", ()),
            label=f"morphology ids for {episode_id}",
        )
        tags = tuple(str(tag) for tag in raw_tags)
        raw_interpretations = _require_sequence(
            row.get("competing_interpretations", ()),
            label=f"competing interpretations for {episode_id}",
        )
        interpretations = tuple(str(item) for item in raw_interpretations)

        episode_bad = False
        if domain not in _ALLOWED_DOMAINS:
            episode_bad = True
        else:
            domain_counts[domain] += 1
        if not source_kind.startswith(_REQUIRED_EPISODE_SOURCE_PREFIX):
            episode_bad = True
        if not source_locator or not documented_claim:
            episode_bad = True
        if private_cognition != _REQUIRED_PRIVATE_COGNITION:
            episode_bad = True
        if morphology_role != _REQUIRED_MORPHOLOGY_ROLE:
            episode_bad = True
        if historical_use != _REQUIRED_HISTORICAL_USE:
            episode_bad = True
        if protected_gold is not False:
            episode_bad = True
        if not tags or len(tags) != len(set(tags)):
            episode_bad = True
        if (
            len(interpretations) < minimum_competing_interpretations
            or len(set(interpretations)) < minimum_competing_interpretations
            or any(not item for item in interpretations)
        ):
            episode_bad = True

        for tag in tags:
            if tag not in registered_dimension_ids:
                unknown_dimensions.add(tag)
                episode_bad = True
                continue
            dimension_counts[tag] += 1
            if domain in _ALLOWED_DOMAINS:
                dimension_domains[tag].add(domain)

        if jump_status == "NO_JUMP_CONTROL":
            no_jump_controls += 1
            if _FIXED_REGIME_CONTROL not in tags:
                invalid_controls.append(episode_id)
                episode_bad = True

        if episode_bad:
            malformed.append(episode_id)

    return (
        len(raw_episodes),
        domain_counts,
        no_jump_controls,
        dimension_counts,
        dimension_domains,
        tuple(sorted(set(malformed))),
        tuple(sorted(unknown_dimensions)),
        tuple(sorted(set(invalid_controls))),
    )


def _basis_support_mismatches(
    basis_by_id: Mapping[str, Mapping[str, object]],
    *,
    dimension_counts: Mapping[str, int],
    dimension_domains: Mapping[str, set[str]],
) -> tuple[str, ...]:
    mismatches: list[str] = []
    for dimension_id, row in basis_by_id.items():
        frozen_count = int(row.get("frozen_episode_support", -1))
        raw_domains = _require_sequence(
            row.get("frozen_domain_buckets", ()),
            label=f"frozen domains for {dimension_id}",
        )
        frozen_domains = {str(item) for item in raw_domains}
        if frozen_count != int(dimension_counts.get(dimension_id, 0)):
            mismatches.append(dimension_id)
            continue
        if frozen_domains != set(dimension_domains.get(dimension_id, set())):
            mismatches.append(dimension_id)
    return tuple(sorted(set(mismatches)))


def _analyze_saturation(
    saturation: Mapping[str, object],
    *,
    registered_dimension_ids: set[str],
) -> tuple[int, int, tuple[str, ...], tuple[str, ...]]:
    raw_rounds = _require_sequence(
        saturation.get("rounds", ()),
        label="saturation rounds",
    )
    seen_round_ids: set[str] = set()
    material_change_round_ids: list[str] = []
    unknown_dimensions: set[str] = set()
    primary_source_count = 0

    for index, raw in enumerate(raw_rounds):
        row = _require_mapping(raw, label=f"saturation round {index}")
        round_id = str(row.get("round_id", ""))
        if not round_id or round_id in seen_round_ids:
            raise ValueError("saturation round ids must be unique and non-empty")
        seen_round_ids.add(round_id)
        if row.get("material_change") is True:
            material_change_round_ids.append(round_id)
        if str(row.get("result", "")) != "NO_MATERIAL_CHANGE":
            material_change_round_ids.append(round_id)
        raw_sources = _require_sequence(
            row.get("primary_sources", ()),
            label=f"primary sources for {round_id}",
        )
        if not raw_sources:
            raise ValueError(f"saturation round has no primary sources: {round_id}")
        primary_source_count += len(raw_sources)
        for raw_source in raw_sources:
            source = _require_mapping(raw_source, label=f"source in {round_id}")
            if not str(source.get("source_id", "")) or not str(source.get("locator", "")):
                raise ValueError(f"saturation source lacks identity/locator in {round_id}")
            mapped = _require_sequence(
                source.get("mapped_dimensions", ()),
                label=f"mapped dimensions in {round_id}",
            )
            if not mapped:
                raise ValueError(f"saturation source has no mapped dimensions in {round_id}")
            for dimension_id in (str(item) for item in mapped):
                if dimension_id not in registered_dimension_ids:
                    unknown_dimensions.add(dimension_id)
        raw_new = _require_sequence(
            row.get("new_dimension_ids", ()),
            label=f"new dimensions in {round_id}",
        )
        if raw_new:
            material_change_round_ids.append(round_id)

    return (
        len(raw_rounds),
        primary_source_count,
        tuple(sorted(set(material_change_round_ids))),
        tuple(sorted(unknown_dimensions)),
    )


def build_discovery_morphology_closure_report(
    *,
    atlas: Mapping[str, object],
    basis: Mapping[str, object],
    saturation: Mapping[str, object],
    expected: Mapping[str, object],
) -> DiscoveryMorphologyClosureReport:
    """Validate the pre-frozen #506 corpus/basis/saturation packet."""

    dimension_ids, basis_by_id = _basis_dimensions(basis)
    registered_dimensions = set(dimension_ids)

    expected_atlas = _require_mapping(expected.get("atlas", {}), label="expected atlas")
    expected_basis = _require_mapping(expected.get("basis", {}), label="expected basis")
    expected_saturation = _require_mapping(
        expected.get("post_basis_saturation", {}),
        label="expected saturation",
    )
    minimum_competing = int(
        expected_atlas.get("minimum_competing_interpretations_per_episode", 2)
    )

    (
        episode_count,
        domain_counts,
        no_jump_controls,
        dimension_counts,
        dimension_domains,
        malformed,
        unknown_dimensions,
        invalid_controls,
    ) = _analyze_atlas(
        atlas,
        registered_dimension_ids=registered_dimensions,
        minimum_competing_interpretations=minimum_competing,
    )

    support_mismatches = _basis_support_mismatches(
        basis_by_id,
        dimension_counts=dimension_counts,
        dimension_domains=dimension_domains,
    )

    (
        saturation_round_count,
        saturation_source_count,
        material_change_round_ids,
        saturation_unknown_dimensions,
    ) = _analyze_saturation(
        saturation,
        registered_dimension_ids=registered_dimensions,
    )

    expected_domain_counts = {
        str(key): int(value)
        for key, value in _require_mapping(
            expected_atlas.get("domain_counts", {}),
            label="expected domain counts",
        ).items()
    }
    expected_support = {
        str(key): int(value)
        for key, value in _require_mapping(
            expected_basis.get("dimension_episode_support", {}),
            label="expected dimension support",
        ).items()
    }

    dimension_episode_support = tuple(
        sorted((dimension_id, int(dimension_counts.get(dimension_id, 0))) for dimension_id in dimension_ids)
    )
    dimension_domain_support = tuple(
        sorted((dimension_id, len(dimension_domains.get(dimension_id, set()))) for dimension_id in dimension_ids)
    )
    all_four = tuple(
        sorted(
            dimension_id
            for dimension_id in dimension_ids
            if set(dimension_domains.get(dimension_id, set())) == set(_ALLOWED_DOMAINS)
        )
    )

    minimum_episode_support = int(
        expected_basis.get("minimum_episode_support_per_dimension", 0)
    )
    minimum_domain_support = int(
        expected_basis.get("minimum_domain_support_per_dimension", 0)
    )
    minimum_all_four = int(
        expected_basis.get("minimum_dimensions_spanning_all_four_domains", 0)
    )

    all_checks_passed = (
        str(atlas.get("version", "")) == "DiscoveryMorphologyAtlas.v1"
        and str(basis.get("version", "")) == "DiscoveryMorphologyBasis.v1"
        and str(saturation.get("version", "")) == "DiscoveryMorphologySaturation.v1"
        and bool(saturation.get("basis_frozen_before_rounds")) is True
        and episode_count == int(expected_atlas.get("episodes", -1))
        and dict(domain_counts) == expected_domain_counts
        and no_jump_controls == int(expected_atlas.get("no_jump_controls", -1))
        and len(dimension_ids) == int(expected_basis.get("dimensions", -1))
        and dict(dimension_episode_support) == expected_support
        and all(count >= minimum_episode_support for _, count in dimension_episode_support)
        and all(count >= minimum_domain_support for _, count in dimension_domain_support)
        and len(all_four) >= minimum_all_four
        and not malformed
        and not unknown_dimensions
        and not support_mismatches
        and not invalid_controls
        and saturation_round_count == int(expected_saturation.get("rounds", -1))
        and saturation_source_count == int(expected_saturation.get("primary_sources", -1))
        and len(material_change_round_ids) == int(
            expected_saturation.get("material_change_rounds", -1)
        )
        and not saturation_unknown_dimensions
        and str(basis.get("candidate_terminal", ""))
        == str(expected.get("candidate_terminal", ""))
        == DiscoveryMorphologyTerminal.USEFUL_MORPHOLOGY_BASIS_FOUND.value
    )

    terminal = (
        DiscoveryMorphologyTerminal.USEFUL_MORPHOLOGY_BASIS_FOUND
        if all_checks_passed
        else DiscoveryMorphologyTerminal.CANNOT_CHECK
    )

    payload = {
        "version": "DiscoveryMorphologyClosureReport.v1",
        "episode_count": episode_count,
        "domain_counts": [list(item) for item in sorted(domain_counts.items())],
        "no_jump_control_count": no_jump_controls,
        "dimension_count": len(dimension_ids),
        "dimension_episode_support": [list(item) for item in dimension_episode_support],
        "dimension_domain_support": [list(item) for item in dimension_domain_support],
        "all_four_domain_dimension_ids": list(all_four),
        "malformed_episode_ids": list(malformed),
        "unknown_dimension_ids": list(unknown_dimensions),
        "basis_support_mismatch_ids": list(support_mismatches),
        "invalid_no_jump_control_ids": list(invalid_controls),
        "post_basis_round_count": saturation_round_count,
        "post_basis_primary_source_count": saturation_source_count,
        "material_change_round_ids": list(material_change_round_ids),
        "saturation_unknown_dimension_ids": list(saturation_unknown_dimensions),
        "terminal": terminal.value,
        "all_checks_passed": all_checks_passed,
        "grants_historical_cognition_authority": False,
        "grants_atom_independence_authority": False,
        "grants_jump_authority": False,
        "grants_novelty_authority": False,
        "grants_protected_benchmark_authority": False,
        "grants_issue_closure_authority": False,
    }
    report = DiscoveryMorphologyClosureReport(
        episode_count=payload["episode_count"],
        domain_counts=tuple(tuple(item) for item in payload["domain_counts"]),
        no_jump_control_count=payload["no_jump_control_count"],
        dimension_count=payload["dimension_count"],
        dimension_episode_support=tuple(
            tuple(item) for item in payload["dimension_episode_support"]
        ),
        dimension_domain_support=tuple(
            tuple(item) for item in payload["dimension_domain_support"]
        ),
        all_four_domain_dimension_ids=tuple(payload["all_four_domain_dimension_ids"]),
        malformed_episode_ids=tuple(payload["malformed_episode_ids"]),
        unknown_dimension_ids=tuple(payload["unknown_dimension_ids"]),
        basis_support_mismatch_ids=tuple(payload["basis_support_mismatch_ids"]),
        invalid_no_jump_control_ids=tuple(payload["invalid_no_jump_control_ids"]),
        post_basis_round_count=payload["post_basis_round_count"],
        post_basis_primary_source_count=payload["post_basis_primary_source_count"],
        material_change_round_ids=tuple(payload["material_change_round_ids"]),
        saturation_unknown_dimension_ids=tuple(
            payload["saturation_unknown_dimension_ids"]
        ),
        terminal=DiscoveryMorphologyTerminal(payload["terminal"]),
        all_checks_passed=payload["all_checks_passed"],
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "DiscoveryMorphologyClosureReport",
    "DiscoveryMorphologyTerminal",
    "build_discovery_morphology_closure_report",
]
