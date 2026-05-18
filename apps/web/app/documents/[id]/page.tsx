import { notFound } from "next/navigation";

import { getDocument } from "../../api-client";
import { DocumentView } from "./DocumentView";

export const dynamic = "force-dynamic";

export default async function DocumentPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const docId = Number(id);
  if (!Number.isFinite(docId)) notFound();
  let doc;
  try {
    doc = await getDocument(docId);
  } catch (err) {
    if (err instanceof Error && err.message === "not-found") notFound();
    throw err;
  }
  return <DocumentView doc={doc} />;
}
