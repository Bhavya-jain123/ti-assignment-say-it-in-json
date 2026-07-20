# Starter configs

Sample `.pfcfg` trees for the assignment. **Do not edit these in place** — copy patterns into your `solution/` tests if you need variants.

## Layout

```
configs/
├── _base/              # shared defaults
├── templates/          # reusable pipeline templates
├── customers/          # per-customer entry configs
├── environments/       # environment overlays
└── edge-cases/         # stress tests for verifier design
```

See [`../briefs/format-reference.md`](../briefs/format-reference.md) for partial syntax rules.
