import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document


@pytest.mark.asyncio
async def test_list_documents_returns_summaries_newest_first(client: AsyncClient, session: AsyncSession) -> None:
    session.add_all([
        Document(filename="a.pdf", page_count=1, byte_size=10, content_markdown="A"),
        Document(filename="b.pdf", page_count=2, byte_size=20, content_markdown="B"),
    ])
    await session.commit()

    resp = await client.get("/documents")
    assert resp.status_code == 200
    body = resp.json()
    filenames = [item["filename"] for item in body["items"]]
    assert filenames == ["b.pdf", "a.pdf"]
    # Summaries omit content_markdown
    assert "content_markdown" not in body["items"][0]
