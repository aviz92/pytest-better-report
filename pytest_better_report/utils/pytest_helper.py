from _pytest.python import Function


def get_test_path_without_parameters(item: Function) -> str:
    """Get the test name without parameters."""
    return item.nodeid.split("[")[0]


def get_test_name_without_parameters(item: Function) -> str:
    """Get the test name without parameters."""
    return item.nodeid.split(".py::")[-1].split("[")[0]


def get_pytest_test_name(item: Function) -> str:
    """Get the test name without parameters."""
    return item.nodeid.split(".py::")[-1]


def get_test_full_name(item: Function) -> str:
    """Get the full name of the test, including parameters if available."""
    test_name = get_test_name_without_parameters(item=item)
    return f"{test_name}[{item.callspec.params}]" if getattr(item, "callspec", None) else test_name


def get_test_full_path(item: Function) -> str:
    """Get the full name of the test, including parameters if available."""
    test_name = get_test_path_without_parameters(item=item)
    return f"{test_name}[{item.callspec.params}]" if getattr(item, "callspec", None) else test_name
