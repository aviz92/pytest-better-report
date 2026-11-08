"""The current run's results, importable while the run is in progress.

    from pytest_better_report import execution_results, test_results

Same names and shapes as ``pytest_plugins.better_report`` had: ``execution_results`` holds ``"execution_info"``
(an ``ExecutionData``), ``"environment_info"`` and optionally ``"pytest_command"``; ``test_results`` maps each test's
full name to its ``TestData``.

The reporter fills these dicts in place (never rebinds them), so a name bound by ``from ... import`` always sees the
current run. They stay empty without ``--better-report``.

Runs can nest in one process (e.g. ``pytester.runpytest_inprocess`` inside a run): starting a run stashes the
enclosing run's contents and ending it puts them back, so the outer run's results survive. The outermost run's
results are kept after it ends, until the next run starts.
"""

from typing import Any

from pytest_better_report.models import TestData

execution_results: dict[str, Any] = {}
test_results: dict[str, TestData] = {}

type _Snapshot = tuple[dict[str, Any], dict[str, TestData]]

# One entry per active run: the contents the dicts had when that run started.
_enclosing_snapshots: list[_Snapshot] = []


def start_run() -> None:
    """Stash the enclosing run's results (if any) and empty the dicts for a new run."""
    _enclosing_snapshots.append((dict(execution_results), dict(test_results)))
    execution_results.clear()
    test_results.clear()


def end_run() -> None:
    """Restore the enclosing run's results; after the outermost run, keep its results readable."""
    if not _enclosing_snapshots:
        return
    saved_execution, saved_tests = _enclosing_snapshots.pop()
    if not _enclosing_snapshots:
        return
    _replace_contents(target=execution_results, source=saved_execution)
    _replace_contents(target=test_results, source=saved_tests)


def _replace_contents(target: dict[str, Any], source: dict[str, Any]) -> None:
    target.clear()
    target.update(source)
