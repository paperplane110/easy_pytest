import pytest

class TestWithParams:
    @pytest.fixture(scope='class', autouse=True)
    def setup_class(self):
        print("\n[Setup] Setting up the test class...")
        yield
        print("\n[Teardown] Cleaning up...")

    def test_with_version(self, test_version):
        print(f"Testing version: {test_version}")
        assert test_version is not None, "Test version must be specified"

    def test_one_scenario(self, one_scenario):
        print(f"\nExecuting scenario: {one_scenario}")
        # Here you would implement the actual test logic for each scenario
        assert True, f"Scenario {scenario} failed"