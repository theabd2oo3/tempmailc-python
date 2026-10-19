"""
Main client for TempMailAPI
"""
import time
import random
import string
import json
from typing import Optional, List, Dict, Any, Callable, Union
import requests

from .exceptions import (
    TempMailError,
    AuthenticationError,
    DomainNotAllowedError,
    TimeoutError,
    RateLimitError,
    APIConnectionError
)
from .models import Domain, Message
from .mailbox import Mailbox
from .kopeechka import KopeechkaClient


class TempMailAPI:
    """
    Official Python SDK client for TempMailAPI (https://private.tempmailc.com).
    
    Provides high-speed OTP extraction, real-time message streaming,
    webhook management, and full Kopeechka 2.0 compatibility.
    """
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://private.tempmailc.com",
        timeout: float = 30.0,
        session: Optional[requests.Session] = None
    ):
        if not api_key or not str(api_key).strip():
            raise AuthenticationError("API key is required to initialize TempMailAPI client.")
        
        self.api_key = str(api_key).strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "TempMailAPI-Python-SDK/1.0",
            "X-API-Key": self.api_key
        })
        self._cached_domains: List[str] = []
        self._kopeechka = KopeechkaClient(self)

    @property
    def kopeechka(self) -> KopeechkaClient:
        """Access Kopeechka 2.0 protocol methods."""
        return self._kopeechka

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        timeout: Optional[float] = None
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        params = dict(params or {})
        
        # Ensure code is sent if not already passed
        if "code" not in params and "token" not in params:
            params["code"] = self.api_key

        try:
            res = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                stream=stream,
                timeout=timeout or self.timeout
            )
        except requests.RequestException as e:
            raise APIConnectionError(f"Network request to {url} failed: {e}") from e

        # Translate API status codes & JSON errors
        if res.status_code == 401 or res.status_code == 403:
            try:
                err_data = res.json()
                err_code = err_data.get("error", "")
                if err_code in ("invalid_trial_code", "invalid_code", "trial_expired", "subscription_expired"):
                    raise AuthenticationError(f"Authentication failed: {err_data.get('message', err_code)}")
                elif err_code == "domain_not_allowed":
                    raise DomainNotAllowedError(f"Domain not allowed: {err_data.get('message', err_code)}")
                elif err_code == "account_suspended":
                    raise AuthenticationError("Account is suspended.")
            except (ValueError, AttributeError):
                pass
            raise AuthenticationError(f"Access forbidden (HTTP {res.status_code}). Check your Master API Key.")

        elif res.status_code == 429:
            raise RateLimitError("Rate limit or stream concurrency limit exceeded.")

        return res

    def get_domains(self, refresh: bool = False) -> List[str]:
        """
        Fetch the list of private domains assigned to your account.
        
        :param refresh: If True, bypass internal memory cache.
        :return: List of domain strings (e.g. ['emroana.com']).
        """
        if self._cached_domains and not refresh:
            return list(self._cached_domains)

        res = self._request("GET", "/api/v1/domains")
        data = res.json()
        if not data.get("ok"):
            raise TempMailError(f"Failed to fetch domains: {data.get('error')}")

        domains = data.get("domains", [])
        self._cached_domains = domains
        return domains

    def create_mailbox(
        self,
        domain: Optional[str] = None,
        prefix: Optional[str] = None,
        site: str = "any"
    ) -> Mailbox:
        """
        Create a new temporary mailbox.

        :param domain: Target domain. If None, uses the first assigned domain.
        :param prefix: Custom email username. If None, generates a natural human prefix.
        :param site: Optional target site name.
        :return: Mailbox instance ready for receiving OTPs and emails.
        """
        if not domain:
            available = self.get_domains()
            if not available:
                raise TempMailError("No private domains found for this account.")
            domain = available[0]

        if not prefix:
            first_names = ["alex", "sam", "max", "leo", "ryan", "eva", "noah", "mia", "lucas", "emma"]
            last_names = ["smith", "taylor", "brown", "wilson", "davis", "clark", "hall", "lee"]
            prefix = f"{random.choice(first_names)}.{random.choice(last_names)}{random.randint(10, 99)}"

        clean_email = f"{prefix.strip().lower()}@{domain.strip().lower()}"
        return Mailbox(self, clean_email)

    def get_code(self, email: str) -> Optional[str]:
        """
        Query the instant verification code endpoint for an email address.
        
        :param email: Mailbox address.
        :return: Extracted verification code string if found, otherwise None.
        """
        res = self._request("GET", "/api/v1/code", params={"email": email})
        data = res.json()
        if data.get("status") == "ok":
            return str(data.get("code") or "")
        return None

    def wait_for_code(
        self,
        email: str,
        timeout: float = 60.0,
        interval: float = 2.0
    ) -> str:
        """
        Poll the fast-path endpoint until an OTP code arrives or timeout occurs.

        :param email: Mailbox address.
        :param timeout: Maximum wait time in seconds (default 60s).
        :param interval: Polling interval in seconds (default 2s).
        :return: Extracted OTP code string.
        :raises TimeoutError: If code does not arrive before timeout.
        """
        start = time.time()
        while time.time() - start < timeout:
            code = self.get_code(email)
            if code:
                return code
            time.sleep(interval)
        raise TimeoutError(f"No verification code received for {email} within {timeout}s.")

    def get_inbox(self, email: str) -> Optional[Message]:
        """
        Retrieve full parsed message details for an address.
        
        :param email: Mailbox address.
        :return: Message object, or None if inbox is empty.
        """
        res = self._request("GET", "/api/v1/inbox", params={"email": email})
        data = res.json()
        if data.get("status") == "ok":
            return Message.from_dict(data, email=email)
        return None

    def wait_for_message(
        self,
        email: str,
        timeout: float = 60.0,
        interval: float = 2.0
    ) -> Message:
        """
        Poll until an email message arrives.
        
        :param email: Mailbox address.
        :param timeout: Maximum wait time in seconds.
        :param interval: Polling interval in seconds.
        :return: Received Message object.
        """
        start = time.time()
        while time.time() - start < timeout:
            msg = self.get_inbox(email)
            if msg:
                return msg
            time.sleep(interval)
        raise TimeoutError(f"No email message received for {email} within {timeout}s.")

    def get_html(self, email: str) -> Optional[str]:
        """
        Get the raw HTML content of the latest email.
        """
        res = self._request("GET", "/api/v1/html", params={"email": email})
        try:
            data = res.json()
            if data.get("status") == "ok":
                return data.get("html")
        except ValueError:
            return res.text
        return None

    def get_viewer_url(self, email: str) -> str:
        """
        Generate the authenticated SEC-03 Sandboxed HTML Viewer URL.
        """
        return f"{self.base_url}/api/v1/view-html?email={email.strip().lower()}&code={self.api_key}"

    def stream(
        self,
        email: str,
        callback: Callable[[Dict[str, Any]], None],
        full: bool = False,
        timeout: float = 60.0
    ) -> None:
        """
        Subscribe to Server-Sent Events (SSE) for real-time instant email delivery.

        :param email: Mailbox address to watch.
        :param callback: Invoked with payload dict when email arrives.
        :param full: Include full HTML in event payload.
        :param timeout: Maximum stream duration in seconds.
        """
        params = {"email": email, "full": "true" if full else "false"}
        headers = {"Accept": "text/event-stream"}
        
        start = time.time()
        res = self._request("GET", "/api/v1/stream", params=params, stream=True, timeout=timeout + 5)
        
        for line in res.iter_lines(decode_unicode=True):
            if time.time() - start > timeout:
                break
            if not line:
                continue
            if line.startswith("data: "):
                raw_json = line[6:].strip()
                try:
                    payload = json.loads(raw_json)
                    evt_type = payload.get("event")
                    if evt_type == "new_email" or payload.get("code") or payload.get("text"):
                        callback(payload)
                        return
                    elif evt_type == "timeout":
                        break
                except json.JSONDecodeError:
                    pass

    # ========================
    # Webhook Management
    # ========================
    def set_webhook(self, url: str) -> Dict[str, Any]:
        """
        Configure an HTTP webhook URL for automated email forwarding.
        """
        res = self._request("POST", "/api/v1/webhook", json_data={"url": url})
        return res.json()

    def get_webhook(self) -> Dict[str, Any]:
        """
        Retrieve current webhook configuration and recent delivery logs.
        """
        res = self._request("GET", "/api/v1/webhook")
        return res.json()

    def delete_webhook(self) -> bool:
        """
        Deactivate and remove the configured webhook URL.
        """
        res = self._request("DELETE", "/api/v1/webhook")
        data = res.json()
        return bool(data.get("ok"))

    def test_webhook(self) -> Dict[str, Any]:
        """
        Send an immediate test ping payload to your configured webhook URL.
        """
        res = self._request("POST", "/api/v1/webhook/test")
        return res.json()


# Friendly alias
TempMail = TempMailAPI
