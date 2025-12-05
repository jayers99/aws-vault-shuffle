#!/usr/bin/env python3
"""Application layer: Use case orchestration and workflows."""

__version__ = "0.1.0"


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "application",
        "description": "Application layer for use case orchestration",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }
