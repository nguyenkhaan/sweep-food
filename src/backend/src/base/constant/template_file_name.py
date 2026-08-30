"""Email template names shared by email callers."""

from typing import Final

EMAIL_TEMPLATE_FILENAMES: Final[dict[str, str]] = {
    "VERIFY_EMAIL": "verify_email.html",
    "CHANGE_EMAIL": "change_email.html",
    "RESET_PASSWORD": "reset_password.html",
    "CHANGE_PASSWORD": "change_password.html",
    "STEP_UP_AUTH": "step_up_auth.html",
    "BASE_EMAIL": "base_email.html",
}
