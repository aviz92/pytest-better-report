# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-11-01

First standalone release. Extracted from the `better_report` plugin and the `better_report_compare` CLI of
[pytest-plugins](https://github.com/aviz92/pytest-plugins). Same flags, same output files and JSON schema: a drop-in
replacement.

### Added
- `test_user_properties` in `test_results.json`: the test's user properties (`record_property`, or any plugin that
  adds them), e.g. the reason from [pytest-fail2skip](https://github.com/aviz92/pytest-fail2skip).
- Tests for the `better_report_compare` CLI.

### Changed
- `test_markers` records every marker except pytest's structural ones (`parametrize`, `usefixtures`,
  `filterwarnings`); markers with positional arguments were dropped.
- A test's status is decided from pytest's final reports, after every plugin has finished changing them, so a
  plugin that converts outcomes (e.g. failures into skips) is reflected regardless of plugin load order.
- An error in teardown marks the test as `failed` (it was ignored, so the test was reported as passed). The first
  failing phase's message is kept.
- Tests are registered when collection finishes instead of in a terminal-reporter hook, so the report is complete
  even with `-p no:terminal`.
- The 0.3 s pause after collection is gone.
- BR no longer calls `load_dotenv()` itself. Note: `custom-python-logger` still does on import.
- The `failed-skipped` status is removed: nothing produces it since `fail2skip` moved to its own package.
- The logger is named `pytest_better_report` (was `pytest_plugins.better_report`).

### Removed
- `--add-parameters`. It copied every test parameter to the top level of the test's entry, where a parameter
  named like a report field (e.g. `test_name`) silently overwrote that field. Parameters are always recorded in
  `test_parameters`, which ELK and similar tools index as `test_parameters.<name>`.

### Fixed
- `execution_duration_sec` was typed as a string.
- Results lived in module-level dicts, so a second run in the same process inherited the first run's tests and status.
- `--result-each-test` never logged anything (it checked an attribute nothing set).
- The Markdown report crashed with `KeyError` when a test raised with a JSON object as its message.
- A message that parsed as JSON but not as an object (e.g. `"404"`) replaced the whole `exception_message` with a bare
  value, breaking `--traceback` and the Markdown report; it is now kept as text.
- The Markdown report crashed with `KeyError` on any status missing from its table.

---
