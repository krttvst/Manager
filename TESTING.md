# Testing

## Quick Commands

Backend (local venv):
```bash
cd backend
.venv/bin/python -m pytest -q
```

## Backend Test Strategy (Roadmap)

Current state:
- `backend/tests/` contains API-level tests via `fastapi.testclient.TestClient`.
- Tests use SQLite `:memory:` with `StaticPool` to keep a single in-memory DB connection.

Next steps:
1. RBAC coverage
   - Add tests for posts endpoints (create/update/submit-approval) to confirm `viewer` is forbidden and `author` is allowed.
   - Add tests for channels create/delete to confirm `admin` only.
2. Workflow coverage (post status transitions)
   - Draft -> Pending -> Approved -> Scheduled -> Published.
   - Rejection path: Pending -> Rejected -> Draft after edits.
   - Negative tests: invalid transitions return 400, scheduling in the past returns 400.
3. Suggestions security
   - Missing/invalid `X-API-Key` returns 401.
   - Accept/reject requires `editor|admin`.
4. Rate limiter graceful degradation
   - When `RATE_LIMIT_ENABLED=true` but limiter init fails (or `app.state.rate_limiter_ready=False`), endpoints still respond (no 500).
5. Metrics/docs hardening
   - In `APP_ENV=production` with no `METRICS_TOKEN`, `/metrics` is hidden (404).
   - With token: requires `X-Metrics-Token`.
   - Docs disabled by default in production (unless `DOCS_ENABLED=true`).
6. Media upload
   - Reject too-large file (413).
   - Reject non-image file (400).
   - Successful upload returns both `url` and `preview_url`.
7. Celery task tests (optional)
   - Unit-test selection logic and that `publish_post()` is called for due posts.
   - Note: DB locking (`with_for_update(skip_locked=True)`) is DB-specific; for reliable tests consider running task tests against Postgres in CI.

## Where We Store “Test Cases”

Automated test cases:
- Backend: `backend/tests/` (pytest)
- Frontend (when added): `frontend/src/**/__tests__/` or `frontend/tests/`

Human-readable acceptance/regression cases (optional, but recommended):
- `tests/cases/*.md` (short scenario + expected result + link to automated test if exists)

