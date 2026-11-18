"""Тесты точки входа EVA."""

import unittest

from eva.main import main


class TestMain(unittest.TestCase):
    def test_main_is_callable(self) -> None:
        self.assertTrue(callable(main))


if __name__ == "__main__":
    unittest.main()