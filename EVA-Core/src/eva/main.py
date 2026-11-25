"""Точка входа приложения EVA-Core."""

from __future__ import annotations

from aiohttp import web

from eva.app import create_app
from eva.config import Config


def main() -> None:
    """Запускает EVA-Core HTTP-сервер."""
    config = Config.load()
    app = create_app(config)
    web.run_app(
        app,
        host=config.host,
        port=config.port,
        print=print,
    )


if __name__ == "__main__":
    main()