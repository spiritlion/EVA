"""Хранилище состояния кластера в памяти EVA-Core."""

from __future__ import annotations

from collections.abc import Iterator
from threading import Lock


class Registry:
    """In-memory хранилище состояния кластера.

    Хранит регистрационные запросы и зарегистрированные узлы.
    Потокобезопасно (Lock). Данные живут только в памяти — при
    перезапуске Core состояние сбрасывается. Объём небольшой, подходит
    для стартовой версии без внешней БД.
    """

    def __init__(self) -> None:
        self._requests: dict[str, dict] = {}
        self._nodes: dict[str, dict] = {}
        self._lock = Lock()

    def put_request(self, request_id: str, response: dict) -> None:
        """Сохраняет результат регистрации по id запроса."""
        with self._lock:
            self._requests[request_id] = response

    def get_request(self, request_id: str) -> dict | None:
        """Возвращает сохранённый ответ регистрации или None."""
        with self._lock:
            return self._requests.get(request_id)

    def iter_requests(self) -> Iterator[dict]:
        """Перечисляет все сохранённые ответы регистрации."""
        with self._lock:
            return iter(list(self._requests.values()))

    def put_node(self, node: dict) -> None:
        """Сохраняет или обновляет информацию об узле по node_id."""
        with self._lock:
            self._nodes[node["node_id"]] = node

    def get_node(self, node_id: str) -> dict | None:
        """Возвращает информацию об узле или None."""
        with self._lock:
            return self._nodes.get(node_id)

    def iter_nodes(self) -> Iterator[dict]:
        """Перечисляет все зарегистрированные узлы."""
        with self._lock:
            return iter(list(self._nodes.values()))