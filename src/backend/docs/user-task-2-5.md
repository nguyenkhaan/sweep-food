# Spec: Task 2.5 Current User APIs

## Objective

Deliver authenticated, ownership-safe user profile and verified-contact APIs. The JWT identity endpoint is intentionally minimal for frontend initialization; profile data stays behind its own route.

## API Contract

- `GET /api/users/me` requires an access JWT and returns only `user_id` and `roles`.
- `GET /api/users/profile` requires an access JWT and returns the caller's profile, preferences, and verified-contact timestamps.
- `PATCH /api/users/profile` requires an access JWT and updates only the caller's display name or preferences.
- `POST /api/users/me/email/request-verification` sends and returns an email OTP. It uses `VERIFY_EMAIL` until an email is verified, then `CHANGE_EMAIL` for later replacements.
- `POST /api/users/me/email/verify` accepts only `otp`, resolves the pending email from Redis, consumes that email OTP, persists the verified email address, and returns `Verify Change Email successfully` as plain text.
- `POST /api/users/me/phone/request-change` sends and returns a `CHANGE_PHONE` SMS OTP. When `user.email` exists, it also sends the same OTP to that email using the `CHANGE_PHONE` template.
- `POST /api/users/me/phone/confirm-change` accepts only `otp`, resolves the pending phone from Redis, consumes that SMS OTP, updates the caller's phone number, and returns `Verify Change Phone succesfully` as plain text.

All OTP issuance remains production-shaped: a random OTP is stored hashed in Redis and sent through the configured provider. In `dev` and `test`, `DEFAULT_OTP` additionally verifies an existing matching challenge.

## Boundaries

- Every route uses `require_authentication`; the inherited OpenAPI configuration automatically exposes Bearer JWT security for Swagger UI.
- No route accepts another user's ID. Database reads and writes are scoped to the authenticated subject.
- Email and phone uniqueness are checked before delivery and again before persistence.
- Pending email and phone Redis values are scoped to one authenticated user, expire with their OTP, are overwritten by a new request, and are removed after successful verification.
- This task needs no schema migration: it uses existing `users` fields (`name`, `preferences`, `email`, `email_verified_at`, `phone_e164`, and `phone_verified_at`).
- Password recovery via verified email and FCM device registration remain outside this user-module scope.

## Verification

```bash
.venv/bin/pytest -q
PYLINTHOME=/tmp/sweep-food-pylint .venv/bin/ruff check src/module/user src/test/test_user_service.py src/test/test_user_router.py
PYLINTHOME=/tmp/sweep-food-pylint .venv/bin/mypy src/module/user src/test/test_user_service.py src/test/test_user_router.py
PYLINTHOME=/tmp/sweep-food-pylint .venv/bin/pylint src/module/user src/test/test_user_service.py src/test/test_user_router.py
```
