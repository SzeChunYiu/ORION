from __future__ import annotations

from orion.study.p1_causal.causal_context import (
    CausalDependency,
    dual_slice_causal_context,
)


def test_dual_slice_unions_static_semantics_and_executed_trace() -> None:
    context = dual_slice_causal_context(
        failing_ids=("failure",),
        static_dependencies=(
            CausalDependency("spec", "solver", "STATIC"),
            CausalDependency("solver", "failure", "STATIC"),
            CausalDependency("unrelated", "other", "STATIC"),
        ),
        dynamic_dependencies=(
            CausalDependency("tool", "failure", "DYNAMIC"),
            CausalDependency("environment", "tool", "DYNAMIC"),
        ),
    )
    assert context.static_ids == ("failure", "solver", "spec")
    assert context.dynamic_ids == ("environment", "failure", "tool")
    assert context.included_ids == (
        "environment",
        "failure",
        "solver",
        "spec",
        "tool",
    )
    assert "unrelated" not in context.included_ids


def test_causal_context_is_context_not_authority() -> None:
    context = dual_slice_causal_context(
        failing_ids=("f",),
        static_dependencies=(CausalDependency("a", "f", "STATIC"),),
        dynamic_dependencies=(),
    )
    assert context.included_ids == ("a", "f")
    assert not hasattr(context, "granted")
    assert not hasattr(context, "licensed_actions")


def test_slice_kind_mismatch_is_rejected() -> None:
    try:
        dual_slice_causal_context(
            failing_ids=("f",),
            static_dependencies=(CausalDependency("a", "f", "DYNAMIC"),),
            dynamic_dependencies=(),
        )
    except ValueError as exc:
        assert "static slice contains non-static edge" in str(exc)
    else:
        raise AssertionError("mis-typed dependency slice must fail closed")
