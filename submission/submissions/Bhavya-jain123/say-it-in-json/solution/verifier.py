import json
import sys
from pathlib import Path

from converter import convert_file
from evaluator import (
    EvaluationError,
    evaluate_json,
    evaluate_legacy,
)


def compare_configs(legacy, migrated):
    """
    Compare two effective configurations and return
    the differences.
    """

    differences = []

    all_keys = sorted(
        set(legacy.keys()) | set(migrated.keys())
    )

    for key in all_keys:
        old_value = legacy.get(key, "<missing>")
        new_value = migrated.get(key, "<missing>")

        if old_value != new_value:
            differences.append({
                "key": key,
                "legacy": old_value,
                "json": new_value
            })

    return differences


def verify_file(pfcfg_path, output_json, env):
    """
    Convert and verify one .pfcfg file.
    """

    # Convert legacy configuration to JSON.
    converted = convert_file(pfcfg_path)

    with open(output_json, "w", encoding="utf-8") as file:
        json.dump(
            converted,
            file,
            indent=2,
            ensure_ascii=False
        )

    # Evaluate original configuration.
    legacy = evaluate_legacy(
        pfcfg_path,
        env
    )

    # Evaluate migrated JSON.
    migrated = evaluate_json(
        output_json,
        env
    )

    differences = compare_configs(
        legacy,
        migrated
    )

    return differences


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python verifier.py <config.pfcfg>"
        )
        sys.exit(1)

    pfcfg_path = Path(sys.argv[1])

    if not pfcfg_path.exists():
        print(f"File not found: {pfcfg_path}")
        sys.exit(1)

    environments = [
        {
            "CI": "1"
        },
        {
            "CI": ""
        }
    ]

    all_results = []
    unmigratable = []

    for env in environments:

        environment_name = (
            "CI=1"
            if env.get("CI")
            else "CI=\"\""
        )

        output_json = (
            pfcfg_path.parent /
            f"{pfcfg_path.stem}.{environment_name.replace('=', '_').replace('\"', '')}.json"
        )

        try:
            differences = verify_file(
                pfcfg_path,
                output_json,
                env
            )

            passed = len(differences) == 0

            result = {
                "file": str(pfcfg_path),
                "environment": environment_name,
                "passed": passed,
                "differences": differences
            }

            all_results.append(result)

            if passed:
                print(
                    f"PASS  {pfcfg_path}  {environment_name}"
                )
            else:
                print(
                    f"FAIL  {pfcfg_path}  {environment_name}"
                )

                for difference in differences:
                    print(
                        f"      {difference['key']}: "
                        f"{difference['legacy']} != "
                        f"{difference['json']}"
                    )

        except (EvaluationError, ValueError) as error:

            print(
                f"UNMIGRATABLE  {pfcfg_path}  "
                f"{environment_name}"
            )

            unmigratable.append({
                "file": str(pfcfg_path),
                "section": "",
                "key": "",
                "reason": str(error)
            })

    # Write verification results.
    results_path = (
        pfcfg_path.parent /
        "verification-results.json"
    )

    with open(
        results_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            all_results,
            file,
            indent=2,
            ensure_ascii=False
        )

    # Write unmigratable report.
    report_path = (
        pfcfg_path.parent /
        "unmigratable.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            unmigratable,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(
        f"Verification results: {results_path}"
    )

    print(
        f"Unmigratable report: {report_path}"
    )


if __name__ == "__main__":
    main()
