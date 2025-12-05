#!/usr/bin/env python3
"""Unit tests for vault domain models."""

from datetime import datetime, timezone

import pytest

from aws_vault_shuffle.domain.vault import RecoveryPoint, Vault


class TestRecoveryPoint:
    """Tests for RecoveryPoint domain model."""

    def test_create_recovery_point(self):
        """Test creating a recovery point with required fields."""
        rp = RecoveryPoint(
            arn="arn:aws:backup:us-east-1:123456789012:recovery-point:abc-123",
            vault_name="test-vault",
            resource_arn="arn:aws:ec2:us-east-1:123456789012:volume/vol-123",
            resource_type="EBS",
            creation_date=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            status="COMPLETED",
        )

        assert rp.arn == "arn:aws:backup:us-east-1:123456789012:recovery-point:abc-123"
        assert rp.vault_name == "test-vault"
        assert rp.resource_type == "EBS"
        assert rp.status == "COMPLETED"

    def test_recovery_point_is_completed(self):
        """Test is_completed() method."""
        rp = RecoveryPoint(
            arn="arn:test",
            vault_name="vault",
            resource_arn="arn:resource",
            resource_type="EBS",
            creation_date=datetime.now(timezone.utc),
            status="COMPLETED",
        )

        assert rp.is_completed() is True

    def test_recovery_point_is_failed(self):
        """Test is_failed() method."""
        rp = RecoveryPoint(
            arn="arn:test",
            vault_name="vault",
            resource_arn="arn:resource",
            resource_type="EBS",
            creation_date=datetime.now(timezone.utc),
            status="FAILED",
        )

        assert rp.is_failed() is True

    def test_recovery_point_age_days(self):
        """Test age_days() calculation."""
        creation = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        reference = datetime(2025, 1, 10, 12, 0, 0, tzinfo=timezone.utc)

        rp = RecoveryPoint(
            arn="arn:test",
            vault_name="vault",
            resource_arn="arn:resource",
            resource_type="EBS",
            creation_date=creation,
            status="COMPLETED",
        )

        assert rp.age_days(reference) == 9

    def test_recovery_point_immutable(self):
        """Test that RecoveryPoint is immutable (frozen)."""
        rp = RecoveryPoint(
            arn="arn:test",
            vault_name="vault",
            resource_arn="arn:resource",
            resource_type="EBS",
            creation_date=datetime.now(timezone.utc),
            status="COMPLETED",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            rp.status = "FAILED"


class TestVault:
    """Tests for Vault domain model."""

    def test_create_vault(self):
        """Test creating a vault with required fields."""
        vault = Vault(
            name="test-vault",
            arn="arn:aws:backup:us-east-1:123456789012:backup-vault:test-vault",
            region="us-east-1",
        )

        assert vault.name == "test-vault"
        assert vault.region == "us-east-1"
        assert vault.recovery_points == ()

    def test_vault_recovery_point_count(self):
        """Test recovery_point_count() method."""
        rp1 = RecoveryPoint(
            arn="arn:test1",
            vault_name="vault",
            resource_arn="arn:resource1",
            resource_type="EBS",
            creation_date=datetime.now(timezone.utc),
            status="COMPLETED",
        )
        rp2 = RecoveryPoint(
            arn="arn:test2",
            vault_name="vault",
            resource_arn="arn:resource2",
            resource_type="RDS",
            creation_date=datetime.now(timezone.utc),
            status="COMPLETED",
        )

        vault = Vault(
            name="test-vault",
            arn="arn:test",
            region="us-east-1",
            recovery_points=(rp1, rp2),
        )

        assert vault.recovery_point_count() == 2

    def test_vault_completed_recovery_points(self):
        """Test completed_recovery_points() filters correctly."""
        rp_completed = RecoveryPoint(
            arn="arn:completed",
            vault_name="vault",
            resource_arn="arn:resource1",
            resource_type="EBS",
            creation_date=datetime.now(timezone.utc),
            status="COMPLETED",
        )
        rp_failed = RecoveryPoint(
            arn="arn:failed",
            vault_name="vault",
            resource_arn="arn:resource2",
            resource_type="RDS",
            creation_date=datetime.now(timezone.utc),
            status="FAILED",
        )

        vault = Vault(
            name="test-vault",
            arn="arn:test",
            region="us-east-1",
            recovery_points=(rp_completed, rp_failed),
        )

        completed = vault.completed_recovery_points()
        assert len(completed) == 1
        assert completed[0].arn == "arn:completed"

    def test_vault_total_backup_size(self):
        """Test total_backup_size_bytes() calculation."""
        rp1 = RecoveryPoint(
            arn="arn:test1",
            vault_name="vault",
            resource_arn="arn:resource1",
            resource_type="EBS",
            creation_date=datetime.now(timezone.utc),
            status="COMPLETED",
            backup_size_bytes=1000,
        )
        rp2 = RecoveryPoint(
            arn="arn:test2",
            vault_name="vault",
            resource_arn="arn:resource2",
            resource_type="RDS",
            creation_date=datetime.now(timezone.utc),
            status="COMPLETED",
            backup_size_bytes=2000,
        )
        rp3 = RecoveryPoint(
            arn="arn:test3",
            vault_name="vault",
            resource_arn="arn:resource3",
            resource_type="S3",
            creation_date=datetime.now(timezone.utc),
            status="COMPLETED",
            backup_size_bytes=None,  # Unknown size
        )

        vault = Vault(
            name="test-vault",
            arn="arn:test",
            region="us-east-1",
            recovery_points=(rp1, rp2, rp3),
        )

        assert vault.total_backup_size_bytes() == 3000

    def test_vault_immutable(self):
        """Test that Vault is immutable (frozen)."""
        vault = Vault(
            name="test-vault",
            arn="arn:test",
            region="us-east-1",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            vault.name = "new-name"
