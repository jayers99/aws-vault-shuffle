#!/usr/bin/env python3
"""Unit tests for config loader."""

import tempfile
from pathlib import Path

import pytest
import yaml

from aws_vault_shuffle.domain.config import RegionConfig
from aws_vault_shuffle.infrastructure.config_loader import (
    load_from_cli,
    load_from_yaml,
)


class TestLoadFromCLI:
    """Tests for load_from_cli()."""

    def test_load_from_cli_basic(self):
        """Test loading config from CLI arguments."""
        config = load_from_cli(
            account="123456789012",
            regions="us-east-1,us-west-2",
        )

        assert isinstance(config, RegionConfig)
        assert config.source_account == "123456789012"
        assert config.regions == ("us-east-1", "us-west-2")

    def test_load_from_cli_with_spaces(self):
        """Test loading handles spaces in region list."""
        config = load_from_cli(
            account="123456789012",
            regions="us-east-1, us-west-2 , eu-west-1",
        )

        assert config.regions == ("us-east-1", "us-west-2", "eu-west-1")

    def test_load_from_cli_with_optional_fields(self):
        """Test loading with optional cross-account fields."""
        config = load_from_cli(
            account="123456789012",
            regions="us-east-1",
            assume_role_arn="arn:aws:iam::123456789012:role/BackupReader",
            external_id="ext-123",
            session_name="test-session",
        )

        assert config.assume_role_arn == "arn:aws:iam::123456789012:role/BackupReader"
        assert config.external_id == "ext-123"
        assert config.session_name == "test-session"

    def test_load_from_cli_validates_account(self):
        """Test that domain validation is applied."""
        with pytest.raises(ValueError, match="12-digit number"):
            load_from_cli(
                account="invalid",
                regions="us-east-1",
            )


class TestLoadFromYAML:
    """Tests for load_from_yaml()."""

    def test_load_from_yaml_basic(self):
        """Test loading config from YAML file."""
        config_data = {
            "source_account": "123456789012",
            "regions": ["us-east-1", "us-west-2"],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            config = load_from_yaml(temp_path)

            assert isinstance(config, RegionConfig)
            assert config.source_account == "123456789012"
            assert config.regions == ("us-east-1", "us-west-2")
        finally:
            Path(temp_path).unlink()

    def test_load_from_yaml_with_optional_fields(self):
        """Test loading YAML with optional fields."""
        config_data = {
            "source_account": "123456789012",
            "regions": ["us-east-1"],
            "assume_role_arn": "arn:aws:iam::123456789012:role/BackupReader",
            "external_id": "ext-123",
            "session_name": "custom-session",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            config = load_from_yaml(temp_path)

            assert config.assume_role_arn == "arn:aws:iam::123456789012:role/BackupReader"
            assert config.external_id == "ext-123"
            assert config.session_name == "custom-session"
        finally:
            Path(temp_path).unlink()

    def test_load_from_yaml_file_not_found(self):
        """Test error when YAML file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="not found"):
            load_from_yaml("/nonexistent/config.yml")

    def test_load_from_yaml_missing_source_account(self):
        """Test error when source_account is missing."""
        config_data = {
            "regions": ["us-east-1"],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="source_account"):
                load_from_yaml(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_from_yaml_missing_regions(self):
        """Test error when regions are missing."""
        config_data = {
            "source_account": "123456789012",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="regions"):
                load_from_yaml(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_from_yaml_invalid_format(self):
        """Test error when YAML is not a dictionary."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("- just\n- a\n- list\n")
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match="YAML dictionary"):
                load_from_yaml(temp_path)
        finally:
            Path(temp_path).unlink()
