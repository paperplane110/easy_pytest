import pytest
from src.package.main import plus, minus


class TestMain:
    def test_plus_int(self):
        assert plus(1, 2) == 3

    def test_plus_float(self):
        assert plus(1.5, 2.0) == 3.5

    def test_minus_int(self):
        assert minus(1, 2) == -1

    def test_minus_float(self):
        assert minus(1.5, 2.0) == -0.5
