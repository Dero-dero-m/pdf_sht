import base64

import pytest

from app.services.pdf_parser import extract_markdown
from tests.conftest import FakeAnthropic


@pytest.mark.asyncio
async def test_extract_markdown_sends_pdf_as_base64_document_block() -> None:
    fake = FakeAnthropic(markdown="# Hello\n\nWorld.")
    pdf = b"%PDF-1.4 fake bytes"
    md = await extract_markdown(pdf, "doc.pdf", client=fake, model="claude-sonnet-4-6")
    assert md == "# Hello\n\nWorld."
    assert len(fake.calls) == 1
    call = fake.calls[0]
    assert call["model"] == "claude-sonnet-4-6"
    user_msg = call["messages"][0]
    assert user_msg["role"] == "user"
    blocks = user_msg["content"]
    doc_block = next(b for b in blocks if b["type"] == "document")
    assert doc_block["source"]["type"] == "base64"
    assert doc_block["source"]["media_type"] == "application/pdf"
    assert base64.b64decode(doc_block["source"]["data"]) == pdf


@pytest.mark.asyncio
async def test_extract_markdown_raises_on_empty_response() -> None:
    fake = FakeAnthropic(markdown="")
    with pytest.raises(ValueError, match="empty"):
        await extract_markdown(b"x", "doc.pdf", client=fake, model="m")
