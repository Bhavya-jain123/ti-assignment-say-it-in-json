# Say It in JSON

A take-home assignment for harness engineering and agentic system design.

Read [`candidate/intro.md`](../../candidate/intro.md) first if you have not already — it explains how we hire and why your AI session exports matter more than polish on the final code.

---

## Scenario

You have joined **PipelineForge**, a fictional CI/CD platform. For fifteen years, customer build pipelines have been configured in a text format called **`.pfcfg`** — a crusty INI dialect with comments, file includes, conditional blocks, and environment-variable interpolation. It works. Nobody loves it.

The platform lead, **Jordan Okonkwo**, is migrating every customer to a **JSON-based config format**. There are thousands of customer configs in the wild. Jordan's memo (linked below) is blunt: **a wrong migration silently breaks customer builds**. Customers may not notice until a release fails in production. The migration converter matters less than **proof that it is correct**.

You inherit:

- A **starter directory** of sample legacy configs ([`starter/configs/`](starter/configs/)) — representative of real customer trees, including a few nasty edge cases.
- A **partial format reference** ([`briefs/format-reference.md`](briefs/format-reference.md)) — enough to parse the samples, deliberately incomplete on how includes and interpolation should behave in JSON.

Your job is not to build a production-grade migration service for thousands of tenants. Your job is to **design the target JSON schema** (Jordan left this underspecified on purpose), **build a converter** by driving an AI agent, and **construct equivalence verification** — machinery that demonstrates old-config and new-config produce **identical effective settings** for the same environment, plus a **report for configs that cannot be migrated automatically**.

Read Jordan's brief. The business constraint — silent failure — should shape every decision you make.

| Document | From |
| -------- | ---- |
| [Platform lead brief](briefs/platform-lead-brief.md) | Jordan Okonkwo, Platform Lead |
| [Format reference (partial)](briefs/format-reference.md) | Internal wiki excerpt |

---

## What you are building

There is a **starter config tree** but **no starter code**. You choose language, tooling, and dependencies. We expect a **thin vertical slice**: schema + converter + verifier + unmigratable report.

At minimum, your solution must include:

1. **A JSON schema (documented)** for the target format — including your decisions on how to represent features that have no direct JSON equivalent (includes, conditional blocks, cross-key references, interpolation). A JSON Schema file, a TypeScript interface, or equivalent formal description is fine.
2. **A converter** from `.pfcfg` → your JSON format for the configs in `starter/configs/` (and any additional test configs you add).
3. **A reference evaluator** for legacy `.pfcfg` that computes **effective settings** — the fully resolved configuration for a given environment.
4. **Equivalence verification** that, for each config, compares effective settings from the legacy path vs. the JSON path and reports match/mismatch with enough detail to debug failures. Run this against at least:
   - one CI-like fixture (`CI` set and non-empty), and
   - one non-CI fixture (`CI` unset or empty),
   plus any extra fixtures you need.
5. **An unmigratable report** — machine-readable output (JSON or NDJSON) listing items that cannot be converted or verified automatically. Each item must include at least: `file`, `section`, `key`, and `reason` (`line` optional).

You decide how much to build beyond this. A strong submission is narrow, verified, and honest about what "equivalent" means — not a feature-complete migration platform.

---

## Deliverables

Submit everything below. Incomplete submissions are acceptable if your `DECISIONS.md` says what is missing and what you would do next.

### 1. Working artifact (`solution/`)

Your schema, converter, reference evaluator, and verification harness. Include:

- `README.md` with setup and how to run the converter and verifier (target: a reviewer can run it in **≤ 15 minutes** on a laptop with only free tools).
- Enough code to demonstrate the behaviors you claim on the starter configs.

### 2. AI session exports (`sessions/`)

**This is the primary deliverable we evaluate.**

Export **every working session** you used to build this assignment — Cursor, Claude Code, Windsurf, Copilot Chat, or any other agentic tool. Each export must include:

- **Your prompts** (what you asked, in full — not summaries you wrote later).
- **The agent's detailed output** — tool calls, reasoning, code diffs, errors, retries. Sanitized marketing screenshots are not substitutes.

**Cursor users:** use *Export Chat* (or equivalent) to produce `.md` files. Name them in chronological order, e.g. `01-schema-design.md`, `02-converter.md`.

**Other tools:** submit the closest equivalent full transcript. If your tool cannot export, paste raw logs into markdown files. Do not paraphrase the agent's output.

Hiding, heavily editing, or omitting sessions **disqualifies** the submission. We are hiring people who drive AI in the open.

### 3. Decisions note (`DECISIONS.md`)

One page or less. Structured prose, not a novel. Cover:

- How you represented includes, conditionals, and interpolation in JSON — and what you rejected.
- Your definition of **effective settings** and why it matches (or deliberately approximates) legacy behavior.
- What your verifier proves and what it does *not* prove.
- Known gaps in the starter configs or your solution.
- What you would build next with another four hours.

---

## AI mandate

**Heavy AI use is required.** Use agents aggressively for implementation, research, and debugging.

The transcript is not a confession — it is your portfolio. We score how you frame problems, pack context the agent cannot know, decompose work, catch bluffs, and recover from failures. A beautiful repo with an empty or sanitized `sessions/` folder tells us nothing useful.

---

## What we evaluate

We read your session exports against a rubric focused on **driving**, not typing:

| Dimension | What we look for |
| --------- | ---------------- |
| **Understanding** | Did you grasp silent-failure risk and schema tradeoffs before coding? |
| **Prompting** | Clear goals, useful context (evaluation order, include graphs), iterative refinement |
| **Critical review** | Noticing where AI output is plausible but incorrect; questioning whether your verifier actually proves equivalence |
| **Debugging** | Systematic diagnosis when verifier and converter disagree |
| **Decomposition** | Deliberately sequenced work with real decisions between phases, not one giant prompt |
| **Communication** | A reviewer can follow your intent from the exports and `DECISIONS.md` alone |

We do **not** grade variable names, micro-optimizations, or framework fashion. Agents already do that better than we can manually.

---

## Timebox and definition of done

| | |
| --- | --- |
| **Expected effort** | 4–6 hours |
| **Hard cap** | One weekend from when you receive this assignment |
| **Done enough** | Runnable converter + verifier + unmigratable report + honest `DECISIONS.md` + complete session exports |

Submitting unfinished work with a clear "here is what I would do next" is **better signal** than a rushed façade of completeness. Death-marches to fake polish are noise.

---

## Submission logistics

Follow these steps exactly. Ambiguity here is unfair; ambiguity in schema design is the assignment.

1. **Fork** this repository to your own GitHub account.
2. Create your submission directory:

   ```
   submissions/<your-github-username>/say-it-in-json/
   ├── solution/          # schema, converter, verifier + README
   ├── sessions/          # AI session exports (.md)
   └── DECISIONS.md
   ```

3. **Open a pull request** against the upstream `ti-hiring` repository with your submission. Title format: `[submission] <your-github-username> — Say It in JSON`.
4. In the PR description, include:
   - Total time spent (honest estimate).
   - One sentence on the hardest decision you made.
5. **Do not** commit API keys, paid-service credentials, or real customer data. Use fake values in environment fixtures.

If you cannot open a PR (private fork policy, etc.), email a link to your fork and the commit SHA instead — but PR is strongly preferred.

---

## Questions

Questions about the assignment? Email [recruiter@pipelineforge-hiring.example.invalid](mailto:recruiter@pipelineforge-hiring.example.invalid).

---

## Source documents

- [Platform lead brief — "Silent failures are worse than slow migrations"](briefs/platform-lead-brief.md)
- [Format reference — `.pfcfg` syntax (partial)](briefs/format-reference.md)
- [Starter config tree](starter/configs/)

Good luck. We are looking for someone in command — not a perfect run.
