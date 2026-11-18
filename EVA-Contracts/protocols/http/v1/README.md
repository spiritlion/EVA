# EVA HTTP API — Version 1

## 1. General Information

- Protocol: HTTP/1.1
- Data format: JSON
- API prefix: `/api/v1`
- Content-Type: `application/json`
- Character encoding: UTF-8

## 2. Node Registration

### Submit Registration Request

`POST /api/v1/nodes/registration-requests`

Назначение: Agent отправляет запрос на регистрацию нового устройства.

Request: `node-registration-request.schema.json`

Response: `node-registration-response.schema.json`

Possible statuses:
- `pending_approval`
- `approved`
- `rejected`

### Get Registration Status

`GET /api/v1/nodes/registration-requests/{request_id}`

Назначение: Agent проверяет состояние своего запроса.

Response: `node-registration-response.schema.json`

## 3. Node Management

### Get Node Information

`GET /api/v1/nodes/{node_id}`

Назначение: получить информацию о зарегистрированном узле.

### Submit Node Capabilities

`PUT /api/v1/nodes/{node_id}/capabilities`

Назначение: передать или обновить инвентаризацию оборудования.

### Submit Node Telemetry

`POST /api/v1/nodes/{node_id}/telemetry`

Назначение: передать динамические показатели состояния устройства.

## 4. Event Communication

### Get Events

`GET /api/v1/events`

Назначение: получить события кластера с возможностью последующей пагинации.

## 5. Error Handling

Все ошибки API должны использовать общий формат:

`schemas/v1/common/error.schema.json`

HTTP status codes:

- `400` — Bad Request
- `401` — Unauthorized
- `403` — Forbidden
- `404` — Not Found
- `409` — Conflict
- `422` — Validation Error
- `429` — Too Many Requests
- `500` — Internal Server Error
- `503` — Service Unavailable

## 6. Reliability

- Повторные запросы регистрации не должны создавать дубликаты.
- Повторная отправка телеметрии должна корректно обрабатываться.
- Порядок сообщений должен учитываться там, где он имеет значение.
- Временная недоступность Core не должна приводить к потере всей локальной информации Agent.

## 7. Security

- Все удалённые соединения должны использовать TLS.
- Каждый Agent должен иметь собственную идентичность.
- Неавторизованные устройства не должны получать доступ к управляющим операциям.
- Механизм аутентификации и выдачи ключей определяется отдельной спецификацией.

## 8. Compatibility

- API использует независимое версионирование.
- Несовместимые изменения требуют новой версии API.
- Core должен корректно обрабатывать неподдерживаемые версии контрактов.
