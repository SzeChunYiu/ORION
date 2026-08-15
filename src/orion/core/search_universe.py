from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class SearchUniverseState:
    """W_t: ORION's current model of what knowledge may be relevant."""

    active_domain_ids: tuple[str, ...] = ()
    candidate_domain_ids: tuple[str, ...] = ()
    searched_domain_ids: tuple[str, ...] = ()
    route_ids: tuple[str, ...] = ()
    route_kind_ids: tuple[str, ...] = ()
    representation_ids: tuple[str, ...] = ()
    open_coverage_residual_ids: tuple[str, ...] = ()

    def add_candidates(self, domain_ids: tuple[str, ...]) -> "SearchUniverseState":
        return replace(self, candidate_domain_ids=_union(self.candidate_domain_ids, domain_ids))

    def activate_domains(self, domain_ids: tuple[str, ...]) -> "SearchUniverseState":
        return replace(self, active_domain_ids=_union(self.active_domain_ids, domain_ids))

    def mark_searched(
        self,
        domain_ids: tuple[str, ...],
        route_ids: tuple[str, ...],
        route_kind_ids: tuple[str, ...],
    ) -> "SearchUniverseState":
        return replace(
            self,
            searched_domain_ids=_union(self.searched_domain_ids, domain_ids),
            route_ids=_union(self.route_ids, route_ids),
            route_kind_ids=_union(self.route_kind_ids, route_kind_ids),
        )

    def add_representations(self, representation_ids: tuple[str, ...]) -> "SearchUniverseState":
        return replace(self, representation_ids=_union(self.representation_ids, representation_ids))


def _union(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*left, *right)))
