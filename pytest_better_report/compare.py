"""
CLI tool to compare two better-report JSON log files.

Checks if all pytest_test_name entries are equal, lists missing tests from each file,
and for matching tests compares their test_status and lists all diffs.

Usage:
    python better_report_compare.py -a <file_a.json> -b <file_b.json> [--fail-on-diff]
"""

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from python_base_command import BaseCommand, CommandError, CommandParser

PASS_SYMBOL = "✓"
FAIL_SYMBOL = "✗"
DIFF_SYMBOL = "≠"

SEP = "─" * 100


def _log_missing(missing: list[str], source: str, target: str) -> None:
    if missing:
        print(f"\n{FAIL_SYMBOL}  Tests in {source} but MISSING from {target}  ({len(missing)})")
        for name in missing:
            print(f"     - {name}")
    else:
        print(f"\n{PASS_SYMBOL}  No tests missing from {target}")


def _log_status_diffs(status_diffs: list[tuple[str, str, str]]) -> None:
    if status_diffs:
        col_w = max(len(name) for name, _, _ in status_diffs)
        print(f"\n{DIFF_SYMBOL}  Status differences in common tests  ({len(status_diffs)})")
        print(f"     {'TEST NAME':<{col_w}}  {'STATUS IN A':<12}  STATUS IN B")
        print("     " + "-" * (col_w + 28))
        for name, s_a, s_b in status_diffs:
            print(f"     {name:<{col_w}}  {s_a:<12}  {s_b}")
    else:
        print(f"\n{PASS_SYMBOL}  All common tests have identical statuses")


@dataclass(frozen=True)
class ComparisonSummary:
    file_a: Path
    file_b: Path
    total_a: int
    total_b: int
    common_count: int
    only_in_a: list[str]
    only_in_b: list[str]
    status_diffs: list[tuple[str, str, str]]
    test_file_name: str | None = None

    @property
    def identical(self) -> bool:
        return not (self.only_in_a or self.only_in_b or self.status_diffs)


def _log_summary(summary: ComparisonSummary) -> None:
    print(f"\n{SEP}")
    print("  BETTER-REPORT COMPARISON")
    print(SEP)
    print(f"  File A : {summary.file_a}")
    print(f"  File B : {summary.file_b}")
    if summary.test_file_name:
        print(f"  Filter : test_file_name = {summary.test_file_name}")
    print(f"  Tests  : {summary.total_a} in A  |  {summary.total_b} in B  |  {summary.common_count} in common")
    print(SEP)

    _log_missing(summary.only_in_a, source="A", target="B")
    _log_missing(summary.only_in_b, source="B", target="A")
    _log_status_diffs(summary.status_diffs)

    print(f"\n{SEP}")
    if not summary.identical:
        print("  RESULT: DIFFERENCES FOUND")
    else:
        print("  RESULT: REPORTS ARE IDENTICAL")
    print(f"{SEP}\n")


def load_report(path: Path, test_file_name: str | None = None) -> dict[str, dict]:
    with open(path) as f:
        raw = json.load(f)
    indexed: dict[str, dict] = {}
    for entry in raw.values():
        if test_file_name and entry.get("test_file_name") != test_file_name:
            continue
        if pytest_name := entry.get("pytest_test_name"):
            indexed[pytest_name] = entry
    return indexed


def compare_reports(file_a: Path, file_b: Path, test_file_name: str | None = None) -> bool:
    report_a = load_report(file_a, test_file_name)
    report_b = load_report(file_b, test_file_name)

    names_a = set(report_a.keys())
    names_b = set(report_b.keys())

    only_in_a = sorted(names_a - names_b)
    only_in_b = sorted(names_b - names_a)
    common = sorted(names_a & names_b)

    status_diffs = [
        (name, report_a[name]["test_status"], report_b[name]["test_status"])
        for name in common
        if report_a[name].get("test_status") != report_b[name].get("test_status")
    ]

    summary = ComparisonSummary(
        file_a=file_a,
        file_b=file_b,
        total_a=len(names_a),
        total_b=len(names_b),
        common_count=len(common),
        only_in_a=only_in_a,
        only_in_b=only_in_b,
        status_diffs=status_diffs,
        test_file_name=test_file_name,
    )
    _log_summary(summary=summary)
    return summary.identical


class Command(BaseCommand):
    help = "Compare two better-report JSON log files for test coverage and status differences."
    version = "1.0.0"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-a",
            "--file-a",
            type=Path,
            required=True,
            help="Path to the first better-report JSON file.",
        )
        parser.add_argument(
            "-b",
            "--file-b",
            type=Path,
            required=True,
            help="Path to the second better-report JSON file.",
        )
        parser.add_argument(
            "--fail-on-diff",
            action="store_true",
            default=False,
            help="Exit with non-zero code if any differences are found.",
        )
        parser.add_argument(
            "--test-file-name",
            type=str,
            required=False,
            default=None,
            help="Filter comparison to tests belonging to this test_file_name "
            "(e.g. test_advertiser_services_missing.py).",
        )

    def handle(self, **kwargs: Any) -> None:
        file_a: Path = kwargs["file_a"]
        file_b: Path = kwargs["file_b"]
        fail_on_diff: bool = kwargs["fail_on_diff"]
        test_file_name: str | None = kwargs.get("test_file_name")

        for label, path in (("A", file_a), ("B", file_b)):
            if not path.exists():
                raise FileNotFoundError(f"File {label} not found: {path}")

        identical = compare_reports(file_a, file_b, test_file_name)

        if fail_on_diff and not identical:
            raise CommandError("Reports have differences.")


def main() -> None:
    """Entry point: run the compare command from CLI."""
    print('Starting "Better Report Compare"')

    os.environ["PYTHON_BASE_COMMAND_LOG_FILE"] = "false"
    Command().run_from_argv(argv=sys.argv)


if __name__ == "__main__":
    main()
