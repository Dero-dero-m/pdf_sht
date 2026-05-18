"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { uploadDocument } from "./api-client";

export function UploadForm() {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  async function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    try {
      const doc = await uploadDocument(file);
      startTransition(() => router.push(`/documents/${doc.id}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      e.target.value = "";
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <label className="inline-flex items-center justify-center h-12 px-5 rounded-full bg-black text-white cursor-pointer dark:bg-white dark:text-black">
        {pending ? "Uploading…" : "Upload PDF"}
        <input type="file" accept="application/pdf" onChange={onChange} hidden />
      </label>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
