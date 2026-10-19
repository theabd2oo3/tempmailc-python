"""
Data models for TempMailAPI
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Domain:
    """Represents an assigned private domain."""
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass
class Message:
    """Represents a received email message."""
    email: str
    sender: str
    subject: str
    date: str
    message: str
    code: Optional[str] = None
    html_url: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], email: str = "") -> "Message":
        # Extract potential OTP if present
        msg_text = str(data.get("message", "") or "")
        return cls(
            email=str(data.get("email") or email),
            sender=str(data.get("sender", "Unknown")),
            subject=str(data.get("subject", "No Subject")),
            date=str(data.get("date", "")),
            message=msg_text,
            code=data.get("code"),
            html_url=data.get("html_url"),
            raw=data
        )


@dataclass
class KopeechkaOrder:
    """Represents an active mailbox order from Kopeechka protocol."""
    task_id: int
    email: str
    domain: str
    site: str = "any"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KopeechkaOrder":
        mail = data.get("mail") or data.get("email") or ""
        dom = mail.split("@")[-1] if "@" in mail else ""
        return cls(
            task_id=int(data.get("id", 0)),
            email=mail,
            domain=dom,
            site=str(data.get("site", "any"))
        )
