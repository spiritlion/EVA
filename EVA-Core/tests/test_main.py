"""Тесты HTTP-эндпоинтов EVA-Core."""

import unittest

from aiohttp.test_utils import TestClient, TestServer

from eva.app import REGISTRY_KEY, create_app
from eva.config import Config

VALID_REQUEST = {
    "contract_version": "1.0.0",
    "request_id": "550e8400-e29b-41d4-a716-446655440010",
    "agent_id": "550e8400-e29b-41d4-a716-446655440001",
    "node_name": "test-node",
    "platform": "Windows",
    "agent_version": "0.1.0",
    "requested_at": "2026-11-01T09:00:00Z",
}

NODE = {
    "contract_version": "1.0.0",
    "node_id": "550e8400-e29b-41d4-a716-446655440aaa",
    "agent_id": "550e8400-e29b-41d4-a716-446655440001",
    "node_name": "ws-1",
    "status": "online",
    "registered_at": "2026-11-01T10:00:00Z",
    "capabilities": {
        "contract_version": "1.0.0",
        "agent_id": "550e8400-e29b-41d4-a716-446655440001",
        "collected_at": "2026-11-01T12:00:00Z",
        "platform": {"os": "Windows", "architecture": "x86_64"},
        "cpu": {"model": "Ryzen 7", "logical_cores": 16},
        "memory": {"total_bytes": 34359738368},
    },
}

CAPABILITIES = {
    "contract_version": "1.0.0",
    "agent_id": "550e8400-e29b-41d4-a716-446655440001",
    "collected_at": "2026-11-01T12:00:00Z",
    "platform": {"os": "Windows", "architecture": "x86_64"},
    "cpu": {"logical_cores": 16, "physical_cores": 8},
    "memory": {"total_bytes": 34359738368},
}

TELEMETRY = {
    "contract_version": "1.0.0",
    "agent_id": "550e8400-e29b-41d4-a716-446655440001",
    "collected_at": "2026-11-01T12:00:00Z",
    "sequence_number": 1,
    "cpu": {"usage_percent": 23.5},
    "memory": {"used_bytes": 12000000000, "available_bytes": 20000000000},
}


class RegistrationEndpointTest(unittest.IsolatedAsyncioTestCase):
    """Проверка POST /api/v1/nodes/registration-requests."""

    async def asyncSetUp(self) -> None:
        app = create_app(Config())
        self.client = TestClient(TestServer(app))
        await self.client.start_server()

    async def asyncTearDown(self) -> None:
        await self.client.close()

    async def test_valid_request_returns_pending_approval(self) -> None:
        resp = await self.client.post(
            "/api/v1/nodes/registration-requests",
            json=VALID_REQUEST,
        )
        self.assertEqual(resp.status, 202)

        body = await resp.json()
        self.assertEqual(body["contract_version"], "1.0.0")
        self.assertEqual(body["request_id"], VALID_REQUEST["request_id"])
        self.assertEqual(body["agent_id"], VALID_REQUEST["agent_id"])
        self.assertEqual(body["status"], "pending_approval")
        self.assertIn("issued_at", body)

    async def test_missing_required_field_returns_400(self) -> None:
        bad = dict(VALID_REQUEST)
        bad.pop("node_name")

        resp = await self.client.post(
            "/api/v1/nodes/registration-requests",
            json=bad,
        )
        self.assertEqual(resp.status, 400)

        body = await resp.json()
        self.assertEqual(body["code"], "VALIDATION_ERROR")
        self.assertIn("details", body)
        self.assertEqual(body["details"]["errors"][0]["message"], "'node_name' is a required property")

    async def test_bad_json_returns_400(self) -> None:
        resp = await self.client.post(
            "/api/v1/nodes/registration-requests",
            data="not-json",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status, 400)
        body = await resp.json()
        self.assertEqual(body["code"], "INVALID_JSON")

    async def test_status_returns_saved_registration(self) -> None:
        await self.client.post(
            "/api/v1/nodes/registration-requests",
            json=VALID_REQUEST,
        )

        resp = await self.client.get(
            f"/api/v1/nodes/registration-requests/{VALID_REQUEST['request_id']}"
        )
        self.assertEqual(resp.status, 200)
        body = await resp.json()
        self.assertEqual(body["request_id"], VALID_REQUEST["request_id"])
        self.assertEqual(body["status"], "pending_approval")

    async def test_status_unknown_request_returns_404(self) -> None:
        resp = await self.client.get(
            "/api/v1/nodes/registration-requests/00000000-0000-0000-0000-000000000000"
        )
        self.assertEqual(resp.status, 404)
        body = await resp.json()
        self.assertEqual(body["code"], "NOT_FOUND")


class NodeEndpointTest(unittest.IsolatedAsyncioTestCase):
    """Проверка GET /nodes/{id}, PUT capabilities, POST telemetry."""

    NODE_ID = NODE["node_id"]

    async def asyncSetUp(self) -> None:
        app = create_app(Config())
        app[REGISTRY_KEY].put_node(dict(NODE))
        self.client = TestClient(TestServer(app))
        await self.client.start_server()

    async def asyncTearDown(self) -> None:
        await self.client.close()

    async def test_get_node_info(self) -> None:
        resp = await self.client.get(f"/api/v1/nodes/{self.NODE_ID}")
        self.assertEqual(resp.status, 200)
        body = await resp.json()
        self.assertEqual(body["node_id"], self.NODE_ID)
        self.assertEqual(body["status"], "online")

    async def test_get_unknown_node_returns_404(self) -> None:
        resp = await self.client.get(
            "/api/v1/nodes/00000000-0000-0000-0000-000000000000"
        )
        self.assertEqual(resp.status, 404)
        body = await resp.json()
        self.assertEqual(body["code"], "NOT_FOUND")

    async def test_put_capabilities_updates_node(self) -> None:
        resp = await self.client.put(
            f"/api/v1/nodes/{self.NODE_ID}/capabilities",
            json=CAPABILITIES,
        )
        self.assertEqual(resp.status, 204)

        body = await (await self.client.get(f"/api/v1/nodes/{self.NODE_ID}")).json()
        self.assertEqual(body["capabilities"]["cpu"]["physical_cores"], 8)
        self.assertIsNotNone(body.get("last_seen_at"))

    async def test_put_invalid_capabilities_returns_400(self) -> None:
        resp = await self.client.put(
            f"/api/v1/nodes/{self.NODE_ID}/capabilities",
            json={"bad": True},
        )
        self.assertEqual(resp.status, 400)
        body = await resp.json()
        self.assertEqual(body["code"], "VALIDATION_ERROR")

    async def test_post_telemetry_updates_node(self) -> None:
        resp = await self.client.post(
            f"/api/v1/nodes/{self.NODE_ID}/telemetry",
            json=TELEMETRY,
        )
        self.assertEqual(resp.status, 204)

        body = await (await self.client.get(f"/api/v1/nodes/{self.NODE_ID}")).json()
        self.assertEqual(body["telemetry"]["sequence_number"], 1)

    async def test_put_capabilities_unknown_node_returns_404(self) -> None:
        resp = await self.client.put(
            "/api/v1/nodes/00000000-0000-0000-0000-000000000000/capabilities",
            json=CAPABILITIES,
        )
        self.assertEqual(resp.status, 404)


if __name__ == "__main__":
    unittest.main()