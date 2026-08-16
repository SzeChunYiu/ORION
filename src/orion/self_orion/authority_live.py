from __future__ import annotations

import os

from orion.self_orion.authority_http import (
    ProtectedAuthorityEvaluatorHTTPConfig,
    ProtectedAuthorityExecutorHTTPConfig,
    ProtectedAuthorityHTTPEvaluator,
    ProtectedAuthorityHTTPExecutor,
)
from orion.self_orion.authority_trial import AuthorityTrialBinding, AuthorityTrialRunner


def build_live_authority_trial_runner(
    *,
    binding: AuthorityTrialBinding,
    executor_endpoint: str,
    executor_token: str,
    executor_artifact_hash: str,
    evaluator_endpoint: str,
    evaluator_token: str,
) -> AuthorityTrialRunner:
    executor = ProtectedAuthorityHTTPExecutor(
        ProtectedAuthorityExecutorHTTPConfig(
            endpoint=executor_endpoint,
            bearer_token=executor_token,
            executor_artifact_hash=executor_artifact_hash,
        )
    )
    evaluator = ProtectedAuthorityHTTPEvaluator(
        ProtectedAuthorityEvaluatorHTTPConfig(
            endpoint=evaluator_endpoint,
            bearer_token=evaluator_token,
            evaluator_artifact_hash=binding.evaluator_artifact_hash,
            evaluation_epoch_id=binding.evaluation_epoch_id,
        )
    )
    return AuthorityTrialRunner(executor=executor, evaluator=evaluator)


def build_live_authority_trial_runner_from_env(
    *,
    binding: AuthorityTrialBinding,
    executor_endpoint_env: str = "ORION_AUTHORITY_ATTACK_EXECUTOR_URL",
    executor_token_env: str = "ORION_AUTHORITY_ATTACK_EXECUTOR_TOKEN",
    executor_artifact_hash_env: str = "ORION_AUTHORITY_ATTACK_EXECUTOR_ARTIFACT_HASH",
    evaluator_endpoint_env: str = "ORION_AUTHORITY_EVALUATOR_URL",
    evaluator_token_env: str = "ORION_AUTHORITY_EVALUATOR_TOKEN",
) -> AuthorityTrialRunner:
    values = {
        executor_endpoint_env: os.environ.get(executor_endpoint_env, ""),
        executor_token_env: os.environ.get(executor_token_env, ""),
        executor_artifact_hash_env: os.environ.get(executor_artifact_hash_env, ""),
        evaluator_endpoint_env: os.environ.get(evaluator_endpoint_env, ""),
        evaluator_token_env: os.environ.get(evaluator_token_env, ""),
    }
    missing = tuple(name for name, value in values.items() if not value)
    if missing:
        raise RuntimeError(
            "missing live authority-trial service configuration: "
            + ",".join(missing)
        )
    return build_live_authority_trial_runner(
        binding=binding,
        executor_endpoint=values[executor_endpoint_env],
        executor_token=values[executor_token_env],
        executor_artifact_hash=values[executor_artifact_hash_env],
        evaluator_endpoint=values[evaluator_endpoint_env],
        evaluator_token=values[evaluator_token_env],
    )


__all__ = [
    "build_live_authority_trial_runner",
    "build_live_authority_trial_runner_from_env",
]
