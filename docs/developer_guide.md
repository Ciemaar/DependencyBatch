# Developer Guide

Welcome to the `dependency_batch` project developer guide! This document explains how to set up your environment, run tests, and contribute to the codebase.

## Environment Setup

### Prerequisites

- Python 3.12 or higher
- Git

### Creating a Virtual Environment

It's highly recommended to use a virtual environment for development.

```bash
# Clone the repository
git clone <repository_url>
cd <repository_url>

# Create a virtual environment
python3 -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

### Installing Dependencies

Install the development tools required:

```bash
pip install -r requirements.txt
```

This installs tools like `pytest`, `hypothesis`, `ruff`, `pyright`, and `mdformat`.

## Development Workflow

### Testing

This project uses `pytest` for unit testing and `hypothesis` for property-based testing. Tests are located in the `tests/` directory.

To run the entire test suite:

```bash
PYTHONPATH=. pytest
```

To run a specific test file:

```bash
PYTHONPATH=. pytest tests/test_dependency_batch.py
```

### Type Checking

We use `pyright` to enforce type safety. All new code must be fully type-hinted using modern Python syntax (e.g., `list[str]` instead of `typing.List[str]`).

To run the type checker:

```bash
pyright .
```

### Linting and Formatting

We use `ruff` to enforce code style and formatting. It replaces tools like `flake8`, `isort`, and `black`.

To check for linting errors:

```bash
ruff check .
```

To format code automatically:

```bash
ruff format .
```

To check formatting without modifying files (useful in CI):

```bash
ruff format --check .
```

### Markdown Formatting

We use `mdformat` to ensure consistent markdown styling across documentation files.

To format all markdown files:

```bash
mdformat .
```

To check markdown formatting:

```bash
mdformat --check .
```

## Continuous Integration (CI)

This repository is configured with GitHub Actions. The workflow in `.github/workflows/ci.yml` runs automatically on every push and pull request to the `main` or `master` branches.

The CI pipeline runs:

1. `ruff check .`
1. `ruff format --check .`
1. `mdformat --check .`
1. `pyright .`
1. `pytest`

All these checks must pass before a PR can be merged.

## Architecture Guidelines

- **Python Version:** Always write code compatible with Python 3.12+. Avoid using deprecated standard library functions (e.g., use `tempfile` instead of `os.tmpnam`).
- **Security:** Be mindful of file operations. When working with archives, use secure extraction methods (e.g., `tarfile.extractall(filter="data")` to prevent ZipSlip attacks).
- **AWS Integration:** AWS integration (S3, SQS) is explicitly deferred. Do not implement AWS stubs or features without consulting the project roadmap.
