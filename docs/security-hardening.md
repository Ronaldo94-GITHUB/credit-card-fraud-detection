# API Security Hardening

## Phase 26

This phase adds defense-in-depth protections around the
fraud detection API.

## Request body limit

Default maximum request body:

65536 bytes

Environment variable:

SECURITY_MAX_BODY_BYTES

Oversized requests return:

413 Payload Too Large

## JSON Content-Type enforcement

The following JSON endpoints require:

Content-Type: application/json

Protected endpoints:

POST /predict

POST /ground-truth

Invalid media types return:

415 Unsupported Media Type

## Host Header protection

Host validation is enabled by default.

Environment variable:

SECURITY_ENFORCE_TRUSTED_HOSTS=true

Default trusted hosts:

localhost

127.0.0.1

testserver

credit-card-fraud-detection-v5li.onrender.com

Custom configuration:

SECURITY_TRUSTED_HOSTS

Example:

api.example.com,localhost,testserver

## Security headers

Responses include:

X-Content-Type-Options: nosniff

X-Frame-Options: DENY

Referrer-Policy: no-referrer

Permissions-Policy

X-Permitted-Cross-Domain-Policies: none

## HSTS

When the request is HTTPS, or when the trusted proxy
reports:

X-Forwarded-Proto: https

the API returns:

Strict-Transport-Security

HTTPS redirection is intentionally not enabled inside the
application in this phase.

TLS termination is handled by the deployment platform.

## Administrative endpoint

GET /security/hardening

Requires:

X-Admin-API-Key

The endpoint reports the active hardening configuration
without exposing secrets.

## Existing controls preserved

Phase 26 does not replace:

prediction rate limiting

admin API key authentication

audit logging

request IDs

CORS

ground truth protection

explainability protection

## Validation

Run:

python scripts/validate_security_hardening.py

Expected important results:

HEALTH_HTTP=200

INVALID_HOST_HTTP=400

WRONG_CONTENT_TYPE_HTTP=415

OVERSIZED_PAYLOAD_HTTP=413

SECURITY_STATUS_HTTP=200

SECURITY_HARDENING_VALID=True

## Environment variables

Optional:

SECURITY_MAX_BODY_BYTES

SECURITY_TRUSTED_HOSTS

SECURITY_ENFORCE_TRUSTED_HOSTS

SECURITY_HEADERS_ENABLED

SECURITY_VALIDATE_CONTENT_TYPE

SECURITY_HSTS_ENABLED

## Important limitation

Application middleware is defense in depth.

For a larger public deployment, perimeter controls such as
a managed WAF, DDoS protection, infrastructure rate
limiting and centralized secret management should remain
outside the application itself.
