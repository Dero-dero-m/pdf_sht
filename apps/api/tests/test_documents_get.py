import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Document


@pytest.mark.asyncio
async def test_get_document_returns_detail(client: AsyncClient, session: AsyncSession) -> None:
    doc = Document(filename="a.pdf", page_count=1, byte_size=10, content_markdown="# Hi")
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    resp = await client.get(f"/documents/{doc.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == doc.id
    assert body["content_markdown"] == "# Hi"


@pytest.mark.asyncio
async def test_get_document_404(client: AsyncClient) -> None:
    resp = await client.get("/documents/9999")
    assert resp.status_code == 404
