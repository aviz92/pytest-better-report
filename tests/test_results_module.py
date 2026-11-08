# pylint: disable=protected-access  # the fixture must reset the module's run stack to isolate each test
from collections.abc import Generator

import pytest

from pytest_better_report import results
from pytest_better_report.results import end_run, execution_results, start_run, test_results


@pytest.fixture(autouse=True)
def isolated_results() -> Generator[None, None, None]:
    saved = (dict(execution_results), dict(test_results), list(results._enclosing_snapshots))
    execution_results.clear()
    test_results.clear()
    results._enclosing_snapshots.clear()
    yield
    execution_results.clear()
    execution_results.update(saved[0])
    test_results.clear()
    test_results.update(saved[1])
    results._enclosing_snapshots[:] = saved[2]


class TestRunLifecycle:
    def test_start_run_empties_dicts_in_place(self) -> None:
        execution_results["execution_info"] = "previous"
        exec_ref, tests_ref = execution_results, test_results
        start_run()
        assert not execution_results and not test_results
        assert results.execution_results is exec_ref and results.test_results is tests_ref

    def test_outermost_run_keeps_results_after_end(self) -> None:
        start_run()
        execution_results["execution_info"] = "run"
        end_run()
        assert execution_results == {"execution_info": "run"}

    def test_nested_run_restores_enclosing_results(self) -> None:
        start_run()
        execution_results["execution_info"] = "outer"
        start_run()
        execution_results["execution_info"] = "inner"
        end_run()
        assert execution_results == {"execution_info": "outer"}
        end_run()
        assert execution_results == {"execution_info": "outer"}

    def test_end_run_without_start_is_noop(self) -> None:
        execution_results["execution_info"] = "kept"
        end_run()
        assert execution_results == {"execution_info": "kept"}
