"""HTTP-маршруты управления узлами EVA-Core."""

from __future__ import annotations

from aiohttp import web
from aiohttp_swagger3 import SwaggerDocs

from eva.app import CONFIG_KEY
from eva.validation import validate_json


def add_node_routes(app: SwaggerDocs) -> None:
    """Регистрирует маршруты узлов в приложении."""
    app.add_post(
        "/api/v1/nodes/registration-requests",
        handle_registration_request,
    )


async def handle_registration_request(request: web.Request) -> web.StreamResponse:
    """Обрабатывает запрос на регистрацию нового узла.

    ---
    tags: [nodes]
    summary: Отправить запрос на регистрацию узла
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/RegistrationRequest'
    responses:
      '202':
        description: Регистрация принята, ожидает подтверждения
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RegistrationResponse'
      '400':
        description: Некорректный запрос
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
    """
    config = request.app[CONFIG_KEY]

    try:
        payload = await request.json()
    except Exception:
        return web.json_response(
            {
                "contract_version": "1.0.0",
                "code": "INVALID_JSON",
                "message": "Request body is not valid JSON.",
                "retryable": False,
                "occurred_at": _now(),
            },
            status=400,
        )

    errors = validate_json(
        payload,
        config.registration_request_schema_path,
    )

    if errors:
        return web.json_response(
            {
                "contract_version": "1.0.0",
                "code": "VALIDATION_ERROR",
                "message": "Registration request does not match the contract.",
                "retryable": False,
                "occurred_at": _now(),
                "details": {"errors": errors},
            },
            status=400,
        )

    response = _registration_response(payload)

    return web.json_response(response, status=202)


def _now() -> str:
    """Возвращает текущее время в формате ISO 8601 (UTC)."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _registration_response(request_payload: dict) -> dict:
    """Формирует ответ на учётную запись узла.

    Пока узел переходит в статус pending_approval: регистрация
    требует ручного подтверждения администратором.
    """
    return {
        "contract_version": "1.0.0",
        "request_id": request_payload["request_id"],
        "agent_id": request_payload["agent_id"],
        "status": "pending_approval",
        # node_id не выдаётся до одобрения; issued_at — момент ответа.
        "issued_at": _now(),
    }