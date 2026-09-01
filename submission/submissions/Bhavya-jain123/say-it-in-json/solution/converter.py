import json
import re
import sys
from pathlib import Path


def parse_value(value):
    """Convert simple .pfcfg values into JSON-friendly values."""

    value = value.strip()

    # Quoted string
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
        value = value.replace('\\"', '"').replace("\\\\", "\\")
        return value

    # Boolean
    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    # Comma-separated list
    if "," in value:
        return [item.strip() for item in value.split(",")]

    # Integer
    if re.fullmatch(r"-?\d+", value):
        return int(value)

    # Keep everything else as a string.
    # This is important because interpolation such as
    # ${VAR:-default} or $(section.key) must survive conversion.
    return value


def convert_file(input_path):
    input_path = Path(input_path)

    result = {
        "version": 1,
        "includes": [],
        "sections": {},
        "conditionals": []
    }

    current_section = None
    conditional_stack = []

    with input_path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    i = 0

    while i < len(lines):
        raw_line = lines[i]
        line_number = i + 1
        line = raw_line.strip()

        # Empty line
        if not line:
            i += 1
            continue

        # Comments
        if line.startswith("#") or line.startswith(";"):
            i += 1
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

            result["includes"].append({
                "path": include_path,
                "once": once
            })

            i += 1
            continue

        # ---------------------------------------------------------
        # CONDITIONAL START
        # ---------------------------------------------------------
        conditional_match = re.match(
            r"^@(ifdef|ifndef)\s+([A-Za-z_][A-Za-z0-9_]*)$",
            line
        )

        if conditional_match:
            conditional_type = conditional_match.group(1)
            variable = conditional_match.group(2)

            conditional = {
                "type": conditional_type,
                "variable": variable,
                "sections": {}
            }

            result["conditionals"].append(conditional)

            conditional_stack.append(conditional)

            current_section = None

            i += 1
            continue

        # ---------------------------------------------------------
        # CONDITIONAL END
        # ---------------------------------------------------------
        if line == "@endif":
            if conditional_stack:
                conditional_stack.pop()

            current_section = None

            i += 1
            continue

        # ---------------------------------------------------------
        # SECTION
        # ---------------------------------------------------------
        section_match = re.match(r"^\[([^\]]+)\]$", line)

        if section_match:
            section_name = section_match.group(1).strip()

            if conditional_stack:
                current_section = section_name

                current_conditional = conditional_stack[-1]

                if section_name not in current_conditional["sections"]:
                    current_conditional["sections"][section_name] = {}

            else:
                current_section = section_name

                if section_name not in result["sections"]:
                    result["sections"][section_name] = {}

            i += 1
            continue

        # ---------------------------------------------------------
        # KEY = VALUE
        # ---------------------------------------------------------
        key_match = re.match(r"^([^=]+?)\s*=\s*(.*)$", line)

        if key_match:
            if current_section is None:
                raise ValueError(
                    f"{input_path}:{line_number}: "
                    "key found before a section header"
                )

            key = key_match.group(1).strip()
            value = parse_value(key_match.group(2))

            if conditional_stack:
                current_conditional = conditional_stack[-1]

                if current_section not in current_conditional["sections"]:
                    current_conditional["sections"][current_section] = {}

                current_conditional["sections"][
                    current_section
                ][key] = value

            else:
                result["sections"][
                    current_section
                ][key] = value

            i += 1
            continue

        # ---------------------------------------------------------
        # Unsupported syntax
        # ---------------------------------------------------------
        raise ValueError(
            f"{input_path}:{line_number}: "
            f"unsupported syntax: {line}"
        )

    return result


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python converter.py "
            "<input.pfcfg> <output.json>"
        )
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    converted = convert_file(input_path)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            converted,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Converted {input_path} -> {output_path}")


if __name__ == "__main__":
    main()
