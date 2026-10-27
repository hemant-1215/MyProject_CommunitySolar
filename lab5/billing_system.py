"""Subscription billing system: trials, plans, coupons, proration, refunds,
card encryption, signed webhooks and HTML invoices."""

import calendar
import hashlib
import hmac
import html
import os
import secrets
import sys
from datetime import date

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from defusedxml import ElementTree

PLANS = {"basic": 199, "pro": 499, "team": 999}
GST = 0.18
TRIAL_DAYS = 14
MAX_ATTEMPTS = 3
BILLING_PERIOD_DAYS = 30


def _load_secret(name, size):
    """Read a hex-encoded secret from the environment.

    Falls back to an ephemeral random value (with a warning) so the demo runs,
    but real deployments must set the variable.
    """
    value = os.environ.get(name)
    if value:
        return bytes.fromhex(value)
    print(f"WARNING: {name} not set; using a temporary random value.",
          file=sys.stderr)
    return secrets.token_bytes(size)


WEBHOOK_SECRET = _load_secret("WEBHOOK_SECRET", 32)
CARD_KEY = _load_secret("CARD_KEY", 32)  # 32 bytes -> AES-256

subscriptions = {}
coupons = {
    "WELCOME10": {"percent": 10, "expires": date(2026, 12, 31)},
    "FRIENDS150": {"percent": 150, "expires": date(2027, 1, 31)},
}


def subscribe(user, plan, start):
    """Create a trial subscription for a user."""
    subscriptions[user] = {
        "plan": plan, "start": start, "status": "trial", "invoices": [],
    }
    return subscriptions[user]


def is_trial_over(user, today):
    """Return True once the 14-day trial has fully elapsed."""
    return (today - subscriptions[user]["start"]).days >= TRIAL_DAYS


def apply_coupon(amount, code, today=None):
    """Apply a valid, unexpired coupon; ignore unknown or invalid ones."""
    today = today or date.today()
    coupon = coupons.get(code)
    if coupon is None or today > coupon["expires"]:
        return amount
    if not 0 <= coupon["percent"] <= 100:
        return amount
    return amount - amount * coupon["percent"] / 100


def invoice_amount(user, code=None, today=None):
    """Plan price plus GST, minus any coupon, rounded to 2 decimals."""
    plan_price = PLANS[subscriptions[user]["plan"]]
    with_tax = plan_price * (1 + GST)
    return round(apply_coupon(with_tax, code, today), 2)


def next_billing_date(current):
    """Same day next month, clamped to month end, rolling over December."""
    year = current.year + current.month // 12
    month = current.month % 12 + 1
    day = min(current.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def prorate_upgrade(user, new_plan, today, period_end):
    """Charge the price difference for the days left in the period."""
    old = PLANS[subscriptions[user]["plan"]]
    new = PLANS[new_plan]
    days_in_period = calendar.monthrange(period_end.year, period_end.month)[1]
    days_left = max((period_end - today).days, 0)
    subscriptions[user]["plan"] = new_plan
    return round((new - old) * days_left / days_in_period, 2)


def retry_payment(charge):
    """Call charge() up to MAX_ATTEMPTS times; return attempts used."""
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        if charge():
            break
    return attempts


def cancel_refund(user, days_used):
    """Refund the unused part of the billing period."""
    price = PLANS[subscriptions[user]["plan"]]
    days_unused = max(BILLING_PERIOD_DAYS - days_used, 0)
    return round(price * days_unused / BILLING_PERIOD_DAYS, 2)


def coupon_code():
    """Generate an unpredictable coupon code."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "SAVE-" + "".join(secrets.choice(alphabet) for _ in range(6))


def active_users():
    """Users with no invoices yet (original behaviour, kept as-is)."""
    return {u for u, sub in subscriptions.items() if not sub["invoices"]}


def encrypt_card(card_number):
    """Encrypt a card number with AES-GCM; output is nonce + ciphertext."""
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(CARD_KEY).encrypt(nonce, card_number.encode(), None)
    return (nonce + ciphertext).hex()


def decrypt_card(token):
    """Reverse encrypt_card."""
    raw = bytes.fromhex(token)
    return AESGCM(CARD_KEY).decrypt(raw[:12], raw[12:], None).decode()


def verify_webhook(body, signature):
    """Check the HMAC-SHA256 signature in constant time."""
    expected = hmac.new(WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_webhook(xml_bytes):
    """Parse a webhook payload with a parser that blocks XXE attacks."""
    root = ElementTree.fromstring(xml_bytes)
    return {"event": root.findtext("event"), "user": root.findtext("user")}


def render_invoice(user, amount):
    """Render an HTML invoice, escaping user-supplied text."""
    if amount < 0:
        raise ValueError("amount must be non-negative")
    return (f"<h1>Invoice for {html.escape(str(user))}</h1>"
            f"<p>Total: Rs.{html.escape(str(amount))}</p>")


def main():
    """Run the built-in demo."""
    subscribe("asha", "pro", date(2026, 9, 1))
    subscribe("<b onmouseover=alert(1)>ravi</b>", "basic", date(2026, 9, 20))
    print("Trial over on 09-15?", is_trial_over("asha", date(2026, 9, 15)))
    print("Pro invoice with WELCOME10:",
          invoice_amount("asha", "WELCOME10", date(2026, 10, 1)))
    print("Pro invoice with FRIENDS150:",
          invoice_amount("asha", "FRIENDS150", date(2026, 10, 1)))
    print("Coupon on its expiry day:",
          invoice_amount("asha", "WELCOME10", date(2026, 12, 31)))
    print("Next billing after 2026-10-15:",
          next_billing_date(date(2026, 10, 15)))
    print("Next billing after 2026-12-31:",
          next_billing_date(date(2026, 12, 31)))
    print("Upgrade pro->team, 10 days left in Feb:",
          prorate_upgrade("asha", "team", date(2027, 2, 18),
                          date(2027, 2, 28)))
    print("Payment attempts (max 3, always failing):",
          retry_payment(lambda: False))
    print("Refund after using 25 of 30 days:", cancel_refund("asha", 25))
    card = "4111111111111111"
    print("Same card, same ciphertext?",
          encrypt_card(card) == encrypt_card(card))
    print("Decrypts back:", decrypt_card(encrypt_card(card)) == card)
    sig = hmac.new(WEBHOOK_SECRET, b"<x/>", hashlib.sha256).hexdigest()
    print("Webhook verified:", verify_webhook(b"<x/>", sig))
    print("Webhook:", parse_webhook(
        b"<hook><event>paid</event><user>asha</user></hook>"))
    print("Invoice HTML:",
          render_invoice("<b onmouseover=alert(1)>ravi</b>", 199))
    print("Coupon:", coupon_code())


if __name__ == "__main__":
    main()
