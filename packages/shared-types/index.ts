/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface DocumentDetail {
  id: number;
  filename: string;
  page_count: number;
  byte_size: number;
  created_at: string;
  /**
   * Markdown extracted by Claude.
   */
  content_markdown: string;
}
export interface DocumentList {
  items: DocumentSummary[];
}
export interface DocumentSummary {
  id: number;
  filename: string;
  page_count: number;
  byte_size: number;
  created_at: string;
}
