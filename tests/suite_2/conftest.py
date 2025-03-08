import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--test-version",
        help="Version number to test"
    )
    parser.addoption(
        "--scena",
        action="append",
        default=[],
        help="Test scenarios to run (can be specified multiple times)"
    )

@pytest.fixture
def test_version(request):
    return request.config.getoption("--test-version")

@pytest.fixture
def test_scenarios(request):
    scenarios = request.config.getoption("--scena")
    if not scenarios:
        pytest.skip("No test scenarios specified")
    return scenarios
