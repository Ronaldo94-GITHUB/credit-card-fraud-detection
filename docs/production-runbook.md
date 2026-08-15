# Production Deployment Runbook

## Production services

Backend:

https://credit-card-fraud-detection-v5li.onrender.com

Frontend:

https://credit-card-fraud-detection-frontend-k6ki.onrender.com

## Deployment flow

1. Push code to the main branch.
2. GitHub Actions runs Production CI.
3. All quality gates must pass.
4. Render deploys the approved commit.
5. Render health check validates application readiness.
6. Production smoke tests validate public API endpoints.

## Required CI checks

- Backend Quality
- Frontend Quality
- Docker Quality
- Repository Security
- Production Gate

## Backend health check

Recommended Render Health Check Path:

/readiness

Expected response:

HTTP 200

The readiness endpoint should indicate that the application
and required runtime dependencies are ready.

## Production smoke test

Run manually:

python scripts/production_smoke_test.py

Expected final output:

PRODUCTION_SMOKE_OK=True

## Rollback procedure

If a new production deploy introduces a regression:

1. Open the backend service in Render.
2. Open Deploys.
3. Identify the last known-good successful deploy.
4. Select Rollback.
5. Confirm rollback to that deploy.
6. Wait until the service becomes healthy.
7. Run:

python scripts/production_smoke_test.py

8. Confirm:

PRODUCTION_SMOKE_OK=True

9. Investigate the failed commit separately before redeploying.

## Rollback decision criteria

Rollback should be considered when one or more occur:

- readiness endpoint fails
- health endpoint fails
- model cannot be loaded
- persistent database becomes unavailable
- production smoke test fails
- repeated HTTP 5xx responses
- severe inference regression
- critical security regression

## Administrative secret

ADMIN_API_KEY must never be committed to Git.

The local development copy:

.phase14_admin_key.txt

must remain ignored by Git.

## Operational verification

After every production deployment verify:

- /health
- /readiness
- /model-info
- /security/status
- /metrics/persistent

## Incident workflow

1. Detect failure.
2. Stop further releases.
3. Check Render logs.
4. Determine whether rollback is required.
5. Restore last known-good version.
6. Run production smoke tests.
7. Document root cause.
8. Fix through normal CI.
9. Redeploy only after all checks pass.
