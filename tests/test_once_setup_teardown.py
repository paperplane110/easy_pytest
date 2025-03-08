import pytest

class TestExample:

    @pytest.fixture(scope='class', autouse=True)
    def setup_class(self):
        # 前处理逻辑
        print("\n[Setup] Setting up the test class...")
        self.env_check()
        self.upgrade()

        print("\n[Test] Running tests...")
        yield  # 这是测试的执行点

        # 后处理逻辑
        print("\n[Teardown] Tearing down the test class...")
        self.post_cleanup()

    def env_check(self):
        print("env check done")
        assert True, "env check failed"

    def upgrade(self):
        print("upgrade done")
        assert True, "upgrade failed"

    def test_case_1(self):
        print("Running test_case_1")
        assert True

    def test_case_2(self):
        print("Running test_case_2")
        assert True

    def post_cleanup(self):
        print("post cleanup done")
        assert True, "post cleanup failed"