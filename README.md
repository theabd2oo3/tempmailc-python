# TempMailAPI Python SDK 🚀

The official, high-performance Python SDK for [TempMailAPI](https://private.tempmailc.com).

Built for developers, automation engineers, and bots. Delivers verification codes (OTP) in `<1ms`, supports real-time Server-Sent Events (SSE) streaming, automated webhooks, and 100% drop-in compatibility with the **Kopeechka 2.0** protocol.

---

## 📦 Installation

```bash
pip install tempmail-api
```

*(Optional) For async support:*
```bash
pip install "tempmail-api[async]"
```

---

## ⚡ Quickstart

### 1. Instant OTP Extraction (Zero-Poller)
```python
from tempmail_api import TempMail

# Initialize with your Master API Code (from https://private.tempmailc.com/dashboard)
client = TempMail(api_key="YOUR_MASTER_CODE")

# 1. Create a mailbox on your assigned private domain
mailbox = client.create_mailbox()
print(f"Generated Mailbox: {mailbox.email}")

# 2. Trigger your signup on target service (e.g. GitHub, OpenAI, Discord)
# ...

# 3. Wait for OTP (blocks until code arrives or timeout)
otp_code = mailbox.wait_for_code(timeout=60)
print(f"✅ Extracted OTP Code: {otp_code}")
```

---

### 2. Reading Full Inboxes & HTML Messages
```python
from tempmail_api import TempMail

client = TempMail(api_key="YOUR_MASTER_CODE")
mailbox = client.create_mailbox()

# Wait for a full parsed email
message = mailbox.wait_for_message(timeout=60)
print(f"From: {message.sender}")
print(f"Subject: {message.subject}")
print(f"Date: {message.date}")
print(f"Body:\n{message.message}")

# Open isolated sandboxed viewer in browser
print(f"Viewer URL: {mailbox.viewer_url}")
```

---

### 3. Real-Time Streaming via SSE (Microsecond Latency)
No polling, no delay. Incoming emails are pushed immediately via Server-Sent Events.

```python
from tempmail_api import TempMail

client = TempMail(api_key="YOUR_MASTER_CODE")
mailbox = client.create_mailbox()

def on_email_received(payload):
    print("⚡ Instant Push Event Received:")
    print(f"Code: {payload.get('code')}")
    print(f"Text: {payload.get('text')}")

mailbox.stream(callback=on_email_received, timeout=60)
```

---

### 4. Kopeechka 2.0 Protocol (Drop-In Replacement)
If your existing automation (ZennoPoster, BAS, custom scripts) uses Kopeechka:

```python
from tempmail_api import TempMail

client = TempMail(api_key="YOUR_MASTER_CODE")

# Order mailbox for a specific service
order = client.kopeechka.get_email(site="instagram.com")
print(f"Order #{order.task_id} -> {order.email}")

# Wait for code or activation link
code = client.kopeechka.wait_for_message(order.task_id, timeout=60)
print(f"Verification Value: {code}")

# Check remaining request quota
balance = client.kopeechka.get_balance()
print(f"Remaining Balance: {balance}")
```

---

### 5. Automated Webhook Forwarding
Receive incoming emails directly on your server HTTP endpoints:

```python
from tempmail_api import TempMail

client = TempMail(api_key="YOUR_MASTER_CODE")

# Configure destination URL
client.set_webhook("https://my-backend.com/api/incoming-emails")

# Send a test ping to verify endpoint
client.test_webhook()

# Fetch active configuration and delivery logs
status = client.get_webhook()
print(status)
```

---

## 📚 API Reference

| Method | Description |
| :--- | :--- |
| `client.get_domains()` | Returns list of private domains assigned to your plan. |
| `client.create_mailbox(domain=None, prefix=None)` | Creates a new `Mailbox` helper instance. |
| `client.get_code(email)` | Fast-path OTP extraction (<1ms). Returns string or `None`. |
| `client.wait_for_code(email, timeout=60)` | Polls until OTP arrives. Free smart-polling (no quota deduction for duplicates). |
| `client.get_inbox(email)` | Returns parsed `Message` object. |
| `client.get_html(email)` | Returns raw email HTML string. |
| `client.get_viewer_url(email)` | Returns SEC-03 sandboxed viewer web link. |
| `client.stream(email, callback)` | Listens for real-time SSE push events. |
| `client.kopeechka.*` | Kopeechka 2.0 protocol methods (`get_email`, `get_message`, `get_balance`, `cancel`). |

---

## 🔒 Security
All network requests are authenticated via HTTPS against `https://private.tempmailc.com`.
HTML content is isolated using SEC-03 Sandboxed iframes with strict Content-Security-Policies.

## 📄 License
MIT License. Created by the TempMailAPI Team.
