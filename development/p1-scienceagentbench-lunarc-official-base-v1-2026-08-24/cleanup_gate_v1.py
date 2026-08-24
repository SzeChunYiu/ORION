#!/usr/bin/env python3
"""Pure fail-closed cleanup gates for the LUNARC official-base smoke."""

from __future__ import annotations

from typing import Any


def driver_cleanup_passed(
    *,
    adapter_probe_container_removed: bool,
    container_removed: bool,
    built_image_removed: bool,
    base_image_removed: bool,
    remaining_image_ids: list[str],
    cleanup_errors: list[dict[str, str]],
) -> bool:
    return (
        adapter_probe_container_removed
        and container_removed
        and built_image_removed
        and base_image_removed
        and remaining_image_ids == []
        and cleanup_errors == []
    )


def batch_cleanup_passed(
    data: dict[str, Any],
    *,
    driver_rc: int,
    job_root_removed: bool,
    socket_root_removed: bool,
) -> bool:
    cleanup = data.get("cleanup")
    adapter = data.get("rootless_runtime_adapter")
    if not isinstance(cleanup, dict) or not isinstance(adapter, dict):
        return False
    return (
        driver_rc == 0
        and data.get("status") == "PASS"
        and data.get("error") is None
        and adapter.get("singlemap_adapter_probe_container_removed") is True
        and cleanup.get("container_removed") is True
        and cleanup.get("built_image_removed") is True
        and cleanup.get("resolved_base_image_removed") is True
        and cleanup.get("remaining_image_ids") == []
        and cleanup.get("cleanup_errors") == []
        and job_root_removed
        and socket_root_removed
    )
