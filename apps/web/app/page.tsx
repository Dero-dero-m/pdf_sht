import { DocumentList } from "./DocumentList";
import { UploadForm } from "./UploadForm";

export const dynamic = "force-dynamic";

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">PDF Parser</h1>
        <UploadForm />
      </header>
      <DocumentList />
    </main>
  );
}
