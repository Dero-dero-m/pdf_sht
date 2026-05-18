"""Canonical Pydantic schemas. TS types are generated from this module."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):
    id: int
    filename: str
    page_count: int
    byte_size: int
    created_at: datetime


class DocumentDetail(DocumentSummary):
    content_markdown: str = Field(description="Markdown extracted by Claude.")


class DocumentList(BaseModel):
    items: list[DocumentSummary]
