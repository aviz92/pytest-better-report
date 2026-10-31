from pytest_better_report.models.status import ExecutionStatus


class TestExecutionStatus:
    def test_all_expected_members_defined(self) -> None:
        expected = {
            "COLLECTED",
            "STARTED",
            "PENDING",
            "PASSED",
            "FAILED",
            "XFAIL",
            "XPASS",
            "CANCELLED",
            "SKIPPED",
        }
        actual = {s.name for s in ExecutionStatus}
        assert actual == expected, f"Expected members {expected}, got {actual}"

    def test_passed_value(self) -> None:
        assert ExecutionStatus.PASSED == "passed", "Expected PASSED value to be 'passed'"

    def test_failed_value(self) -> None:
        assert ExecutionStatus.FAILED == "failed", "Expected FAILED value to be 'failed'"

    def test_skipped_value(self) -> None:
        assert ExecutionStatus.SKIPPED == "skipped", "Expected SKIPPED value to be 'skipped'"

    def test_xfail_value(self) -> None:
        assert ExecutionStatus.XFAIL == "xfailed", "Expected XFAIL value to be 'xfailed'"

    def test_xpass_value(self) -> None:
        assert ExecutionStatus.XPASS == "xpassed", "Expected XPASS value to be 'xpassed'"

    def test_collected_value(self) -> None:
        assert ExecutionStatus.COLLECTED == "collected", "Expected COLLECTED value to be 'collected'"

    def test_is_str_subclass(self) -> None:
        assert isinstance(ExecutionStatus.PASSED, str), "ExecutionStatus members should be str instances"

    def test_string_comparison_works(self) -> None:
        assert ExecutionStatus.PASSED == "passed", "StrEnum should compare equal to its string value"
        assert ExecutionStatus.FAILED != "passed", "Different statuses should not be equal"

    def test_string_formatting(self) -> None:
        result = f"status={ExecutionStatus.PASSED}"
        assert result == "status=passed", f"Expected 'status=passed', got '{result}'"
