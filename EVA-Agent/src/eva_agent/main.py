"""Точка входа приложения EVA-Agent."""

from __future__ import annotations

import asyncio

import aiohttp

from eva_agent.client import register
from eva_agent.config import AgentConfig


async def _run() -> None:
    config = AgentConfig()
    async with aiohttp.ClientSession() as session:
        response = await register(config, session)
        print("EVA-Agent: запрос регистрации отправлен.")
        print(f"EVA-Agent: Core ответил статусом {response.get('_http_status')}.")
        print(f"EVA-Agent: статус запроса — {response.get('status')}.")
        if "reason" in response:
            print(f"EVA-Agent: причина — {response['reason']}")


def main() -> None:
    """Запускает EVA-Agent."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()