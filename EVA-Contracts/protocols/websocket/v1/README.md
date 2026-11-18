# EVA WebSocket Protocol — v1

## 1. General

WebSocket provides persistent bidirectional communication between EVA Core and EVA Agents.

- Protocol: WebSocket
- Data format: JSON
- Encoding: UTF-8
- Endpoint: `/ws/v1`
- Transport security: WSS (WebSocket over TLS)

## 2. Connection lifecycle

1. Agent establishes a secure WebSocket connection to Core.
2. Agent authenticates using its individual identity and credentials.
3. Core validates the Agent.
4. Core accepts or rejects the connection.
5. After successful authentication, both sides may exchange messages.
6. On connection loss, Agent attempts to reconnect automatically.

## 3. Message envelope

All messages use a common structure:

- `message_id` — unique UUID of the message.
- `message_type` — message type.
- `protocol_version` — protocol version.
- `correlation_id` — optional identifier linking related messages.
- `occurred_at` — UTC timestamp.
- `payload` — message-specific data.

## 4. Message types

### Connection

- `connection.hello` — Agent announces its connection.
- `connection.accepted` — Core accepts the connection.
- `connection.rejected` — Core rejects the connection.
- `connection.close` — graceful disconnection.

### Events

- `event.publish` — publish an event.
- `event.ack` — acknowledge event receipt.
- `event.replay` — request missed events after reconnection.

Events must follow the common event envelope defined in `events/v1/event-envelope.schema.json`.

### Commands

- `command.dispatch` — Core sends a command to an Agent.
- `command.accepted` — Agent accepts a command.
- `command.result` — Agent reports the result.
- `command.failed` — Agent reports a failure.

### Heartbeat

- `heartbeat.ping` — connection health check.
- `heartbeat.pong` — heartbeat response.

## 5. Reliability

- Messages have unique identifiers.
- Event delivery uses at-least-once semantics.
- Receivers must support deduplication.
- Events are acknowledged after successful receipt.
- Agents temporarily buffer important outgoing events during disconnection.
- After reconnecting, missed events can be requested using `event.replay`.
- Ordering is guaranteed within an individual event stream, not globally.

## 6. Reconnection

- Agent automatically attempts reconnection after connection loss.
- Reconnection uses an increasing delay between attempts.
- After reconnecting, Agent authenticates again.
- Agent reports its current state.
- Missed events are requested using the last acknowledged sequence number.

## 7. Heartbeat

- Core and Agent periodically exchange heartbeat messages.
- Missing heartbeat responses indicate a potentially lost connection.
- Heartbeat intervals and timeout thresholds are configurable.

## 8. Security

- WSS is required.
- Every Agent has an individual identity and credentials.
- Core validates the Agent before accepting messages.
- Messages from unauthorized Agents are rejected.
- Credential rotation and revocation must be supported.

## 9. Compatibility

- WebSocket protocol is independently versioned.
- Breaking protocol changes require a new major protocol version.
- Message types and payloads must be validated.
- Unsupported message types must be rejected or safely ignored according to their compatibility rules.

## 10. Implementation notes

This document defines the protocol contract, not its implementation.

Concrete message schemas, authentication details, heartbeat thresholds and reconnection parameters will be specified separately.