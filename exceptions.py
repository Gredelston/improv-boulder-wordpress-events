"""Custom exception types."""

class InvalidResponseException(Exception):
    """An HTTP request returned an unexpected response."""

class UndeterminedEventCategoryException(ValueError):
    """Failure to determine an event's category (show/class/workshop)."""
