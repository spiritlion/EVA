"""Automatic validation of EVA JSON Schema contracts."""

import json
from pathlib import Path

from jsonschema.validators import validator_for


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
EVENTS_DIR = PROJECT_ROOT / "events"


def validate_schema_file(path: Path) -> bool:
    """Validate JSON syntax and JSON Schema structure."""

    try:
        with path.open("r", encoding="utf-8") as file:
            schema = json.load(file)

        validator_class = validator_for(schema)
        validator_class.check_schema(schema)

        print(f"[OK] {path.relative_to(PROJECT_ROOT)}")
        return True

    except json.JSONDecodeError as error:
        print(f"[JSON ERROR] {path.name}: {error}")
    except Exception as error:
        print(f"[SCHEMA ERROR] {path.name}: {error}")

    return False


def main() -> None:
    """Validate all schemas in EVA-Contracts."""

    schema_files = sorted(
        path
        for directory in (SCHEMAS_DIR, EVENTS_DIR)
        for path in directory.rglob("*.schema.json")
    )

    if not schema_files:
        print("No schema files found.")
        return

    results = [
        validate_schema_file(path)
        for path in schema_files
    ]

    passed = sum(results)
    failed = len(results) - passed

    print("\nValidation summary:")
    print(f"Total: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()