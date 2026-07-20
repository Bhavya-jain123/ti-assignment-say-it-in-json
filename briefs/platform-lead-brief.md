# Brief from Jordan Okonkwo, Platform Lead

**To:** New harness engineer (you)  
**Re:** `.pfcfg` → JSON migration — proof before rollout  
**Date:** Internal — fictional scenario

---

Look, I'm not going to dress this up. We're fifteen years into PipelineForge running on `.pfcfg` files. Every customer has a directory tree. Some are fifty lines; some are five thousand with includes stacked six deep. The format is ugly but **deterministic** — or at least, it's been deterministic long enough that everyone has stopped asking questions.

We're moving to JSON. Not because JSON is better. Because every other tool in the ecosystem speaks JSON, our new pipeline editor is JSON-native, and I'm tired of maintaining a bespoke parser in three languages.

## What actually keeps me up at night

**Wrong migrations that look fine.**

We've seen this movie. A competitor shipped a config converter that passed their internal tests, rolled it out, and spent six weeks unwinding customer incidents. Builds didn't fail immediately — they failed when someone toggled a feature flag, or when a cached layer expired, or when an env var was unset on a Tuesday. The converter had translated syntax correctly and **semantics incorrectly**.

That's the bar. I don't care if your converter is slow. I don't care if it's pretty. I care that you can **prove** old and new configs produce the same effective settings for the same environment.

"Effective settings" means: after includes, conditionals, and interpolation are resolved, what does the pipeline actually see? Not the on-disk text. Not a pretty-printed JSON tree. The **resolved key-value reality**.

## What I'm asking you to deliver (this assignment slice)

This is a thin slice of the real program. Realistically we have **thousands** of customer trees. You get a **starter sample** (~15 files) that is representative — including a few configs our support team has flagged as "weird."

You need to:

1. **Design the JSON schema.** I'm intentionally not giving you one. Includes don't exist in JSON. Neither does `${VAR:-$(section.fallback)}`. You decide how we represent those. Document the tradeoffs. If your schema can't round-trip, say so.

2. **Build a converter.** Use your AI tools — that's how we work here. But read what it generates, line by line. We've shipped converters before that translated syntax perfectly and semantics wrong. Passed every test we had at the time. Took a team a week to find in production.

3. **Build verification.** Some machinery — tests, a CLI, property checks, whatever — that demonstrates equivalence. I want to run one command and see green/red per config, not eyeball diffs.

4. **Report what you can't migrate.** Some configs will need human review. I want a machine-readable report: which file, which key, why. "Skipped" is not an answer. "Unresolved `$(build.compiler)` — circular reference detected" is.

## What I'm not asking for

- A hosted migration service.
- Perfect coverage of every `.pfcfg` edge case from 2009.
- A JSON Schema that validates every internal wiki example — the wiki is wrong in places.

## Success criteria (you define the details)

I'll know you're done when I can:

1. Run your converter on `starter/configs/`.
2. Run your verifier with a few environment fixtures you provide.
3. See which configs pass, which fail, and which are unmigratable — with reasons I trust.

If your verifier passes but you can't explain what it proves, that's a fail.

— Jordan
