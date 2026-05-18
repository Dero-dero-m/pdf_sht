from typing import Any

import anthropic
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.deps import get_anthropic_client
from app.models import Document
from app.services.pdf_parser import extract_markdown
from scaffold_shared_types.schemas import DocumentDetail

router = APIRouter(prefix="/documents", tags=["documents"])


def _count_pages(pdf_bytes: bytes) -> int:
    return max(pdf_bytes.count(b"/Type /Page"), 1)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DocumentDetail)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    anthropic_client: Any = Depends(get_anthropic_client),
) -> DocumentDetail:
    settings = get_settings()
    if (file.content_type or "").lower() != "application/pdf" and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only application/pdf uploads are accepted.")
    data = await file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_bytes} bytes.")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        markdown = await extract_markdown(
            data,
            file.filename or "document.pdf",
            client=anthropic_client,
            model=settings.anthropic_model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {exc}") from exc

    doc = Document(
        filename=file.filename or "document.pdf",
        page_count=_count_pages(data),
        byte_size=len(data),
        content_markdown=markdown,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return DocumentDetail.model_validate(doc, from_attributes=True)
