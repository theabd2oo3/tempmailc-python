"""
Live Integration Tests for TempMailAPI Python SDK
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tempmail_api import TempMail, TempMailError

TEST_API_KEY = "1YXHPRbaRBs"  # Active team user key for verification

def test_full_pipeline():
    print(">>> 1. Initializing TempMail client...")
    client = TempMail(api_key=TEST_API_KEY)
    assert client.api_key == TEST_API_KEY

    print(">>> 2. Testing get_domains()...")
    domains = client.get_domains()
    print(f"Assigned domains: {domains}")
    assert isinstance(domains, list)
    assert len(domains) > 0

    print(">>> 3. Testing create_mailbox()...")
    mailbox = client.create_mailbox()
    print(f"Created mailbox: {mailbox.email}")
    assert "@" in mailbox.email
    assert mailbox.domain in domains

    print(">>> 4. Testing get_code() on empty mailbox...")
    code = mailbox.get_code()
    print(f"Initial code check: {code}")
    assert code is None

    print(">>> 5. Testing get_inbox() on empty mailbox...")
    inbox = mailbox.get_inbox()
    print(f"Initial inbox check: {inbox}")
    assert inbox is None

    print(">>> 6. Testing viewer_url...")
    viewer_url = mailbox.viewer_url
    print(f"Viewer URL: {viewer_url}")
    assert "https://private.tempmailc.com/api/v1/view-html" in viewer_url
    assert f"code={TEST_API_KEY}" in viewer_url

    print(">>> 7. Testing Kopeechka get_balance()...")
    balance = client.kopeechka.get_balance()
    print(f"Kopeechka balance: {balance}")
    assert balance > 0

    print(">>> 8. Testing Kopeechka get_email() and cancel()...")
    order = client.kopeechka.get_email(site="any")
    print(f"Kopeechka order #{order.task_id}: {order.email}")
    assert order.task_id > 0
    assert "@" in order.email

    cancelled = client.kopeechka.cancel(order.task_id)
    print(f"Cancelled status: {cancelled}")
    assert cancelled is True

    print("\n[SUCCESS] ALL LIVE SDK INTEGRATION TESTS PASSED 100%!")


if __name__ == "__main__":
    test_full_pipeline()
