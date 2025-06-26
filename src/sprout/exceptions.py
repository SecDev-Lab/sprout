"""Custom exceptions for sprout."""

from typing import Any


class SproutError(Exception):
    """Base exception for sprout errors."""

    def __init__(self, message: str, *args: Any) -> None:
        """Initialize the exception with a message."""
        super().__init__(message, *args)
        self.message = message
