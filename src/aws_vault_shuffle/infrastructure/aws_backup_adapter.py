#!/usr/bin/env python3
"""Infrastructure module for AWS Backup SDK operations."""

from datetime import datetime
from typing import Any, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from aws_vault_shuffle.domain.vault import RecoveryPoint, Vault

__version__ = "0.1.0"


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "aws_backup_adapter",
        "description": "AWS Backup SDK adapter for cloud operations",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }


class AWSBackupAdapter:
    """
    Adapter for AWS Backup operations using boto3.

    This infrastructure component translates between AWS SDK and domain models.
    It implements the BackupClient protocol defined in application layer.
    """

    def __init__(
        self,
        assume_role_arn: Optional[str] = None,
        external_id: Optional[str] = None,
        session_name: str = "aws-vault-shuffle",
    ):
        """
        Initialize AWS Backup adapter.

        Args:
            assume_role_arn: Optional IAM role ARN to assume
            external_id: Optional external ID for role assumption
            session_name: Session name for role assumption
        """
        self.assume_role_arn = assume_role_arn
        self.external_id = external_id
        self.session_name = session_name
        self._sessions: dict[str, Any] = {}

    def _get_session(self, region: str) -> Any:
        """
        Get or create a boto3 session for a region.

        Uses cached sessions to avoid repeated role assumptions.
        """
        if region in self._sessions:
            return self._sessions[region]

        if self.assume_role_arn:
            # Assume role for cross-account access
            sts_client = boto3.client("sts")
            assume_params = {
                "RoleArn": self.assume_role_arn,
                "RoleSessionName": self.session_name,
            }
            if self.external_id:
                assume_params["ExternalId"] = self.external_id

            response = sts_client.assume_role(**assume_params)
            credentials = response["Credentials"]

            session = boto3.Session(
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                region_name=region,
            )
        else:
            # Use default credentials
            session = boto3.Session(region_name=region)

        self._sessions[region] = session
        return session

    def _get_backup_client(self, region: str) -> Any:
        """Get AWS Backup client for a region."""
        session = self._get_session(region)
        return session.client("backup")

    def list_vaults(self, region: str) -> list[Vault]:
        """
        List all backup vaults in a region.

        Args:
            region: AWS region to query

        Returns:
            List of Vault domain objects (without recovery points)

        Raises:
            ClientError: If AWS API call fails
            BotoCoreError: If boto3 encounters an error
        """
        client = self._get_backup_client(region)
        vaults: list[Vault] = []

        try:
            paginator = client.get_paginator("list_backup_vaults")
            for page in paginator.paginate():
                for vault_data in page.get("BackupVaultList", []):
                    vault = Vault(
                        name=vault_data["BackupVaultName"],
                        arn=vault_data["BackupVaultArn"],
                        region=region,
                        recovery_points=(),  # Will be populated separately
                    )
                    vaults.append(vault)

        except (ClientError, BotoCoreError) as e:
            # Re-raise with context
            raise RuntimeError(
                f"Failed to list backup vaults in {region}: {e}"
            ) from e

        return vaults

    def list_recovery_points(self, vault_name: str, region: str) -> list[Vault]:
        """
        List all recovery points for a vault.

        Args:
            vault_name: Name of the backup vault
            region: AWS region

        Returns:
            List containing a single Vault object with recovery points populated

        Raises:
            ClientError: If AWS API call fails
            BotoCoreError: If boto3 encounters an error
        """
        client = self._get_backup_client(region)
        recovery_points: list[RecoveryPoint] = []

        try:
            paginator = client.get_paginator("list_recovery_points_by_backup_vault")
            for page in paginator.paginate(BackupVaultName=vault_name):
                for rp_data in page.get("RecoveryPoints", []):
                    # Convert AWS data to domain model
                    rp = RecoveryPoint(
                        arn=rp_data["RecoveryPointArn"],
                        vault_name=vault_name,
                        resource_arn=rp_data["ResourceArn"],
                        resource_type=rp_data.get("ResourceType", "UNKNOWN"),
                        creation_date=rp_data["CreationDate"],
                        status=rp_data["Status"],
                        backup_size_bytes=rp_data.get("BackupSizeInBytes"),
                        completion_date=rp_data.get("CompletionDate"),
                    )
                    recovery_points.append(rp)

            # Get vault ARN (need to describe the vault)
            vault_response = client.describe_backup_vault(BackupVaultName=vault_name)

            vault = Vault(
                name=vault_name,
                arn=vault_response["BackupVaultArn"],
                region=region,
                recovery_points=tuple(recovery_points),
            )

            return [vault]

        except (ClientError, BotoCoreError) as e:
            raise RuntimeError(
                f"Failed to list recovery points for vault {vault_name} in {region}: {e}"
            ) from e


def main() -> None:
    """Demonstrate AWS Backup adapter usage (requires AWS credentials)."""
    print("AWS Backup Adapter - requires valid AWS credentials")
    print("This is a placeholder for real AWS operations")
    print()
    print("In tests, use a fake implementation instead of calling real AWS APIs")


if __name__ == "__main__":
    main()
