"""Валидация данных по схемам EVA-Contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, exceptions
from jsonschema import validators as jsonschema_validators


def _load_schema(path: Path) -> dict:
    """Загружает JSON Schema из файла."""
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_json(payload: Any, schema_path: Path) -> list[dict]:
    """Валидирует payload против схемы.

    Возвращает список ошибок в виде [{"path": ..., "message": ...}].
    Пустой список означает, что данные корректны.

    Пока схемы валидируются по одному файлу без внешних $ref-реестров;
    проверка выполняется Draft 2020-12 с поддержкой форматов (uuid, date-time).
    """
    schema = _load_schema(schema_path)

    validator_class = jsonschema_validators.validator_for(schema)
    if validator_class is Draft202012Validator:
        validator = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )
    else:
        validator = validator_class(schema)

    errors: list[dict] = []
    for error in validator.iter_errors(payload):
        location = ".".join(str(part) for part in error.absolute_path)
        errors.append(
            {
                "path": location,
                "message": error.message,
            }
        )

    return errors