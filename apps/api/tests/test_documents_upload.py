import io

import pytest
from httpx import AsyncClient

from tests.conftest import FakeAnthropic


def _minimal_pdf(pages: int = 1) -> bytes:
    # Just needs the magic header and enough "/Type /Page" markers for the page-count heuristic.
    body = b"%PDF-1.4\n" + b"\n".join(b"/Type /Page" for _ in range(pages))
    return body + b"\n%%EOF\n"


@pytest.mark.asyncio
async def test_upload_pdf_persists_document(client: AsyncClient, fake_anthropic: FakeAnthropic) -> None:
    fake_anthropic.markdown = "# Title\n\nBody."
    pdf = _minimal_pdf(pages=3)
    files = {"file": ("doc.pdf", io.BytesIO(pdf), "application/pdf")}
    resp = await client.post("/documents", files=files)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["filename"] == "doc.pdf"
    assert body["page_count"] == 3
    assert body["byte_size"] == len(pdf)
    assert body["content_markdown"] == "# Title\n\nBody."
    assert isinstance(body["id"], int)


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf(client: AsyncClient) -> None:
    files = {"file": ("a.txt", b"hello", "text/plain")}
    resp = await client.post("/documents", files=files)
    assert resp.status_code == 400
    assert "pdf" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_rejects_oversize(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "10")
    files = {"file": ("big.pdf", b"%PDF-1.4 lots of bytes here", "application/pdf")}
    resp = await client.post("/documents", files=files)
    assert resp.status_code == 413
    get_settings.cache_clear()
