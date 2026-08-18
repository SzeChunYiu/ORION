"""Cause-confusable pair/triple schema with gold hidden from candidates."""

from __future__ import annotations

from dataclasses import dataclass

from .belief import AuthorityClass
from .licensing import EpistemicAction


class GoldLeakError(RuntimeError):
    """Candidate code touched protected gold."""


@dataclass(frozen=True)
class PublicMemberView:
    """Candidate-facing state.

    Pair/bundle identity and the host's causal-family name are intentionally not
    represented here. They remain on ``CauseConfusableBundle`` in host custody.
    ``member_id`` must be opaque with respect to the protected responsibility.
    """

    member_id: str
    shared_surface_symptoms: tuple[str, ...]
    prompt: str
    observable_resources: tuple[str, ...]
    allowed_probe_ids: tuple[str, ...]
    allowed_intervention_ids: tuple[str, ...] = ()

    def to_payload(self) -> dict:
        return {
            "member_id": self.member_id,
            "shared_surface_symptoms": list(self.shared_surface_symptoms),
            "prompt": self.prompt,
            "observable_resources": list(self.observable_resources),
            "allowed_probe_ids": list(self.allowed_probe_ids),
            "allowed_intervention_ids": list(self.allowed_intervention_ids),
        }


@dataclass(frozen=True)
class ProtectedGold:
    true_stage: AuthorityClass
    warranted_actions: tuple[EpistemicAction, ...]
    forbidden_actions: tuple[EpistemicAction, ...]
    true_coordinate: str = ""


@dataclass(frozen=True)
class World:
    """Host-side instrument. Candidates must not receive this object."""

    gold: ProtectedGold
    probe_reports: dict[str, AuthorityClass | None]
    intervention_directions: dict[str, str]


@dataclass(frozen=True)
class CauseConfusableMember:
    public: PublicMemberView
    world: World


@dataclass(frozen=True)
class CauseConfusableBundle:
    bundle_id: str
    confusable_kind: str
    arity: str
    shared_surface_symptoms: tuple[str, ...]
    members: tuple[CauseConfusableMember, ...]
    gold_hidden_from_candidates: bool = True

    def public_members(self) -> tuple[PublicMemberView, ...]:
        return tuple(member.public for member in self.members)

    def gold_for(self, member_id: str) -> ProtectedGold:
        for member in self.members:
            if member.public.member_id == member_id:
                return member.world.gold
        raise KeyError(member_id)

    def world_for(self, member_id: str) -> World:
        for member in self.members:
            if member.public.member_id == member_id:
                return member.world
        raise KeyError(member_id)


def gold_leak(view: PublicMemberView) -> tuple[str, ...]:
    """Candidate-visible fields/ids that would expose protected structure."""

    payload = view.to_payload()
    leaks: list[str] = []
    forbidden_keys = (
        "true_stage",
        "protected_gold",
        "warranted_actions",
        "true_coordinate",
        "gold",
        "bundle_id",
        "confusable_kind",
    )
    for key in forbidden_keys:
        if key in payload:
            leaks.append(f"field:{key}")
    member_id = view.member_id.lower()
    for token in (
        "evidence",
        "execution",
        "formulation",
        "search-universe",
        "search_universe",
        "retrieval",
        "implementation",
        "environment",
        "measurement",
        "method-basis",
        "method_basis",
    ):
        if token in member_id:
            leaks.append(f"member_id:{token}")
    return tuple(leaks)


def _member(
    *,
    bundle_id: str,
    kind: str,
    symptoms: tuple[str, ...],
    member_id: str,
    prompt: str,
    stage: AuthorityClass,
    warranted: tuple[EpistemicAction, ...],
    probe_reports: dict[str, AuthorityClass | None],
    intervention_directions: dict[str, str],
    resources: tuple[str, ...] = ("trace.jsonl", "environment.log"),
) -> CauseConfusableMember:
    # ``bundle_id`` and ``kind`` are accepted here because the host-side bundle
    # constructor owns them; they are deliberately not copied into the public
    # candidate view.
    _ = (bundle_id, kind)
    public = PublicMemberView(
        member_id=member_id,
        shared_surface_symptoms=symptoms,
        prompt=prompt,
        observable_resources=resources,
        allowed_probe_ids=tuple(probe_reports),
        allowed_intervention_ids=tuple(intervention_directions),
    )
    forbidden = tuple(
        action
        for action in (
            EpistemicAction.REWRITE_FORMULATION,
            EpistemicAction.EXPAND_SEARCH_UNIVERSE,
            EpistemicAction.BROAD_WM_MUTATION,
            EpistemicAction.REWRITE_METHOD,
        )
        if action not in warranted
    )
    world = World(
        gold=ProtectedGold(
            true_stage=stage,
            warranted_actions=warranted,
            forbidden_actions=forbidden,
        ),
        probe_reports=probe_reports,
        intervention_directions=intervention_directions,
    )
    return CauseConfusableMember(public=public, world=world)


def known_answer_bundles() -> tuple[CauseConfusableBundle, ...]:
    """Constructed pairs/triples for unit tests. Not the prospective holdout."""

    retrieval_symptoms = (
        "required source not in working set",
        "lookup returns empty",
    )
    retrieval = CauseConfusableBundle(
        bundle_id="pair-retrieval-vs-search",
        confusable_kind="retrieval_miss_vs_search_universe_miss",
        arity="pair",
        shared_surface_symptoms=retrieval_symptoms,
        members=(
            _member(
                bundle_id="pair-retrieval-vs-search",
                kind="retrieval_miss_vs_search_universe_miss",
                symptoms=retrieval_symptoms,
                member_id="p1cr-ka-001",
                prompt="The cited table is missing from the working corpus.",
                stage=AuthorityClass.EVIDENCE,
                warranted=(EpistemicAction.ACQUIRE_EVIDENCE,),
                probe_reports={
                    "omitted_source_retrieval": AuthorityClass.EVIDENCE,
                    "blind_control": None,
                },
                intervention_directions={
                    "acquire_omitted_source": "appear",
                    "expand_active_domains": "vanish",
                },
            ),
            _member(
                bundle_id="pair-retrieval-vs-search",
                kind="retrieval_miss_vs_search_universe_miss",
                symptoms=retrieval_symptoms,
                member_id="p1cr-ka-002",
                prompt="The cited table is missing from the working corpus.",
                stage=AuthorityClass.SEARCH_UNIVERSE,
                warranted=(
                    EpistemicAction.EXPAND_SEARCH_UNIVERSE,
                    EpistemicAction.REOPEN_DEPENDENCIES,
                ),
                probe_reports={
                    "omitted_source_retrieval": AuthorityClass.SEARCH_UNIVERSE,
                    "blind_control": None,
                },
                intervention_directions={
                    "acquire_omitted_source": "vanish",
                    "expand_active_domains": "appear",
                },
            ),
        ),
    )
    exec_symptoms = ("rerun disagrees with the logged result",)
    execution = CauseConfusableBundle(
        bundle_id="pair-implementation-vs-environment",
        confusable_kind="implementation_failure_vs_environment_tool_failure",
        arity="pair",
        shared_surface_symptoms=exec_symptoms,
        members=(
            _member(
                bundle_id="pair-implementation-vs-environment",
                kind="implementation_failure_vs_environment_tool_failure",
                symptoms=exec_symptoms,
                member_id="p1cr-ka-003",
                prompt="The solver output does not match the frozen fixture.",
                stage=AuthorityClass.FORMULATION,
                warranted=(
                    EpistemicAction.REWRITE_FORMULATION,
                    EpistemicAction.REOPEN_DEPENDENCIES,
                ),
                probe_reports={
                    "environment_sanity": AuthorityClass.FORMULATION,
                    "blind_control": None,
                },
                intervention_directions={
                    "repair_tooling": "vanish",
                    "rewrite_implicated_coordinate": "appear",
                },
            ),
            _member(
                bundle_id="pair-implementation-vs-environment",
                kind="implementation_failure_vs_environment_tool_failure",
                symptoms=exec_symptoms,
                member_id="p1cr-ka-004",
                prompt="The solver output does not match the frozen fixture.",
                stage=AuthorityClass.EXECUTION,
                warranted=(EpistemicAction.REPAIR_EXECUTION,),
                probe_reports={
                    "environment_sanity": AuthorityClass.EXECUTION,
                    "blind_control": None,
                },
                intervention_directions={
                    "repair_tooling": "appear",
                    "rewrite_implicated_coordinate": "vanish",
                },
            ),
        ),
    )
    return (retrieval, execution)
