import json
from pathlib import Path

from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


ROOT = Path(__file__).resolve().parents[1]


def main():
    schemas = list((ROOT / "schemas").rglob("*.schema.json"))
    schemas += list((ROOT / "events").rglob("*.schema.json"))

    registry = Registry()

    for path in schemas:
        with path.open("r", encoding="utf-8") as file:
            schema = json.load(file)

        resource = Resource.from_contents(
            schema,
            default_specification=DRAFT202012
        )

        registry = registry.with_resource(
            uri=schema["$id"],
            resource=resource
        )

    failed = 0

    for path in schemas:
        with path.open("r", encoding="utf-8") as file:
            schema = json.load(file)

        try:
            registry.resolver(base_uri=schema["$id"]).lookup(
                schema["$id"]
            )

            print(f"[OK] {path.relative_to(ROOT)}")

        except Exception as error:
            failed += 1
            print(f"[FAIL] {path.relative_to(ROOT)}")
            print(f"       {error}")

    print("\nValidation summary:")
    print(f"Total: {len(schemas)}")
    print(f"Failed: {failed}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()