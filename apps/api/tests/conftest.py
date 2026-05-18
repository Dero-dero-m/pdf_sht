from collections.abc import AsyncIterator
from typing import Any

import pytest
import sqlalchemy
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.db import get_session
from app.deps import get_anthropic_client
from app.main import app as _app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine() -> AsyncEngine:
    # NullPool: don't cache connections across tests — pytest-asyncio creates a fresh
    # event loop per test, and asyncpg connections can't be reused across loops.
    return create_async_engine(get_settings().test_database_url, poolclass=NullPool)


@pytest.fixture
async def session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Per-test session against the test DB. Truncates the documents table to guarantee isolation."""
    connection = await test_engine.connect()
    SessionLocal = async_sessionmaker(bind=connection, expire_on_commit=False)
    async with SessionLocal() as s:
        await s.execute(sqlalchemy.text("TRUNCATE documents RESTART IDENTITY"))
        await s.commit()
        yield s
    await connection.close()


class FakeAnthropic:
    """Stand-in for anthropic.AsyncAnthropic. Override `.markdown` per test."""

    def __init__(self, markdown: str = "# Stub\n\nHello.") -> None:
        self.markdown = markdown
        self.calls: list[dict[str, Any]] = []

        class _Messages:
            async def create(inner_self, **kwargs: Any) -> Any:  # noqa: N805
                self.calls.append(kwargs)
                block = type("Block", (), {"type": "text", "text": self.markdown})()
                return type("Resp", (), {"content": [block]})()

        self.messages = _Messages()


@pytest.fixture
def fake_anthropic() -> FakeAnthropic:
    return FakeAnthropic()


@pytest.fixture
async def client(session: AsyncSession, fake_anthropic: FakeAnthropic) -> AsyncIterator[AsyncClient]:
    async def _override_session() -> AsyncIterator[AsyncSession]:
        yield session

    async def _override_anthropic() -> AsyncIterator[FakeAnthropic]:
        yield fake_anthropic

    _app.dependency_overrides[get_session] = _override_session
    _app.dependency_overrides[get_anthropic_client] = _override_anthropic
    transport = ASGITransport(app=_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    _app.dependency_overrides.clear()
