from enum import StrEnum


class ExecutionStatus(StrEnum):
    COLLECTED = "collected"
    STARTED = "started"
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    XFAIL = "xfailed"
    XPASS = "xpassed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
