from __future__ import annotations

from types import SimpleNamespace

from orion.core.search import SearchRouteKind
from orion.core.solution import SolutionStatus
from orion.kernel.store import EntryKind, LedgerStore
from orion.knowledge.providers.arxiv import TransportResponse
from orion.knowledge.research_loop import RouteBinding
from orion.knowledge.searchers import LocalCorpusSearcher, build_arxiv_searcher
from orion.knowledge.space import Claim, KnowledgeSpace
from orion.self_orion.development_driver import (
    DevelopmentKnowledgeClass,
    EmpiricalWorkItem,
)
from orion.self_orion.knowledge_runtime import ShadowKnowledgeRuntime
from orion.self_orion.research_loop import ShadowSelfOrionResearchLoop


class _Driver:
    def plan_empirical_work(self, *, limit):
        return (
            EmpiricalWorkItem(
                "empirical:SEARCH.QUERY.v0:0",
                "SEARCH.QUERY.v0",
                "fresh ORION conformance on hidden retrieval tasks",
                DevelopmentKnowledgeClass.LIVE_EVIDENCE,
                8,
                "needs evidence",
            ),
        )[:limit]


class _Runtime:
    def solve(self, problem, *, variation_signature, evaluation_epoch_id, split_id):
        assert problem.problem_id.startswith("self-orion:")
        assert variation_signature[0] == "self-orion-shadow"
        return SimpleNamespace(
            solution=SimpleNamespace(
                status=SolutionStatus.CANNOT_CHECK,
                evidence_ids=("evidence:runtime",),
                residual_ids=("external-evaluator-needed",),
            ),
            experience_episode_id="episode:root",
            mechanic_experience_episode_ids=("episode:mechanic",),
        )


def _arxiv_response(_: str) -> TransportResponse:
    return TransportResponse(
        status=200,
        body="""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom' xmlns:arxiv='http://arxiv.org/schemas/atom'>
  <entry>
    <id>http://arxiv.org/abs/2608.12345v1</id>
    <title>Fresh hidden retrieval conformance evidence</title>
    <summary>Independent evaluation of retrieval coverage and failure modes.</summary>
    <published>2026-08-01T00:00:00Z</published>
    <updated>2026-08-01T00:00:00Z</updated>
    <author><name>Example Author</name></author>
    <arxiv:primary_category term='cs.IR'/>
  </entry>
</feed>""",
        headers={},
    )


def test_shadow_self_orion_reaches_previously_unwired_knowledge_stack(tmp_path):
    local_root = tmp_path / "local"
    local_root.mkdir()
    (local_root / "discipline.md").write_text(
        "# Canonical empirical discipline\n\n"
        "A canonical treatment of empirical_open in an established discipline "
        "must expose failure modes and evidence boundaries.\n"
    )

    local = LocalCorpusSearcher(local_root)
    now = [0.0]
    arxiv = build_arxiv_searcher(
        transport=_arxiv_response,
        clock=lambda: now[0],
        max_results=5,
    )
    bindings = (
        RouteBinding(
            SearchRouteKind.PARENT_DISCIPLINE,
            "local-corpus",
            "parent-discipline-local-v1",
            local,
        ),
        RouteBinding(
            SearchRouteKind.FRESHNESS,
            "arxiv",
            "freshness-arxiv-v1",
            arxiv,
        ),
    )

    space = KnowledgeSpace()
    claim = space.add_claim(
        Claim(
            text="fresh ORION hidden retrieval tasks require independent conformance evidence",
            evidence_digests=frozenset({"digest:one"}),
            source_ids=frozenset({"source:a", "source:b"}),
        )
    )
    store = LedgerStore(tmp_path / "ledger")
    knowledge = ShadowKnowledgeRuntime(
        store=store,
        bindings=bindings,
        declared_routes=(
            SearchRouteKind.PARENT_DISCIPLINE,
            SearchRouteKind.FRESHNESS,
        ),
        space=space,
    )

    result = ShadowSelfOrionResearchLoop(
        _Runtime(),
        driver=_Driver(),
        knowledge_runtime=knowledge,
    ).run_next(limit=1)[0]

    # local.py and the rate-gated arXiv provider are now real route backends;
    # research_loop.py sends both through ingest.py before Shadow sees them.
    assert len(result.knowledge_candidate_ids) == 2
    assert result.knowledge_unavailable_routes == ()
    assert result.knowledge_residuals == ()
    assert claim.claim_id in result.knowledge_supporting_claim_ids
    assert result.proposal_only
    assert result.solution_status is SolutionStatus.CANNOT_CHECK

    # rate.py is not a shelved constant table: the live route consumed arXiv's
    # three-second budget and a second immediate request would be refused.
    assert arxiv.gate.wait_seconds("arxiv") == 3.0

    # Durable source/read receipts prove the research path crossed the ingestion
    # boundary instead of returning transient test-only objects.
    assert len(store.entries(EntryKind.SOURCE)) == 2
    assert len(store.entries(EntryKind.READ)) == 2
