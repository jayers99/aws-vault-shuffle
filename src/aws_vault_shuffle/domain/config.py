#!/usr/bin/env python3
"""Domain models for configuration."""

from dataclasses import dataclass
from typing import Optional

__version__ = "0.1.0"


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "config",
        "description": "Domain models for configuration",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }


@dataclass(frozen=True)
class RegionConfig:
    """
    Configuration for AWS regions to scan.

    This is a pure domain object with validation logic.
    Immutable to ensure consistency.
    """

    source_account: str
    regions: tuple[str, ...]
    assume_role_arn: Optional[str] = None
    external_id: Optional[str] = None
    session_name: str = "aws-vault-shuffle"

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Validate account number format (12 digits)
        if not self.source_account.isdigit() or len(self.source_account) != 12:
            raise ValueError(
                f"source_account must be a 12-digit number, got: {self.source_account}"
            )

        # Validate at least one region
        if not self.regions:
            raise ValueError("At least one region must be specified")

        # Validate region format (basic check)
        for region in self.regions:
            if not region or "-" not in region:
                raise ValueError(f"Invalid region format: {region}")

    def region_count(self) -> int:
        """Return the number of regions configured."""
        return len(self.regions)

    def has_cross_account_role(self) -> bool:
        """Check if cross-account role assumption is configured."""
        return self.assume_role_arn is not None


def main() -> None:
    """Demonstrate domain model usage (for testing)."""
    # Example valid config
    config = RegionConfig(
        source_account="123456789012",
        regions=("us-east-1", "us-west-2", "eu-west-1"),
        assume_role_arn="arn:aws:iam::123456789012:role/BackupReader",
    )

    print(f"Account: {config.source_account}")
    print(f"Regions: {config.regions}")
    print(f"Region count: {config.region_count()}")
    print(f"Cross-account: {config.has_cross_account_role()}")

    # Example invalid config (will raise ValueError)
    try:
        invalid = RegionConfig(
            source_account="invalid",
            regions=("us-east-1",),
        )
    except ValueError as e:
        print(f"\nValidation error (expected): {e}")


if __name__ == "__main__":
    main()
