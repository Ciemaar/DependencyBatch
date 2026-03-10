# Tooling Evaluation

This document outlines the evaluation of various development tools for the `dependency_batch` project. Our goal is to use modern, fast, and type-safe tools that provide a great developer experience.

## Formatting & Linting

### Candidates:

- **Black + Flake8 + isort:** The traditional standard. Very stable, but requires running multiple Python-based CLI tools, which can be slow and require complex configuration synchronization.
- **Ruff:** An extremely fast Python linter and code formatter written in Rust. It replaces Flake8, Black, isort, pydocstyle, and many other tools.

**Decision:** **Ruff**

- *Justification:* Ruff is orders of magnitude faster. By consolidating formatting, import sorting, and linting into a single tool, it simplifies `pyproject.toml` and CI workflows. It natively supports the Google docstring convention we require.

## Type Checking

### Candidates:

- **Mypy:** The original standard type checker for Python. Robust and widely used, but can be slow on large codebases and sometimes struggles with complex type inferences (like advanced generics).
- **Pyright:** Microsoft's fast type checker written in TypeScript. Excels at complex type inference, provides excellent IDE integration (Pylance in VS Code), and is generally much faster than Mypy.
- **Ty:** A newer, blazingly fast type checker written in Rust by Astral (creators of Ruff). Still early in development but very promising.

**Decision:** **Pyright**

- *Justification:* While `ty` was evaluated and is incredibly fast, `pyright` offers a more mature, stable type-checking environment with proven accuracy and widespread IDE support. `pyright` perfectly handles our `Iterable`, `Path`, and standard library generics. We migrated from `ty` back to `pyright` based on stability requirements.

## Testing

### Candidates:

- **unittest:** Built into Python. Verbose, requires class-based test structures, and has less powerful mocking/fixture systems out of the box.
- **pytest:** The industry standard for Python testing. Supports simple function-based tests, powerful dependency injection via fixtures, and an immense plugin ecosystem.

**Decision:** **pytest** (along with `pytest-cov` and `hypothesis`)

- *Justification:* Pytest makes tests incredibly easy to write and read. We utilize `pytest-cov` to enforce our strict 100% test coverage requirement. We also adopted **Hypothesis** for property-based testing, which automatically generates edge-case data for our queue operations, finding bugs traditional unit tests might miss.

## Documentation Generation

### Candidates:

- **Sphinx:** The traditional documentation generator (used by Python itself). Extremely powerful but uses reStructuredText (reST) by default, which has a steeper learning curve than Markdown.
- **MkDocs (with Material theme):** A fast, simple static site generator geared towards project documentation. Uses standard Markdown (which we already write in our `docs/` folder) and the Material theme is widely considered the best-looking and most accessible documentation theme available.

**Decision:** **MkDocs (Material Theme)**

- *Justification:* Our documentation is already written in Markdown (`user_guide.md`, `developer_guide.md`). MkDocs allows us to seamlessly compile these into a beautiful, searchable static website with minimal configuration.

## Markdown Formatting

### Candidates:

- **Prettier:** Excellent formatter, but requires a Node.js environment (via `nodeenv`), complicating a pure Python stack.
- **mdformat:** A Python-based, commonmark-compliant Markdown formatter.

**Decision:** **mdformat**

- *Justification:* Keeps our dependency stack pure Python. Integrates easily into CI and formatting hooks alongside Ruff.

## Pre-commit Automation

To ensure all these tools run locally before a developer pushes code, we need an automation tool.

**Decision:** **pre-commit**

- *Justification:* The industry standard for managing git pre-commit hooks. It ensures `ruff`, `pyright`, and `mdformat` run automatically, preventing broken or unformatted code from reaching GitHub.
