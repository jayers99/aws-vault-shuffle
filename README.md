# aws-vault-shuffle

CLI tool to copy AWS Backup recovery points between AWS accounts at scale.

## Overview

`aws-vault-shuffle` helps you migrate AWS Backup recovery points across accounts efficiently and safely. It provides inventory, verification, and copy capabilities with built-in dry-run modes and progress tracking.

## Current Features

- **Inventory/List**: Retrieve all backup vaults and recovery points from a specified AWS account across multiple regions

## Planned Features

- Copy recovery points to destination account
- Verify successful migrations
- Resume interrupted batch operations
- Detailed reporting and audit logs

## Installation

### Prerequisites

- Python 3.12+ (managed via pyenv)
- pipenv for dependency management
- AWS credentials configured with appropriate cross-account permissions

### Setup

```bash
# Install Python 3.12.10 via pyenv
pyenv install 3.12.10
pyenv local 3.12.10

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell
```

## Usage

### List Vaults and Recovery Points

```bash
# Using CLI arguments
python -m aws_vault_shuffle.cli list \
  --account 123456789012 \
  --regions us-east-1,us-west-2,eu-west-1

# Using config file
python -m aws_vault_shuffle.cli list --config config.yml

# Dry-run mode (safe default)
python -m aws_vault_shuffle.cli list \
  --account 123456789012 \
  --regions us-east-1 \
  --dry-run
```

### Configuration File

See `config.example.yml` for a template:

```yaml
source_account: "123456789012"
regions:
  - us-east-1
  - us-west-2
  - eu-west-1
```

## Architecture

Follows lightweight Domain-Driven Design principles:

- **Domain**: Pure business logic (Vault, RecoveryPoint, RegionConfig models)
- **Application**: Use case orchestration (InventoryService)
- **Infrastructure**: AWS SDK calls, configuration loading, I/O

## Development

### Running Tests

```bash
# Run all tests
pipenv run pytest

# Run with coverage
pipenv run pytest --cov=aws_vault_shuffle --cov-report=term-missing

# Run only unit tests
pipenv run pytest tests/unit/

# Run specific test file
pipenv run pytest tests/unit/domain/test_vault.py
```

### Test-Driven Development

This project follows strict TDD practices:
1. Write failing test first
2. Implement minimal code to pass
3. Refactor while keeping tests green

### Trunk-Based Development

- Work in small, releasable increments
- Keep `main` branch always deployable
- No long-lived feature branches

## AWS Permissions

The tool requires AWS credentials with the following permissions in the source account:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "backup:ListBackupVaults",
        "backup:ListRecoveryPointsByBackupVault",
        "backup:DescribeRecoveryPoint"
      ],
      "Resource": "*"
    }
  ]
}
```

## Security

- Never hardcode AWS credentials
- Use IAM roles and temporary credentials
- Supports AWS SSO, environment variables, and EC2 instance profiles
- All operations are logged
- Dry-run mode enabled by default for destructive operations

## Contributing

This is a solo trunk-based project following Modern Software Engineering principles (Dave Farley). See `.claude/prompts.md` for detailed guard rails and development philosophy.

## License

MIT

## Author

John Ayers

## Version

0.1.0 (Initial Development)
