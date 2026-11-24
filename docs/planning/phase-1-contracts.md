# Фаза 1 — Контракты (EVA-Contracts)

Цель: полное описание «языка» обмена между Core и Agent.

## Статус: ✅ в основном реализовано

Полный каталог контрактов со статусами: [`EVA-Contracts/CONTRACTS.md`](../../EVA-Contracts/CONTRACTS.md).

## Что сделано

- Каркас протокола **v1**: регистрация, capabilities, telemetry, общие ошибки.
- WebSocket-сообщения: соединение (`hello/accepted/rejected/close`), команды (`dispatch/accepted/result/failed`), события (`publish/ack/replay`), heartbeat (`ping/pong`).
- Общие структуры: `error`, `event-envelope`, `message-envelope`.
- Реестр типов событий: [`EVA-Contracts/EVENT_TYPES.md`](../../EVA-Contracts/EVENT_TYPES.md).
- Политика версионирования: [`EVA-Contracts/VERSIONING.md`](../../EVA-Contracts/VERSIONING.md).
- Аутентификация: `agent-credentials.schema.json` + [`EVA-Contracts/AUTH.md`](../../EVA-Contracts/AUTH.md).
- Инструменты валидации: `tools/validate_*.py`.

## Открытые задачи

| Задача | Приоритет | Статус |
|---|---|---|
| Проверить расхождение версии capabilities (VERSIONING 1.1.0 vs schema const 1.0.0) | P1 | ⬜ |
| Маппинг HTTP-статусов → error-формат | P1 | ⬜ |
| Сделать `credentials` в `connection.hello` обязательным или нет | P1 | ⬜ |
| Task Contracts (жизненный цикл, приоритеты, отмена) | P2 | ⬜ |
| События и отмена/прогресс команд (`command.progress`, `command.cancel`) | P2 | ⬜ |
| Model Contracts (load/unload/pin/list) | P2 | ⬜ |
| Выдача/ротация/отзыв ключей | P2 | ⬜ |
| Хранилище, резервный Core, обновления, администрирование | P3 | ⬜ |

## Проверка

```bash
# в EVA-Contracts, через .venv
python tools/validate_schemas.py
python tools/validate_examples.py
python tools/validate_refs.py
```