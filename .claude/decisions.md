# Architecture Decisions

This document tracks significant architecture and design decisions made during AI-assisted development.

## Decision Log

### [2025-12-04] Initial Architecture: DDD with Three Layers

**Context:**
Starting a new CLI tool to migrate AWS Backup recovery points between accounts. Need to keep cloud dependencies isolated and testable.

**Decision:**
Adopt lightweight Domain-Driven Design with three layers:
- **Domain**: Pure Python logic (Vault, RecoveryPoint dataclasses)
- **Application**: Use case orchestration (InventoryService)
- **Infrastructure**: AWS SDK calls (AWSBackupAdapter), config loading

**Rationale:**
- Keeps business logic cloud-agnostic and easily testable with fakes
- Enables TDD without slow AWS API calls
- Makes it easy to add GCP support later if needed
- Clear separation of concerns

**Alternatives Considered:**
- Flat structure with direct boto3 calls throughout
  - Rejected: Hard to test, couples logic to AWS SDK
- Full DDD with aggregates, repositories, events
  - Rejected: Over-engineered for a simple CLI tool

---

### [2025-12-04] Dependency Management: pipenv vs poetry vs uv

**Context:**
Need to manage Python dependencies and virtual environments.

**Decision:**
Use pipenv for dependency management.

**Rationale:**
- Specified in project guard rails
- Simple, well-established tool
- Pipfile/Pipfile.lock provide reproducible builds
- Good enough for solo development

**Alternatives Considered:**
- poetry: More features, but heavier
- uv: Faster, but newer and less stable
- requirements.txt: Too manual, no lock file

---

### [2025-12-04] CLI Framework: argparse vs Click vs Typer

**Context:**
Need to build command-line interface for list/copy/verify operations.

**Decision:**
Use standard library `argparse`.

**Rationale:**
- Specified in guard rails (use stdlib unless strong reason)
- No external dependencies
- Sufficient for our needs (subcommands, flags, help text)
- Familiar to most Python developers

**Alternatives Considered:**
- Click: Nice API, but adds dependency
- Typer: Modern with type hints, but adds dependency
- Both rejected: No compelling reason to add dependency

---

### [2025-12-04] Config Format: YAML vs JSON vs TOML

**Context:**
Users need to specify account number and regions in a config file.

**Decision:**
Use YAML for configuration files.

**Rationale:**
- Human-friendly (comments, multi-line, readable)
- Standard in DevOps tooling
- PyYAML is minimal dependency

**Alternatives Considered:**
- JSON: Less human-friendly, no comments
- TOML: Good, but YAML more familiar for AWS users
- ENV files: Not structured enough for lists

---

## Template for New Decisions

```markdown
### [YYYY-MM-DD] Brief Title

**Context:**
What problem are we solving? What constraints exist?

**Decision:**
What did we decide to do?

**Rationale:**
Why is this the best choice?

**Alternatives Considered:**
What else did we think about and why did we reject it?
```
