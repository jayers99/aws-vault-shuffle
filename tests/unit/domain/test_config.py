#!/usr/bin/env python3
"""Unit tests for config domain models."""

import pytest

from aws_vault_shuffle.domain.config import RegionConfig


class TestRegionConfig:
    """Tests for RegionConfig domain model."""

    def test_create_valid_config(self):
        """Test creating a valid region config."""
        config = RegionConfig(
            source_account="123456789012",
            regions=("us-east-1", "us-west-2"),
        )

        assert config.source_account == "123456789012"
        assert config.regions == ("us-east-1", "us-west-2")
        assert config.session_name == "aws-vault-shuffle"

    def test_config_with_optional_fields(self):
        """Test config with optional cross-account fields."""
        config = RegionConfig(
            source_account="123456789012",
            regions=("us-east-1",),
            assume_role_arn="arn:aws:iam::123456789012:role/BackupReader",
            external_id="external-123",
            session_name="custom-session",
        )

        assert config.assume_role_arn == "arn:aws:iam::123456789012:role/BackupReader"
        assert config.external_id == "external-123"
        assert config.session_name == "custom-session"

    def test_invalid_account_number_non_digits(self):
        """Test validation fails for non-digit account number."""
        with pytest.raises(ValueError, match="12-digit number"):
            RegionConfig(
                source_account="abc123456789",
                regions=("us-east-1",),
            )

    def test_invalid_account_number_wrong_length(self):
        """Test validation fails for wrong account number length."""
        with pytest.raises(ValueError, match="12-digit number"):
            RegionConfig(
                source_account="12345",  # Too short
                regions=("us-east-1",),
            )

    def test_empty_regions(self):
        """Test validation fails for empty regions."""
        with pytest.raises(ValueError, match="At least one region"):
            RegionConfig(
                source_account="123456789012",
                regions=(),
            )

    def test_invalid_region_format(self):
        """Test validation fails for invalid region format."""
        with pytest.raises(ValueError, match="Invalid region format"):
            RegionConfig(
                source_account="123456789012",
                regions=("invalid",),  # No hyphen
            )

    def test_region_count(self):
        """Test region_count() method."""
        config = RegionConfig(
            source_account="123456789012",
            regions=("us-east-1", "us-west-2", "eu-west-1"),
        )

        assert config.region_count() == 3

    def test_has_cross_account_role(self):
        """Test has_cross_account_role() method."""
        config_with_role = RegionConfig(
            source_account="123456789012",
            regions=("us-east-1",),
            assume_role_arn="arn:aws:iam::123456789012:role/BackupReader",
        )

        config_without_role = RegionConfig(
            source_account="123456789012",
            regions=("us-east-1",),
        )

        assert config_with_role.has_cross_account_role() is True
        assert config_without_role.has_cross_account_role() is False

    def test_config_immutable(self):
        """Test that RegionConfig is immutable (frozen)."""
        config = RegionConfig(
            source_account="123456789012",
            regions=("us-east-1",),
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            config.source_account = "999999999999"
