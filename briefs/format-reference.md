# PipelineForge Config (`.pfcfg`) — Format Reference

**Status:** Internal wiki excerpt. **Incomplete by design** — several semantic rules are disputed in `#config-migration` and have not been finalized for the JSON migration.

---

## Overview

`.pfcfg` files are UTF-8 text. They configure PipelineForge build pipelines: toolchains, steps, artifacts, notifications, and environment-specific overrides.

Files are organized in customer directories and composed via includes. A single **entry config** (e.g. `pipeline.pfcfg`) typically pulls in shared templates and environment overlays.

---

## Basic syntax

```ini
# Comment to end of line
; Also a comment

[section]
key = value

[parent.child]
nested_key = another value
```

- **Sections** use `[name]` or `[dotted.path]`. Keys belong to the most recent section header.
- **Keys** use `key = value`. Whitespace around `=` is ignored.
- **Quoted values** use double quotes. Inside quotes, `\"` and `\\` are escaped. Unquoted values cannot contain leading/trailing whitespace (trimmed).
- **List values** are comma-separated without spaces after commas, e.g. `steps = compile,test,publish`.

---

## Includes

```ini
@include relative/path.pfcfg
@include_once shared/base.pfcfg
```

- Paths are **relative to the directory of the file containing the directive**.
- `@include` merges the included file's sections and keys into the current config tree.
- `@include_once` skips the file if that exact path was already included in this load (tracked per top-level entry config).
- Include directives must appear **before** any section headers in that file.

**Open question for JSON migration:** JSON has no include mechanism. Decide how your schema represents this and defend the tradeoff in `DECISIONS.md`.

---

## Conditional blocks

```ini
@ifdef CI
[build]
parallel = true
@endif

@ifndef DEPLOY_KEY
[deploy]
; block omitted when DEPLOY_KEY is set
skip = true
@endif
```

- `@ifdef VAR` … `@endif` — block is parsed only if `VAR` is set and non-empty in the process environment.
- `@ifndef VAR` … `@endif` — block is parsed only if `VAR` is unset or empty.
- Conditionals can wrap section headers and keys. Nested conditionals are supported.

**Open question:** Order of conditional evaluation relative to includes is not documented here. Resolve it from how the starter configs behave and state your interpretation in `DECISIONS.md`.

---

## Interpolation

Values may contain:

| Syntax | Meaning (as commonly implemented) |
| ------ | ----------------------------------- |
| `${VAR}` | Value of environment variable `VAR`, or empty string if unset |
| `${VAR:-default}` | `VAR` if set and non-empty, else `default` |
| `${VAR:+alternate}` | `alternate` if `VAR` set and non-empty, else empty |
| `$(section.key)` | Value of another key after includes/conditionals are merged |
| `$(dotted.section.key)` | Same; section path is dot-separated |

**Disputed / undocumented:**

- The production parser enforces a maximum expansion pass limit; behavior beyond it is an error. The exact limit is not documented here — pick a reasonable one, document it in `DECISIONS.md`, and make sure your verifier can detect and report the case.
- Circular `$(section.key)` references — behavior is error, not infinite loop.

**Open question for JSON migration:** JSON has no interpolation mechanism. Decide how your schema represents these values and defend the tradeoff in `DECISIONS.md`.

---

## Starter configs

See [`../starter/configs/`](../starter/configs/). Entry points for verification:

| Entry config |
| ------------ |
| `customers/acme-corp/pipeline.pfcfg` |
| `customers/globex/pipeline.pfcfg` |
| `customers/initech/pipeline.pfcfg` |
| `edge-cases/interpolation-cascade.pfcfg` |
| `edge-cases/conditional-includes.pfcfg` |

---

## What this document does not specify

- A canonical JSON target schema (your job).
- Equivalence definition beyond informal "effective settings" (your job).
- Behavior when the same key is set in an included file and a conditional block (resolve empirically from starter configs and document your interpretation).

If you and the agent disagree with this reference, **state your interpretation in `DECISIONS.md`** and make your verifier encode it.
