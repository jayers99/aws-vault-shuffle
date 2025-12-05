#!/usr/bin/env python3
"""Infrastructure layer: AWS SDK calls, configuration, logging, I/O."""

__version__ = "0.1.0"


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "infrastructure",
        "description": "Infrastructure layer for AWS SDK calls and I/O",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }
