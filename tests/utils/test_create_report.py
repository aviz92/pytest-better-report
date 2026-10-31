from pytest_better_report.utils.create_report import generate_md_report


def _make_test_entry(
    test_full_name: str = "test_foo",
    test_status: str = "passed",
    test_duration_sec: float | None = 1.0,
    exception_message: dict | None = None,
) -> dict:
    return {
        "test_full_name": test_full_name,
        "test_status": test_status,
        "test_duration_sec": test_duration_sec,
        "exception_message": exception_message,
    }


class TestGenerateMdReport:
    def test_report_contains_header(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry()})
        assert "## ✅ Test Report Summary" in result, "Expected report header"

    def test_report_contains_table_headers(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry()})
        assert "| No. | Test Name | Status | Duration | Message |" in result, "Expected table headers row"

    def test_passed_test_shows_checkmark_icon(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry(test_status="passed")})
        assert "✅" in result, "Expected ✅ icon for passed test"

    def test_failed_test_shows_x_icon(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry(test_status="failed")})
        assert "❌" in result, "Expected ❌ icon for failed test"

    def test_skipped_test_shows_skip_icon(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry(test_status="skipped")})
        assert "⏭️" in result, "Expected ⏭️ icon for skipped test"

    def test_xfailed_test_shows_x_icon(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry(test_status="xfailed")})
        assert "❌" in result, "Expected ❌ icon for xfailed test"

    def test_json_object_message_without_message_key(self) -> None:
        # Regression: a test that raises with a JSON object as its message crashed the report with KeyError.
        entry = _make_test_entry(test_status="failed", exception_message={"code": 500, "reason": "server error"})
        result = generate_md_report(report={"t": entry})
        assert '{"code": 500, "reason": "server error"}' in result, "Expected the JSON object in the message column"

    def test_unexpected_status_does_not_crash(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry(test_status="started")})
        assert "started" in result, "Expected an unknown status to be rendered as-is"

    def test_exception_message_shown_in_row(self) -> None:
        result = generate_md_report(
            report={
                "t": _make_test_entry(
                    test_status="failed",
                    exception_message={"message": "AssertionError: boom"},
                )
            }
        )
        assert "AssertionError: boom" in result, "Expected exception message in report row"

    def test_no_exception_shows_dash_placeholder(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry(exception_message=None)})
        assert "`-`" in result, "Expected dash placeholder when no exception"

    def test_duration_formatted_to_two_decimal_places(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry(test_duration_sec=1.5)})
        assert "1.50s" in result, "Expected duration formatted to 2 decimal places"

    def test_none_duration_shows_dash_placeholder(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry(test_status="collected", test_duration_sec=None)})
        assert "| - |" in result, "Expected dash placeholder for unrun test with no duration"

    def test_summary_shows_correct_total_count(self) -> None:
        report = {
            "t1": _make_test_entry("test_1"),
            "t2": _make_test_entry("test_2"),
            "t3": _make_test_entry("test_3"),
        }
        result = generate_md_report(report=report)
        assert "Total: 3" in result, "Expected total count of 3 in summary"

    def test_empty_report_shows_zero_total(self) -> None:
        result = generate_md_report(report={})
        assert "Total: 0" in result, "Expected total count of 0 for empty report"

    def test_test_name_appears_in_row(self) -> None:
        result = generate_md_report(report={"t": _make_test_entry(test_full_name="test_my_function")})
        assert "test_my_function" in result, "Expected test name to appear in the report row"

    def test_multiple_tests_all_appear_in_report(self) -> None:
        report = {
            "t1": _make_test_entry("test_alpha", test_status="passed"),
            "t2": _make_test_entry("test_beta", test_status="failed"),
        }
        result = generate_md_report(report=report)
        assert "test_alpha" in result, "Expected test_alpha in report"
        assert "test_beta" in result, "Expected test_beta in report"
        assert "✅" in result, "Expected passed icon"
        assert "❌" in result, "Expected failed icon"
