"""Конфигурация EVA-Core."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Настройки запуска EVA-Core."""

    host: str = field(
        default_factory=lambda: os.environ.get("EVA_HOST", "127.0.0.1")
    )
    port: int = field(
        default_factory=lambda: int(os.environ.get("EVA_PORT", "8080"))
    )
    contracts_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get(
                "EVA_CONTRACTS_DIR",
                str(Path(__file__).resolve().parents[3] / "EVA-Contracts"),
            )
        )
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