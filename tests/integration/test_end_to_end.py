#!/usr/bin/env python3
"""End-to-end integration tests for aws-vault-shuffle CLI."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from aws_vault_shuffle.cli import main


class TestListCommandIntegration:
    """Integration tests for the list command with mocked AWS responses."""

    @patch("boto3.Session")
    def test_list_command_with_mocked_aws(self, mock_session_class, capsys):
        """Test list command with mocked boto3 responses."""
        # Setup mock boto3 client
        mock_backup_client = MagicMock()

        # Mock list_backup_vaults response
        mock_backup_client.get_paginator.return_value.paginate.return_value = [
            {
                "BackupVaultList": [
                    {
                        "BackupVaultName": "test-vault-1",
                        "BackupVaultArn": "arn:aws:backup:us-east-1:123456789012:backup-vault:test-vault-1",
                    },
                    {
                        "BackupVaultName": "test-vault-2",
                        "BackupVaultArn": "arn:aws:backup:us-east-1:123456789012:backup-vault:test-vault-2",
                    },
                ]
            }
        ]

        # Mock describe_backup_vault response
        mock_backup_client.describe_backup_vault.return_value = {
            "BackupVaultArn": "arn:aws:backup:us-east-1:123456789012:backup-vault:test-vault-1",
        }

        # Mock list_recovery_points_by_backup_vault response
        def mock_paginate_recovery_points(**kwargs):
            vault_name = kwargs.get("BackupVaultName")
            if vault_name == "test-vault-1":
                return [
                    {
                        "RecoveryPoints": [
                            {
                                "RecoveryPointArn": "arn:aws:backup:us-east-1:123456789012:recovery-point:rp1",
                                "ResourceArn": "arn:aws:ec2:us-east-1:123456789012:volume/vol-123",
                                "ResourceType": "EBS",
                                "CreationDate": datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                                "Status": "COMPLETED",
                                "BackupSizeInBytes": 1073741824,  # 1 GB
                            }
                        ]
                    }
                ]
            return [{"RecoveryPoints": []}]

        # Setup mock session and client
        mock_session = MagicMock()
        mock_session.client.return_value = mock_backup_client
        mock_session_class.return_value = mock_session

        # Override paginator behavior for recovery points
        mock_backup_client.get_paginator.side_effect = lambda op: (
            MagicMock(paginate=mock_paginate_recovery_points)
            if op == "list_recovery_points_by_backup_vault"
            else MagicMock(
                paginate=MagicMock(
                    return_value=[
                        {
                            "BackupVaultList": [
                                {
                                    "BackupVaultName": "test-vault-1",
                                    "BackupVaultArn": "arn:aws:backup:us-east-1:123456789012:backup-vault:test-vault-1",
                                }
                            ]
                        }
                    ]
                )
            )
        )

        # Run the CLI command
        exit_code = main([
            "list",
            "--account", "123456789012",
            "--regions", "us-east-1",
        ])

        assert exit_code == 0

        # Verify output
        captured = capsys.readouterr()
        assert "test-vault-1" in captured.out
        # Currently just shows placeholder message, will be updated in implementation

    @patch("boto3.Session")
    def test_list_command_with_no_vaults(self, mock_session_class, capsys):
        """Test list command when account has no vaults."""
        # Setup mock boto3 client with empty response
        mock_backup_client = MagicMock()
        mock_backup_client.get_paginator.return_value.paginate.return_value = [
            {"BackupVaultList": []}
        ]

        mock_session = MagicMock()
        mock_session.client.return_value = mock_backup_client
        mock_session_class.return_value = mock_session

        # Run the CLI command
        exit_code = main([
            "list",
            "--account", "123456789012",
            "--regions", "us-east-1",
        ])

        assert exit_code == 0

        # Should handle empty results gracefully
        captured = capsys.readouterr()
        assert exit_code == 0


class TestListCommandWithConfigFile:
    """Integration tests for list command using config file."""

    @patch("boto3.Session")
    def test_list_command_with_config_file(self, mock_session_class, capsys, tmp_path):
        """Test list command loading config from YAML file."""
        # Create temporary config file
        config_file = tmp_path / "test_config.yml"
        config_file.write_text("""
source_account: "123456789012"
regions:
  - us-east-1
  - us-west-2
""")

        # Setup mock boto3
        mock_backup_client = MagicMock()
        mock_backup_client.get_paginator.return_value.paginate.return_value = [
            {"BackupVaultList": []}
        ]

        mock_session = MagicMock()
        mock_session.client.return_value = mock_backup_client
        mock_session_class.return_value = mock_session

        # Run CLI with config file
        exit_code = main([
            "list",
            "--config", str(config_file),
        ])

        assert exit_code == 0
