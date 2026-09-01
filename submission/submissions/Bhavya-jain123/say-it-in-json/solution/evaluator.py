import json
import os
import re
from pathlib import Path


MAX_EXPANSION_DEPTH = 20


class EvaluationError(Exception):
    pass


def is_truthy(value):
    """CI-style condition: present and non-empty."""
    return value is not None and str(value) != ""


def get_nested_value(config, path):
    """
    Resolve a dotted key such as:
        build.compiler
    """
    parts = path.split(".")

    current = config

    for part in parts:
        if not isinstance(current, dict) or part not in current:
            raise EvaluationError(
                f"unknown configuration key: {path}"
            )

        current = current[part]

    return current


def expand_string(value, config, env, stack=None, depth=0):
    """
    Resolve:
        ${VAR}
        ${VAR:-default}
        $(section.key)
    """

    if stack is None:
        stack = []

    if depth > MAX_EXPANSION_DEPTH:
        raise EvaluationError("maximum interpolation depth exceeded")

    # $(section.key)
    key_pattern = re.compile(r"\$\(([^)]+)\)")

    def replace_key(match):
        key = match.group(1).strip()

        if key in stack:
            cycle = " -> ".join(stack + [key])
            raise EvaluationError(
                f"circular reference detected: {cycle}"
            )

        referenced = get_nested_value(config, key)

        if isinstance(referenced, (dict, list)):
            return str(referenced)

        return expand_string(
            str(referenced),
            config,
            env,
            stack + [key],
            depth + 1
        )

    previous = None

    while previous != value:
        previous = value
        value = key_pattern.sub(replace_key, value)

    # ${VAR}, ${VAR:-default}, ${VAR:+alternative}
    env_pattern = re.compile(
        r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::([-+])([^}]*))?\}"
    )

    def replace_env(match):
        name = match.group(1)
        operator = match.group(2)
        argument = match.group(3)

        value = env.get(name)

        if operator is None:
            return "" if value is None else str(value)

        if operator == "-":
            # Use default when variable is unset or empty.
            if not is_truthy(value):
                return argument
            return str(value)

        if operator == "+":
            # Use alternative when variable is set and non-empty.
            if is_truthy(value):
                return argument
            return ""

        return ""

    value = env_pattern.sub(replace_env, value)

    return value


def resolve_value(value, config, env):
    """Recursively resolve values inside dictionaries/lists."""

    if isinstance(value, str):
        return expand_string(value, config, env)

    if isinstance(value, list):
        return [
            resolve_value(item, config, env)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: resolve_value(item, config, env)
            for key, item in value.items()
        }

    return value


def flatten_config(config):
    """
    Convert:

        {
            "build": {
                "compiler": "gcc"
            }
        }

    into:

        {
            "build.compiler": "gcc"
        }
    """

    result = {}

    def visit(value, prefix):
        if isinstance(value, dict):
            for key, child in value.items():
                new_prefix = (
                    f"{prefix}.{key}"
                    if prefix
                    else key
                )
                visit(child, new_prefix)
        else:
            result[prefix] = value

    visit(config, "")

    return result


def evaluate_json(json_path, env=None):
    """
    Evaluate the migrated JSON configuration.
    """

    if env is None:
        env = {}

    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    sections = data.get("sections", {})

    # First create a copy of the raw configuration.
    resolved = sections

    # Apply conditionals.
    for conditional in data.get("conditionals", []):
        variable = conditional["variable"]
        condition_type = conditional["type"]

        value = env.get(variable)

        active = (
            is_truthy(value)
            if condition_type == "ifdef"
            else not is_truthy(value)
        )

        if not active:
            continue

        for section, values in conditional["sections"].items():
            if section not in resolved:
                resolved[section] = {}

            resolved[section].update(values)

    resolved = resolve_value(
        resolved,
        resolved,
        env
    )

    return flatten_config(resolved)


def evaluate_legacy(path, env=None, included_files=None):
    """
    Evaluate the original .pfcfg configuration.

    Handles:
      - sections
      - key/value pairs
      - @include
      - @include_once
      - @ifdef
      - @ifndef
      - @endif
      - environment interpolation
      - cross-key interpolation
    """

    if env is None:
        env = {}

    path = Path(path).resolve()

    if included_files is None:
        included_files = set()

    # Prevent include loops.
    if path in included_files:
        return {}

    included_files.add(path)

    config = {}

    current_section = None
    condition_stack = [True]

    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    for line_number, raw_line in enumerate(lines, start=1):

        line = raw_line.strip()

        # Ignore blank lines.
        if not line:
            continue

        # Ignore comments.
        if line.startswith("#") or line.startswith(";"):
            continue

        # ---------------------------------------------------------
        # CONDITIONALS
        # ---------------------------------------------------------

        match = re.match(
            r"^@(ifdef|ifndef)\s+([A-Za-z_][A-Za-z0-9_]*)$",
            line
        )

        if match:
            condition_type = match.group(1)
            variable = match.group(2)

            value = env.get(variable)

            if condition_type == "ifdef":
                condition = is_truthy(value)
            else:
                condition = not is_truthy(value)

            # Nested conditions only work if the parent is active.
            condition_stack.append(
                condition_stack[-1] and condition
            )

            continue

        if line == "@endif":
            if len(condition_stack) == 1:
                raise EvaluationError(
                    f"{path}:{line_number}: unexpected @endif"
                )

            condition_stack.pop()
            continue

        # If a conditional block is inactive, ignore everything
        # inside it except nested conditional directives.
        if not condition_stack[-1]:
            continue

        # ---------------------------------------------------------
        # INCLUDE
        # ---------------------------------------------------------

        include_match = re.match(
            r"^@include(_once)?\s+(.+)$",
            line
        )

        if include_match:

            once = include_match.group(1) == "_once"
            include_path = include_match.group(2).strip()

            include_file = (
                path.parent / include_path
            ).resolve()

            if not include_file.exists():
                raise EvaluationError(
                    f"{path}:{line_number}: "
                    f"include not found: {include_path}"
                )

            if once and include_file in included_files:
                continue

            included_config = evaluate_legacy(
                include_file,
                env,
                included_files
            )

            for section, values in included_config.items():

                if section not in config:
                    config[section] = {}

                config[section].update(values)

            continue

        # ---------------------------------------------------------
        # SECTION
        # ---------------------------------------------------------

        section_match = re.match(
            r"^\[([^\]]+)\]$",
            line
        )

        if section_match:

            current_section = section_match.group(1).strip()

            if current_section not in config:
                config[current_section] = {}

            continue

        # ---------------------------------------------------------
        # KEY = VALUE
        # ---------------------------------------------------------

        key_match = re.match(
            r"^([^=]+?)\s*=\s*(.*)$",
            line
        )

        if key_match:

            if current_section is None:
                raise EvaluationError(
                    f"{path}:{line_number}: "
                    "key found before section"
                )

            key = key_match.group(1).strip()
            value = parse_value(
                key_match.group(2)
            )

            config[current_section][key] = value

            continue

        raise EvaluationError(
            f"{path}:{line_number}: "
            f"unsupported syntax: {line}"
        )

    if len(condition_stack) != 1:
        raise EvaluationError(
            f"{path}: missing @endif"
        )

    # Resolve interpolation only after all files have
    # been combined.
    resolved = resolve_value(
        config,
        config,
        env
    )

    return config
