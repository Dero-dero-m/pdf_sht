"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { uploadDocument } from "./api-client";

export function UploadForm() {
  const router = useRouter();
  const [navPending, startTransition] = useTransition();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const busy = uploading || navPending;

  async function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      const doc = await uploadDocument(file);
      startTransition(() => {
        router.refresh();
        router.push(`/documents/${doc.id}`);
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <label
        aria-busy={busy}
        className={`inline-flex items-center justify-center h-12 px-5 rounded-full bg-black text-white dark:bg-white dark:text-black ${
          busy ? "cursor-not-allowed opacity-70" : "cursor-pointer"
        }`}
      >
        {busy && (
          <span
            className="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
            aria-hidden
          />
        )}
        {uploading ? "Parsing PDF…" : navPending ? "Opening…" : "Upload PDF"}
        <input
          type="file"
          accept="application/pdf"
          onChange={onChange}
          disabled={busy}
          hidden
        />
      </label>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
