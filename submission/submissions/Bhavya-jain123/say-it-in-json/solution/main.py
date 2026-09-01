import sys
from pathlib import Path

from converter import convert_file
from evaluator import (
    EvaluationError,
    evaluate_json,
    evaluate_legacy,
)


def compare_configs(old_config, new_config):
    differences = []

    all_keys = sorted(
        set(old_config.keys()) |
        set(new_config.keys())
    )

    for key in all_keys:
        old_value = old_config.get(key, "<missing>")
        new_value = new_config.get(key, "<missing>")

        if old_value != new_value:
            differences.append({
                "key": key,
                "legacy": old_value,
                "json": new_value
            })

    return differences


def find_configs(repo_root):
    """
    Find the supplied .pfcfg fixtures.
    """

    starter = repo_root / "starter"

    return sorted(starter.rglob("*.pfcfg"))


def run_verification(pfcfg_path):
    environments = [
        {"CI": "1"},
        {"CI": ""}
    ]

    results = []

    for env in environments:

        env_name = (
            "CI=1"
            if env.get("CI")
            else 'CI=""'
        )

        try:
            # Convert .pfcfg -> JSON in memory.
            converted = convert_file(pfcfg_path)

            # Temporary JSON file beside the source.
            json_path = pfcfg_path.with_suffix(
                ".migrated.json"
            )

            import json

            with open(
                json_path,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    converted,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            # Evaluate both representations.
            legacy = evaluate_legacy(
                pfcfg_path,
                env
            )

            migrated = evaluate_json(
                json_path,
                env
            )

            differences = compare_configs(
                legacy,
                migrated
            )

            passed = len(differences) == 0

            results.append({
                "file": str(pfcfg_path),
                "environment": env_name,
                "passed": passed,
                "differences": differences
            })

            if passed:
                print(
                    f"  PASS  {env_name}"
                )
            else:
                print(
                    f"  FAIL  {env_name}"
                )

                for difference in differences:
                    print(
                        f"        {difference['key']}: "
                        f"{difference['legacy']} != "
                        f"{difference['json']}"
                    )

        except (EvaluationError, ValueError) as error:

            print(
                f"  UNMIGRATABLE  {env_name}: {error}"
            )

            results.append({
                "file": str(pfcfg_path),
                "environment": env_name,
                "passed": False,
                "unmigratable": True,
                "error": str(error)
            })

    return results


def main():
    # Repository root:
    # solution/main.py
    #       ↑
    # submissions/Bhavya-jain123/say-it-in-json/
    solution_dir = Path(__file__).resolve().parent
    submission_dir = solution_dir.parent.parent.parent
    repo_root = submission_dir.parent.parent.parent

    print("=" * 60)
    print("Say It in JSON - Migration Verification")
    print("=" * 60)
    print()

    configs = find_configs(repo_root)

    if not configs:
        print("No .pfcfg files found.")
        print(
            "Make sure the repository contains the "
            "starter fixtures."
        )
        sys.exit(1)

    total = 0
    passed = 0
    failed = 0
    unmigratable = 0

    all_results = []

    for config in configs:

        print(f"{config}")

        results = run_verification(config)

        all_results.extend(results)

        for result in results:
            total += 1

            if result.get("unmigratable"):
                unmigratable += 1
            elif result["passed"]:
                passed += 1
            else:
                failed += 1

        print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)

    print(f"Total checks:       {total}")
    print(f"Passed:             {passed}")
    print(f"Failed:             {failed}")
    print(f"Unmigratable:       {unmigratable}")

    print()

    if failed == 0:
        print("Migration verification completed.")
    else:
        print("Migration verification found differences.")


if __name__ == "__main__":
    main()
