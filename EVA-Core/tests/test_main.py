"""Тесты HTTP-эндпоинтов EVA-Core."""

import unittest

from aiohttp.test_utils import TestClient, TestServer

from eva.app import create_app
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


if __name__ == "__main__":
    unittest.main()