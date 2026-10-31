import json
import subprocess
import sys
from pathlib import Path

import pytest

from pytest_better_report.compare import compare_reports, load_report


def _entry(name: str, status: str, file_name: str = "test_a.py") -> dict:
    return {"pytest_test_name": name, "test_status": status, "test_file_name": file_name}


def _write(path: Path, entries: list[dict]) -> Path:
    path.write_text(json.dumps({entry["pytest_test_name"]: entry for entry in entries}), encoding="utf-8")
    return path


@pytest.fixture(name="report_a")
def fixture_report_a(tmp_path: Path) -> Path:
    return _write(tmp_path / "a.json", [_entry("test_one", "passed"), _entry("test_two", "failed")])


class TestCompareReports:
    def test_identical_reports(self, tmp_path: Path, report_a: Path) -> None:
        report_b = _write(tmp_path / "b.json", [_entry("test_one", "passed"), _entry("test_two", "failed")])
        assert compare_reports(report_a, report_b) is True

    def test_status_difference(self, tmp_path: Path, report_a: Path, capsys: pytest.CaptureFixture[str]) -> None:
        report_b = _write(tmp_path / "b.json", [_entry("test_one", "passed"), _entry("test_two", "passed")])
        assert compare_reports(report_a, report_b) is False
        assert "test_two" in capsys.readouterr().out

    def test_missing_test(self, tmp_path: Path, report_a: Path, capsys: pytest.CaptureFixture[str]) -> None:
        report_b = _write(tmp_path / "b.json", [_entry("test_one", "passed")])
        assert compare_reports(report_a, report_b) is False
        assert "MISSING from B" in capsys.readouterr().out

    def test_filter_by_test_file_name(self, tmp_path: Path) -> None:
        report = _write(
            tmp_path / "r.json", [_entry("test_one", "passed", "test_a.py"), _entry("test_x", "passed", "test_b.py")]
        )
        assert list(load_report(report, test_file_name="test_b.py")) == ["test_x"]


class TestCompareCli:
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "pytest_better_report.compare", *args], capture_output=True, text=True, check=False
        )

    def test_identical_exits_zero(self, tmp_path: Path, report_a: Path) -> None:
        report_b = _write(tmp_path / "b.json", [_entry("test_one", "passed"), _entry("test_two", "failed")])
        result = self._run("-a", str(report_a), "-b", str(report_b), "--fail-on-diff")
        assert result.returncode == 0, result.stdout + result.stderr
        assert "REPORTS ARE IDENTICAL" in result.stdout

    def test_difference_with_fail_on_diff_exits_non_zero(self, tmp_path: Path, report_a: Path) -> None:
        report_b = _write(tmp_path / "b.json", [_entry("test_one", "failed"), _entry("test_two", "failed")])
        result = self._run("-a", str(report_a), "-b", str(report_b), "--fail-on-diff")
        assert result.returncode != 0, result.stdout + result.stderr
        assert "DIFFERENCES FOUND" in result.stdout

    def test_difference_without_fail_on_diff_exits_zero(self, tmp_path: Path, report_a: Path) -> None:
        report_b = _write(tmp_path / "b.json", [_entry("test_one", "failed"), _entry("test_two", "failed")])
        result = self._run("-a", str(report_a), "-b", str(report_b))
        assert result.returncode == 0, result.stdout + result.stderr
