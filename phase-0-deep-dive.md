# Phase 0 Deep-Dive — Setup & Workflow Foundation

**Calendar:** Weeks 1–2 of the plan. Calendar time: 2–3 weeks at sustainable pace.

**The job of this phase:** Build the scaffolding that makes every subsequent week cheaper. The mistake people make here is treating Phase 0 as "the boring part before the real learning" and rushing through it. The opposite is true: Phase 0 is the highest-leverage phase because *everything else compounds on what you build here*. A weak CLAUDE.md means re-explaining your conventions every session for six months. A weak starter monorepo means scaffolding the same boilerplate twelve times. A weak rhythm means burning out in week 5.

**How to use this document:** Read it once before starting Phase 0. Then keep it open as a checklist while you execute. Anything marked "skip on first pass" — actually skip it. The goal is *operational by end of week 2*, not perfect.

---

## How to Use This Plan

Two paragraphs of instruction so you don't have to figure it out while tired:

**The tool side, the concept side, the questions, the three flavors of importance.** Each phase document has four kinds of content. The **tool sections** tell you *what* exists and which to pick. The **concept sections** explain the underlying ideas — read these slower; they're what makes you actually good. The **open questions** at the end of the document are deliberately not answered — they're prompts for further study and are good fog-session material. And the **why-it-matters notes** come in two flavors that I'll mark explicitly: the *engineering* reason (why this matters for the system to work well) and, where it's not obvious, the *freelance* reason (why this matters for getting paid more or won bids). Lead with the engineering one; the freelance one is bonus.

**The execution loop.** Open this document at the start of the week, look at the week's deliverables in the main plan, find the relevant section here, read it, then *go work on it*. When the work hits a question you don't know the answer to, that question goes in your `LEARNINGS.md`. Don't try to read this document end-to-end before starting work — it's too long, and reading without doing produces no durable understanding. The pattern is: read enough to start, work, hit confusion, return to the document, re-read with sharper questions, work more. Two reads beat one read every time.

---

## The Mental Model for Phase 0

Phase 0 builds three artifacts:

1. **A workspace** — hardware, OS, terminal, editor, Claude Code, MCP, the basic dev environment
2. **A starter monorepo** — the boilerplate you'll fork for every project for the next 5 years
3. **A rhythm** — daily/weekly habits that survive fog days

Plus one rehearsal artifact: a throwaway project that exercises everything end-to-end, so you find the gaps before they cost you on a paid project.

The order matters. Workspace → starter → rhythm → rehearsal. Each depends on the previous.

---

## Concepts to Internalize This Phase

These are the mental scaffolds that make tool decisions cheap later. Each concept is short on purpose — internalize the *idea*, not memorize the words.

### 1. The dependency-graph view of dev environments

Every tool you install creates a node in a dependency graph. Future-you has to update, debug, or migrate every node. The cost of a tool is not its install cost — it's the *carrying cost over years*.

Practical implication: prefer fewer, deeper tools over many shallow ones. One terminal multiplexer (tmux), not three GUI alternatives. One package manager per language, not five. When evaluating "should I install X?", the question is "will I use this enough to justify maintaining it?"

**Engineering reason this matters:** A messy environment is a constant tax on every task. Five-minute friction × 1000 sessions = 80 hours/year of pure waste.

**Freelance reason:** Clients don't see your environment, but they *feel* it through your responsiveness. The freelancer with a clean rig ships in three days; the one re-fighting their setup ships in a week.

### 2. CLAUDE.md as durable context

Claude has a context window — it loads what's in front of it and forgets the rest. Every time you open a new Claude Code session, the context starts fresh. Without CLAUDE.md, you re-explain your conventions every session: "use Python 3.12, FastAPI not Flask, prefer Pydantic models, don't add comments unless I ask…" That's tax on every interaction.

CLAUDE.md is loaded automatically. It's *durable context*. The shift in mental model: stop thinking of Claude Code as a tool you talk to, start thinking of it as a tool you *configure*. The CLAUDE.md is the configuration.

**Engineering reason:** Reduces the variance of Claude's output. A well-configured Claude is a different tool than a default one. Without CLAUDE.md, you fight the same battles over and over (it adds excessive comments, picks the wrong libraries, structures files differently than the rest of your codebase). With CLAUDE.md, you set the rules once and they hold.

**Freelance reason:** When you onboard to a client codebase, the first artifact you create is *their* CLAUDE.md. This signals seniority — junior freelancers ask Claude to figure out conventions every time; senior freelancers codify them. Clients notice.

### 3. Reversibility classification

Some decisions are easily reversed (the file naming convention you picked). Some are nearly irreversible (the database engine after you've shipped to production with 50K rows). Most decisions sit on this spectrum.

The skill is *spending decision-making capacity proportional to reversibility*. A reversible decision deserves 5 minutes; an irreversible one deserves a fog session and a written decision doc. Most people invert this — they agonize over reversible choices ("which terminal theme") and rush irreversible ones ("which database").

**Engineering reason:** Reversibility-aware decision-making compounds. Move fast on reversible things; you can fix them later. Move carefully on irreversible things; the cost of a wrong choice is permanent.

**Freelance reason:** Clients' decision-making is often inverted — they obsess over reversible UX choices and rush past architectural ones. Your value as a freelancer is partly that you can spot this and gently redirect.

### 4. The verify habit (and the trust-but-verify default)

Claude Code generates code. The code looks plausible. Plausibility ≠ correctness. The pattern that distinguishes senior from junior Claude Code use is *aggressive verification*: every generated change is read, tested, and smoke-tested before commit.

This isn't paranoia — it's calibration. Claude is right ~80–90% of the time on routine tasks, but the 10–20% where it's wrong includes things like "drops a database table," "introduces a subtle race condition," "imports from a deprecated module." You don't know which case you're in until you check.

**Engineering reason:** The cost of a bug shipped is much higher than the cost of a 30-second verification. The math is asymmetric and obvious; the discipline to *actually do the verification* is the rare skill.

**Freelance reason:** The freelancer who ships subtle bugs to clients loses repeat business. The one who verifies before commit looks like they "just don't break things" — which is, weirdly, the most valued reputation a developer can have.

### 5. The lever queue and externalized cognition

Decisions are expensive when you're tired. Pre-made decisions are free. The lever queue is a FIFO list of small, pre-scoped tasks you maintain when energy is good and pull from when energy is low.

The deeper concept: your future self is a *different person* with less context, less energy, less working memory. Treat them like a junior developer you're handing off to. Leave them clear instructions, scoped tasks, and decision documents — not a vague mental note that "I'll remember."

**Engineering reason:** Cognitive load is the bottleneck on bad days, not skill or tooling. Externalization moves the cost from "execution time" to "preparation time" — and preparation time is cheap when energy is good.

**Freelance reason:** Doesn't directly apply, but the pattern transfers — clients who give you well-scoped tasks pay better than clients who give you vague directives. Recognizing the difference helps you bid better.

### 6. CLI-first as a workflow philosophy

You've already chosen CLI-primary as your direction. The deeper *why* worth internalizing:

- **CLI tools compose.** Pipe one into another. GUI tools don't compose.
- **CLI tools are scriptable.** Anything you do twice can be a script.
- **CLI tools are fast.** No mouse, no menus, no rendering.
- **CLI tools work everywhere.** SSH into a remote box and you have your whole stack. Try doing that with Cursor's GUI.
- **CLI tools have transparent state.** What's running is what you see; no hidden dialogs.

But CLI-first has costs: discoverability is worse (you have to *know* commands), and visualizations are weaker (looking at a chart in the terminal is genuinely worse than in a browser). The right pattern is CLI by default, GUI for visualization-heavy tasks (architecture diagrams, dashboards, large diffs).

**Engineering reason:** CLI workflows scale. You can SSH into your Mac Mini from a coffee shop laptop and have full power. You can script your dev setup. You can run things in parallel. GUI workflows hit a ceiling.

**Freelance reason:** CLI proficiency is an underrated bid signal. Clients meeting you on Zoom see your terminal — fluent CLI use signals "this person knows what they're doing" in a way that flipping through GUI menus doesn't.

---

## The Workspace Layer

### Hardware

You've already speced the Mac Mini M4 (16GB/512GB). The single most important configuration choice: **set it up as a headless SSH server from day one.** Don't connect a monitor, don't use it as a desktop. SSH from your existing Windows machines.

The reasoning: a headless dev server is a *different machine* than a desktop. It encourages CLI-first habits, it stays clean (no Slack notifications, no browser tabs eating RAM), and it forces you to script things. A Mac Mini you sit in front of becomes another desktop with another set of distractions.

**Why SSH-first matters specifically for AI work:** Long-running tasks (model loading, document indexing, batch embedding) want a stable backend you don't have to physically supervise. SSH + tmux + Claude Code lets a 4-hour indexing job run while you walk away. Plug a monitor into the Mac Mini and the temptation to "just check on it" never goes away.

**Skip on first pass:** GUI macOS configuration beyond the bare minimum. Don't customize the dock or wallpaper — you'll never see them. Don't install Homebrew GUI apps until you have a reason.

### Terminal & shell

Pick a terminal multiplexer and learn it. The two real options:

| Tool | When to pick | Strengths | Weaknesses |
|---|---|---|---|
| **tmux** | The default. Most documentation. | Ubiquitous, scriptable, runs over SSH natively. | Default keybindings are awkward; learning curve. |
| **Zellij** | Modern alternative. | Better defaults, discoverable UI, plugins. | Smaller community. |

**Recommendation:** tmux. Not because it's better, but because every SSH-based Linux server has tmux available and `man tmux` is everywhere. It's the *boring choice that compounds* — five years from now, your tmux skills will still apply.

The minimum tmux skill set: create sessions, detach/reattach, split panes (vertical and horizontal), switch between panes, kill panes, named sessions per project. That's about 15 minutes of practice and it becomes muscle memory in a week.

**Shell:** Stick with the default zsh on macOS unless you have a strong reason. Maybe install **Starship** for a fast cross-shell prompt — it's the closest thing to a free productivity boost in the shell layer.

**Skip on first pass:** elaborate shell themes, fish/nushell experiments, learning vim if you don't already know it (use a less-controversial editor for now and revisit later).

### Editor

You're going to use Claude Code as your primary code-touching surface. But you still need an editor for:
- Reading code without invoking Claude
- Quick edits where invoking Claude is overkill
- Viewing diffs
- Reviewing Claude's work

The default Mac Mini answer:
- **Neovim** if you already know vim or are willing to invest 2–3 weeks to learn (it pays back over a career; it doesn't pay back in a week)
- **Helix** if you want a modern vim-like that's easier to start with
- **VS Code** via SSH Remote, if you want a familiar GUI; this works headless because the GUI runs on the Windows machine

**Recommendation:** VS Code with the Remote-SSH extension is the path of least resistance. You get the familiar GUI on Windows, but the actual code lives on the Mac Mini and runs in the Mac Mini's environment. This is the practical hybrid that gets you started fastest.

**Open question for further study:** Should you eventually invest in Neovim? The answer depends on whether you'll do enough terminal-only work (e.g., SSH into a server with no GUI) to justify it. Defer this decision — six months of freelancing will tell you.

### Claude Code

Install it on the Mac Mini, not on your Windows machines. The mental model: the Mac Mini is *the* dev environment; Windows machines are thin clients that SSH in.

Configuration to do in week 1:

1. **Authenticate with your subscription.** Use the Anthropic account that has Claude.ai Pro/Max. Claude Code uses the same auth.
2. **Pick a default model.** Sonnet is the default; you can switch to Opus per-session for harder tasks. Don't bother changing the default.
3. **Configure tool permissions.** Claude Code asks before running shell commands. You can pre-approve patterns. Start with strict — approve only safe read-only commands. Loosen as you get comfortable.
4. **Set up the `~/.claude/` directory** with your global CLAUDE.md and your initial slash commands.

Claude Code's killer features that you should learn deliberately, in order of priority:

| Feature | Why it matters | When to use |
|---|---|---|
| **Plan mode** | Forces explicit thinking before execution. Highest-leverage feature in the tool. | Every nontrivial task. Default mode. |
| **Custom slash commands** | Crystallize your repeated patterns. Free productivity gain. | When you notice yourself typing the same thing twice. |
| **Subagents** | Specialized configurations for recurring task types. | When a task type recurs (code review, test writing, migrations). |
| **Hooks** | Pre/post-action scripts that prevent disasters and automate verification. | Once you have things worth protecting (Phase 2+). |
| **MCP integration** | Lets Claude Code call external tools/data sources. | Once you have MCP servers worth connecting (Phase 2+). |

**Engineering reason this matters:** Claude Code without configuration is ~30% as productive as Claude Code with configuration. The slash commands, CLAUDE.md, and hooks compound — each one saves seconds per use, and you use them thousands of times.

**Freelance reason:** Clients are slowly catching on that fluent Claude Code use is a 2–3× throughput multiplier. The freelancer with `/plan`, `/review`, `/test` reflexive in their fingers ships in days what others ship in weeks. This compounds into pricing power: you bid the same hours but produce more.

### MCP (Model Context Protocol)

You're not building MCP servers in Phase 0 — that's Phase 2. But you should *consume* one, just to understand the model.

Install the official Anthropic filesystem MCP server (or the GitHub one). Wire it into Claude Code. Now Claude Code can read your filesystem (or query GitHub) directly via the protocol, instead of you copy-pasting files in.

The conceptual lesson: **MCP is just a standardized way for AI agents to call external tools and read external resources.** That's it. The hype is justified because before MCP, every integration was bespoke — now they're plug-and-play. Phase 2 will go deep; Phase 0 is just first contact.

**Open question for further study:** What's the minimum useful MCP server you could build for your own workflow? (e.g., a server that reads your ATTENDANT data, or your prediction log.) Hold this question — it'll become the answer in Phase 2.

### Package management

| Language | Use this | Skip these |
|---|---|---|
| **Python** | `uv` (the modern, fast, Rust-based one) | `pip` directly, `poetry`, `pipenv`, `conda` |
| **Node.js** | `pnpm` | `npm`, `yarn` |
| **System packages on macOS** | `brew` | MacPorts |

`uv` is *the* modern Python package manager. It's 10–100× faster than pip, handles virtual environments transparently, and has a single sane command structure. Coming from `pip + venv`, the speed difference is shocking. Pick it now and don't look back.

`pnpm` over `npm` is a smaller but real win — it's faster, uses less disk space (deduplicates packages across projects), and has stricter dependency resolution that catches bugs npm misses.

**Engineering reason:** Package management is one of those layers where the boring answer is consistently the right one. `uv` and `pnpm` are the boring answers in 2026.

---

## The Starter Monorepo

This is the artifact you'll fork for every project for years. It's worth one week of investment.

### Monorepo concept (briefly)

A monorepo holds multiple related projects (frontend, backend, shared libraries) in one Git repository. The alternative is a *polyrepo* setup — separate repos per project. For solo freelance work, monorepo wins decisively because:

- One clone, one PR, one CI pipeline
- Shared types between frontend and backend in the same place
- Atomic changes across services (change the API and the frontend in one commit)
- Easier to spin up locally (one `docker compose up`)

The cost of a monorepo is shared dependencies — if your frontend wants Next.js 17 and your backend's Python wrapper wants something incompatible, you have to coordinate. For solo work this is rarely an issue.

### The structure

```
freelance-starter/
├── apps/
│   ├── web/                     # Next.js 16 App Router
│   └── api/                     # FastAPI + Pydantic AI
├── packages/
│   ├── shared-types/            # Pydantic models + zod schemas mirrored
│   └── ui/                      # shared shadcn components
├── infra/
│   ├── docker-compose.yml       # local services: postgres, redis, etc.
│   └── neon-branch.sh           # spin up per-PR DB branches
├── .claude/
│   ├── commands/                # custom slash commands
│   ├── agents/                  # subagent configs
│   └── mcp.json                 # MCP server wiring
├── CLAUDE.md                    # project context for Claude Code
├── pnpm-workspace.yaml          # pnpm monorepo config
└── README.md
```

### What goes in each piece, conceptually

#### `apps/web/` — the Next.js app

This is your frontend. Phase 1 will fill it out; Phase 0 just gets it scaffolded.

**Concept to internalize: App Router vs. Pages Router.** Next.js has two routing systems. Pages Router (the old one) is file-based and stable. App Router (the new one, since Next 13) is also file-based but supports React Server Components, streaming, layouts, and the modern patterns. **Use App Router.** Ignore tutorials that use Pages Router unless they're explicitly about migration.

**Concept to internalize: Server Components vs. Client Components.** This is the single most important Next.js concept and the most-confused. The TL;DR:

- **Server Components** run on the server, can access the database/file system directly, and never ship JavaScript to the client. They're fast and SEO-friendly. *Default to this.*
- **Client Components** run in the browser. They can use `useState`, `useEffect`, event handlers, browser APIs. Mark them with `"use client"` at the top of the file. *Use only when you need interactivity.*

Beginners mark everything `"use client"` because it "just works." This kills the whole benefit of App Router. Senior pattern: server components by default, push `"use client"` as far down the tree as possible (a button is client; the page wrapper is server).

**Open question for further study:** When does it make sense to fetch data in a Client Component vs. a Server Component? (Hint: server for initial render, client for user-driven refreshes.)

#### `apps/api/` — the FastAPI backend

This holds your Python API. Phase 1 fills it out.

**Concept to internalize: async vs. sync in Python.** FastAPI is async-first. Most LLM API calls are I/O-bound (you're waiting on a network response). Async lets one process handle many concurrent requests by switching tasks during I/O wait. Sync would block. For LLM-heavy work, async is critical — a sync FastAPI app handling 10 concurrent users would be 10× slower than the async version.

The mental model: `async def` is a function that *can pause*. `await` is the pause point. While it's paused, the event loop runs other tasks. You don't write threading code; the runtime handles it.

**Common gotcha:** if you call a sync function inside an async function, the entire event loop blocks. This is why "is this library async-compatible?" matters when picking dependencies. The OpenAI Python SDK has both `OpenAI()` (sync) and `AsyncOpenAI()` (async) — use the async one in FastAPI.

**Open question for further study:** When is it OK to mix sync and async? (FastAPI's docs have a good answer involving `run_in_threadpool` for unavoidable sync calls.)

#### `packages/shared-types/`

The thing that makes monorepos worth their weight. The frontend (TypeScript) and backend (Python) both need to know the shape of, say, a `ChatMessage`. Without sharing, you define it twice and they drift. With sharing, you define it once and use both.

The 2026 pattern: Pydantic models on the Python side, generate TypeScript types from them (via `pydantic2ts` or similar), import the generated types in the frontend. Whenever the Pydantic model changes, regenerate. The tooling for this is mature; the discipline is just "remember to regenerate."

Phase 0 just scaffolds the folder. Phase 1 fills it.

#### `packages/ui/`

Shared React components — the shadcn primitives plus any custom components you build. The reason this is a separate package: you want them importable from any frontend in the monorepo (web, admin, future mobile, etc.) without copy-pasting.

#### `infra/docker-compose.yml`

This file is the single most important productivity tool in your monorepo. It defines the local services you need: Postgres (with pgvector), Redis, maybe MinIO for S3-compatible storage.

When a new project starts (or when you SSH into the Mac Mini after a week away), `docker compose up -d` and your entire backend stack is running. No "wait, did I install Postgres?" No "what version of Redis was this?" The compose file is the truth.

**Concept to internalize: containers vs. VMs.** A container is a process that thinks it has its own filesystem and network, but actually shares the host kernel. They start in milliseconds and use almost no overhead. VMs are full virtual machines — minutes to start, gigabytes of RAM. For dev environments, containers win every time.

**Skip on first pass:** Kubernetes. It's container *orchestration* for production at scale. You don't need it. `docker compose` is sufficient through Phase 4 and beyond.

#### `.claude/`

The Claude Code configuration for this project. This directory commits with your code, so when you fork the starter, you fork the Claude configuration too. This is a quietly enormous productivity gain — your slash commands, subagents, and MCP wiring travel with the project.

#### `CLAUDE.md`

The single most important text file in your monorepo. Treated separately below.

### The CLAUDE.md template — explained

A CLAUDE.md should have these sections:

```markdown
# Project: [name]

## What this is
[One paragraph. Audience: a senior developer joining tomorrow.]

## Stack & conventions
[Versions, file structure, naming, lint/format/test commands, gotchas.]

## Workflows
[How to add a feature, run locally, deploy, the "don't do X" list.]

## Current state / TODO
[Living scratchpad. Last worked on X. Open question Y.]
```

**Why each section exists:**

- **What this is** — Without context, Claude generates plausible-but-generic code. The first paragraph tells Claude *what kind of system this is*, which biases all subsequent generation toward appropriate patterns.

- **Stack & conventions** — Stops Claude from picking different libraries each session. "Use `uv`, not pip. Use `pnpm`, not npm. We're on Python 3.12 and Node 22. Lint with ruff, format with ruff, type-check with mypy strict. Test with pytest. Commands: `make test`, `make lint`, `make format`."

- **Workflows** — The "we add features by..." section. "New API endpoint: define Pydantic schema in `shared/schemas/`, route in `api/routes/`, integration test in `tests/`. Don't import from `legacy/`."

- **Current state / TODO** — Where you write *what you were last doing* before you stopped. Six days later when you come back, this is the difference between "what was I working on" (10 minutes lost) and immediate resumption.

**The discipline:** update CLAUDE.md *every Friday* during your weekly polish. It rots if you don't.

### The five Phase 0 slash commands — explained

> **Status note (2026-05-16):** These five commands are **not** implemented in this repo's `.claude/commands/`. They were filtered to user scope and live in `~/.claude/commands/` instead, so they apply to every project rather than being forked per-starter. The project-local `.claude/commands/` directory is deliberately left empty. Future Claude Code sessions: do **not** add `/plan`, `/review`, `/explain`, `/test`, or `/decompose` to `.claude/commands/` here — that's a user-scope decision, not a project-scope one. Project-local slash commands are still fair game when a command is genuinely repo-specific.

Custom slash commands live in `~/.claude/commands/` (global) or `.claude/commands/` (project-local). They're markdown files where the filename becomes the command and the content is the prompt template.

The templates below are kept here for reference (so the user-scope versions can be regenerated if they're ever lost), not as a build list for this project:

#### `/plan`

```markdown
Read the relevant files in the codebase. Then propose a plan for: $ARGUMENTS

Do not execute. Output:
1. Files you'd touch
2. Key decisions and the reasoning
3. Risks or unknowns
4. Estimated time
```

**Why:** Forces explicit thinking before execution. The single highest-leverage habit in Claude Code use.

#### `/review`

```markdown
Review the diff staged in git for:
- Bugs and edge cases
- Security issues (SQL injection, XSS, secrets in code)
- Performance concerns
- Style consistency with the codebase
- Whether it matches the original intent

Be specific. Cite file:line.
```

**Why:** Treats Claude as a code reviewer. Catches what you miss when you're tired. Pairs with the verify habit.

#### `/explain`

```markdown
Explain $ARGUMENTS as if onboarding me to this codebase.
- What does it do?
- How does it fit in the system?
- What invariants does it rely on?
- What would break if it changed?

Use plain language.
```

**Why:** When you encounter unfamiliar code, this beats reading line-by-line. Especially useful in client codebases.

#### `/test`

```markdown
Write tests for $ARGUMENTS.
- Mirror the existing test structure (look at /tests or alongside the file)
- Cover happy path, edge cases, and error cases
- Don't test implementation details; test behavior
```

**Why:** Test-writing is repetitive. Claude does it well when given the existing patterns. The `/test` command pairs with the verify habit — write code, write tests, run them.

#### `/decompose`

```markdown
Break $ARGUMENTS into atomic, independently-shippable steps.
Each step should:
- Be completable in 30-60 minutes
- Leave the codebase in a working state
- Be reviewable in isolation

Output as a numbered list with brief descriptions.
```

**Why:** Big tasks become unmanageable when held in your head. Decomposition externalizes the structure. Especially useful for fog-session compatibility — a decomposed task can be picked up one step at a time on bad days.

### Subagents (briefly)

Subagents are specialized Claude configurations for recurring task types. Each subagent has its own system prompt, its own context, and its own permissions.

You don't need them in Phase 0 — they're a Phase 1+ tool. But know they exist. The mental model: **a slash command is a one-shot prompt template; a subagent is a persistent specialist with memory of its role.**

Phase 0 placeholder: create `.claude/agents/` directory. Build out subagents in Phase 1.

### Hooks (briefly)

Hooks are scripts that run *before* or *after* Claude Code takes actions. They live in `.claude/hooks/`.

You probably don't need hooks in Phase 0 — there's nothing to protect yet. But Phase 2 will introduce safety hooks (block destructive shell commands, prevent force-push to main, require confirmation before touching prod). Know they exist; learn the mechanism in Phase 0 if you want, but don't configure aggressive hooks before you have things worth protecting.

**Open question for further study:** What's the minimum hook set that prevents the most likely disasters? (Suggested answer: block `rm -rf` outside `/tmp`, block `git push --force`, block raw `DROP TABLE`. Three hooks, ~95% of likely disasters caught.)

---

## The Rhythm

The plan only works if executed. Phase 0 establishes the rhythm.

### The energy-tiered daily structure

Repeating from the main plan because it's load-bearing:

| Energy | Time block | What you do |
|---|---|---|
| Good | 2× 90-min deep blocks | Real implementation. Plan-then-execute. The hardest brick of the week. |
| Medium | 1× 90-min block | Polish, debugging, docs. Test-writing. Lighter Claude Code use. |
| Low | 1× 45-min fog session | Read docs. Watch one technical talk. Update CLAUDE.md. |
| Zombie | 0 commits | Walk. Sleep. The plan still progresses because the system runs without you. |

**Why 90-minute blocks:** Research on cognitive cycles (ultradian rhythms) suggests humans concentrate well for 60–120 minutes before performance degrades. 90 is a reasonable midpoint. Past 90, you're producing slop and verifying poorly. Take a 15-minute break, walk, come back for the second block.

**Why two blocks max on Good days:** Above 3 blocks/day, you compound tiredness into the next day. The plan is built for sustainability. Heroic 12-hour days are not the goal; consistent 3-hour days are.

### The fog session protocol

Use when energy is low but you want progress:

1. Pick from the lever queue (no decision-making during fog sessions)
2. Set a 45-min timer
3. Plan-mode in Claude Code — it generates, you evaluate
4. Execute or read
5. One commit, or one paragraph in a doc, or one closed tab — any concrete artifact
6. Add the next lever queue item for future-you

The fog session is *the* load-bearing daily practice. It's the version of the plan that runs on bad days.

**Why fog sessions matter:** Most plans assume "good days." Real life has bad days. A plan that produces zero output on bad days produces 30–50% less than its potential. A plan with a graceful fog mode produces 70–90% of its potential because *something* shipped on the bad days.

### The weekly cadence

```
Monday        — Plan the week. Pick the brick. Write the milestone.
Tuesday–Thu   — Build. Two deep blocks/day on Good days.
Friday        — Polish. Tests. Docs. Update CLAUDE.md.
Saturday      — Review (30 min). Update lever queue. Then rest.
Sunday        — Off. Or one restorative fog session.
```

**Why Saturday review and not Sunday:** Sunday review is too close to Monday — you can't act on the review until next week, and the review becomes guilt-laden ("I should be working"). Saturday review with Sunday rest separates *thinking about work* from *doing work*. Sunday is genuinely off.

### The artifacts (`RHYTHM.md`, `LEVER_QUEUE.md`)

Maintain both in your starter monorepo (or in a personal-meta repo if you want to keep them out of project repos).

`RHYTHM.md` contains:
- The energy-tiered structure
- The fog session protocol
- Your weekly cadence
- Anything you've learned about your own patterns

`LEVER_QUEUE.md` contains:
- A FIFO list of small (45–90 min), pre-scoped tasks
- Each entry: what to do, where it touches, what done looks like
- Add to it during Saturday review; pull from it during fog sessions

**Engineering reason:** These docs externalize cognition. Without them, every day starts with "what should I do today?" — a decision that's expensive on tired days. With them, the decision is pre-made.

---

## The Throwaway Dogfood Project

Spec: a tiny project that uses the full stack end-to-end, deployed publicly, *thrown away after the lesson is learned*.

### Why throwaway specifically

The temptation is to make the dogfood project *real* — "as long as I'm building something, let me make it useful." Resist this. Throwaway means:
- You can break things without consequence
- You can experiment with patterns you're not sure about
- You can abandon it when you've learned what you needed
- The pressure is off — you're testing the workflow, not building a product

A real project pulls you into "make it good," which is the opposite of "discover where the workflow is thin."

### What it should test

The minimum end-to-end loop:

1. **Frontend:** A Next.js page with a single button or form
2. **Backend:** A FastAPI endpoint the button calls
3. **LLM:** The endpoint hits Claude or OpenAI
4. **Storage:** The result is stored in Postgres (with pgvector if you want to test that)
5. **Deploy:** The whole thing is live at a URL

The point isn't the feature — it's that you've exercised every layer. You'll discover:
- Your CLAUDE.md is missing something (you keep re-explaining a pattern)
- Your Docker Compose is missing something (you forgot to add Redis)
- Your verify habit needs a slash command shortcut
- You're slower than you thought at one specific layer

These are the lessons Phase 0 exists to surface. Better to surface them on a throwaway than on a real client project.

### Suggested throwaway projects

- **A daily-news summarizer** that pulls 5 RSS feeds, summarizes via Claude, posts the summary to a tiny Next.js page
- **A `/q` Telegram bot** that takes a question, hits an LLM, returns the answer
- **A "mood log" CLI** that takes a 1–10 rating, stores it in SQLite, and graphs it on a tiny web page

Pick one in 5 minutes. Don't deliberate. The point is the workflow exercise.

### Concept to internalize: deployment as a *first-class skill*

Most beginners treat deployment as "the thing at the end." This is wrong. Deployment is a layer of the stack you have to be fluent in, because:

- A project that doesn't deploy doesn't exist (clients can't see it)
- Deployment problems compound — fix them at the throwaway stage, not at the bid-winning portfolio stage
- "Works on my machine" is the most expensive sentence in software

The Phase 0 deployment goal: **the throwaway is on a public URL within 5 days**. If you hit a deployment wall, that's a *feature* of the dogfood project — it surfaces something you needed to learn.

**Open question for further study:** Vercel + Railway is the default. Why not Fly.io? When would you pick Fly? (Hint: edge use cases, persistent volumes, longer-running processes.)

---

## Phase 0 Tools — The Full Inventory

Compressed reference for everything mentioned above:

| Tool | Layer | Phase 0 priority | Why |
|---|---|---|---|
| **Mac Mini M4 + macOS** | Hardware | Essential | Already specced |
| **tmux** | Terminal | Essential | Multiplexer; survives SSH disconnects |
| **Starship** | Shell prompt | Important | Fast, informative prompt |
| **VS Code + Remote-SSH** | Editor | Essential | Path of least resistance |
| **Claude Code** | AI dev environment | Essential | The whole point |
| **Docker + Docker Compose** | Containers | Essential | Local dev environment |
| **uv** | Python pkg mgr | Essential | Modern, fast, sane |
| **pnpm** | Node pkg mgr | Essential | Better than npm |
| **Git + GitHub** | Version control | Essential | Default |
| **GitHub Actions** | CI/CD | Important | Free for public repos; ship in Phase 1 |
| **Vercel account** | Hosting (frontend) | Important | Sign up; deploy in Phase 1 |
| **Railway or Fly.io account** | Hosting (backend) | Important | Sign up; deploy in Phase 1 |
| **Neon account** | Database | Important | Sign up; use in Phase 1 |
| **Anthropic API key** | LLM | Essential | Already have |
| **OpenAI API key** | LLM | Essential | Need for embeddings + fallback |
| **OrbStack** | Docker on Mac | Optional | Faster than Docker Desktop, free for personal use |
| **OpenRouter account** | LLM gateway | Optional | Phase 1+ |

**Skip explicitly on first pass:**
- Kubernetes / k3s
- A database GUI (use `psql` from the terminal; you'll appreciate it later)
- Helm, Terraform, anything Infrastructure-as-Code
- Custom shell themes beyond Starship
- Multiple LLM provider accounts beyond OpenAI + Anthropic
- Self-hosted Langfuse (use Cloud free tier in Phase 1)
- Better Auth, Clerk (Phase 1 decision)

---

## Common Failure Modes in Phase 0

The things that most commonly derail this phase, with mitigations:

### "I'll set up the perfect environment"

Two weeks in, you're still tweaking your tmux config. The starter monorepo doesn't exist. No dogfood project shipped.

**Mitigation:** Set a deadline. *End of week 2: monorepo committed, throwaway deployed.* Anything not on that critical path is excluded. Tmux config tweaking is exclusion zone.

### "I'll learn everything before building"

You read the FastAPI docs front to back, the Next.js docs front to back, every page of the Pydantic AI repo. No code shipped.

**Mitigation:** The throwaway dogfood project is the antidote. You can't read your way to fluency — you have to build. Reading without doing produces the *illusion* of competence; building reveals the gaps.

### "I'll skip the boring setup and get to the cool AI stuff"

You skip the monorepo, skip CLAUDE.md, skip the rhythm, jump straight to building docchat. Six weeks later, you're still re-explaining your conventions to Claude every session and you've never deployed anything.

**Mitigation:** Phase 0 is non-negotiable. It feels boring because it doesn't have visible AI output, but it's the highest-leverage phase. Trust the plan.

### Heroic week → collapse

You do 50 hours in week 1, get tons done, feel great. Week 2 you can barely function. Week 3 you're behind, demoralized.

**Mitigation:** Cap your daily effort even on Good days. Two 90-minute blocks max. The plan assumes sustainable pace. Heroic effort *steals from your future weeks.*

---

## Phase 0 Success Criteria — Detailed

The criteria from the main plan, expanded:

- [ ] **You can start a fresh Claude Code session, type `/plan`, describe a task, and Claude produces a plan that respects your conventions without you re-explaining them.** *Test:* open a new session in your starter monorepo, run `/plan add a /healthcheck endpoint to the FastAPI app`. The plan should reference your async pattern, your Pydantic conventions, your test patterns.

- [ ] **You can open the starter monorepo and have a local dev environment running in under 10 minutes.** *Test:* Time yourself. Clone the repo into a fresh directory, `docker compose up -d`, install dependencies, start dev servers, hit a URL. Under 10 minutes including the time to read your own README.

- [ ] **The throwaway project is deployed and accessible at a URL.** *Test:* Send the URL to someone (anyone), they can use it.

- [ ] **`RHYTHM.md` exists and you've followed it for at least 5 days.** *Test:* You can describe what you did each of the last 5 days using the energy tiers. At least one of those days was a fog session that produced output.

If any of these aren't true at the end of week 2, *don't move to Phase 1 yet.* Spend 2–3 more days getting them solid. The cost of weak Phase 0 → catastrophic Phase 1 is far higher than the cost of an extra few days here.

---

## Open Questions for Further Study

Things deliberately not answered above. Each is a good fog-session prompt or weekend reading:

1. **What's the minimum useful CLAUDE.md for a client codebase you're onboarding to?** (You'll answer this in Phase 4 when you onboard to your first client.)

2. **When does it make sense to fetch data in a Client Component vs. a Server Component in Next.js?** (Phase 1 will surface this — when you build the docchat frontend.)

3. **When is it OK to mix sync and async in FastAPI?** (Phase 1 will surface this — when you have an unavoidable sync dependency.)

4. **What's the minimum hook set that prevents the most likely disasters?** (Phase 2 will revisit this when you have things worth protecting.)

5. **What's the minimum useful MCP server you could build for your own workflow?** (Phase 2 will answer this directly.)

6. **Is Neovim worth the 2–3 week investment for you specifically?** (Defer until Month 6+ of freelancing — by then you'll know.)

7. **When should you consider switching from `pnpm` to a different Node package manager?** (Probably never, but Bun's package manager is worth watching.)

8. **At what scale of dev environment does Kubernetes make sense?** (Almost never for solo freelance — but understanding *why* it exists helps with enterprise clients later.)

9. **What's your personal "Good day" baseline?** (Track this for 4 weeks. It's the input to realistic week-planning.)

10. **What's the minimum viable backup strategy for the Mac Mini?** (Time Machine + GitHub for code. But what about local databases, secrets, your `.claude/` directory? Resolve this before you accumulate anything irreplaceable.)

---

## Closing Note on Phase 0

The temptation throughout Phase 0 is to feel like you're *not really learning*. You haven't built a RAG system. You haven't shipped an AI agent. You've configured tmux and written a CLAUDE.md and made a tiny project that summarizes news.

The truth: every hour spent on Phase 0 *saves 5–10 hours* in Phase 1+. The starter monorepo is reused. The CLAUDE.md skills transfer to every client codebase. The slash commands fire thousands of times. The rhythm is the difference between a sustainable 6-month project and a 5-week flameout.

Phase 0 is invisible work that compounds. Trust the plan. Ship the boring artifacts. Phase 1 starts when these are solid — not when you feel like moving on.

When you finish Phase 0, the next document is `phase-1-deep-dive.md`. Don't skim ahead. Phase 0 is enough to think about.
