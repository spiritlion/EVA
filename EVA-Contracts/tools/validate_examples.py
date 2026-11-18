import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"
EXAMPLES_DIR = ROOT / "examples"


def load_registry():
    """Load all schemas into a registry for resolving $ref."""

    registry = Registry()

    schema_files = list(SCHEMAS_DIR.rglob("*.schema.json"))
    schema_files += list((ROOT / "events").rglob("*.schema.json"))

    for path in schema_files:
        with path.open("r", encoding="utf-8") as file:
            schema = json.load(file)

        Draft202012Validator.check_schema(schema)

        resource = Resource.from_contents(
            schema,
            default_specification=DRAFT202012
        )

        registry = registry.with_resource(
            uri=schema["$id"],
            resource=resource
        )

    return registry


def find_schema(example_path):
    """Find the schema corresponding to an example."""

    relative = example_path.relative_to(EXAMPLES_DIR)
    parts = relative.parts

    # WebSocket examples use grouped schemas.
    if len(parts) >= 4 and parts[1] == "websocket":
        group = parts[2]

        schema_names = {
            "connection": "connection.schema.json",
            "heartbeat": "heartbeat.schema.json",
            "events": "event-message.schema.json",
            "commands": "command.schema.json"
        }

        schema_name = schema_names.get(group)

        if schema_name is None:
            raise ValueError(f"Unknown WebSocket group: {group}")

        return (
            SCHEMAS_DIR
            / "v1"
            / "websocket"
            / group
            / schema_name
        )

    # Other examples mirror the schema directory structure.
    schema_relative = Path(*parts).with_name(
        example_path.name.replace(
            ".example.json",
            ".schema.json"
        )
    )

    return SCHEMAS_DIR / schema_relative


def main():
    registry = load_registry()

    example_files = list(EXAMPLES_DIR.rglob("*.example.json"))

    if not example_files:
        print("[ERROR] No example files found.")
        raise SystemExit(1)

    failed = 0

    for example_path in example_files:
        try:
            schema_path = find_schema(example_path)

            if not schema_path.exists():
                raise FileNotFoundError(
                    f"Schema not found: {schema_path}"
                )

            with schema_path.open("r", encoding="utf-8") as file:
                schema = json.load(file)

            with example_path.open("r", encoding="utf-8") as file:
                example = json.load(file)

            validator = Draft202012Validator(
                schema,
                registry=registry,
                format_checker=FormatChecker()
            )

            errors = sorted(
                validator.iter_errors(example),
                key=lambda error: list(error.absolute_path)
            )

            if errors:
                failed += 1
                print(f"[FAIL] {example_path.relative_to(ROOT)}")

                for error in errors:
                    location = ".".join(
                        str(part) for part in error.absolute_path
                    )
                    print(f"       {location}: {error.message}")

            else:
                print(f"[OK] {example_path.relative_to(ROOT)}")

        except Exception as error:
            failed += 1
            print(f"[FAIL] {example_path.relative_to(ROOT)}")
            print(f"       {error}")

    print("\nValidation summary:")
    print(f"Total: {len(example_files)}")
    print(f"Passed: {len(example_files) - failed}")
    print(f"Failed: {failed}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()