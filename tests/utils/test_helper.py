import json
from pathlib import Path

from pytest_better_report.models import ExecutionStatus
from pytest_better_report.utils.helper import get_project_root, open_json, save_as_json, save_as_markdown


class TestGetProjectRoot:
    def test_returns_path_when_git_marker_exists(self) -> None:
        root = get_project_root(marker=".git")
        assert root is not None, "Expected project root to be found via .git marker"
        assert (root / ".git").exists(), "Expected .git to exist at the returned root"

    def test_returns_none_for_nonexistent_marker(self) -> None:
        root = get_project_root(marker="__nonexistent_marker_xyz__")
        assert root is None, "Expected None when no parent has the given marker"


class TestOpenJson:
    def test_reads_flat_json_correctly(self, tmp_path: Path) -> None:
        data = {"key": "value", "number": 42}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data))
        result = open_json(json_file)
        assert result == data, f"Expected {data}, got {result}"

    def test_reads_nested_json_correctly(self, tmp_path: Path) -> None:
        data = {"nested": {"a": 1, "b": [1, 2, 3]}}
        json_file = tmp_path / "nested.json"
        json_file.write_text(json.dumps(data))
        result = open_json(json_file)
        assert result == data, f"Expected {data}, got {result}"

    def test_reads_empty_dict(self, tmp_path: Path) -> None:
        json_file = tmp_path / "empty.json"
        json_file.write_text("{}")
        result = open_json(json_file)
        assert result == {}, f"Expected empty dict, got {result}"


class TestSaveAsJson:
    def test_creates_file_with_correct_content(self, tmp_path: Path) -> None:
        data = {"status": "passed", "count": 5}
        output_file = tmp_path / "output.json"
        save_as_json(path=output_file, data=data)
        assert output_file.exists(), "Expected output file to be created"
        result = json.loads(output_file.read_text())
        assert result == data, f"Expected {data}, got {result}"

    def test_creates_nested_parent_dirs(self, tmp_path: Path) -> None:
        nested_path = tmp_path / "a" / "b" / "output.json"
        save_as_json(path=nested_path, data={"x": 1})
        assert nested_path.exists(), "Expected file to be created inside nested dirs"

    def test_content_is_indented_json(self, tmp_path: Path) -> None:
        data = {"key": "value"}
        output_file = tmp_path / "output.json"
        save_as_json(path=output_file, data=data)
        content = output_file.read_text()
        assert "\n" in content, "Expected indented (multi-line) JSON output"

    def test_uses_custom_default_serializer(self, tmp_path: Path) -> None:
        data = {"status": ExecutionStatus.PASSED}
        output_file = tmp_path / "output.json"
        save_as_json(path=output_file, data=data, default=str)
        result = json.loads(output_file.read_text())
        assert result["status"] == "passed", f"Expected 'passed', got {result['status']}"

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        output_file = tmp_path / "output.json"
        save_as_json(path=output_file, data={"first": True})
        save_as_json(path=output_file, data={"second": True})
        result = json.loads(output_file.read_text())
        assert result == {"second": True}, "Expected file to be overwritten"


class TestSaveAsMarkdown:
    def test_creates_file_with_correct_content(self, tmp_path: Path) -> None:
        content = "# Report\n\nSome content."
        output_file = tmp_path / "report.md"
        save_as_markdown(path=output_file, data=content)
        assert output_file.exists(), "Expected markdown file to be created"
        assert output_file.read_text() == content, "Expected file content to match input"

    def test_creates_nested_parent_dirs(self, tmp_path: Path) -> None:
        nested_path = tmp_path / "reports" / "subdir" / "report.md"
        save_as_markdown(path=nested_path, data="# Test")
        assert nested_path.exists(), "Expected file to be created inside nested dirs"

    def test_empty_string_creates_empty_file(self, tmp_path: Path) -> None:
        output_file = tmp_path / "empty.md"
        save_as_markdown(path=output_file, data="")
        assert output_file.exists(), "Expected file to be created"
        assert output_file.read_text() == "", "Expected empty file content"
