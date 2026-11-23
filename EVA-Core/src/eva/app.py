"""Фабрика приложения EVA-Core."""

from __future__ import annotations

from pathlib import Path

from aiohttp import web
from aiohttp_swagger3 import SwaggerDocs, SwaggerInfo, SwaggerUiSettings

from eva.config import Config
from eva.storage import Registry

CONFIG_KEY: web.AppKey[Config] = web.AppKey("eva.config", Config)
SWAGGER_KEY: web.AppKey[SwaggerDocs] = web.AppKey("eva.swagger", SwaggerDocs)
REGISTRY_KEY: web.AppKey[Registry] = web.AppKey("eva.registry", Registry)

COMPONENTS_FILE = Path(__file__).resolve().parent / "swagger_components.yaml"


def create_app(config: Config | None = None) -> web.Application:
    """Создаёт и настраивает приложение EVA-Core.

    Возвращает aiohttp Application со встроенным Swagger UI (/swagger)
    и API-эндпоинтами. SwaggerDocs-обвязка хранится в app по ключу SWAGGER_KEY.

    validate=False: валидация запросов выполняется в EVA по контрактам
    (eva.validation), а не повторно через SwaggerRoute.
    """
    app_config = config or Config()
    app = web.Application()
    app[CONFIG_KEY] = app_config
    app[REGISTRY_KEY] = Registry()

    swagger = SwaggerDocs(
        app,
        info=SwaggerInfo(
            title="EVA Core API",
            version="v1",
            description="API центрального управляющего компонента EVA.",
        ),
        components=str(COMPONENTS_FILE),
        validate=False,
        swagger_ui_settings=SwaggerUiSettings(path="/swagger"),
    )
    app[SWAGGER_KEY] = swagger

    # Маршруты регистрируются в отдельных модулях.
    from eva.routes.nodes import add_node_routes

    add_node_routes(swagger)

    return app