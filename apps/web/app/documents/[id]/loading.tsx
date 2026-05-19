export default function Loading() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-6 px-6 py-12">
      <nav className="flex items-center justify-between">
        <div className="h-4 w-28 rounded bg-zinc-200 dark:bg-zinc-800 animate-pulse" />
        <div className="h-10 w-36 rounded-full bg-zinc-200 dark:bg-zinc-800 animate-pulse" />
      </nav>
      <header className="flex flex-col gap-2">
        <div className="h-7 w-2/3 rounded bg-zinc-200 dark:bg-zinc-800 animate-pulse" />
        <div className="h-3 w-1/3 rounded bg-zinc-200 dark:bg-zinc-800 animate-pulse" />
      </header>
      <article className="flex flex-col gap-3">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-3 rounded bg-zinc-200 dark:bg-zinc-800 animate-pulse"
            style={{ width: `${85 - i * 7}%` }}
          />
        ))}
      </article>
    </main>
  );
}
