"""
Asynchronous client for TempMailAPI using httpx
"""
import time
import random
import json
from typing import Optional, List, Dict, Any, Callable
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


class AsyncTempMailAPI:
    """
    Asynchronous client for high-performance scraping and bot automation.
    Requires `httpx` package.
    """
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://private.tempmailc.com",
        timeout: float = 30.0
    ):
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is required for AsyncTempMailAPI. Install it via 'pip install httpx'.")

        if not api_key or not str(api_key).strip():
            raise AuthenticationError("API key is required.")

        self.api_key = str(api_key).strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "User-Agent": "TempMailAPI-AsyncPython-SDK/1.0",
                "X-API-Key": self.api_key
            },
            timeout=self.timeout
        )
        self._cached_domains: List[str] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ):
        params = dict(params or {})
        if "code" not in params and "token" not in params:
            params["code"] = self.api_key

        try:
            res = await self._client.request(
                method=method,
                url=path,
                params=params,
                json=json_data
            )
        except Exception as e:
            raise APIConnectionError(f"Async request failed: {e}") from e

        if res.status_code in (401, 403):
            raise AuthenticationError("Authentication failed or access denied.")
        elif res.status_code == 429:
            raise RateLimitError("Rate limit exceeded.")

        return res

    async def get_domains(self) -> List[str]:
        if self._cached_domains:
            return self._cached_domains
        res = await self._request("GET", "/api/v1/domains")
        data = res.json()
        domains = data.get("domains", [])
        self._cached_domains = domains
        return domains

    async def get_code(self, email: str) -> Optional[str]:
        res = await self._request("GET", "/api/v1/code", params={"email": email})
        data = res.json()
        if data.get("status") == "ok":
            return str(data.get("code") or "")
        return None

    async def wait_for_code(self, email: str, timeout: float = 60.0, interval: float = 2.0) -> str:
        import asyncio
        start = time.time()
        while time.time() - start < timeout:
            code = await self.get_code(email)
            if code:
                return code
            await asyncio.sleep(interval)
        raise TimeoutError(f"No OTP code received for {email} within {timeout}s.")

    async def get_inbox(self, email: str) -> Optional[Message]:
        res = await self._request("GET", "/api/v1/inbox", params={"email": email})
        data = res.json()
        if data.get("status") == "ok":
            return Message.from_dict(data, email=email)
        return None
