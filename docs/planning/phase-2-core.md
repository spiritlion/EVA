# Фаза 2 — EVA-Core

Цель: работающий центральный компонент с управлением устройствами, API и хранением состояния.

## Статус: 🟡 частично

## Что сделано

- HTTP-сервер на aiohttp.
- Эндпоинты регистрации и узлов:
  - `POST /api/v1/nodes/registration-requests`
  - `GET  /api/v1/nodes/registration-requests/{request_id}`
  - `GET  /api/v1/nodes/{node_id}`
  - `PUT  /api/v1/nodes/{node_id}/capabilities`
  - `POST /api/v1/nodes/{node_id}/telemetry`
- Валидация всех входящих данных по JSON Schema-контрактам.
- In-memory хранилище кластера (`src/eva/storage.py`).
- Swagger UI на `/swagger` (OpenAPI 3.0).

Детали: [`EVA-Core/README.md`](../../EVA-Core/README.md).

## Открытые задачи

| Задача | Приоритет | Статус |
|---|---|---|
| Подтверждение регистрации администратором (approve/reject) | P1 | ⬜ |
| Постоянное хранилище (вместо in-memory) | P2 | ⬜ |
| WebSocket-канал `GET /ws/v1` (соединение, heartbeat, события) | P2 | ⬜ |
| Резервный Core + защита от split-brain | P3 | ⬜ |
| Аутентификация запросов по `agent-credentials` | P1 | ⬜ |

## Проверка

```bash
# в EVA-Core
.venv/Scripts/python -m unittest discover -s tests -v
```