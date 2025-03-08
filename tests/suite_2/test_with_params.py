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

    def test_scenarios(self, test_scenarios):
        for scenario in test_scenarios:
            print(f"\nExecuting scenario: {scenario}")
            # Here you would implement the actual test logic for each scenario
            assert True, f"Scenario {scenario} failed"