![PyPI version](https://img.shields.io/pypi/v/pytest-better-report)
![Python](https://img.shields.io/badge/python->=3.12-blue)
![Development Status](https://img.shields.io/badge/status-stable-green)
![Maintenance](https://img.shields.io/maintenance/yes/2026)
![PyPI](https://img.shields.io/pypi/dm/pytest-better-report)
![License](https://img.shields.io/pypi/l/pytest-better-report)

---

# 💡 pytest-better-report
A pytest plugin that writes a structured report of every run: a JSON file per test, a JSON file for the run with CI
metadata (repo, PR/MR, pipeline, commit), and an optional Markdown summary. Includes a CLI to compare two runs.

---

## 📦 Installation
```bash
uv add pytest-better-report
```

---

## 🚀 Features
  - ✅ **Structured JSON** — `test_results.json` (one entry per test) and `execution_results.json` (the run)
  - ✅ **CI traceability** — repo name, PR / MR number, pipeline number and commit in the run report
  - ✅ **Markdown summary** — a table of every test with status, duration and message
  - ✅ **Structured failure data** — raise with a JSON object as the message to record it as data
  - ✅ **Compare two runs** — `better_report_compare` lists missing tests and status differences
  - ✅ **Plays well with other plugins** — statuses come from pytest's final reports, whatever the plugin order
  - ✅ **Zero footprint without the flag** — nothing is registered, no hook runs

---

## 🛠️ How to Use
```bash
pytest --better-report --md-report --pr-number=123 --commit="$GIT_SHA"
```
Files are written to `results_output/` (or `<output-dir>/results_output/`):

| File | Content |
|---|---|
| `test_results.json` | One entry per test: name, file, class, parameters, markers, status, times, exception, user properties |
| `execution_results.json` | The run: status, start / end / duration, CI metadata, environment, optionally the pytest command |
| `test_report.md` | With `--md-report`: a table of all tests and a summary by status |

---

## ⚙️ Flags
| Flag | Description |
|---|---|
| `--better-report` | Enable the report |
| `--output-dir=DIR` | Write the files to `DIR/results_output/` |
| `--md-report` | Also write `test_report.md` |
| `--traceback` | Add the crash location and traceback frames to each exception |
| `--repo-name`, `--pr-number`, `--mr-number`, `--pipeline-number`, `--commit` | CI metadata for `execution_results.json` |
| `--pytest-command` | Record the pytest command line in `execution_results.json` |
| `--pytest-xfail-strict` | Treat an unexpected pass (XPASS) as a failure of the run |
| `--result-each-test` | Log each test's result after it runs |
| `--log-collected-tests` | Log every collected test at the start (works without `--better-report` too) |

---

## 📊 Statuses
Each test gets one status in `test_results.json`.
The run as a whole gets `execution_info.execution_status` in `execution_results.json`: `failed` if **at least one**
test has a status marked "Yes" in the last column, otherwise `passed`.

This is the report's own verdict on the run, written into the file. It is separate from pytest's exit code, which this
plugin doesn't change.

| Test status | Meaning | Makes `execution_status` = `failed` |
|---|---|---|
| `passed` | Passed | No |
| `failed` | Failed or errored in setup, call or teardown | Yes |
| `skipped` | Skipped (marker, fixture, or a plugin that converted the outcome) | No |
| `xfailed` | Expected failure | No |
| `xpassed` | Unexpected pass | Only with `--pytest-xfail-strict` |
| `collected` | Collected but not run (e.g. the run stopped early) | No |

---

## ▶️ Usage Examples
### Record structured failure data
```python
import json

def test_api():
    response = call_api()
    if response.status != 200:
        raise AssertionError(json.dumps({"status": response.status, "body": response.text}))
```
The exception is recorded as `{"status": ..., "body": ...}` instead of plain text.

### Compare two runs
```bash
better_report_compare -a main/test_results.json -b branch/test_results.json --fail-on-diff
```
Lists tests missing from either side and tests whose status changed; exits non-zero with `--fail-on-diff` when
there are differences. `--test-file-name` limits the comparison to one test file.

---

## 🔁 Migrating from pytest-plugins
This plugin was previously `better_report` in `pytest-plugins`. Flags, file names and the JSON schema are unchanged.
Both register the same options, so don't install them together until you're on a `pytest-plugins` release without it.
Differences you may notice:
- A test that errors in teardown is now `failed` (it was reported as passed).
- The `failed-skipped` status no longer exists; converted failures are `skipped`, with the reason in `test_user_properties`.
- The logger is named `pytest_better_report`.
- `--add-parameters` was removed. Parameters are always recorded in `test_parameters`; in ELK / Kibana query them
  as `test_parameters.<name>` instead of `<name>`. Passing the flag now fails with "unrecognized arguments".

---

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-addition`
3. Make your changes
4. Commit your changes: `git commit -m 'Add my addition'`
5. Push to the branch: `git push origin feature/my-addition`
6. Open a Pull Request

Additions that promote clean, productive, and maintainable development are always welcome.

---

## 📄 License
MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Thanks
Thanks for exploring this repository! <br>
Happy coding!

[![GitHub](https://img.shields.io/badge/GitHub-aviz92-181717?logo=github)](https://github.com/aviz92)
&nbsp; [![PyPI](https://img.shields.io/badge/PyPI-aviz-3775A9?logo=pypi)](https://pypi.org/user/aviz/)
&nbsp; [![Blog](https://img.shields.io/badge/Blog-aviz92.github.io-0066CC?logo=googlechrome)](https://aviz92.github.io/)
&nbsp; [![LinkedIn](https://img.shields.io/badge/LinkedIn-avi--zaguri-0A66C2?logo=linkedin)](https://www.linkedin.com/in/avi-zaguri-41869b11b)
