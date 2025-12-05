#!/usr/bin/env python3
"""Unit tests for inventory service."""

from datetime import datetime, timezone

import pytest

from aws_vault_shuffle.application.inventory_service import InventoryService
from aws_vault_shuffle.domain.config import RegionConfig
from aws_vault_shuffle.domain.vault import RecoveryPoint, Vault


class FakeBackupClient:
    """Fake AWS Backup client for testing (no real AWS calls)."""

    def __init__(self):
        """Initialize fake client with test data."""
        self.vaults_by_region = {
            "us-east-1": [
                Vault(
                    name="vault-east-1",
                    arn="arn:aws:backup:us-east-1:123456789012:backup-vault:vault-east-1",
                    region="us-east-1",
                ),
            ],
            "us-west-2": [
                Vault(
                    name="vault-west-1",
                    arn="arn:aws:backup:us-west-2:123456789012:backup-vault:vault-west-1",
                    region="us-west-2",
                ),
                Vault(
                    name="vault-west-2",
                    arn="arn:aws:backup:us-west-2:123456789012:backup-vault:vault-west-2",
                    region="us-west-2",
                ),
            ],
        }

        # Recovery points for each vault
        self.recovery_points = {
            ("vault-east-1", "us-east-1"): [
                RecoveryPoint(
                    arn="arn:aws:backup:us-east-1:123456789012:recovery-point:rp1",
                    vault_name="vault-east-1",
                    resource_arn="arn:aws:ec2:us-east-1:123456789012:volume/vol-1",
                    resource_type="EBS",
                    creation_date=datetime.now(timezone.utc),
                    status="COMPLETED",
                ),
            ],
            ("vault-west-1", "us-west-2"): [],
            ("vault-west-2", "us-west-2"): [
                RecoveryPoint(
                    arn="arn:aws:backup:us-west-2:123456789012:recovery-point:rp2",
                    vault_name="vault-west-2",
                    resource_arn="arn:aws:rds:us-west-2:123456789012:db:mydb",
                    resource_type="RDS",
                    creation_date=datetime.now(timezone.utc),
                    status="COMPLETED",
                ),
            ],
        }

    def list_vaults(self, region: str) -> list[Vault]:
        """Return fake vaults for a region."""
        return self.vaults_by_region.get(region, [])

    def list_recovery_points(self, vault_name: str, region: str) -> list[Vault]:
        """Return fake recovery points for a vault."""
        rps = self.recovery_points.get((vault_name, region), [])

        # Find the vault
        vaults = self.vaults_by_region.get(region, [])
        vault = next((v for v in vaults if v.name == vault_name), None)

        if vault:
            # Return vault with recovery points
            return [
                Vault(
                    name=vault.name,
                    arn=vault.arn,
                    region=vault.region,
                    recovery_points=tuple(rps),
                )
            ]

        return []


class TestInventoryService:
    """Tests for InventoryService."""

    def test_list_all_vaults_single_region(self):
        """Test listing vaults from a single region."""
        fake_client = FakeBackupClient()
        service = InventoryService(fake_client)

        config = RegionConfig(
            source_account="123456789012",
            regions=("us-east-1",),
        )

        vaults = service.list_all_vaults(config)

        assert len(vaults) == 1
        assert vaults[0].name == "vault-east-1"
        assert vaults[0].region == "us-east-1"
        assert vaults[0].recovery_point_count() == 1

    def test_list_all_vaults_multiple_regions(self):
        """Test listing vaults from multiple regions."""
        fake_client = FakeBackupClient()
        service = InventoryService(fake_client)

        config = RegionConfig(
            source_account="123456789012",
            regions=("us-east-1", "us-west-2"),
        )

        vaults = service.list_all_vaults(config)

        assert len(vaults) == 3  # 1 from east, 2 from west
        vault_names = {v.name for v in vaults}
        assert vault_names == {"vault-east-1", "vault-west-1", "vault-west-2"}

    def test_list_all_vaults_includes_recovery_points(self):
        """Test that vaults include their recovery points."""
        fake_client = FakeBackupClient()
        service = InventoryService(fake_client)

        config = RegionConfig(
            source_account="123456789012",
            regions=("us-west-2",),
        )

        vaults = service.list_all_vaults(config)

        # vault-west-1 has 0 recovery points
        vault_west_1 = next(v for v in vaults if v.name == "vault-west-1")
        assert vault_west_1.recovery_point_count() == 0

        # vault-west-2 has 1 recovery point
        vault_west_2 = next(v for v in vaults if v.name == "vault-west-2")
        assert vault_west_2.recovery_point_count() == 1
        assert vault_west_2.recovery_points[0].resource_type == "RDS"

    def test_list_all_vaults_empty_region(self):
        """Test listing vaults from a region with no vaults."""
        fake_client = FakeBackupClient()
        service = InventoryService(fake_client)

        config = RegionConfig(
            source_account="123456789012",
            regions=("eu-west-1",),  # Not in fake data
        )

        vaults = service.list_all_vaults(config)

        assert len(vaults) == 0
