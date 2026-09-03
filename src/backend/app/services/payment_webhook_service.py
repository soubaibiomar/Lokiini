from __future__ import annotations

import hashlib
import hmac
import time


class WebhookAuthenticationError(ValueError):
    pass


def payload_sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def sign_webhook(secret: str, timestamp: str, body: bytes) -> str:
    message = timestamp.encode("ascii") + b"." + body
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def verify_webhook_signature(
    *, secret: str | None, timestamp: str | None, signature: str | None,
    body: bytes, tolerance_seconds: int = 300, now: int | None = None,
) -> None:
    if not secret:
        raise WebhookAuthenticationError("Payment webhook secret is not configured")
    if not timestamp or not signature:
        raise WebhookAuthenticationError("Missing payment webhook authentication headers")
    try:
        timestamp_value = int(timestamp)
    except ValueError as exc:
        raise WebhookAuthenticationError("Invalid payment webhook timestamp") from exc
    current_time = int(time.time()) if now is None else now
    if abs(current_time - timestamp_value) > tolerance_seconds:
        raise WebhookAuthenticationError("Payment webhook timestamp is outside the replay window")
    supplied = signature.removeprefix("sha256=")
    expected = sign_webhook(secret, timestamp, body)
    if not hmac.compare_digest(supplied, expected):
        raise WebhookAuthenticationError("Invalid payment webhook signature")
