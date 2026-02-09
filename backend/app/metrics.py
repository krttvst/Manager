from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

SUGGESTION_CREATED_TOTAL = Counter(
    "suggestion_created_total",
    "Total suggestions created",
)

POST_STATUS_TRANSITIONS_TOTAL = Counter(
    "post_status_transitions_total",
    "Post status transitions",
    ["from_status", "to_status"],
)

TELEGRAM_ERRORS_TOTAL = Counter(
    "telegram_errors_total",
    "Telegram API errors",
    ["action", "retryable"],
)

PUBLISH_SUCCESS_TOTAL = Counter(
    "publish_success_total",
    "Total successful publish operations",
)

PUBLISH_RETRY_TOTAL = Counter(
    "publish_retry_total",
    "Total publish retries",
)

PUBLISH_FAIL_TOTAL = Counter(
    "publish_fail_total",
    "Total failed publish operations",
)
