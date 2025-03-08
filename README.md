# 🛸 漫步 pytest 

记录我在工作的 pytest 实践经验，类似于 How to ...

- 【不是】以 pytest 功能为导向的文档
- 【是】以我工作时遇到问题为导向来组织文档
- 配合本代码库，一边看一边敲命令，能更好理解

希望能帮助到大家 🤝

## 目录

- [🛸 漫步 pytest](#-漫步-pytest)
  - [目录](#目录)
  - [0. 安装本项目（可跳过）](#0-安装本项目可跳过)
  - [1. 组织测试项目](#1-组织测试项目)
    - [测试项目的结构](#测试项目的结构)
    - [测试脚本的命名规则](#测试脚本的命名规则)
  - [2. 测试函数的组织](#2-测试函数的组织)
  - [3. 梳理测试流程](#3-梳理测试流程)
  - [4. 只执行一次的 setup 和 teardown](#4-只执行一次的-setup-和-teardown)
    - [问题：什么是 pytest.fixture，是干什么用的](#问题什么是-pytestfixture是干什么用的)
  - [5. 命令行传参给测试任务](#5-命令行传参给测试任务)
    - [方法：](#方法)
    - [问题: 什么是conftest.py](#问题-什么是conftestpy)
    - [我的对传入参数的要求：](#我的对传入参数的要求)
    - [测试脚本如何获取参数](#测试脚本如何获取参数)
  - [6. ‘参数化’生成测试用例](#6-参数化生成测试用例)
    - [我怎么理解‘参数化’生成测试用例](#我怎么理解参数化生成测试用例)
    - [怎么用 pytest 进行参数化测试](#怎么用-pytest-进行参数化测试)
  - [参考：](#参考)

## 0. 安装本项目（可跳过）

```bash
git clone
cd learn_pytest
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 1. 组织测试项目

面对一个空文件夹、一个被测对象，我遇到的第一个问题就是，我如何组织测试项目，如何组织测试脚本。

按照文档指导，我总结了以下规则：

### 测试项目的结构

  - 测试项目 tests/ 与源码 src/ 平级
  - 测试项目 tests/ 可组织任意层级的**子文件夹**
  - 测试项目 tests/ 必须包含 `__init__.py` 文件，否则 pytest 无法识别测试脚本

### 测试脚本的命名规则

- pytest 无法识别 test.py 文件
- 测试脚本 test_*.py 必须以 `test_` 开头，否则 pytest 无法识别测试脚本
- 测试脚本 *_test.py 必须以 `_test` 结尾，否则 pytest 无法识别测试脚本

```
.
├── README.md
├── src                 <--- 源码项目
│  └── package
│     ├── __init__.py
│     └── main.py
└── tests               <--- 测试项目
   ├── __init__.py
   └── test_suite_1     <--- 测试套件
      ├── __init__.py
      └── test_main.py  <--- 测试脚本
```

现在我们试着来进行第一次测试：

```bash
# -v 打印更多信息，显示测试 parent_suite and case_name
pytest -v
# ...
# ==================== test session starts =====================
# tests/suite_1/test_main.py::test_plus_int PASSED  [ 25%]
# tests/suite_1/test_main.py::test_plus_float PASSED   [ 50%]
# tests/suite_1/test_main.py::test_minus_int PASSED  [ 75%]
# tests/suite_1/test_main.py::test_minus_float PASSED  [100%]
# ===================== 4 passed in 0.01s =======================
```

## 2. 测试函数的组织

现在我们来看下我们的测试脚本 [`test_main.py`](./tests/suite_1/test_main.py)

```python
import pytest
from src.package.main import plus, minus

def test_plus_int():
    assert plus(1, 2) == 3
def test_plus_float():
    ...
def test_minus_int():
    ...
def test_minus_float():
    ...
```

测试函数零散的放在文件中，不利于测试函数的组织和管理，我们可以将测试函数放在类中，比如`class TestSomething`，这样有几点好处：

- 测试函数可以被组织在类中，方便管理
- fixture 的作用域可以被限制在类中，方便管理
  - 比如，让每个测试函数执行相同的 setup 函数，和 teardown 函数
  - 比如，在整个测试流程前执行一次 setup 函数，和在整个测试流程后执行一次 teardown 函数

## 3. 梳理测试流程

在工作中，我面临的测试流程是这样的，每个 `o` 代表一个步骤

```
| setup |  tests  | teardown |
         /-o-o-o-\
o-o-o-o-<--o-o-o-->-o-o-o-o
         \-o-o-o-/
```

1. setup: 测试前，环境准备流程很长，在测试前执行一次即可，若失败则整个测试流程失败。
2. tests: 测试过程:
   1. 有 n 个测试场景，每个测试场景有 k 个步骤
   2. n 个**场景是动态传入**的，通过命令行参数传入
   3. n 个**场景间相互独立**，每个场景的步骤是一样的，比如：
      1. 测试场景 1: 测试函数 A, B, C
      2. 测试场景 2: 测试函数 A, B, C
   4. k 个**步骤前后依赖**，比如函数 A 依赖函数 B 的结果
3. teardown: 测试后，环境清理流程很长，在测试后执行一次即可，若失败则整个测试流程失败。

面对这个需求，我们来拆解一下实现的路径：

- 首先找到一种方法，让 setup 和 teardown 只执行一次，而不是每个测试都执行
- pytest 命令行传参的方法，让我动态的传入每次要测试的 n 个场景
- 根据我传入的 n 个场景动态的生成这些平行的 n 个测试链条

现在让我来逐一解决一下。

## 4. 只执行一次的 setup 和 teardown

方法：使用 fixture，作用域为 class 级, 并且使用 autouse=True 参数

### 问题：什么是 pytest.fixture，是干什么用的

- fixture 是一个装饰器，被它装饰的函数可以在作用域范围内被任意的使用，所以我们能用它做以下事情：
  - 环境准备
  - 数据准备
  - 等等...
- 具体文档：[About fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)

示例代码：[tests/test_once_setup_teardown.py](./tests/test_once_setup_teardown.py)

```python
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
```

让我们来试一试：

```bash
pytest -s tests/test_once_setup_teardown.py

# tips: -s let print() to stdout
```

输出结果为：

```
tests/test_once_setup_teardown.py 
[Setup] Setting up the test class...
env check done
upgrade done

[Test] Running tests...
Running test_case_1
.Running test_case_2
.
[Teardown] Tearing down the test class...
post cleanup done
```

能看到 setup 和 teardown 只执行了一次。

- [x] 首先找到一种方法，让 setup 和 teardown 只执行一次，而不是每个测试都执行
- [ ] pytest 命令行传参的方法，让我动态的传入每次要测试的 n 个场景
- [ ] 根据我传入的 n 个场景动态的生成这些平行的 n 个测试链条

接下来解决传参的问题。

## 5. 命令行传参给测试任务

### 方法：

- 在测试脚本同层级的目录新建 conftest.py
- 在 conftest.py 中定义 pytest_addoption 函数，用来接收命令行传入的参数

### 问题: 什么是conftest.py

- conftest.py 是 pytest 的一个特殊文件，是一批测试脚本所共用的‘配置’文件
- pytest 会自动加载 conftest.py 中的 fixture，并在测试脚本中使用。我们不用在测试脚本里显式的`import`我们定义的 fixture 了
- 作用范围：conftest 所在的目录及其子目录

### 我的对传入参数的要求：

- test_version: 要测试的版本号
- scena: 要测试的场景，可以传入多个

示例代码：[tests/suite_2/conftest.py](./tests/suite_2/conftest.py)

```python
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
```

上面有三个函数函数，我们一一介绍一下

1. `pytest_addoption`：这个函数定义了接受那些参数，形式与 `argsparser` 一致
2. `test_version`: 这个函数接受参数 `request`，这个参数由 pytest 自动定义并传入，我们不用特别关心。
   1. 我们从 request 对象中拿到了传入参数 --test-version
   2. 并给这个函数加上 fixture，这样在测试脚本中，我们就能直接获取版本了，只需这样：`def test_func(test_version)`
3. `test_scenarios`：作用同上，我们对传入的 `--scena` 进行了处理然后返回。

### 测试脚本如何获取参数

我们对[第四章中的函数](#4-只执行一次的-setup-和-teardown)进行修改：[tests/suite_2/test_with_params.py](./tests/suite_2/test_with_params.py)

```python
import pytest

class TestWithParams:
    @pytest.fixture(scope='class', autouse=True)
    def setup_class(self):
        ...

    def test_with_version(self, test_version):
        print(f"Testing version: {test_version}")
        assert test_version is not None, "Test version must be specified"

    def test_scenarios(self, test_scenarios):
        for scenario in test_scenarios:
            print(f"\nExecuting scenario: {scenario}")
            assert True, f"Scenario {scenario} failed"
```

首先看下 test_ 开头的函数，他们的入参是 test_version、test_scenarios，这两个名字和[上一步](#测试脚本如何获取参数)中定义的两个 fixture 相对应。在测试运行时，由 pytest 的 fixture 机制来传入实际的值——也就是我们通过命令行传入的值。

现在让我们试一试

```bash
pytest -sv tests/suite_2/test_with_params.py --test-version 1.0.0 --scena scenario1 --scena scenario2
```

输出结果为：

```
collected 2 items
tests/suite_2/test_with_params.py::TestWithParams::test_with_version 
[Setup] Setting up the test class...
Testing version: 1.0.0
PASSED
tests/suite_2/test_with_params.py::TestWithParams::test_scenarios 
Executing scenario: scenario1

Executing scenario: scenarioa2
PASSED
[Teardown] Cleaning up...
```

我们看到这些关键打印，以为我们的参数已经成功传入了测试脚本，我们想要的就是这个效果：

- **Testing version: 1.0.0**
- **Executing scenario: scenario1**
- **Executing scenario: scenario2**

但是有一点是不符合预期的，虽然 scenario 都执行了，但是 pytest 把它当成了一个用例，因为我们其实是在一个测试函数中用 for 循环来遍历 scenario。

这显然是不符合我们要求的，我们希望每一个 scenario 都是一个用例。

再回顾一下需要解决的问题：

- [x] 首先找到一种方法，让 setup 和 teardown 只执行一次，而不是每个测试都执行
- [x] pytest 命令行传参的方法，让我动态的传入每次要测试的 n 个场景
- [ ] 根据我传入的 n 个场景动态的生成这些平行的 n 个测试链条

我们接下来解决第三个问题，也就是‘**参数化**’生成测试用例。

## 6. ‘参数化’生成测试用例

### 我怎么理解‘参数化’生成测试用例

其实很好理解，每一个参数都生成一个测试用例。在我工作的情景中，

- 参数：多个测试场景 scenarios
- 参数化测试：
  - 把测试场景每一个都跑一遍
  - 每跑一次就认为是一个测试用例

### 怎么用 pytest 进行参数化测试

参考[官方文档](https://docs.pytest.org/en/stable/how-to/parametrize.html#basic-pytest-generate-tests-example)，pytest 提供了三种方法：

- @pytest.fixture + params
- @pytest.mark.parametrize
- hook: pytest_generate_tests

前两种的参数化以来我们将参数硬编码到代码中，这和我们‘动态传入scenario’的需求不符合，所以采用第三种方法。

我们需要对 conftest 进行改造：[tests/suite_3/conftest.py](./tests/suite_3/conftest.py)

```python
# ============ conftest.py ============
# skip code above

def pytest_generate_tests(metafunc: pytest.Metafunc):
    if "one_scenario" in metafunc.fixturenames:
        metafunc.parametrize("one_scenario", metafunc.config.getoption("scena"))
```

并对测试脚本进行改造：[test/suite_3/test_with_parametrize.py](./tests/suite_3/test_with_parametrize.py)

```python
# ============ test_with_parametrize.py ============
# skip code above

    def test_one_scenario(self, one_scenario):
        print(f"\nExecuting scenario: {one_scenario}")
        # Here you would implement the actual test logic for each scenario
        assert True, f"Scenario {scenario} failed"
```

我们首先看 contest.py, 首先是判断语句

```python
if "one_scenario" in metafunc.fixturenames:
```

意思是，我们的测试函数的参数中，对 'one_scenario' 这个参数有需求吗，有需求的话就进行下面的参数化调用

```python
metafunc.parametrize("one_scenario", metafunc.config.getoption("scena"))
```

第一参数，`"one_scenario"`,测试函数所需参数的名字。

第二个参数 `metafunc.config.getoption("scena")`，把命令行参数 `scena` 逐一传给 `one_scenario`

现在我们再看看测试函数：

```python
def test_one_scenario(self, one_scenario):
```

我们看到这个函数需要 `one_scenario`，和上面 conftest.py 的 `if "one_scenario" in metafunc.fixturenames` 正好对应，于是‘参数化’的效果就会作用于这个函数了。

总结一下，需要一一对应的位置有三处，如下

```python
# ============ conftest.py ============
def pytest_generate_tests(metafunc: pytest.Metafunc):
            👇
    if "one_scenario" in metafunc.fixturenames:
                                👇
        metafunc.parametrize("one_scenario", metafunc.config.getoption("scena"))

# ============ test_with_parametrize.py ============
                                    👇
    def test_one_scenario(self, one_scenario):
        ...
```

现在让我跑一下测试看看

```bash
pytest -sv tests/suite_3/test_with_parametrize.py --test-version 1.0.0 --scena scenario1 --scena scenario2
```

```
tests/suite_3/test_with_parametrize.py::TestWithParams::test_with_version 
[Setup] Setting up the test class...
Testing version: 1.0.0
PASSED
tests/suite_3/test_with_parametrize.py::TestWithParams::test_one_scenario[scenario1] 
Executing scenario: scenario1
PASSED
tests/suite_3/test_with_parametrize.py::TestWithParams::test_one_scenario[scenario2] 
Executing scenario: scenario2
PASSED
[Teardown] Cleaning up...
```

能看到，scenario1 和 scenario2 都被当成单独的用例了！
 
整个过程涉及多个概念，大家有时间可以具体的去了解，相见[参考](#参考)

至此三个问题都解决了 👏

- [x] 首先找到一种方法，让 setup 和 teardown 只执行一次，而不是每个测试都执行
- [x] pytest 命令行传参的方法，让我动态的传入每次要测试的 n 个场景
- [x] 根据我传入的 n 个场景动态的生成这些平行的 n 个测试链条

---

## 参考：

- 项目结构：
  - https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure%3E
  - https://packaging.python.org/en/latest/tutorials/packaging-projects/
- 测试内部结构：https://docs.pytest.org/en/stable/explanation/anatomy.html#test-anatomy

参数化测试

- [pytest_generate_tests(metafunc)](https://docs.pytest.org/en/stable/reference/reference.html#pytest.hookspec.pytest_generate_tests)：pytest hook，Generate (multiple) parametrized calls to a test function.
  - 生成多个参数化调用，将这些调用应用于测试函数
  - 说人话就是，我们可以对‘参数化测试’进行更加定制化的配置。比如在我们的例子中，其实
- [pytest.Metafunc](https://docs.pytest.org/en/stable/reference/reference.html#metafunc): They help to inspect a test function and to generate tests according to test configuration or values specified in the class or module where a test function is defined.
  - 代表一个测试函数
  - 可以获取测试配置、测试类中的值、测试函数所属的测试模块
  - 结合以上信息来生成测试
- [pytest.Metafunc.fixturenames](https://docs.pytest.org/en/stable/reference/reference.html#pytest.Metafunc.fixturenames): 测试函数所需要的 fixture 集合，是个 list[str]
- [pytest.Metafunc.parametrize](https://docs.pytest.org/en/stable/reference/reference.html#pytest.Metafunc.parametrize):
  - MetaFunc的方法，可以参数化生成测试，我们主要用这个函数来生成多个测试