"""ORION-P5 protected hidden-cause study utilities."""

from .freeze import (
    freeze_protected_suite,
    mint_root_cause_nonce,
    nonce_weakness,
    sha256_json,
    validate_protected_suite,
)
from .negative_history_chain import (
    build_negative_history_chain,
    validate_result_archive_with_negative_history,
    verify_negative_history_chain,
)
from .v2_evidence import (
    content_digest,
    result_archive_digest,
    run_manifest_digest,
    validate_result_archive,
    validate_run_manifest,
)

__all__ = [
    "build_negative_history_chain",
    "content_digest",
    "freeze_protected_suite",
    "mint_root_cause_nonce",
    "nonce_weakness",
    "result_archive_digest",
    "run_manifest_digest",
    "sha256_json",
    "validate_protected_suite",
    "validate_result_archive",
    "validate_result_archive_with_negative_history",
    "validate_run_manifest",
    "verify_negative_history_chain",
]
