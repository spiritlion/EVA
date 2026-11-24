# EVA-Core

Центральный управляющий компонент распределённой системы EVA.

EVA-Core — «мозг» кластера: принимает подключения агентов, обрабатывает регистрацию узлов, хранит состояние кластера и предоставляет API. Он не исполняет вычисления сам, а координирует работу агентов.

## Возможности (реализовано)

- **HTTP-сервер** на базе aiohttp.
- **Регистрация узла**: `POST /api/v1/nodes/registration-requests` — принимает запрос по контракту, возвращает `pending_approval`.
- **Статус регистрации**: `GET /api/v1/nodes/registration-requests/{request_id}`.
- **Информация об узле**: `GET /api/v1/nodes/{node_id}`.
- **Capabilities**: `PUT /api/v1/nodes/{node_id}/capabilities` — обновление статичных возможностей узла.
- **Telemetry**: `POST /api/v1/nodes/{node_id}/telemetry` — приём динамических показателей.
- **Валидация** всех входящих данных по JSON Schema-контрактам из `EVA-Contracts`.
- **In-memory хранилище** кластера (`eva/storage.py`) — запросы регистрации и узлы. Пока без внешней БД; сбрасывается при перезапуске.
- **Swagger UI** на `/swagger` — интерактивная документация API (OpenAPI 3.0).

## Структура

```
EVA-Core/
├── pyproject.toml
├── src/eva/
│   ├── main.py        # точка входа (python -m eva.main)
│   ├── app.py         # фабрика приложения (SwaggerDocs)
│   ├── config.py      # настройки (host, port, пути контрактов)
│   ├── storage.py     # in-memory реестр запросов и узлов
│   ├── validation.py  # валидация по JSON Schema
│   ├── routes/nodes.py# HTTP-эндпоинты узлов
│   └── swagger_components.yaml
└── tests/test_main.py # unittest-тесты эндпоинтов
```

## Требования

- Python 3.13+
- Зависимости: `aiohttp`, `aiohttp-swagger3`, `jsonschema[format]` (см. `pyproject.toml`).
- Путь к `EVA-Contracts` настроен через `config.py` (по умолчанию — соседний каталог).

## Установка

```bash
# в каталоге EVA-Core
python -m venv .venv
.venv/Scripts/pip install -e .
```

## Запуск

```bash
.venv/Scripts/python -m eva.main
```

По умолчанию сервер слушает `127.0.0.1:8080`.

Настройки через переменные окружения:

| Переменная | Значение по умолчанию | Описание |
|---|---|---|
| `EVA_HOST` | `127.0.0.1` | Адрес прослушивания |
| `EVA_PORT` | `8080` | Порт |
| `EVA_CONTRACTS_DIR` | `../EVA-Contracts` (сосед) | Каталог контрактов |

## API

Все эндпоинты — под префиксом `/api/v1`. Swagger UI доступен на `/swagger`.

| Метод | Путь | Назначение |
|---|---|---|
| `POST` | `/api/v1/nodes/registration-requests` | Запросить регистрацию узла |
| `GET` | `/api/v1/nodes/registration-requests/{request_id}` | Статус запроса регистрации |
| `GET` | `/api/v1/nodes/{node_id}` | Информация об узле |
| `PUT` | `/api/v1/nodes/{node_id}/capabilities` | Обновить возможности узла |
| `POST` | `/api/v1/nodes/{node_id}/telemetry` | Отправить телеметрию узла |

## Тесты

```bash
.venv/Scripts/python -m unittest discover -s tests -v
```

## Статус разработки

Реализованы: регистрация, узлы, capabilities, telemetry, Swagger UI. Ожидает реализации: подтверждение регистрации администратором, постоянное хранилище, WebSocket-канал команд и событий, планировщик задач, резервный Core.