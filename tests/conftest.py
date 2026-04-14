import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--no-mocks",
        action="store_true",
        default=False,
        help="run e2e tests without mocks",
    )
