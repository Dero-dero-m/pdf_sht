from pathlib import PurePosixPath
from typing import Any

import anthropic
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.deps import get_anthropic_client
from app.models import Document
from app.services.docx_export import markdown_to_docx_bytes
from app.services.pdf_parser import extract_markdown
from scaffold_shared_types.schemas import DocumentDetail, DocumentList, DocumentSummary

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


@router.get("", response_model=DocumentList)
async def list_documents(session: AsyncSession = Depends(get_session)) -> DocumentList:
    result = await session.execute(
        select(Document).order_by(Document.created_at.desc(), Document.id.desc())
    )
    docs = result.scalars().all()
    return DocumentList(
        items=[DocumentSummary.model_validate(d, from_attributes=True) for d in docs]
    )


@router.get("/{doc_id}", response_model=DocumentDetail)
async def get_document(doc_id: int, session: AsyncSession = Depends(get_session)) -> DocumentDetail:
    doc = await session.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentDetail.model_validate(doc, from_attributes=True)


@router.get("/{doc_id}/docx")
async def download_docx(doc_id: int, session: AsyncSession = Depends(get_session)) -> Response:
    doc = await session.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    body = markdown_to_docx_bytes(doc.content_markdown)
    stem = PurePosixPath(doc.filename).stem or "document"
    headers = {"content-disposition": f'attachment; filename="{stem}.docx"'}
    return Response(
        content=body,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )
