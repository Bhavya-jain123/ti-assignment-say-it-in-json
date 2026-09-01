# Design Decisions

## 1. Goal

The goal of the migration is to represent the supplied `.pfcfg`
configuration format in JSON while preserving its effective behavior.

A migrated configuration is considered correct when its fully resolved
configuration matches the configuration produced by the original
`.pfcfg` evaluator under the same environment.

---

## 2. JSON representation

The JSON format contains:

- a version number
- explicit includes
- normal configuration sections
- conditional configuration blocks

The representation preserves constructs that affect evaluation rather
than storing only the final resolved values.

This allows the migrated configuration to be evaluated under different
environments.

---

## 3. Includes

Includes are represented explicitly instead of being flattened during
conversion.

This preserves the relationship between the main configuration and its
included files and allows include and include_once behavior to be
handled during evaluation.

Include paths are interpreted relative to the file containing the
include.

---

## 4. Conditionals

Conditional blocks such as `@ifdef` and `@ifndef` are preserved in the
JSON representation.

They are evaluated using the runtime environment.

For example, an `@ifdef CI` block is active when `CI` exists and is
non-empty.

This avoids making environment-specific decisions during conversion.

---

## 5. Interpolation

Environment interpolation and configuration-key interpolation are
preserved during conversion.

Examples include:

- `${VARIABLE}`
- `${VARIABLE:-default}`
- `${VARIABLE:+alternative}`
- `$(section.key)`

Interpolation is resolved by the evaluator rather than permanently
replacing values during conversion.

---

## 6. Equivalence verification

The migration is verified by evaluating both representations:

    original .pfcfg
          |
          v
    legacy evaluator
          |
          v
    effective configuration

and:

    migrated JSON
          |
          v
    JSON evaluator
          |
          v
    effective configuration

The resulting effective configurations are then compared.

This focuses verification on behavior rather than textual similarity
between the two formats.

---

## 7. Circular references

Cross-key interpolation can create cycles.

For example:

    a.x -> b.y -> a.x

The evaluator detects such cycles and reports them rather than entering
an infinite expansion loop.

---

## 8. Unmigratable configurations

The migration should not silently guess when a configuration cannot be
handled safely.

Such cases are recorded in an unmigratable report containing the file,
section, key, and reason where available.

This makes limitations visible to the migration operator.

---

## 9. Test environments

The verification process tests configurations under both:

- `CI=1`
- `CI=""`

This is necessary because conditional configuration can produce
different effective results depending on the environment.

---

## 10. Scope

The implementation focuses on the syntax and semantic behavior
represented by the supplied assignment fixtures.

Unsupported or unsafe constructs are reported rather than silently
changing their meaning.
