#!/usr/bin/env python3
"""Domain layer: Pure business logic with no external dependencies."""

__version__ = "0.1.0"


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "domain",
        "description": "Domain layer containing pure business logic",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }
