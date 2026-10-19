"""
Mailbox object representing a temporary email address.
"""
import time
from typing import Optional, Dict, Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import TempMailAPI
    from .models import Message


class Mailbox:
    """
    Represents an active temporary mailbox address.
    Provides convenient helper methods for waiting on OTPs and messages.
    """
    def __init__(self, client: "TempMailAPI", email: str):
        self.client = client
        self.email = email.strip().lower()
        self.local, self.domain = self.email.split("@", 1) if "@" in self.email else (self.email, "")

    @property
    def viewer_url(self) -> str:
        """Get the SEC-03 sandboxed browser viewer URL for this mailbox."""
        return self.client.get_viewer_url(self.email)

    def get_code(self) -> Optional[str]:
        """
        Check once for an incoming OTP code.
        Returns the code string if found, otherwise None.
        """
        return self.client.get_code(self.email)

    def wait_for_code(self, timeout: float = 60.0, interval: float = 2.0) -> str:
        """
        Block and poll until a verification code arrives or timeout occurs.

        :param timeout: Maximum seconds to wait (default 60s).
        :param interval: Polling interval in seconds (default 2s).
        :return: Extracted verification code string.
        :raises TimeoutError: If no code arrives within the timeout window.
        """
        return self.client.wait_for_code(self.email, timeout=timeout, interval=interval)

    def get_inbox(self) -> Optional["Message"]:
        """
        Fetch the parsed inbox message for this address.
        Returns a Message object if an email exists, otherwise None.
        """
        return self.client.get_inbox(self.email)

    def wait_for_message(self, timeout: float = 60.0, interval: float = 2.0) -> "Message":
        """
        Block and poll until a full message arrives.

        :param timeout: Maximum seconds to wait.
        :param interval: Polling interval in seconds.
        :return: Parsed Message object.
        """
        return self.client.wait_for_message(self.email, timeout=timeout, interval=interval)

    def get_html(self) -> Optional[str]:
        """Fetch the raw HTML string of the latest email."""
        return self.client.get_html(self.email)

    def stream(self, callback: Callable[[Dict[str, Any]], None], full: bool = False, timeout: float = 60.0) -> None:
        """
        Listen to real-time incoming messages via SSE stream.

        :param callback: Function called whenever a message arrives.
        :param full: Whether to request full HTML in stream events.
        :param timeout: Maximum stream duration in seconds.
        """
        self.client.stream(self.email, callback=callback, full=full, timeout=timeout)

    def __repr__(self) -> str:
        return f"<Mailbox email='{self.email}'>"

    def __str__(self) -> str:
        return self.email
