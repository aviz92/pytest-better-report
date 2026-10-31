import json
from pathlib import Path

import pytest

from pytest_better_report.const import EXECUTION_RESULTS_FILENAME, TEST_RESULTS_FILENAME


class TestBetterReport:
    def test_output_files_created_when_enabled(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_foo() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        output_dir = pytester.path / "results_output"
        assert (
            output_dir / EXECUTION_RESULTS_FILENAME
        ).exists(), f"Expected {EXECUTION_RESULTS_FILENAME} to be created"
        assert (output_dir / TEST_RESULTS_FILENAME).exists(), f"Expected {TEST_RESULTS_FILENAME} to be created"

    def test_no_output_files_without_flag(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_foo() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess()
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        output_dir = pytester.path / "results_output"
        assert not output_dir.exists(), "Expected no output dir when plugin disabled"

    def test_execution_status_passed_on_passing_tests(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_foo() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        execution_file = pytester.path / "results_output" / EXECUTION_RESULTS_FILENAME
        data = json.loads(execution_file.read_text())
        assert (
            data["execution_info"]["execution_status"] == "passed"
        ), f"Expected 'passed', got {data['execution_info']['execution_status']}"

    def test_execution_status_failed_on_failing_tests(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_foo() -> None:
                assert False
        """
        )
        result = pytester.runpytest_subprocess("--better-report")
        assert result.ret == pytest.ExitCode.TESTS_FAILED, f"Expected TESTS_FAILED, got {result.ret}"
        execution_file = pytester.path / "results_output" / EXECUTION_RESULTS_FILENAME
        data = json.loads(execution_file.read_text())
        assert (
            data["execution_info"]["execution_status"] == "failed"
        ), f"Expected 'failed', got {data['execution_info']['execution_status']}"

    def test_test_results_contains_test_entry(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_my_test() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        test_file = pytester.path / "results_output" / TEST_RESULTS_FILENAME
        data = json.loads(test_file.read_text())
        assert len(data) == 1, f"Expected 1 test entry, got {len(data)}"
        test_entry = next(iter(data.values()))
        assert test_entry["test_status"] == "passed", f"Expected 'passed', got {test_entry['test_status']}"

    def test_custom_output_dir(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_foo() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report", "--output-dir=custom_dir")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        output_dir = pytester.path / "custom_dir" / "results_output"
        assert (
            output_dir / EXECUTION_RESULTS_FILENAME
        ).exists(), f"Expected {EXECUTION_RESULTS_FILENAME} in custom output dir"

    def test_md_report_generated_with_flag(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_foo() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report", "--md-report")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        output_dir = pytester.path / "results_output"
        assert (output_dir / "test_report.md").exists(), "Expected test_report.md to be created"

    def test_repo_name_stored_in_execution_results(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_foo() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report", "--repo-name=my-repo")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        execution_file = pytester.path / "results_output" / EXECUTION_RESULTS_FILENAME
        data = json.loads(execution_file.read_text())
        assert (
            data["execution_info"]["repo_name"] == "my-repo"
        ), f"Expected repo_name 'my-repo', got {data['execution_info']['repo_name']}"

    def test_pr_number_stored_in_execution_results(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_foo() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report", "--pr-number=42")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        execution_file = pytester.path / "results_output" / EXECUTION_RESULTS_FILENAME
        data = json.loads(execution_file.read_text())
        assert (
            data["execution_info"]["pull_request_number"] == "42"
        ), f"Expected pull_request_number '42', got {data['execution_info']['pull_request_number']}"

    def test_multiple_tests_all_tracked(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_first() -> None:
                assert True

            def test_second() -> None:
                assert True

            def test_third() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        test_file = pytester.path / "results_output" / TEST_RESULTS_FILENAME
        data = json.loads(test_file.read_text())
        assert len(data) == 3, f"Expected 3 test entries, got {len(data)}"

    def test_skipped_test_does_not_cause_failed_execution_status(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            import pytest

            def test_pass() -> None:
                assert True

            @pytest.mark.skip
            def test_skip() -> None:
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        execution_file = pytester.path / "results_output" / EXECUTION_RESULTS_FILENAME
        data = json.loads(execution_file.read_text())
        assert (
            data["execution_info"]["execution_status"] == "passed"
        ), f"Expected 'passed' when skipped tests present, got {data['execution_info']['execution_status']}"

    def test_skip_during_fixture_setup_marks_test_skipped(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            import pytest

            @pytest.fixture
            def skipping_fixture():
                pytest.skip("skipped test")

            def test_uses_skipping_fixture(skipping_fixture) -> None:
                pass
        """
        )
        result = pytester.runpytest_subprocess("--better-report")
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"
        test_file = pytester.path / "results_output" / TEST_RESULTS_FILENAME
        data = json.loads(test_file.read_text())
        test_entry = next(iter(data.values()))
        assert test_entry["test_status"] == "skipped", f"Expected 'skipped', got {test_entry['test_status']}"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


CONVERTER_CONFTEST = """
import pytest


@pytest.hookimpl({hookimpl_args})
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if call.when == "call" and report.failed:
        report.outcome = "skipped"
        report.longrepr = (str(item.path), 1, "converted")
"""


class TestStatusFromFinalReport:
    @pytest.mark.parametrize("hookimpl_args", ["hookwrapper=True, tryfirst=True", "hookwrapper=True"])
    def test_status_reflects_plugins_that_change_the_outcome(
        self, pytester: pytest.Pytester, hookimpl_args: str
    ) -> None:
        # Regression: BR decided the status inside makereport, so a plugin that converted the outcome after it
        # (e.g. fail2skip, depending on load order) left BR reporting "failed" for a test pytest reported as skipped.
        pytester.makeconftest(CONVERTER_CONFTEST.format(hookimpl_args=hookimpl_args))
        pytester.makepyfile("def test_converted():\n    assert False\n")
        result = pytester.runpytest_subprocess("--better-report")
        result.assert_outcomes(skipped=1)
        data = _read_json(pytester.path / "results_output" / TEST_RESULTS_FILENAME)
        assert data["test_converted"]["test_status"] == "skipped", data["test_converted"]["test_status"]

    def test_teardown_error_marks_test_failed(self, pytester: pytest.Pytester) -> None:
        # Regression: teardown was ignored, so a test that errored in teardown was reported as passed.
        pytester.makepyfile(
            """
            import pytest

            @pytest.fixture
            def broken_cleanup():
                yield
                raise RuntimeError("cleanup failed")

            def test_with_broken_cleanup(broken_cleanup):
                assert True
        """
        )
        result = pytester.runpytest_subprocess("--better-report")
        assert result.ret == pytest.ExitCode.TESTS_FAILED, f"Expected TESTS_FAILED, got {result.ret}"
        test_entry = _read_json(pytester.path / "results_output" / TEST_RESULTS_FILENAME)["test_with_broken_cleanup"]
        assert test_entry["test_status"] == "failed", test_entry["test_status"]
        assert test_entry["exception_message"]["message"] == "cleanup failed", test_entry["exception_message"]
        execution = _read_json(pytester.path / "results_output" / EXECUTION_RESULTS_FILENAME)
        assert execution["execution_info"]["execution_status"] == "failed"

    def test_call_failure_message_kept_when_teardown_also_fails(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            import pytest

            @pytest.fixture
            def broken_cleanup():
                yield
                raise RuntimeError("cleanup failed")

            def test_double_failure(broken_cleanup):
                raise ValueError("the real failure")
        """
        )
        pytester.runpytest_subprocess("--better-report")
        test_entry = _read_json(pytester.path / "results_output" / TEST_RESULTS_FILENAME)["test_double_failure"]
        assert test_entry["exception_message"]["message"] == "the real failure", test_entry["exception_message"]


class TestExceptionMessage:
    def test_json_object_message_is_recorded_as_structured_data(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            import json

            def test_structured():
                raise ValueError(json.dumps({"code": 500, "reason": "server error"}))
        """
        )
        result = pytester.runpytest_subprocess("--better-report", "--md-report")
        assert result.ret == pytest.ExitCode.TESTS_FAILED, f"Expected TESTS_FAILED, got {result.ret}"
        test_entry = _read_json(pytester.path / "results_output" / TEST_RESULTS_FILENAME)["test_structured"]
        assert test_entry["exception_message"] == {"code": 500, "reason": "server error"}
        # Regression: the Markdown report crashed with KeyError on a message without a "message" key.
        assert (pytester.path / "results_output" / "test_report.md").exists()

    def test_json_scalar_message_is_kept_as_text(self, pytester: pytest.Pytester) -> None:
        # Regression: a message that happened to parse as JSON but not as an object (e.g. "404") replaced the
        # whole exception_message with a bare number, breaking --traceback and the Markdown report.
        pytester.makepyfile("def test_status_code():\n    raise ValueError('404')\n")
        result = pytester.runpytest_subprocess("--better-report", "--md-report", "--traceback")
        assert result.ret == pytest.ExitCode.TESTS_FAILED, f"Expected TESTS_FAILED, got {result.ret}"
        test_entry = _read_json(pytester.path / "results_output" / TEST_RESULTS_FILENAME)["test_status_code"]
        assert test_entry["exception_message"]["exception_type"] == "ValueError"
        assert test_entry["exception_message"]["message"] == "404"
        assert "traceback" in test_entry["exception_message"]


class TestRecordedData:
    def test_user_properties_recorded(self, pytester: pytest.Pytester) -> None:
        pytester.makepyfile(
            """
            def test_with_property(record_property):
                record_property("device", "camera-7")
        """
        )
        pytester.runpytest_subprocess("--better-report")
        test_entry = _read_json(pytester.path / "results_output" / TEST_RESULTS_FILENAME)["test_with_property"]
        assert test_entry["test_user_properties"] == {"device": "camera-7"}, test_entry["test_user_properties"]

    def test_results_recorded_without_terminal_plugin(self, pytester: pytest.Pytester) -> None:
        # Regression: tests were registered in a terminal-reporter hook, so -p no:terminal produced an empty report.
        pytester.makepyfile("def test_quiet():\n    assert True\n")
        pytester.runpytest_subprocess("--better-report", "-p", "no:terminal")
        data = _read_json(pytester.path / "results_output" / TEST_RESULTS_FILENAME)
        assert data["test_quiet"]["test_status"] == "passed", data

    def test_result_each_test_is_logged(self, pytester: pytest.Pytester) -> None:
        # Regression: the flag checked an attribute nothing set, so it never logged anything.
        pytester.makepyfile("def test_logged():\n    assert True\n")
        result = pytester.runpytest_subprocess(
            "--better-report", "--result-each-test", "-o", "log_cli=true", "--log-cli-level=DEBUG"
        )
        result.stdout.fnmatch_lines(["*Test Results:*"])


class TestIsolation:
    def test_reporter_not_registered_without_flag(self, pytester: pytest.Pytester) -> None:
        pytester.makeconftest(
            """
            def pytest_sessionstart(session):
                assert not session.config.pluginmanager.has_plugin("better-report-reporter")
        """
        )
        pytester.makepyfile("def test_ok():\n    assert True\n")
        result = pytester.runpytest_subprocess()
        assert result.ret == pytest.ExitCode.OK, f"Expected OK, got {result.ret}"

    def test_no_state_leaks_between_runs_in_same_process(self, pytester: pytest.Pytester) -> None:
        # Regression: results lived in module-level dicts, so a second run in the same process inherited the
        # first run's tests and failures.
        pytester.makepyfile(
            test_first="def test_fails():\n    assert False\n",
            test_second="def test_passes():\n    assert True\n",
        )
        pytester.runpytest_inprocess("test_first.py", "--better-report", "--output-dir=first")
        pytester.runpytest_inprocess("test_second.py", "--better-report", "--output-dir=second")
        second_results = _read_json(pytester.path / "second" / "results_output" / TEST_RESULTS_FILENAME)
        assert list(second_results) == ["test_passes"], list(second_results)
        execution = _read_json(pytester.path / "second" / "results_output" / EXECUTION_RESULTS_FILENAME)
        assert execution["execution_info"]["execution_status"] == "passed"
