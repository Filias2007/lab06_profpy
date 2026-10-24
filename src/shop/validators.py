from __future__ import annotations

import re

from shop.exceptions import ValidationError

_EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def validate_email(email: str) -> str:
    if not isinstance(email, str) or not _EMAIL_PATTERN.fullmatch(email.strip()):
        raise ValidationError(f"Invalid email: {email!r}")
    return email.strip()


def validate_percent(percent: float) -> float:
    if (
        isinstance(percent, bool)
        or not isinstance(percent, (int, float))
        or not 0 <= percent <= 100
    ):
        raise ValidationError(f"Percent must be between 0 and 100, got {percent!r}")
    return percent