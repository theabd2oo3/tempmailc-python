"""
TempMailAPI Exceptions
"""

class TempMailError(Exception):
    """Base exception for all TempMailAPI errors."""
    pass


class AuthenticationError(TempMailError):
    """Raised when the API code / token is missing, invalid, or expired."""
    pass


class DomainNotAllowedError(TempMailError):
    """Raised when an email domain is not assigned to the account."""
    pass


class TimeoutError(TempMailError):
    """Raised when polling or waiting for a code/message exceeds the timeout."""
    pass


class RateLimitError(TempMailError):
    """Raised when daily quota or stream concurrency limits are exceeded."""
    pass


class APIConnectionError(TempMailError):
    """Raised when network or server connection fails."""
    pass
