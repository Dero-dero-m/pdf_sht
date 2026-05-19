export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-8 px-6 py-16">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">PDF Parser</h1>
        <div className="h-12 w-32 rounded-full bg-zinc-200 dark:bg-zinc-800 animate-pulse" />
      </header>
      <ul className="divide-y divide-zinc-200 dark:divide-zinc-800 w-full">
        {[0, 1, 2].map((i) => (
          <li key={i} className="py-3 flex items-center justify-between">
            <div className="h-4 w-48 rounded bg-zinc-200 dark:bg-zinc-800 animate-pulse" />
            <div className="h-3 w-32 rounded bg-zinc-200 dark:bg-zinc-800 animate-pulse" />
          </li>
        ))}
      </ul>
    </main>
  );
}
