#!/usr/bin/env python3
"""Command-line interface for aws-vault-shuffle."""

import argparse
import sys
from typing import Optional

from aws_vault_shuffle.__version__ import __version__

__version__ = "0.1.0"


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "cli",
        "description": "Command-line interface entry point",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="aws-vault-shuffle",
        description="CLI tool to copy AWS Backup recovery points between AWS accounts at scale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual changes)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List all backup vaults and recovery points",
    )
    list_parser.add_argument(
        "--account",
        type=str,
        help="AWS account number (12 digits)",
    )
    list_parser.add_argument(
        "--regions",
        type=str,
        help="Comma-separated list of AWS regions (e.g., us-east-1,us-west-2)",
    )
    list_parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (YAML)",
    )
    list_parser.add_argument(
        "--output",
        choices=["json", "table", "summary"],
        default="table",
        help="Output format (default: table)",
    )

    return parser


def handle_list(args: argparse.Namespace) -> int:
    """Handle the 'list' command."""
    print(f"[DRY-RUN: {args.dry_run}] Listing vaults and recovery points...")

    if args.config:
        print(f"  Using config file: {args.config}")
    else:
        if not args.account:
            print("ERROR: --account is required when not using --config", file=sys.stderr)
            return 1
        if not args.regions:
            print("ERROR: --regions is required when not using --config", file=sys.stderr)
            return 1

        print(f"  Account: {args.account}")
        print(f"  Regions: {args.regions}")

    print(f"  Output format: {args.output}")
    print("\nNOTE: Implementation coming soon (TDD in progress)")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "list":
        return handle_list(args)

    # Fallback for unknown commands
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
