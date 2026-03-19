# Reusable Prompts for Session Reproduction

If you wish to use an AI agent (such as Jules) to achieve a similar modernization refactoring on another repository, you can provide these prompts sequentially.

## 1. Initial Modernization

```text
Upgrade this codebase to modern libraries, Python versions and development practices. Add support for at least python 3.13. Add ruff format, ruff check, tests, and type hinting. Add stubs for the AWS services used in testing.
```

## 2. Refine Architecture & Focus

```text
1. Go ahead and fill in the missing pieces.
2. Do not implement AWS stubs, that will be future work.
3. Yes, upgrade deprecated functions (e.g. os.tmpnam).
4. Use pytest and hypothesis if appropriate.
```

## 3. Configure Testing & Typing specific Tools

```text
Switch type checking to pyright. Add checking for test coverage in the github hooks, no PR should reduce test coverage. Review test coverage results and add any needed tests. Ensure 100% coverage is enforced.
```

## 4. Documentation & Best Practices

```text
Add/update readme and documentation. Add instructions suitable to Jules and JetBrains IDEs, reference this page for additional details https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions?tool=jetbrains. Add user and developer documentation.
```

## 5. Static Analysis & Styling Adjustments

```text
1. Add and run a markdown formatter in this project, make it part of the checks run by github on every PR.
2. Check spelling, punctuation, and grammar of all documentation.
3. Enable ruff checks for missing function, class, and module docstrings. Add any missing docstrings. Ensure that docstrings are meaningful and not placeholders added just to pass tests.
```

## 6. Packaging & Project Configuration

```text
1. Are pytest and the other development tools properly included in the pyproject.toml file so developers can install them easily? Move dev tools into an optional dependency group.
2. Next, move settings as much as possible into pyproject.toml.
3. Add a build-system block to ensure `pip install -e .` works properly.
```

## 7. Granular Code Refactoring (Example PR Feedback)

```text
1. Change the dependency and results variables from lists to sets. The type should be Iterable.
2. Change the `local_dir` property to be a `pathlib.Path` object instead of a string.
3. Make the Job class a context manager that returns `get_local_folder` on enter and closes on exit.
4. Keep nesting low where possible. Use early returns and continue statements in loops rather than nesting within an `if` block.
5. In the event that typing cannot be applied, leave it off rather than using `Any` unless the intent is actually to support all data types. Add these formatting/typing rules to the agent instructions.
```

## 8. Tool Evaluation

```text
Evaluate and test alternative tools for formatting, linting, testing, type checking, documentation, and similar. Keep notes on the suitability of each to this project and adopt the best set of tools. Document this in docs/tooling_evaluation.md.
```
