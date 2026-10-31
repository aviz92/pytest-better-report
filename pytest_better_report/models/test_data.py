from dataclasses import dataclass

from pytest_better_report.models.status import ExecutionStatus


@dataclass
class TestData:
    __test__ = False  # a data model, not a test class (stops pytest from trying to collect it)

    test_file_name: str
    class_test_name: str | None
    test_name: str
    pytest_test_name: str
    test_full_name: str
    test_full_path: str
    test_status: ExecutionStatus = ExecutionStatus.COLLECTED
    test_parameters: dict[str, object] | None = None
    test_markers: list | None = None
    test_start_time: str | None = None
    test_end_time: str | None = None
    test_duration_sec: float | None = None  # only for the tst itself, not including fixtures
    exception_message: dict | None = None
    run_index: int | None = None
    test_user_properties: dict[str, object] | None = None
