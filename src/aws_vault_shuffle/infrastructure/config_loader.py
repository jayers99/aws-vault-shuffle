#!/usr/bin/env python3
"""Infrastructure module for loading configuration from YAML files or CLI arguments."""

from pathlib import Path
from typing import Optional

import yaml

from aws_vault_shuffle.domain.config import RegionConfig

__version__ = "0.1.0"


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "config_loader",
        "description": "Configuration loading from YAML files and CLI arguments",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }


def load_from_yaml(config_path: str) -> RegionConfig:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        RegionConfig domain object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid or missing required fields
        yaml.YAMLError: If config file has invalid YAML syntax
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with path.open("r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a YAML dictionary")

    # Extract required fields
    source_account = data.get("source_account")
    if not source_account:
        raise ValueError("Configuration must specify 'source_account'")

    regions = data.get("regions")
    if not regions:
        raise ValueError("Configuration must specify 'regions'")

    # Extract optional fields
    assume_role_arn = data.get("assume_role_arn")
    external_id = data.get("external_id")
    session_name = data.get("session_name", "aws-vault-shuffle")

    # Create domain object (validation happens in __post_init__)
    return RegionConfig(
        source_account=str(source_account),
        regions=tuple(regions),
        assume_role_arn=assume_role_arn,
        external_id=external_id,
        session_name=session_name,
    )


def load_from_cli(
    account: str,
    regions: str,
    assume_role_arn: Optional[str] = None,
    external_id: Optional[str] = None,
    session_name: str = "aws-vault-shuffle",
) -> RegionConfig:
    """
    Load configuration from CLI arguments.

    Args:
        account: AWS account number (12 digits)
        regions: Comma-separated list of regions
        assume_role_arn: Optional IAM role ARN to assume
        external_id: Optional external ID for role assumption
        session_name: Session name for role assumption

    Returns:
        RegionConfig domain object

    Raises:
        ValueError: If arguments are invalid
    """
    # Parse regions from comma-separated string
    region_list = [r.strip() for r in regions.split(",") if r.strip()]

    # Create domain object (validation happens in __post_init__)
    return RegionConfig(
        source_account=account,
        regions=tuple(region_list),
        assume_role_arn=assume_role_arn,
        external_id=external_id,
        session_name=session_name,
    )


def main() -> None:
    """Demonstrate config loading (for testing)."""
    # Example: Load from CLI args
    config_cli = load_from_cli(
        account="123456789012",
        regions="us-east-1,us-west-2,eu-west-1",
    )
    print("Loaded from CLI:")
    print(f"  Account: {config_cli.source_account}")
    print(f"  Regions: {config_cli.regions}")
    print()

    # Example: Load from YAML (would need actual file)
    # config_yaml = load_from_yaml("config.yml")
    # print("Loaded from YAML:")
    # print(f"  Account: {config_yaml.source_account}")
    # print(f"  Regions: {config_yaml.regions}")


if __name__ == "__main__":
    main()
