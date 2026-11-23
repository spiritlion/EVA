"""HTTP-маршруты управления узлами EVA-Core."""

from __future__ import annotations

from pathlib import Path

from aiohttp import web
from aiohttp_swagger3 import SwaggerDocs

from eva.app import CONFIG_KEY, REGISTRY_KEY
from eva.validation import validate_json


def add_node_routes(app: SwaggerDocs) -> None:
    """Регистрирует маршруты узлов в приложении."""
    app.add_post(
        "/api/v1/nodes/registration-requests",
        handle_registration_request,
    )
    app.add_get(
        "/api/v1/nodes/registration-requests/{request_id}",
        handle_registration_status,
    )
    app.add_get(
        "/api/v1/nodes/{node_id}",
        handle_node_info,
    )
    app.add_put(
        "/api/v1/nodes/{node_id}/capabilities",
        handle_node_capabilities,
    )
    app.add_post(
        "/api/v1/nodes/{node_id}/telemetry",
        handle_node_telemetry,
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

    request.app[REGISTRY_KEY].put_request(
        payload["request_id"],
        response,
    )

    return web.json_response(response, status=202)


async def handle_registration_status(
    request: web.Request,
) -> web.StreamResponse:
    """Возвращает статус запроса на регистрацию узла.

    ---
    tags: [nodes]
    summary: Получить статус запроса на регистрацию узла
    parameters:
      - name: request_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      '200':
        description: Информация о запросе регистрации
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RegistrationResponse'
      '404':
        description: Запрос не найден
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
    """
    request_id = request.match_info["request_id"]
    entry = request.app[REGISTRY_KEY].get_request(request_id)

    if entry is None:
        return web.json_response(
            {
                "contract_version": "1.0.0",
                "code": "NOT_FOUND",
                "message": "Registration request not found.",
                "retryable": False,
                "occurred_at": _now(),
            },
            status=404,
        )

    return web.json_response(entry, status=200)


async def handle_node_info(request: web.Request) -> web.StreamResponse:
    """Возвращает информацию о зарегистрированном узле.

    ---
    tags: [nodes]
    summary: Получить информацию об узле
    parameters:
      - name: node_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      '200':
        description: Информация об узле
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NodeInfo'
      '404':
        description: Узел не найден
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
    """
    node_id = request.match_info["node_id"]
    node = request.app[REGISTRY_KEY].get_node(node_id)

    if node is None:
        return _error_response("NOT_FOUND", "Node not found.", 404)

    return web.json_response(node, status=200)


async def _handle_body_submission(
    request: web.Request,
    schema_path: Path,
) -> dict | None:
    """Извлекает и валидирует тело запроса узла.

    При ошибке записывает HTTP-ответ в request["_error"] и возвращает None.
    """
    config = request.app[CONFIG_KEY]

    try:
        payload = await request.json()
    except Exception:
        request["_error"] = _error_response(
            "INVALID_JSON", "Request body is not valid JSON.", 400
        )
        return None

    errors = validate_json(payload, schema_path)
    if errors:
        request["_error"] = _error_response(
            "VALIDATION_ERROR",
            "Body does not match the contract.",
            400,
            details={"errors": errors},
        )
        return None
    return payload


async def handle_node_capabilities(request: web.Request) -> web.StreamResponse:
    """Принимает и обновляет возможности (capabilities) узла.

    ---
    tags: [nodes]
    summary: Передать или обновить возможности узла
    parameters:
      - name: node_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Capabilities'
    responses:
      '204':
        description: Возможности приняты
      '400':
        description: Некорректные данные
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
      '404':
        description: Узел не найден
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
    """
    node_id = request.match_info["node_id"]
    registry = request.app[REGISTRY_KEY]
    node = registry.get_node(node_id)

    if node is None:
        return _error_response("NOT_FOUND", "Node not found.", 404)

    body = await _handle_body_submission(
        request,
        request.app[CONFIG_KEY].capabilities_schema_path,
    )
    if body is None:
        return request["_error"]

    node = dict(node)
    node["capabilities"] = body
    node["last_seen_at"] = _now()
    registry.put_node(node)
    return web.Response(status=204)


async def handle_node_telemetry(request: web.Request) -> web.StreamResponse:
    """Принимает телеметрию узла.

    ---
    tags: [nodes]
    summary: Передать динамические показатели узла
    parameters:
      - name: node_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Telemetry'
    responses:
      '204':
        description: Телеметрия принята
      '400':
        description: Некорректные данные
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
      '404':
        description: Узел не найден
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
    """
    node_id = request.match_info["node_id"]
    registry = request.app[REGISTRY_KEY]
    node = registry.get_node(node_id)

    if node is None:
        return _error_response("NOT_FOUND", "Node not found.", 404)

    body = await _handle_body_submission(
        request,
        request.app[CONFIG_KEY].telemetry_schema_path,
    )
    if body is None:
        return request["_error"]

    node = dict(node)
    node["telemetry"] = body
    node["last_seen_at"] = _now()
    registry.put_node(node)
    return web.Response(status=204)


def _now() -> str:
    """Возвращает текущее время в формате ISO 8601 (UTC)."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _error_response(
    code: str,
    message: str,
    status: int,
    details: dict | None = None,
) -> web.StreamResponse:
    """Формирует ответ в формате error.schema.json."""
    body: dict = {
        "contract_version": "1.0.0",
        "code": code,
        "message": message,
        "retryable": False,
        "occurred_at": _now(),
    }
    if details is not None:
        body["details"] = details
    return web.json_response(body, status=status)


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