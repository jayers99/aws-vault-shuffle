#!/usr/bin/env python3
"""aws-vault-shuffle: CLI tool to copy AWS Backup recovery points between AWS accounts at scale."""

from aws_vault_shuffle.__version__ import __version__

__all__ = ["__version__"]


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "aws_vault_shuffle",
        "description": "CLI tool to copy AWS Backup recovery points between AWS accounts at scale",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }
