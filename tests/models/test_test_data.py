from pytest_better_report.models.status import ExecutionStatus
from pytest_better_report.models.test_data import TestData


def make_test_data(**kwargs: object) -> TestData:
    defaults = {
        "test_file_name": "test_foo.py",
        "class_test_name": None,
        "test_name": "test_bar",
        "pytest_test_name": "test_bar",
        "test_full_name": "test_bar",
        "test_full_path": "tests/test_foo.py::test_bar",
    }
    defaults.update(kwargs)
    return TestData(**defaults)


class TestTestData:
    def test_default_status_is_collected(self) -> None:
        data = make_test_data()
        assert data.test_status == ExecutionStatus.COLLECTED, f"Expected COLLECTED, got {data.test_status}"

    def test_optional_fields_default_to_none(self) -> None:
        data = make_test_data()
        assert data.test_parameters is None, "Expected None parameters by default"
        assert data.test_markers is None, "Expected None markers by default"
        assert data.test_start_time is None, "Expected None start time by default"
        assert data.test_end_time is None, "Expected None end time by default"
        assert data.test_duration_sec is None, "Expected None duration by default"
        assert data.exception_message is None, "Expected None exception message by default"
        assert data.run_index is None, "Expected None run_index by default"

    def test_required_fields_stored_correctly(self) -> None:
        data = make_test_data(
            test_file_name="test_example.py",
            test_name="test_something",
            test_full_path="tests/test_example.py::test_something",
        )
        assert data.test_file_name == "test_example.py", "Expected test_file_name to match"
        assert data.test_name == "test_something", "Expected test_name to match"
        assert data.test_full_path == "tests/test_example.py::test_something", "Expected test_full_path to match"

    def test_create_with_class_name(self) -> None:
        data = make_test_data(class_test_name="TestFoo")
        assert data.class_test_name == "TestFoo", "Expected class_test_name to match"

    def test_create_with_parameters(self) -> None:
        data = make_test_data(
            test_parameters={"x": 1, "y": 2},
            pytest_test_name="test_bar[x=1,y=2]",
            test_full_name="test_bar[{'x': 1, 'y': 2}]",
        )
        assert data.test_parameters == {"x": 1, "y": 2}, "Expected test_parameters to match"

    def test_create_with_markers(self) -> None:
        data = make_test_data(test_markers=["smoke", "regression"])
        assert data.test_markers == ["smoke", "regression"], "Expected markers to match"

    def test_status_is_mutable(self) -> None:
        data = make_test_data()
        data.test_status = ExecutionStatus.PASSED
        assert data.test_status == ExecutionStatus.PASSED, "Expected status to be updated"

    def test_exception_message_is_mutable(self) -> None:
        data = make_test_data()
        data.exception_message = {"exception_type": "AssertionError", "message": "boom"}
        assert data.exception_message["message"] == "boom", "Expected exception_message to be updatable"

    def test_run_index_set_correctly(self) -> None:
        data = make_test_data(run_index=3)
        assert data.run_index == 3, "Expected run_index to match"

    def test_timing_fields_are_mutable(self) -> None:
        data = make_test_data()
        data.test_start_time = "2024-01-01T12:00:00+00:00"
        data.test_end_time = "2024-01-01T12:00:01+00:00"
        data.test_duration_sec = 1.0
        assert data.test_start_time == "2024-01-01T12:00:00+00:00", "Expected start time to be set"
        assert data.test_end_time == "2024-01-01T12:00:01+00:00", "Expected end time to be set"
        assert data.test_duration_sec == 1.0, "Expected duration to be set"
