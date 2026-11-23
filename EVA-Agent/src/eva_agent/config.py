"""Конфигурация EVA-Agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentConfig:
    """Настройки запуска EVA-Agent."""

    core_url: str = field(
        default_factory=lambda: os.environ.get("EVA_CORE_URL", "http://127.0.0.1:8080")
    )
    agent_id: str = field(
        default_factory=lambda: os.environ.get("EVA_AGENT_ID", "")
    )
    platform: str = field(
        default_factory=lambda: os.environ.get("EVA_PLATFORM", "windows")
    )
    agent_version: str = field(
        default_factory=lambda: os.environ.get("EVA_AGENT_VERSION", "0.1.0")
    )