# Submission directory (template)

This folder shows the expected layout. **Do not submit your work here** — create your own path under `submissions/<your-github-username>/say-it-in-json/` at the repository root.

See [`../assignment.md`](../assignment.md) for full instructions.

## Expected structure

```
submissions/<your-github-username>/say-it-in-json/
├── solution/
│   ├── README.md           # setup + how to run converter and verifier (≤15 min)
│   └── ...                 # schema, converter, reference evaluator, harness
├── sessions/
│   ├── 01-schema-design.md # chronological AI session exports
│   ├── 02-...
│   └── ...
└── DECISIONS.md            # one-page decisions note (see DECISIONS.template.md)
```

## Session export checklist

- [ ] Every working session included, in order
- [ ] Full user prompts (not summaries)
- [ ] Full agent output (tool calls, errors, code — not curated highlights)
- [ ] No secrets or real PII in exports
