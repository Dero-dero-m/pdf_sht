import Link from "next/link";

import { listDocuments } from "./api-client";

export async function DocumentList() {
  const docs = await listDocuments();
  if (docs.length === 0) {
    return <p className="text-sm text-zinc-500">No documents yet.</p>;
  }
  return (
    <ul className="divide-y divide-zinc-200 dark:divide-zinc-800 w-full">
      {docs.map((d) => (
        <li key={d.id} className="py-3 flex items-center justify-between">
          <Link href={`/documents/${d.id}`} className="font-medium hover:underline">
            {d.filename}
          </Link>
          <span className="text-xs text-zinc-500">
            {d.page_count} page{d.page_count === 1 ? "" : "s"} · {new Date(d.created_at).toLocaleString()}
          </span>
        </li>
      ))}
    </ul>
  );
}
