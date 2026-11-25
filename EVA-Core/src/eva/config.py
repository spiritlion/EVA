"""Конфигурация EVA-Core."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Имя файла конфигурации и имя таблицы внутри него.
CONFIG_FILENAME = "eva.toml"
CONFIG_SECTION = "core"


@dataclass(frozen=True)
class Config:
    """Настройки запуска EVA-Core.

    Источники значений (по приоритету, выше — главнее):
    1. переменные окружения EVA_*;
    2. файл конфигурации eva.toml (если существует);
    3. встроенные значения по умолчанию.

    Файл конфигурации автосоздаётся с дефолтами при первом обращении,
    если его ещё нет.
    """

    host: str = field(default="127.0.0.1")
    port: int = field(default=8080)
    contracts_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[3] / "EVA-Contracts"
    )
    config_file: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[3] / CONFIG_FILENAME
    )

    @classmethod
    def load(cls, config_file: Path | None = None) -> "Config":
        """Загружает конфигурацию, автосоздавая файл при необходимости."""
        path = config_file or (
            Path(__file__).resolve().parents[3] / CONFIG_FILENAME
        )
        _ensure_config_file(path)
        values = _read_config_file(path)

        host = os.environ.get("EVA_HOST", values.get("host", "127.0.0.1"))
        port = int(os.environ.get("EVA_PORT", values.get("port", 8080)))
        contracts_dir = Path(
            os.environ.get(
                "EVA_CONTRACTS_DIR",
                values.get("contracts_dir", ""),
            )
        )
        if not str(contracts_dir):
            contracts_dir = Path(__file__).resolve().parents[3] / "EVA-Contracts"

        return cls(
            host=host,
            port=port,
            contracts_dir=contracts_dir,
            config_file=path,
        )

    @property
    def registration_request_schema_path(self) -> Path:
        """Путь к схеме запроса регистрации узла."""
        return (
            self.contracts_dir
            / "schemas"
            / "v1"
            / "node"
            / "registration"
            / "request.schema.json"
        )

    def _node_schema(self, name: str) -> Path:
        return self.contracts_dir / "schemas" / "v1" / "node" / name

    @property
    def node_info_schema_path(self) -> Path:
        """Путь к схеме информации об узле (info.schema.json)."""
        return self._node_schema("info.schema.json")

    @property
    def capabilities_schema_path(self) -> Path:
        """Путь к схеме возможностей узла (capabilities.schema.json)."""
        return self._node_schema("capabilities.schema.json")

    @property
    def telemetry_schema_path(self) -> Path:
        """Путь к схеме телеметрии узла (telemetry.schema.json)."""
        return self._node_schema("telemetry.schema.json")


def _ensure_config_file(path: Path) -> None:
    """Создаёт eva.toml с дефолтами, если файла ещё нет."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"[{CONFIG_SECTION}]\n"
        "host = \"127.0.0.1\"\n"
        "port = 8080\n"
        "# Путь к каталогу контрактов EVA-Contracts\n"
        "# contracts_dir = \"../EVA-Contracts\"\n",
        encoding="utf-8",
    )


def _read_config_file(path: Path) -> dict:
    """Читает таблицу [core] из eva.toml и возвращает её как словарь."""
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    section = data.get(CONFIG_SECTION)
    if not isinstance(section, dict):
        return {}
    return section