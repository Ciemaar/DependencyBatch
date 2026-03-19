# Jules & Copilot Instructions

This project uses specific tooling and standards for Python development. Please follow these guidelines when generating code or assisting with tasks.

## Project Context

- **Language:** Python 3.12+
- **Testing:** `pytest` with `hypothesis` for property-based testing.
- **Linting & Formatting:** `ruff`.
- **Type Checking:** `pyright`.
- **AWS Support:** Deferred. Do not implement AWS stubs (S3, SQS) at this time.

## Code Style & Standards

1. **Type Hints:** All new code must be fully type-hinted. Use modern syntax (`list[str]`, `str | None`) instead of `typing.List`, `typing.Optional`. In the event that typing cannot be applied, leave it off rather than using `Any` unless the intent is actually to support all data types.
1. **Nesting:** Keep nesting low where possible. Use early returns and `continue` statements in loops rather than nesting within an `if` block.
1. **Docstrings:** Use Google-style docstrings for all modules, classes, and public methods.
1. **Imports:** Group imports: standard library, third-party, local. `ruff` handles sorting, but be mindful.
1. **Error Handling:** Use specific exceptions. Avoid bare `except:`.

## Testing

- Write tests in `tests/`.
- Use `pytest` fixtures where appropriate.
- Aim for high test coverage, especially for core logic in `dependency_batch/`.
- Run tests with `PYTHONPATH=. pytest`.

## Tooling Commands

- **Lint:** `ruff check .`
- **Format:** `ruff format .`
- **Type Check:** `pyright .`
- **Test:** `PYTHONPATH=. pytest`

## JetBrains IDE / Copilot Specifics

- When using GitHub Copilot in JetBrains IDEs, ensure it is aware of the `pyproject.toml` configuration.
- Prefer suggestions that align with `ruff` rules (e.g., using `shutil` over `os` for file operations where safer).
- For more details on configuring custom instructions for JetBrains IDEs, refer to: [GitHub Docs: Configure custom instructions for JetBrains](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions?tool=jetbrains).
