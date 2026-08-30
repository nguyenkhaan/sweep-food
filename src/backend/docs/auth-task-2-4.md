# Spec: Task 2.4 Authentication APIs

## Objective

Deliver phone/password authentication with temporary `UNVERIFIED` registrations, SMS OTP verification, password recovery/change, and purpose-scoped access/refresh JWT sessions. Local and test environments accept `DEFAULT_OTP`; production verification requires the Redis-stored OTP.

## API Contract

- `POST /api/auth/register` creates an `UNVERIFIED` user with a password hash, issues a `REGISTER` SMS OTP, and returns the generated OTP for the current MVP client flow.
- `POST /api/auth/register/resend-otp` issues and returns a replacement registration OTP only while the account remains `UNVERIFIED`; the prior Redis OTP for that phone and purpose is invalidated.
- `POST /api/auth/verify/register` verifies the registration OTP, activates the user, and returns only `verify account successfully` as plain text.
- `POST /api/auth/password/reset` issues a `RESET_PASSWORD` SMS OTP for the submitted phone.
- `POST /api/auth/password/change` requires an access token and issues a `CHANGE_PASSWORD` SMS OTP for that user’s phone.
- `POST /api/auth/verify/change-password` verifies either password OTP purpose, changes the password, and revokes active sessions.
- `POST /api/auth/login` accepts only phone and password and returns both access and refresh JWTs.
- `POST /api/auth/token/refresh` accepts a refresh JWT and creates only a new access JWT.
- `POST /api/auth/logout` revokes the submitted refresh-token session and returns `Logout successfully` as plain text. `GET /api/auth/sessions` and `DELETE /api/auth/sessions/{session_id}` inspect and revoke refresh-token sessions.

## Commands

```bash
.venv/bin/pytest -q src/test/test_auth_service.py src/test/test_auth_router.py
.venv/bin/ruff check src/module/auth src/service src/middleware
.venv/bin/mypy src/module/auth src/service src/middleware
XDG_CACHE_HOME=/tmp/pylint-cache .venv/bin/pylint src/module/auth src/service src/middleware
```

## Project Structure

- `src/module/auth/`: request/response DTOs, router, dependency, and `AuthService`.
- `src/service/`: shared JWT, OTP, SMS delivery, and hashing services.
- `src/model/`: user and auth-session persistence models.
- `src/test/`: focused service and API contract tests.

## Code Style

```python
async def verify_register(self, request: VerifyRegisterRequestDTO) -> None:
    try:
        # validate Redis OTP, update the user, and commit one transaction
        ...
    except SQLAlchemyError as error:
        await self.db_session.rollback()
        print(f"Database error: {error}")
        raise
```

Every function is typed. Database failures are rolled back through `SQLAlchemyError`; broad `Exception` handling is prohibited.

## Testing Strategy

Use deterministic fake Redis/delivery/session boundaries for service tests and FastAPI dependency overrides for router tests. Cover registration resend invalidation, plain-text account verification, OTP fallback, password, JWT purposes/secrets, refresh issuance, access renewal, logout, and session ownership.

OTP issue responses contain `otp` and `expires_in_seconds`. Verification requests do not contain a challenge identifier: Redis finds the current OTP by channel, purpose, and hashed destination. The submitted value is valid when it matches the generated Redis-backed OTP or, in local/test MVP flows, `DEFAULT_OTP=123456`.

OTP cooldown, request-limit, and failed-attempt limit errors use HTTP `429`; invalid, expired, mismatched, or already-consumed OTP state uses HTTP `400`. These domain outcomes must never fall through to HTTP `500`.

The custom OpenAPI builder recursively detects `require_authentication` in each route dependency tree. Therefore routes using either `Depends(require_authentication)` or `Depends(require_role(...))` automatically receive the `BearerAuth` security requirement and Swagger lock icon; route decorators must not duplicate `openapi_extra` security declarations.

## Boundaries

- Always: hash passwords and refresh tokens; store only OTP hashes in Redis; revoke sessions after password changes.
- Always: sign access JWTs with `JWT_ACCESS_SECRET`, sign refresh JWTs with `JWT_REFRESH_SECRET`, and require the matching `purpose` claim.
- Ask first: add dependencies, modify a production database outside a migration, or expand to email/phone identity changes.
- Never: return passwords, password hashes, refresh-token hashes, or provider secrets; accept `DEFAULT_OTP` outside `dev` or `test`.

## Success Criteria

- An `UNVERIFIED` registration becomes `ACTIVE` only after a matching OTP.
- Password login issues both JWT types, and refresh JWT can issue a new access JWT.
- Password reset/change validates its purpose and revokes sessions.
- Users can view/revoke only their own sessions; banned users cannot pass protected dependencies.
