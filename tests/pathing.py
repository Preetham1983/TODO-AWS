"""Helpers for importing service modules in tests."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def import_service_main(service_name: str):
    """Import a service main module after adding its root to ``sys.path``."""
    workspace_root = Path(__file__).resolve().parents[1]
    service_root = workspace_root / "services" / service_name
    service_root_str = str(service_root)
    if service_root_str not in sys.path:
        sys.path.insert(0, service_root_str)

    module_name = service_name.removesuffix("_service")
    return importlib.import_module(f"src.{module_name}_service.main")
