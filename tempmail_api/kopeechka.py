"""
Kopeechka 2.0 Compatibility Layer for TempMailAPI.
"""
import time
from typing import Optional, Union, Dict, Any, TYPE_CHECKING
from .exceptions import TempMailError, AuthenticationError, TimeoutError
from .models import KopeechkaOrder

if TYPE_CHECKING:
    from .client import TempMailAPI


class KopeechkaClient:
    """
    Implements 100% compatible Kopeechka 2.0 protocol methods.
    Ideal for ZennoPoster, BAS, and existing registration bot architectures.
    """
    def __init__(self, client: "TempMailAPI"):
        self.client = client

    def get_email(
        self,
        site: str = "any",
        mail_type: str = "",
        regex: str = "",
        subject: str = ""
    ) -> KopeechkaOrder:
        """
        Order a new temporary mailbox.

        :param site: Target website/domain (e.g., 'facebook.com', 'google.com', 'any').
        :param mail_type: Specific domain name if requested.
        :param regex: Custom regular expression to match OTP or confirmation link.
        :param subject: Expected email subject filter.
        :return: KopeechkaOrder instance containing task_id and email.
        """
        params = {
            "token": self.client.api_key,
            "site": site,
            "mail_type": mail_type,
            "regex": regex,
            "subject": subject
        }
        res = self.client._request("GET", "/mailbox-get-email", params=params)
        data = res.json()
        if data.get("status") != "OK":
            err_val = data.get("value", "UNKNOWN_ERROR")
            if err_val == "BAD_TOKEN":
                raise AuthenticationError("Invalid or expired API token.")
            raise TempMailError(f"Kopeechka get_email failed: {err_val}")
        return KopeechkaOrder.from_dict(data)

    def get_message(
        self,
        task_id: Union[int, str],
        full: int = 1
    ) -> Optional[str]:
        """
        Check once for the incoming message / OTP.

        :param task_id: The order ID returned by get_email.
        :param full: Return full text if 1.
        :return: The extracted OTP / activation URL, or None if still waiting.
        """
        params = {
            "id": str(task_id),
            "token": self.client.api_key,
            "full": full
        }
        res = self.client._request("GET", "/mailbox-get-message", params=params)
        data = res.json()
        status = data.get("status")
        if status == "OK":
            return data.get("value")
        elif status in ("WAIT_LINK", "WAIT"):
            return None
        elif status == "ERROR":
            err_val = data.get("value", "")
            if err_val == "BAD_TOKEN":
                raise AuthenticationError("Invalid API token.")
            raise TempMailError(f"Kopeechka get_message error: {err_val}")
        return None

    def wait_for_message(
        self,
        task_id: Union[int, str],
        timeout: float = 60.0,
        interval: float = 2.5,
        full: int = 1
    ) -> str:
        """
        Block and poll until the OTP code or confirmation link arrives.

        :param task_id: Order ID.
        :param timeout: Maximum seconds to wait.
        :param interval: Polling interval in seconds.
        :param full: Return full text if 1.
        :return: Extracted verification code or link string.
        """
        start = time.time()
        while time.time() - start < timeout:
            val = self.get_message(task_id, full=full)
            if val:
                return val
            time.sleep(interval)
        raise TimeoutError(f"Kopeechka order {task_id} timed out after {timeout}s.")

    def get_balance(self) -> float:
        """
        Retrieve remaining request balance.
        """
        params = {"token": self.client.api_key}
        res = self.client._request("GET", "/user-balance", params=params)
        data = res.json()
        if data.get("status") != "OK":
            raise TempMailError(f"Failed to fetch balance: {data.get('value')}")
        return float(data.get("balance", data.get("value", 0.0)))

    def cancel(self, task_id: Union[int, str]) -> bool:
        """
        Cancel an active mailbox task and release resources.
        """
        params = {
            "id": str(task_id),
            "token": self.client.api_key
        }
        res = self.client._request("GET", "/mailbox-cancel", params=params)
        data = res.json()
        return data.get("status") == "OK"
