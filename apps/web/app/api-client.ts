import type {
  DocumentDetail,
  DocumentList,
  DocumentSummary,
} from "@scaffold/shared-types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function listDocuments(): Promise<DocumentSummary[]> {
  const res = await fetch(`${BASE}/documents`, { cache: "no-store" });
  if (!res.ok) throw new Error(`listDocuments: ${res.status}`);
  const data: DocumentList = await res.json();
  return data.items;
}

export async function getDocument(id: number): Promise<DocumentDetail> {
  const res = await fetch(`${BASE}/documents/${id}`, { cache: "no-store" });
  if (res.status === 404) throw new Error("not-found");
  if (!res.ok) throw new Error(`getDocument: ${res.status}`);
  return res.json();
}

export async function uploadDocument(file: File): Promise<DocumentDetail> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${BASE}/documents`, { method: "POST", body: fd });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`upload failed: ${res.status} ${detail}`);
  }
  return res.json();
}

export function docxUrl(id: number): string {
  return `${BASE}/documents/${id}/docx`;
}
