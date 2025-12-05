#!/usr/bin/env python3
"""Command-line interface for aws-vault-shuffle."""

import argparse
import sys
from typing import Optional

from aws_vault_shuffle.__version__ import __version__
from aws_vault_shuffle.application.inventory_service import InventoryService
from aws_vault_shuffle.infrastructure.aws_backup_adapter import AWSBackupAdapter
from aws_vault_shuffle.infrastructure.config_loader import load_from_cli, load_from_yaml

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
    try:
        # Load configuration
        if args.config:
            print(f"Loading configuration from: {args.config}")
            config = load_from_yaml(args.config)
        else:
            if not args.account:
                print("ERROR: --account is required when not using --config", file=sys.stderr)
                return 1
            if not args.regions:
                print("ERROR: --regions is required when not using --config", file=sys.stderr)
                return 1
            config = load_from_cli(
                account=args.account,
                regions=args.regions,
            )

        # Display configuration
        print(f"Account: {config.source_account}")
        print(f"Regions: {', '.join(config.regions)}")
        print(f"Scanning {config.region_count()} region(s)...")
        print()

        # Create AWS Backup adapter
        adapter = AWSBackupAdapter(
            assume_role_arn=config.assume_role_arn,
            external_id=config.external_id,
            session_name=config.session_name,
        )

        # Create inventory service
        inventory_service = InventoryService(adapter)

        # List all vaults and recovery points
        vaults = inventory_service.list_all_vaults(config)

        # Format output
        if args.output == "json":
            _print_json_output(vaults)
        elif args.output == "summary":
            _print_summary_output(vaults)
        else:  # table (default)
            _print_table_output(vaults)

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERROR: Invalid configuration: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"ERROR: AWS operation failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 1


def _print_table_output(vaults) -> None:
    """Print vaults and recovery points in table format."""
    if not vaults:
        print("No backup vaults found.")
        return

    total_vaults = len(vaults)
    total_recovery_points = sum(v.recovery_point_count() for v in vaults)
    total_size = sum(v.total_backup_size_bytes() for v in vaults)

    print(f"Found {total_vaults} vault(s) with {total_recovery_points} recovery point(s)")
    print(f"Total backup size: {_format_bytes(total_size)}")
    print()

    for vault in vaults:
        print(f"Vault: {vault.name} ({vault.region})")
        print(f"  ARN: {vault.arn}")
        print(f"  Recovery Points: {vault.recovery_point_count()}")

        if vault.recovery_points:
            print(f"  Recovery Points:")
            for rp in vault.recovery_points:
                size_str = _format_bytes(rp.backup_size_bytes) if rp.backup_size_bytes else "unknown"
                print(f"    - {rp.resource_type}: {rp.resource_arn}")
                print(f"      Status: {rp.status}, Size: {size_str}, Created: {rp.creation_date}")
        print()


def _print_json_output(vaults) -> None:
    """Print vaults and recovery points in JSON format."""
    import json
    from datetime import datetime

    def json_serializer(obj):
        """JSON serializer for datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    vault_data = []
    for vault in vaults:
        vault_dict = {
            "name": vault.name,
            "arn": vault.arn,
            "region": vault.region,
            "recovery_point_count": vault.recovery_point_count(),
            "total_size_bytes": vault.total_backup_size_bytes(),
            "recovery_points": [
                {
                    "arn": rp.arn,
                    "resource_arn": rp.resource_arn,
                    "resource_type": rp.resource_type,
                    "status": rp.status,
                    "creation_date": rp.creation_date,
                    "backup_size_bytes": rp.backup_size_bytes,
                    "completion_date": rp.completion_date,
                }
                for rp in vault.recovery_points
            ],
        }
        vault_data.append(vault_dict)

    print(json.dumps(vault_data, indent=2, default=json_serializer))


def _print_summary_output(vaults) -> None:
    """Print summary of vaults and recovery points."""
    if not vaults:
        print("No backup vaults found.")
        return

    total_vaults = len(vaults)
    total_recovery_points = sum(v.recovery_point_count() for v in vaults)
    total_size = sum(v.total_backup_size_bytes() for v in vaults)

    # Count by region
    by_region = {}
    for vault in vaults:
        if vault.region not in by_region:
            by_region[vault.region] = {"vaults": 0, "recovery_points": 0, "size_bytes": 0}
        by_region[vault.region]["vaults"] += 1
        by_region[vault.region]["recovery_points"] += vault.recovery_point_count()
        by_region[vault.region]["size_bytes"] += vault.total_backup_size_bytes()

    # Count by resource type
    by_type = {}
    for vault in vaults:
        for rp in vault.recovery_points:
            if rp.resource_type not in by_type:
                by_type[rp.resource_type] = 0
            by_type[rp.resource_type] += 1

    print("=== Summary ===")
    print(f"Total Vaults: {total_vaults}")
    print(f"Total Recovery Points: {total_recovery_points}")
    print(f"Total Size: {_format_bytes(total_size)}")
    print()

    print("By Region:")
    for region, stats in sorted(by_region.items()):
        print(f"  {region}: {stats['vaults']} vault(s), {stats['recovery_points']} recovery point(s), {_format_bytes(stats['size_bytes'])}")
    print()

    if by_type:
        print("By Resource Type:")
        for resource_type, count in sorted(by_type.items()):
            print(f"  {resource_type}: {count}")


def _format_bytes(num_bytes: Optional[int]) -> str:
    """Format bytes into human-readable string."""
    if num_bytes is None:
        return "unknown"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


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
