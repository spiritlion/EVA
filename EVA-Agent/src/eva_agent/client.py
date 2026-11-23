"""HTTP-клиент EVA-Agent для взаимодействия с EVA-Core."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import aiohttp

from eva_agent.config import AgentConfig

CONTRACT_VERSION = "1.0.0"


def build_registration_request(config: AgentConfig) -> dict:
    """Формирует запрос регистрации по контракту registration/request."""
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": str(uuid.uuid4()),
        "agent_id": config.agent_id or str(uuid.uuid4()),
        "node_name": _hostname(),
        "platform": config.platform,
        "agent_version": config.agent_version,
        "requested_at": _now(),
    }


def _hostname() -> str:
    import socket

    return socket.gethostname()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


async def register(
    config: AgentConfig,
    session: aiohttp.ClientSession,
) -> dict:
    """Отправляет запрос регистрации на Core и возвращает ответ.

    Возвращает тело ответа (node-registration-response).
    """
    payload = build_registration_request(config)
    url = f"{config.core_url.rstrip('/')}/api/v1/nodes/registration-requests"
    async with session.post(url, json=payload) as resp:
        body = await resp.json()
        body["_http_status"] = resp.status
        return body