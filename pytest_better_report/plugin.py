"""Structured JSON (and optional Markdown) reporting of a pytest run: ``--better-report``.

Without ``--better-report`` the reporter is never registered, so none of its hooks run.

How results are recorded:
- A test's status is decided from pytest's **final** reports (``pytest_runtest_logreport``), after every plugin has
  finished changing them (e.g. one that converts failures into skips), so the result doesn't depend on plugin
  load order.
- The exception details come from the raw call information, captured in a plain ``pytest_runtest_makereport``
  wrapper. It never reads or decides the outcome there, only the exception, so its order doesn't matter either.
- All state lives on a reporter object created for each run, so nothing leaks between runs in the same process.
"""

import json
import platform
import sys
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from custom_python_logger import get_logger
from python_base_toolkit.utils.data_serialization import default_serialize

from pytest_better_report.const import (
    EXECUTION_RESULTS_FILENAME,
    LOGGER_NAME,
    MD_REPORT_FILENAME,
    OUTPUT_DIR_NAME,
    REPORTER_PLUGIN_NAME,
    TEST_RESULTS_FILENAME,
)
from pytest_better_report.models import ExecutionData, ExecutionStatus, TestData
from pytest_better_report.models.environment_data import EnvironmentData
from pytest_better_report.utils.create_report import generate_md_report
from pytest_better_report.utils.helper import save_as_json, save_as_markdown
from pytest_better_report.utils.pytest_helper import (
    get_pytest_test_name,
    get_test_full_name,
    get_test_full_path,
    get_test_name_without_parameters,
)

logger = get_logger(f"{LOGGER_NAME}.better_report")

_PASSING_STATUSES = (
    ExecutionStatus.COLLECTED,
    ExecutionStatus.PASSED,
    ExecutionStatus.SKIPPED,
    ExecutionStatus.XFAIL,
)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--better-report",
        action="store_true",
        default=False,
        help="Enable the pytest-better-report plugin",
    )
    parser.addoption(
        "--output-dir",
        type=Path,
        action="store",
        default=None,
        help="Directory to save the results and reports",
    )
    parser.addoption("--traceback", action="store_true", default=False, help="Enable detailed traceback in the report")
    parser.addoption(
        "--md-report", action="store_true", default=False, help="Generate a markdown report of the test results"
    )
    parser.addoption("--repo-name", action="store", default=None, help="Git Repository Name")
    parser.addoption("--pr-number", action="store", default=None, help="Pull Request Number")
    parser.addoption("--mr-number", action="store", default=None, help="Merge Request Number")
    parser.addoption("--pipeline-number", action="store", default=None, help="CI Pipeline Number")
    parser.addoption(
        "--commit",
        action="store",
        default=None,
        help="Commit Hash (SHA-1) of the repository at the time of test execution",
    )
    parser.addoption(
        "--add-parameters",
        action="store_true",
        default=None,
        help='Add the test parameters as fields to the "test_results.json" file',
    )
    parser.addoption(
        "--pytest-command",
        action="store_true",
        default=None,
        help='Add the detailed information about the pytest command-line to the "execution_results.json" file',
    )
    parser.addoption(
        "--pytest-xfail-strict",
        action="store_true",
        default=False,
        help="Enable strict xfail handling, treating unexpected passes as failures, if set to True "
        '"execution status" will be "failed" when there is at least one xpass test',
    )
    parser.addoption(
        "--result-each-test",
        action="store_true",
        default=False,
        help="Print the pytest result for each test after its execution",
    )
    parser.addoption(
        "--log-collected-tests",
        action="store_true",
        default=False,
        help="Log all collected tests at the start of the test session",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    if not config.getoption("--better-report"):
        return

    if config.option.output_dir:
        config.option.output_dir = config.option.output_dir / OUTPUT_DIR_NAME
    else:
        config.option.output_dir = Path(OUTPUT_DIR_NAME)

    config.pluginmanager.register(BetterReporter(config=config), REPORTER_PLUGIN_NAME)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    # Gated by its own flag, independent of --better-report (as it always was).
    if not config.getoption("--log-collected-tests"):
        return

    for item in items:
        logger.debug(f"Collected test: {get_test_full_name(item=item)}")


def _iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, UTC).isoformat()


def _status_from_report(report: pytest.TestReport) -> ExecutionStatus | None:
    """The status a single phase report implies, or None if it doesn't change the test's status."""
    if hasattr(report, "wasxfail") and report.skipped:
        return ExecutionStatus.XFAIL
    if hasattr(report, "wasxfail") and report.passed:
        return ExecutionStatus.XPASS
    if report.failed:
        return ExecutionStatus.FAILED
    if report.skipped:
        return ExecutionStatus.SKIPPED
    if report.when == "call" and report.passed:
        return ExecutionStatus.PASSED
    return None


class BetterReporter:
    """Registered only when ``--better-report`` is set; one instance per run holds all of the run's state."""

    def __init__(self, config: pytest.Config) -> None:
        self._config = config
        self.execution_results: dict[str, Any] = {}
        self.test_results: dict[str, TestData] = {}
        self._full_names: dict[str, str] = {}  # nodeid -> key in test_results
        self._setup_stop: dict[str, float] = {}
        self._tests_started = False

    def _get_test_data(self, nodeid: str) -> TestData | None:
        if (full_name := self._full_names.get(nodeid)) is None:
            return None
        return self.test_results.get(full_name)

    def pytest_sessionstart(self, session: pytest.Session) -> None:
        logger.info("Better report plugin enabled.")
        logger.info(f"Output directory set to: {session.config.option.output_dir}")

        self.execution_results["environment_info"] = EnvironmentData(
            python_version=platform.python_version(),
            platform=platform.platform(),
        )
        self.execution_results["execution_info"] = ExecutionData(
            execution_status=ExecutionStatus.STARTED,
            revision=datetime.now(UTC).strftime("%Y%m%d%H%M%S%f"),
            execution_start_time=datetime.now(UTC).isoformat(),
            repo_name=session.config.getoption("--repo-name", None),
            pull_request_number=session.config.getoption("--pr-number", None),
            merge_request_number=session.config.getoption("--mr-number", None),
            pipeline_number=session.config.getoption("--pipeline-number", None),
            commit=session.config.getoption("--commit", None),
        )
        if session.config.getoption("--pytest-command"):
            self.execution_results["pytest_command"] = {
                "real_cli": sys.argv,
                "ini_addopts": session.config.getini("addopts"),
                "raw_args": session.config.invocation_params.args,
            }

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        add_parameters = session.config.getoption("--add-parameters")
        for item in session.items:
            test_full_name = get_test_full_name(item=item)
            has_callspec_params = bool(getattr(item, "callspec", None) and getattr(item.callspec, "params", None))
            self._full_names[item.nodeid] = test_full_name
            self.test_results[test_full_name] = TestData(
                class_test_name=item.cls.__name__ if item.cls else None,
                test_name=get_test_name_without_parameters(item=item),
                pytest_test_name=get_pytest_test_name(item=item),
                test_full_name=test_full_name,
                test_full_path=get_test_full_path(item=item),
                test_file_name=item.path.name,
                test_parameters=item.callspec.params if has_callspec_params else None,
                test_markers=[marker.name for marker in item.iter_markers() if not marker.args],
                test_status=ExecutionStatus.COLLECTED,
                test_start_time=None,
                run_index=len(self.test_results) + 1,
            )
            if has_callspec_params and add_parameters:
                self.test_results[test_full_name].__dict__.update(**item.callspec.params)
        logger.debug(
            f"Tests to be executed: \n{json.dumps(list(self.test_results.keys()), indent=4, default=default_serialize)}"
        )

    # Not tryfirst, and it never reads report.outcome: it only captures the raw exception of each phase.
    @pytest.hookimpl(wrapper=True)
    def pytest_runtest_makereport(
        self, item: pytest.Item, call: pytest.CallInfo[None]
    ) -> Generator[None, pytest.TestReport, pytest.TestReport]:
        report = yield
        if (test_item := self._get_test_data(item.nodeid)) is None:
            return report

        if call.excinfo is None:
            if call.when == "call":
                test_item.exception_message = None
            return report

        # The first failing phase wins: a teardown error doesn't hide the call's failure.
        if call.when != "teardown" or test_item.exception_message is None:
            test_item.exception_message = _exception_message(
                call=call, with_traceback=item.config.getoption("--traceback")
            )
        return report

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if (test_item := self._get_test_data(report.nodeid)) is None:
            logger.warning(f"Test {report.nodeid} missing in test_results")
            return

        if report.when == "setup":
            self._tests_started = True
            self._setup_stop[report.nodeid] = report.stop
            test_item.test_start_time = _iso(report.stop)

        if (status := _status_from_report(report)) is not None:
            test_item.test_status = status

        if report.when != "teardown":
            return

        test_item.test_end_time = _iso(report.start)
        if (setup_stop := self._setup_stop.pop(report.nodeid, None)) is not None:
            test_item.test_duration_sec = report.start - setup_stop
        if report.user_properties:
            test_item.test_user_properties = dict(report.user_properties)

        if self._config.getoption("--result-each-test"):
            logger.debug(f"Test Results: \n{json.dumps(test_item, indent=4, default=default_serialize)}")

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        if session.config.option.collectonly or not self._tests_started:
            return

        self._finalize_execution_info(config=session.config)
        output_dir: Path = session.config.option.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        save_as_json(
            path=output_dir / EXECUTION_RESULTS_FILENAME, data=self.execution_results, default=default_serialize
        )
        save_as_json(path=output_dir / TEST_RESULTS_FILENAME, data=self.test_results, default=default_serialize)
        logger.info(f"Better report: Execution results saved to {output_dir / EXECUTION_RESULTS_FILENAME}")
        logger.info(f"Better report: Test results saved to {output_dir / TEST_RESULTS_FILENAME}")

        logger.info(f"Test session finished with exit status: {exitstatus}")
        if exitstatus != 0:
            failed_tests = [v for v in self.test_results.values() if v.test_status == ExecutionStatus.FAILED]
            logger.debug(f"Failed tests: {json.dumps(failed_tests, indent=4, default=default_serialize)}")

        if session.config.getoption("--md-report"):
            res_md = generate_md_report(report=json.loads(json.dumps(self.test_results, default=default_serialize)))
            save_as_markdown(path=output_dir / MD_REPORT_FILENAME, data=res_md)

    def _finalize_execution_info(self, config: pytest.Config) -> None:
        exec_info: ExecutionData = self.execution_results["execution_info"]
        exec_info.execution_end_time = datetime.now(UTC).isoformat()
        start = datetime.fromisoformat(exec_info.execution_start_time)
        end = datetime.fromisoformat(exec_info.execution_end_time)
        exec_info.execution_duration_sec = (end - start).total_seconds()

        passing_statuses = list(_PASSING_STATUSES)
        if not config.getoption("--pytest-xfail-strict"):
            passing_statuses.append(ExecutionStatus.XPASS)
        all_passed = all(t.test_status in passing_statuses for t in self.test_results.values())
        exec_info.execution_status = ExecutionStatus.PASSED if all_passed else ExecutionStatus.FAILED
        exec_info.test_list = list(self.test_results.keys())


def _exception_message(call: pytest.CallInfo[None], with_traceback: bool) -> dict[str, Any]:
    excinfo = call.excinfo
    message = str(excinfo.value).split("\nassert", maxsplit=1)[0]
    # A test can raise with a JSON object as its message to record structured data; anything else is plain text.
    try:
        parsed = json.loads(message)
    except json.JSONDecodeError:
        parsed = None
    exception_message: dict[str, Any] = (
        parsed if isinstance(parsed, dict) else {"exception_type": excinfo.typename, "message": message}
    )

    if with_traceback:
        exception_message["traceback"] = {
            "repr_crash": excinfo.getrepr().reprcrash,
            "traceback": [str(frame.path) for frame in excinfo.traceback],
        }
    return exception_message
