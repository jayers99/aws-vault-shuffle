# aws-vault-shuffle Guard Rails

This document captures the key prompts, principles, and guard rails for AI-assisted development on this project.

## Core Principles

### 1. Modern Software Engineering (Dave Farley)
- Optimize for fast, frequent, low-risk changes
- Always keep the codebase releasable (trunk-based)
- Prefer clear, simple, composable design; avoid premature abstractions
- Automate everything repeatable: tests, linting, formatting, packaging, release steps

### 2. Test-Driven Development (TDD)
- Tests come first, then minimal implementation, then refactor
- Use pytest
- Keep tests fast and deterministic; use fakes instead of real cloud calls
- Mirror the src layout inside tests/

### 3. Lightweight Domain-Driven Design (DDD)
- **Domain layer**: Pure logic, deterministic, no SDK dependencies
- **Application layer**: Orchestrates use cases and workflows
- **Infrastructure layer**: AWS/GCP calls, configuration, logging, I/O
- Domain objects should be small, explicit dataclasses with behavior
- Use interfaces/protocols for cloud operations to keep the domain independent
- Cloud adapters are replaceable; domain tests use fakes/mocks
- Keep the Ubiquitous Language small, consistent, and evolving

### 4. Runtime & Dependency Management
- Python version managed via pyenv (3.12+)
- Virtualenv and packages managed via pipenv
- Keep dependencies minimal and justified

### 5. Project Layout & CLI-First Design
- Standard library argparse (unless strong reason otherwise)
- All modules must:
  - Work as importable modules AND standalone executables
  - Start with `#!/usr/bin/env python3`
  - Include a `main()` function and `if __name__ == "__main__": main()` block

### 6. File-Level Metadata (every .py file)
Every Python file must include:
- A short module docstring describing the file's responsibility
- `__version__ = "0.1.0"` (semver)
- A `file_info()` function returning:
  - name
  - description
  - version
  - author (default "John Ayers")
  - last_updated (placeholder string)

### 7. Trunk-Based Solo Development
- Work in tiny vertical slices that always leave trunk releasable
- Keep PR-sized increments: tests + implementation + refactor + doc update
- Avoid speculative features
- No long-lived feature branches

### 8. Cloud-Focused Tooling (AWS/GCP)
- Prefer official SDKs: boto3/botocore and google-cloud-*
- Operations must be:
  - Idempotent when possible
  - Safe by default (use --dry-run options)
  - Logged with clear levels and human-readable messages
- Never hardcode credentials
- Use environment variables or cloud-native auth (IMDS, GCP metadata server)
- Separate cloud logic into infrastructure layer

## Project-Specific Context

**Project:** aws-vault-shuffle
**Purpose:** CLI tool to copy AWS Backup recovery points between AWS accounts at scale

**Initial Feature:** Retrieve all vaults and recovery points from specified account number and list of regions (configured via CLI args or config file)

## Ubiquitous Language

- **Vault**: AWS Backup vault containing recovery points
- **RecoveryPoint**: Individual backup snapshot with metadata (ARN, creation time, resource type, status)
- **RegionConfig**: Configuration specifying which AWS regions to scan
- **InventoryService**: Application service that orchestrates listing vaults and recovery points
- **AWSBackupAdapter**: Infrastructure component wrapping boto3 backup client

## Session History

Create dated session notes in `.claude/sessions/` for complex features or significant architectural decisions.

## Last Updated

2025-12-04 - Initial project scaffolding
