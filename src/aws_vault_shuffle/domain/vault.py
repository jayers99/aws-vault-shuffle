#!/usr/bin/env python3
"""Domain models for AWS Backup vaults and recovery points."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

__version__ = "0.1.0"


def file_info() -> dict[str, str]:
    """Return file metadata."""
    return {
        "name": "vault",
        "description": "Domain models for Vault and RecoveryPoint",
        "version": __version__,
        "author": "John Ayers",
        "last_updated": "2025-12-04",
    }


@dataclass(frozen=True)
class RecoveryPoint:
    """
    Represents an AWS Backup recovery point (snapshot/backup).

    This is a pure domain object with no AWS SDK dependencies.
    Immutable to ensure consistency.
    """

    arn: str
    vault_name: str
    resource_arn: str
    resource_type: str
    creation_date: datetime
    status: str
    backup_size_bytes: Optional[int] = None
    completion_date: Optional[datetime] = None

    def is_completed(self) -> bool:
        """Check if the recovery point has completed."""
        return self.status == "COMPLETED"

    def is_failed(self) -> bool:
        """Check if the recovery point has failed."""
        return self.status == "FAILED"

    def age_days(self, reference_date: Optional[datetime] = None) -> int:
        """Calculate age in days from creation date."""
        ref = reference_date or datetime.now(self.creation_date.tzinfo)
        delta = ref - self.creation_date
        return delta.days


@dataclass(frozen=True)
class Vault:
    """
    Represents an AWS Backup vault.

    This is a pure domain object with no AWS SDK dependencies.
    Immutable to ensure consistency.
    """

    name: str
    arn: str
    region: str
    recovery_points: tuple[RecoveryPoint, ...] = ()

    def recovery_point_count(self) -> int:
        """Return the number of recovery points in this vault."""
        return len(self.recovery_points)

    def completed_recovery_points(self) -> tuple[RecoveryPoint, ...]:
        """Return only completed recovery points."""
        return tuple(rp for rp in self.recovery_points if rp.is_completed())

    def total_backup_size_bytes(self) -> int:
        """Calculate total size of all recovery points with known sizes."""
        return sum(
            rp.backup_size_bytes
            for rp in self.recovery_points
            if rp.backup_size_bytes is not None
        )


def main() -> None:
    """Demonstrate domain model usage (for testing)."""
    # Example usage
    rp = RecoveryPoint(
        arn="arn:aws:backup:us-east-1:123456789012:recovery-point:abc-123",
        vault_name="test-vault",
        resource_arn="arn:aws:ec2:us-east-1:123456789012:volume/vol-123",
        resource_type="EBS",
        creation_date=datetime.now(),
        status="COMPLETED",
        backup_size_bytes=1024 * 1024 * 100,  # 100 MB
    )

    vault = Vault(
        name="test-vault",
        arn="arn:aws:backup:us-east-1:123456789012:backup-vault:test-vault",
        region="us-east-1",
        recovery_points=(rp,),
    )

    print(f"Vault: {vault.name}")
    print(f"Recovery points: {vault.recovery_point_count()}")
    print(f"Total size: {vault.total_backup_size_bytes()} bytes")
    print(f"Recovery point age: {rp.age_days()} days")


if __name__ == "__main__":
    main()
