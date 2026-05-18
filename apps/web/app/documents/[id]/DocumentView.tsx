"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import type { DocumentDetail } from "@scaffold/shared-types";
import { docxUrl } from "../../api-client";

export function DocumentView({ doc }: { doc: DocumentDetail }) {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-6 px-6 py-12">
      <nav className="flex items-center justify-between">
        <Link href="/" className="text-sm text-zinc-500 hover:underline">
          ← All documents
        </Link>
        <a
          href={docxUrl(doc.id)}
          className="inline-flex h-10 items-center rounded-full bg-black px-4 text-sm font-medium text-white dark:bg-white dark:text-black"
        >
          Download .docx
        </a>
      </nav>
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">{doc.filename}</h1>
        <p className="text-xs text-zinc-500">
          {doc.page_count} page{doc.page_count === 1 ? "" : "s"} · {new Date(doc.created_at).toLocaleString()}
        </p>
      </header>
      <article className="prose prose-zinc dark:prose-invert max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{doc.content_markdown}</ReactMarkdown>
      </article>
    </main>
  );
}
