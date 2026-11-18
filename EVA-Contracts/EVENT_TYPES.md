# EVA Event Types Registry (v1)

Реестр типов событий, которые могут передаваться через `event.publish`.
Поле `event_type` в `event-envelope` — не произвольная строка, а один из значений ниже.

Обозначение источника (в `source.component`):

- **core** — событие генерирует Core.
- **agent** — событие генерирует Agent.

Приоритеты (как в `CONTRACTS.md`): P1 — нужны для первой связки, P2 — фаза вычислений, P3 — последующие фазы.

Поле `payload` события — объект, структура которого описана в каждой строке.

---

## 6.1. Жизненный цикл узла (node.*)

| event_type | источник | payload | Приоритет |
|---|---|---|---|
| `node.registered` | core | `{ node_id, agent_id, node_name }` | P1 |
| `node.approved` | core | `{ node_id, agent_id }` | P1 |
| `node.rejected` | core | `{ node_id?, agent_id, reason }` | P1 |
| `node.online` | core | `{ node_id, agent_id, last_seen_at }` | P1 |
| `node.offline` | core | `{ node_id, agent_id, reason? }` | P1 |
| `node.capabilities.updated` | agent | `{ node_id?, capabilities }` | P2 |

## 6.2. Телеметрия (telemetry.*)

| event_type | источник | payload | Приоритет |
|---|---|---|---|
| `telemetry.received` | core | `{ node_id, telemetry }` | P2 |
| `telemetry.cpu.threshold` | agent | `{ node_id, usage_percent, threshold }` | P2 |
| `telemetry.temperature.high` | agent | `{ node_id, temperature_celsius, threshold }` | P2 |
| `telemetry.temperature.critical` | agent | `{ node_id, temperature_celsius, threshold }` | P2 |
| `telemetry.temperature.recovered` | agent | `{ node_id, temperature_celsius }` | P2 |

## 6.3. Команды (command.*)

| event_type | источник | payload | Приоритет |
|---|---|---|---|
| `command.dispatched` | core | `{ node_id, command_id, command_name }` | P1 |
| `command.accepted` | agent | `{ node_id, command_id }` | P1 |
| `command.result` | agent | `{ node_id, command_id, result }` | P1 |
| `command.failed` | agent | `{ node_id, command_id, error }` | P1 |
| `command.progress` | agent | `{ node_id, command_id, percent? }` | P2 |
| `command.cancelled` | core | `{ node_id, command_id }` | P2 |

## 6.4. Задачи (task.*)

| event_type | источник | payload | Приоритет |
|---|---|---|---|
| `task.submitted` | core | `{ task_id, node_id? }` | P2 |
| `task.started` | core | `{ task_id, node_id }` | P2 |
| `task.completed` | core | `{ task_id, node_id, result }` | P2 |
| `task.failed` | core | `{ task_id, node_id, error }` | P2 |
| `task.cancelled` | core | `{ task_id }` | P2 |

## 6.5. Модели ИИ (model.*)

| event_type | источник | payload | Приоритет |
|---|---|---|---|
| `model.loaded` | agent | `{ node_id, model_id }` | P3 |
| `model.unloaded` | agent | `{ node_id, model_id }` | P3 |
| `model.pinned` | core | `{ node_id?, model_id }` | P3 |
| `model.error` | agent | `{ node_id, model_id, error }` | P3 |

## 6.6. Хранилище (storage.*)

| event_type | источник | payload | Приоритет |
|---|---|---|---|
| `storage.artifact.created` | core | `{ artifact_id, node_id? }` | P3 |
| `storage.artifact.deleted` | core | `{ artifact_id }` | P3 |
| `storage.cache.invalidated` | core | `{ key }` | P3 |

## 6.7. Резервирование Core (cluster.*)

| event_type | источник | payload | Приоритет |
|---|---|---|---|
| `cluster.leader.elected` | core | `{ leader_id, term }` | P3 |
| `cluster.leader.lost` | core | `{ failed_leader_id, term }` | P3 |
| `cluster.split_brain.detected` | core | `{ term }` | P3 |

## 6.8. Администрирование (admin.*)

| event_type | источник | payload | Приоритет |
|---|---|---|---|
| `admin.registration.approved` | core | `{ request_id, node_id? }` | P1 |
| `admin.registration.rejected` | core | `{ request_id, reason }` | P1 |
| `admin.node.disabled` | core | `{ node_id, reason? }` | P2 |
| `admin.node.enabled` | core | `{ node_id }` | P2 |

— соотносится с `admin.*` событиями подтверждения регистрации.

---

## Замечания по согласованности

1. `node.registered`, `node.approved`, `node.rejected`, `node.online`, `node.offline`, `node.capabilities.updated` опираются на схемы `schemas/v1/node/{registration,capabilities}` и `node-info`.
2. `telemetry.received` включает в payload объект `telemetry` — соответствует `schemas/v1/node/telemetry.schema.json`.
3. `command.*` события соответствуют сообщениям из `schemas/v1/websocket/commands/command.schema.json` (`dispatch`/`accepted`/`result`/`failed`), а `progress`/`cancelled` — пока без схемы (открыты, P2).
4. `task.*`, `model.*`, `storage.*`, `cluster.*`, `admin.*` — типы декларированы; схемы payload появятся вместе с соответствующими контрактами (Task P2, Models/Storage P3).
5. Категории сопоставлены с разделами `CONTRACTS.md` (6 — события; 7 Task; 8 Models; 9 Storage; 12 Резерв. Core; 15 Admin).

---

## Согласованность с существующим

- `node.status.updated` из примера `examples/v1/websocket/events/publish.example.json` — **не включён в реестр**. Его место занимает конкретный `node.online` / `node.offline`. Если хочешь сохранить именно `node.status.updated` — скажи, верну его в реестр как общий статус-событие.

## Замечание по структуре

Реестр сейчас — документальный. Поле `event_type` в `event-envelope` формально остаётся свободной строкой (тип события влияет только на payload; payload — свободный объект). Если нужно жёстко валидировать типы, реестр можно превратить в схему — см. окно «[проверить]» ниже.

---

## Открытый вопрос

Хочешь ли, чтобы реестр был **только документацией** (как сейчас), или превратить его в JSON Schema-каталог, где:
- `schemas/v1/events/types/*.schema.json` — схема payload каждого события;
- `event-message.schema.json` связывает `event_type` с конкретной payload-схемой (через `oneOf`/`$ref`)?

Вариант со схемами даёт жёсткую валидацию (немедленные ошибки при неверном типе), документационный — гибче и проще в начале. Рекомендую для P1 оставить документацию, а схемы payload ввести вместе с Task Contracts (P2), когда события станут сложнее.