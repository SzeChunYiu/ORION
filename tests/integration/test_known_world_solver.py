from orion.core.contributions import AssimilationOutcome, KnowledgeContribution
from orion.core.problem import Problem
from orion.core.residuals import ResidualKind, Responsibility
from orion.core.search import RetrievedItem, SearchQuery, SearchRouteKind
from orion.core.solution import SolutionStatus
from orion.engine.solver import OrionSolver, SolverConfig
from orion.providers.reasoner.base import Diagnosis, ReframeProposal
from orion.providers.reasoner.scripted import ScriptedReasoner
from orion.providers.retrieval.memory import InMemoryRetrievalProvider
from orion.providers.verification.memory import InMemoryVerificationProvider


def _q(query_id, text, kind, domain=None):
    return SearchQuery(query_id, text, f"route:{query_id}", kind, domain)


def test_solver_discovers_missing_domain_reframes_and_saturates():
    seed = RetrievedItem(
        "e:seed",
        "Meaning-sensitive claim normalization has a mature parent discipline outside the initial research-systems vocabulary.",
        "known://seed",
        ("research-systems",),
    )
    semantics = RetrievedItem(
        "e:semantics",
        "Predicate-argument structure and scope distinctions constrain valid normalization.",
        "known://semantics",
        ("computational-linguistics",),
    )

    first_plan = (
        _q("current", "seed", SearchRouteKind.CURRENT_VOCABULARY, "research-systems"),
        _q("function", "function-only", SearchRouteKind.FUNCTION_ONLY),
        _q("parent", "parent-discipline", SearchRouteKind.PARENT_DISCIPLINE),
        _q("bridge", "literature-bridge", SearchRouteKind.LITERATURE_BRIDGE),
        _q("omission", "omission-challenge", SearchRouteKind.ADVERSARIAL_OMISSION),
        _q("fresh", "freshness", SearchRouteKind.FRESHNESS),
    )
    later_plan = (
        _q("linguistics", "linguistic-semantics", SearchRouteKind.CURRENT_VOCABULARY, "computational-linguistics"),
    )

    reasoner = ScriptedReasoner(
        search_plans=[first_plan, later_plan, later_plan, later_plan],
        contributions_by_item_id={
            "e:seed": KnowledgeContribution(
                "c:seed",
                "Meaning-sensitive normalization requires a linguistic semantics projection.",
                AssimilationOutcome.EXPOSES_SEARCH_UNIVERSE_GAP,
                ("e:seed",),
                discovered_domain_ids=("computational-linguistics",),
            ),
            "e:semantics": KnowledgeContribution(
                "c:semantics",
                "Normalization must preserve predicate-argument structure and relevant scope.",
                AssimilationOutcome.NEW_REPRESENTATION,
                ("e:semantics",),
                representation_ids=("predicate-argument-scope",),
            ),
        },
        diagnoses_by_kind={
            ResidualKind.SEARCH_COVERAGE_FAILURE: Diagnosis(
                (Responsibility.SEARCH,),
                "absorbed knowledge exposed an unsearched parent discipline",
            )
        },
        reframes_by_kind={
            ResidualKind.SEARCH_COVERAGE_FAILURE: ReframeProposal(
                add_domain_ids=("computational-linguistics",),
                note="expand W to the newly discovered parent discipline",
            )
        },
        answer_text="Preserve predicate-argument structure and scope when normalizing claims.",
    )
    retrieval = InMemoryRetrievalProvider(
        {
            "seed": (seed,),
            "linguistic-semantics": (semantics,),
        }
    )
    verifier = InMemoryVerificationProvider(frozenset({"e:seed", "e:semantics"}))
    solver = OrionSolver(
        reasoner=reasoner,
        retrieval=retrieval,
        verification=verifier,
        config=SolverConfig(max_iterations=6),
    )

    solution, state, trace = solver.solve(
        Problem(
            "known-world:domain-reframe",
            "How should ORION normalize scientific claims?",
            initial_domain_ids=("research-systems",),
        )
    )

    assert solution.status is SolutionStatus.SOLVED_VERIFIED
    assert "computational-linguistics" in state.search_universe.active_domain_ids
    assert "computational-linguistics" in state.search_universe.searched_domain_ids
    assert state.knowledge.negative_history
    assert state.iterations[-1].flat and state.iterations[-2].flat
    assert "LITERATURE_BRIDGE" in state.search_universe.route_kind_ids
    assert any(event.operator.value == "REFRAME" for event in trace.events)
    assert any(event.operator.value == "SATURATE_BOUNDED" for event in trace.events)


def test_solver_refuses_final_answer_when_search_basis_not_challenged():
    answer = RetrievedItem("e:answer", "A supported answer.", "known://answer", ("domain",))
    plan = (_q("only", "answer", SearchRouteKind.CURRENT_VOCABULARY, "domain"),)
    reasoner = ScriptedReasoner(
        search_plans=[plan],
        contributions_by_item_id={
            "e:answer": KnowledgeContribution(
                "c:answer",
                "A supported answer.",
                AssimilationOutcome.COMPLEMENTARY_FACET,
                ("e:answer",),
            )
        },
        diagnoses_by_kind={},
        reframes_by_kind={},
        answer_text="A supported answer.",
    )
    solver = OrionSolver(
        reasoner=reasoner,
        retrieval=InMemoryRetrievalProvider({"answer": (answer,)}),
        verification=InMemoryVerificationProvider(frozenset({"e:answer"})),
        config=SolverConfig(max_iterations=4),
    )
    solution, _, _ = solver.solve(Problem("known-world:unsaturated", "What is the answer?", initial_domain_ids=("domain",)))
    assert solution.status is SolutionStatus.CANNOT_CHECK
    assert "independent_route_coverage_incomplete" in solution.answer
