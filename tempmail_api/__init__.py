"""
TempMailAPI Official Python SDK
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A modern, lightweight Python client for TempMailAPI (https://private.tempmailc.com).

Basic Usage:
    >>> from tempmail_api import TempMail
    >>> client = TempMail(api_key="YOUR_CODE")
    >>> mailbox = client.create_mailbox()
    >>> print(mailbox.email)
    'alex.smith42@yourdomain.com'
    >>> otp = mailbox.wait_for_code(timeout=60)
    >>> print(f"OTP: {otp}")
"""

__version__ = "1.0.0"
__author__ = "TempMailAPI Team"
__license__ = "MIT"

from .client import TempMailAPI, TempMail
from .mailbox import Mailbox
from .kopeechka import KopeechkaClient
from .models import Domain, Message, KopeechkaOrder
from .exceptions import (
    TempMailError,
    AuthenticationError,
    DomainNotAllowedError,
    TimeoutError,
    RateLimitError,
    APIConnectionError,
)

# Optional async client
try:
    from .async_client import AsyncTempMailAPI
except ImportError:
    pass

__all__ = [
    "TempMailAPI",
    "TempMail",
    "Mailbox",
    "KopeechkaClient",
    "Domain",
    "Message",
    "KopeechkaOrder",
    "TempMailError",
    "AuthenticationError",
    "DomainNotAllowedError",
    "TimeoutError",
    "RateLimitError",
    "APIConnectionError",
]
