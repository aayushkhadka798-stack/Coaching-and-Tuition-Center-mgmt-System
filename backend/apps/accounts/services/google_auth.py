from django.conf import settings
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token


class GoogleTokenError(ValueError):
    """Raised when a Google credential cannot be trusted."""


def verify_google_credential(credential):
    if not settings.GOOGLE_CLIENT_ID:
        raise GoogleTokenError("Google authentication is not configured.")
    try:
        payload = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except (GoogleAuthError, ValueError, TypeError) as error:
        raise GoogleTokenError("Invalid Google credential.") from error

    issuer = payload.get("iss")
    if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
        raise GoogleTokenError("Invalid Google credential.")
    if payload.get("email_verified") is not True:
        raise GoogleTokenError("Invalid Google credential.")
    if not payload.get("email") or not payload.get("sub"):
        raise GoogleTokenError("Invalid Google credential.")
    return payload
