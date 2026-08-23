import json

import pytest

from orion.providers.llm.accounting import AccountingLLMProvider
from orion.providers.llm.base import LLMRequest, LLMResponse


class _LLM:
    def __init__(self, *, fail=False):
        self.fail = fail

    def complete(self, request):
        if self.fail:
            raise RuntimeError("provider failed")
        return LLMResponse(content='{"ok":true}', model_id="model", response_id="response")


def _request(problem_id="task:one"):
    return LLMRequest(
        task="interpret",
        system="system",
        user=json.dumps({"problem": {"problem_id": problem_id}}),
    )


def test_accounting_llm_counts_completed_calls_by_problem_id():
    provider = AccountingLLMProvider(_LLM())
    provider.complete(_request("task:one"))
    provider.complete(_request("task:one"))
    provider.complete(_request("task:two"))
    assert provider.attempted_calls_for_problem("task:one") == 2
    assert provider.attempted_calls_for_problem("task:two") == 1
    assert all(item.completed for item in provider.observations())


def test_accounting_llm_counts_failed_attempts_without_inventing_completion():
    provider = AccountingLLMProvider(_LLM(fail=True))
    with pytest.raises(RuntimeError, match="provider failed"):
        provider.complete(_request("task:failure"))
    assert provider.attempted_calls_for_problem("task:failure") == 1
    assert provider.observations()[0].completed is False


def test_accounting_llm_leaves_non_reasoner_prompt_unbound():
    provider = AccountingLLMProvider(_LLM())
    provider.complete(LLMRequest(task="other", system="system", user="not-json"))
    assert provider.attempted_calls_for_problem("task:one") == 0
    assert provider.observations()[0].problem_id == ""
