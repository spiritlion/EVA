# Фаза 3 — EVA-Agent

Цель: работающий представитель устройства — подключение к Core, авторизация, телеметрия, приём команд.

## Статус: 🟡 каркас

## Что сделано

- Пакет `eva_agent` (config, client, main).
- Формирование запроса регистрации по контракту.
- Отправка регистрации на Core (`POST /api/v1/nodes/registration-requests`).
- Связка Core↔Agent проверена локально (POST → 202, GET → 200).

Детали: [`EVA-Agent/README.md`](../../EVA-Agent/README.md).

## Открытые задачи

| Задача | Приоритет | Статус |
|---|---|---|
| Сбор реальной телеметрии (CPU, память, диск) | P1 | ⬜ |
| Отправка capabilities на Core (`PUT .../capabilities`) | P1 | ⬜ |
| Периодическая отправка telemetry (`POST .../telemetry`) | P1 | ⬜ |
| Циклический heartbeat | P2 | ⬜ |
| WebSocket-соединение и аутентификация | P2 | ⬜ |
| Приём и выполнение команд | P2 | ⬜ |
| Авто-переподключение с `event.replay` | P2 | ⬜ |

## Проверка

```bash
# в EVA-Agent
.venv/Scripts/python -m eva_agent.main
```