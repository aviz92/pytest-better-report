from pytest_better_report.models.execution_data import ExecutionData
from pytest_better_report.models.status import ExecutionStatus


class TestExecutionData:
    def test_create_with_required_fields(self) -> None:
        data = ExecutionData(
            execution_status=ExecutionStatus.STARTED,
            revision="20240101120000000000",
        )
        assert data.execution_status == ExecutionStatus.STARTED, "Expected STARTED status"
        assert data.revision == "20240101120000000000", "Expected revision to match"

    def test_optional_fields_default_to_none(self) -> None:
        data = ExecutionData(
            execution_status=ExecutionStatus.STARTED,
            revision="rev123",
        )
        assert data.execution_start_time is None, "Expected None start time by default"
        assert data.execution_end_time is None, "Expected None end time by default"
        assert data.execution_duration_sec is None, "Expected None duration by default"
        assert data.repo_name is None, "Expected None repo_name by default"
        assert data.pull_request_number is None, "Expected None pull_request_number by default"
        assert data.merge_request_number is None, "Expected None merge_request_number by default"
        assert data.pipeline_number is None, "Expected None pipeline_number by default"
        assert data.commit is None, "Expected None commit by default"
        assert data.test_list is None, "Expected None test_list by default"

    def test_create_with_all_fields(self) -> None:
        data = ExecutionData(
            execution_status=ExecutionStatus.PASSED,
            revision="rev-001",
            execution_start_time="2024-01-01T12:00:00+00:00",
            execution_end_time="2024-01-01T12:01:00+00:00",
            execution_duration_sec="60.0",
            repo_name="my-repo",
            pull_request_number="42",
            merge_request_number="7",
            pipeline_number="100",
            commit="abc123def456",
            test_list=["test_foo", "test_bar"],
        )
        assert data.repo_name == "my-repo", "Expected repo_name to match"
        assert data.pull_request_number == "42", "Expected pull_request_number to match"
        assert data.test_list == ["test_foo", "test_bar"], "Expected test_list to match"

    def test_execution_status_is_mutable(self) -> None:
        data = ExecutionData(
            execution_status=ExecutionStatus.STARTED,
            revision="rev",
        )
        data.execution_status = ExecutionStatus.PASSED
        assert data.execution_status == ExecutionStatus.PASSED, "Expected status to be updated"

    def test_test_list_is_mutable(self) -> None:
        data = ExecutionData(
            execution_status=ExecutionStatus.STARTED,
            revision="rev",
        )
        data.test_list = ["test_one", "test_two"]
        assert data.test_list == ["test_one", "test_two"], "Expected test_list to be updatable"

    def test_execution_end_time_is_mutable(self) -> None:
        data = ExecutionData(
            execution_status=ExecutionStatus.STARTED,
            revision="rev",
        )
        data.execution_end_time = "2024-01-01T12:01:00+00:00"
        assert data.execution_end_time == "2024-01-01T12:01:00+00:00", "Expected execution_end_time to be updatable"
