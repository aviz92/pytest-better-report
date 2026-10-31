import json


def _format_message(exception_message: dict | None) -> str:
    if not exception_message:
        return "-"
    if "message" in exception_message:
        return str(exception_message["message"])
    # A test raised with a JSON object as its message: show the object itself (without the traceback).
    return json.dumps({key: value for key, value in exception_message.items() if key != "traceback"})


def generate_md_report(report: dict) -> str:
    status_icons = {
        "passed": "✅",
        "failed": "❌",
        "xpassed": "✅",
        "xfailed": "❌",
        "skipped": "⏭️",
        "collected": "📋",
    }
    rows = ["| No. | Test Name | Status | Duration | Message |", "|:---:|-----------|:------:|:--------:|---------|"]
    stats = dict.fromkeys(status_icons, 0)
    for index, test in enumerate(report.values(), start=1):
        status = test["test_status"]
        stats[status] = stats.get(status, 0) + 1  # an unexpected status is counted, not a KeyError
        name = test["test_full_name"]
        icon = status_icons.get(status, status)
        duration_sec = test["test_duration_sec"]
        duration = f"{duration_sec:.2f}s" if duration_sec is not None else "-"
        msg = _format_message(exception_message=test["exception_message"])
        rows.append(f"|{index}| `{name}` | {icon} {status} | {duration} | `{msg}` |")

    total_summary = f"\n🧪 Total: {len(report)} &nbsp;&nbsp;| &nbsp;&nbsp;" + " &nbsp;&nbsp;| &nbsp;&nbsp;".join(
        f"{icon} {k.capitalize()}: {v}" for k, v in stats.items() for icon in (status_icons.get(k, ""),)
    )

    return "## ✅ Test Report Summary\n\n" + "\n".join(rows) + f"\n<br> \n\n### Summary: <br> \n{total_summary}"
