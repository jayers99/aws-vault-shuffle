#!/usr/bin/env python3
"""Application service for inventory operations (listing vaults and recovery points)."""

from typing import Protocol

from aws_vault_shuffle.domain.config import RegionConfig
from aws_vault_shuffle.domain.vault import Vault

__version__ = "0.1.0"


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "inventory_service",
        "description": "Application service for listing vaults and recovery points",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }


class BackupClient(Protocol):
    """
    Protocol (interface) for AWS Backup operations.

    This keeps the application layer independent of AWS SDK implementation.
    Infrastructure layer will provide concrete implementations.
    """

    def list_vaults(self, region: str) -> list[Vault]:
        """List all backup vaults in a region."""
        ...

    def list_recovery_points(self, vault_name: str, region: str) -> list[Vault]:
        """List all recovery points for a vault in a region."""
        ...


class InventoryService:
    """
    Use case: List all vaults and recovery points across multiple regions.

    This service orchestrates the workflow but delegates AWS SDK calls
    to the infrastructure layer via the BackupClient protocol.
    """

    def __init__(self, backup_client: BackupClient):
        """Initialize with a backup client implementation."""
        self.backup_client = backup_client

    def list_all_vaults(self, config: RegionConfig) -> list[Vault]:
        """
        List all vaults and their recovery points across all configured regions.

        Args:
            config: Region configuration specifying account and regions to scan

        Returns:
            List of Vault objects with their recovery points
        """
        all_vaults: list[Vault] = []

        for region in config.regions:
            # Get vaults in this region
            vaults = self.backup_client.list_vaults(region)

            # For each vault, get its recovery points
            for vault in vaults:
                vault_with_points = self.backup_client.list_recovery_points(
                    vault.name, region
                )
                all_vaults.extend(vault_with_points)

        return all_vaults


def main() -> None:
    """Demonstrate usage with a fake client (for testing)."""

    # Fake implementation for demonstration
    class FakeBackupClient:
        def list_vaults(self, region: str) -> list[Vault]:
            return [
                Vault(
                    name=f"vault-{region}",
                    arn=f"arn:aws:backup:{region}:123456789012:backup-vault:vault-{region}",
                    region=region,
                )
            ]

        def list_recovery_points(self, vault_name: str, region: str) -> list[Vault]:
            # Return vault with empty recovery points for demo
            return [
                Vault(
                    name=vault_name,
                    arn=f"arn:aws:backup:{region}:123456789012:backup-vault:{vault_name}",
                    region=region,
                    recovery_points=(),
                )
            ]

    # Create service with fake client
    service = InventoryService(FakeBackupClient())

    # Create config
    config = RegionConfig(
        source_account="123456789012",
        regions=("us-east-1", "us-west-2"),
    )

    # List vaults
    vaults = service.list_all_vaults(config)
    print(f"Found {len(vaults)} vaults:")
    for vault in vaults:
        print(f"  - {vault.name} ({vault.region})")


if __name__ == "__main__":
    main()
