# Jules & Copilot Instructions

This project uses specific tooling and standards for Python development. Please follow these guidelines when generating code or assisting with tasks.

## Project Context

- **Language:** Python 3.12+
- **Testing:** `pytest` with `hypothesis` for property-based testing.
- **Linting & Formatting:** `ruff` universally; `mdformat` for Markdown.
- **Type Checking:** `pyright` in strict mode.
- **AWS Support:** Deferred. Do not implement AWS stubs (S3, SQS) at this time.
- **Data Privacy & LLMs:** Treat data as private and local-first. Never send sensitive data to third-party cloud LLM APIs. Default to local inference servers (e.g., Ollama).
- **Package Management:** `uv` is exclusively mandated. `pip`, `poetry`, and `pipenv` are prohibited. Ensure `uv.lock` is always checked into version control.
- **Configuration Model:** Mandate `pydantic-settings` universally for configs.
- **CLI Framework:** Mandate `click` for CLIs and require a `--verbose` flag that sets logging to `DEBUG`. (No `argparse`).
- **Database/Web Frameworks:** Migrate `pymongo` to `motor.motor_asyncio.AsyncIOMotorClient`. Use `FastAPI` to replace complex JS single-page applications.

## Code Style & Standards

1. **Type Hints:** All new code must be fully type-hinted. Use modern syntax (`list[str]`, `str | None`) instead of `typing.List`, `typing.Optional`. Avoid `typing.Any`.
1. **Ternary Operators:** Never use `x or y` shortcut syntax for non-boolean results (e.g., `value or 0.0`). Always use explicit ternary operations like `x if x is not None else y`.
1. **Imports:** Strictly enforce top-of-file imports. Avoid inline/local imports except to break circular imports.
1. **Logging:** Always use the `logging` module (or `structlog`). Never use `print()` for logging.
1. **File & IO:** Strip out `os.path` and use `pathlib.Path` for all path logic. Require context managers for resource cleanup.
1. **Exceptions:** Do not use `assert` statements in production code. Raise an appropriate built-in exception instead.
1. **Serialization:** Always prefer YAML with `yaml.safe_load`. Avoid `pickle` for untrusted data.
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
