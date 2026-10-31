from unittest.mock import MagicMock

from pytest_better_report.utils.pytest_helper import (
    get_pytest_test_name,
    get_test_full_name,
    get_test_full_path,
    get_test_name_without_parameters,
    get_test_path_without_parameters,
)


def make_item(nodeid: str, callspec_params: dict | None = None) -> MagicMock:
    item = MagicMock()
    item.nodeid = nodeid
    if callspec_params is not None:
        callspec = MagicMock()
        callspec.params = callspec_params
        item.callspec = callspec
    else:
        item.callspec = None
    return item


class TestGetTestPathWithoutParameters:
    def test_simple_test(self) -> None:
        item = make_item("tests/test_foo.py::test_bar")
        assert get_test_path_without_parameters(item) == "tests/test_foo.py::test_bar", "Expected path without brackets"

    def test_parametrized_test_strips_brackets(self) -> None:
        item = make_item("tests/test_foo.py::test_bar[param1]")
        assert (
            get_test_path_without_parameters(item) == "tests/test_foo.py::test_bar"
        ), "Expected path without parameters"

    def test_nested_brackets_stripped(self) -> None:
        item = make_item("tests/test_foo.py::test_bar[x=1,y=2]")
        assert (
            get_test_path_without_parameters(item) == "tests/test_foo.py::test_bar"
        ), "Expected path without parameter brackets"


class TestGetTestNameWithoutParameters:
    def test_simple_test(self) -> None:
        item = make_item("tests/test_foo.py::test_bar")
        assert get_test_name_without_parameters(item) == "test_bar", "Expected only the test function name"

    def test_parametrized_test_strips_brackets(self) -> None:
        item = make_item("tests/test_foo.py::test_bar[param1]")
        assert get_test_name_without_parameters(item) == "test_bar", "Expected test name without parameter suffix"

    def test_class_method(self) -> None:
        item = make_item("tests/test_foo.py::TestClass::test_method")
        assert get_test_name_without_parameters(item) == "TestClass::test_method", "Expected class::method format"

    def test_class_method_parametrized(self) -> None:
        item = make_item("tests/test_foo.py::TestClass::test_method[1]")
        assert (
            get_test_name_without_parameters(item) == "TestClass::test_method"
        ), "Expected class::method without parameter suffix"


class TestGetPytestTestName:
    def test_simple_test(self) -> None:
        item = make_item("tests/test_foo.py::test_bar")
        assert get_pytest_test_name(item) == "test_bar", "Expected test function name"

    def test_parametrized_test_includes_brackets(self) -> None:
        item = make_item("tests/test_foo.py::test_bar[x=1]")
        assert get_pytest_test_name(item) == "test_bar[x=1]", "Expected test name with parameter brackets"

    def test_class_method(self) -> None:
        item = make_item("tests/test_foo.py::TestClass::test_method")
        assert get_pytest_test_name(item) == "TestClass::test_method", "Expected class::method format"


class TestGetTestFullName:
    def test_simple_test_without_params(self) -> None:
        item = make_item("tests/test_foo.py::test_bar")
        assert get_test_full_name(item) == "test_bar", "Expected simple test name"

    def test_parametrized_test_includes_param_dict(self) -> None:
        item = make_item("tests/test_foo.py::test_bar[1-2]", callspec_params={"x": 1, "y": 2})
        result = get_test_full_name(item)
        assert result == "test_bar[{'x': 1, 'y': 2}]", f"Expected dict representation of params, got {result}"

    def test_single_param_dict_format(self) -> None:
        item = make_item("tests/test_foo.py::test_bar[1]", callspec_params={"x": 1})
        result = get_test_full_name(item)
        assert result == "test_bar[{'x': 1}]", f"Expected single param dict, got {result}"


class TestGetTestFullPath:
    def test_simple_test_without_params(self) -> None:
        item = make_item("tests/test_foo.py::test_bar")
        assert get_test_full_path(item) == "tests/test_foo.py::test_bar", "Expected full path"

    def test_parametrized_test_includes_param_dict(self) -> None:
        item = make_item("tests/test_foo.py::test_bar[1]", callspec_params={"x": 1})
        result = get_test_full_path(item)
        assert result == "tests/test_foo.py::test_bar[{'x': 1}]", f"Expected full path with param dict, got {result}"

    def test_class_method_without_params(self) -> None:
        item = make_item("tests/test_foo.py::TestClass::test_method")
        assert (
            get_test_full_path(item) == "tests/test_foo.py::TestClass::test_method"
        ), "Expected full class method path"
