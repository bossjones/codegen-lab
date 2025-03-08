from typing import TYPE_CHECKING, Literal

import pytest

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest


@pytest.fixture
def anyio_backend() -> Literal["asyncio"]:
    """Configure the backend to use for anyio fixtures.

    This fixture is used by pytest-anyio to determine which async backend
    to use when running async tests. We're using asyncio as our backend.

    Returns:
        Literal["asyncio"]: The name of the anyio backend to use.

    """
    return "asyncio"
