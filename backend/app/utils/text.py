def _clean(value: str | None) -> str | None:
    """Strip whitespace, returning None if the result is empty."""
    if value is None:
        return None
    return value.strip() or None


def _clean_email(value: str | None) -> str | None:
    """Strip and lowercase an email, returning None if it is blank."""
    cleaned = _clean(value)
    return cleaned.lower() if cleaned else None
