"""Shared pytest configuration for the monorepo."""

from __future__ import annotations

import sys
from pathlib import Path


def _add_service_roots_to_path() -> None:
    workspace_root = Path(__file__).resolve().parents[1]
    service_roots = (
        workspace_root / "services" / "todo_service",
        workspace_root / "services" / "attachment_service",
        workspace_root / "services" / "notification_service",
    )

    for service_root in service_roots:
        service_root_str = str(service_root)
        if service_root_str not in sys.path:
            sys.path.insert(0, service_root_str)


_add_service_roots_to_path()
