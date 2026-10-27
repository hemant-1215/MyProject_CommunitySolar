# Lab 5 - Issues (billing_system.py)

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| Deprecated pyCrypto import (B413) | Security (Bandit) | 8 | Deprecated AES library. | Switch to `cryptography`. |
| Hardcoded secrets (B105) | Security (Bandit) | 14-15 | Keys are committed in source. | Load hex-encoded values from environment variables with temporary random fallback. |
| ECB mode for card encryption | Security (manual) | 72-74 | Deterministic encryption has no integrity protection. | Use AES-GCM with a random nonce. |
| Mako template XSS (B702) | Security (Bandit) | 86 | User input is rendered as HTML without escaping. | Escape values with `html.escape` and use an f-string. |
| XML parsing without XXE protection | Security (manual) | 80-82 | Untrusted XML is parsed with an unsafe default parser. | Use `defusedxml.ElementTree`. |
| Non-constant-time signature comparison | Security (manual) | 76-78 | Equality comparison can leak timing information. | Use `hmac.compare_digest`. |
| Weak PRNG (B311) | Security (Bandit) | 67 | `random` is predictable for security-sensitive codes. | Use `secrets.choice`. |
| Assert for validation (B101) | Security (Bandit) | 85 | Assertions can be removed with optimized Python. | Raise `ValueError`. |
| 150% coupon | Bug | 19, 27-32 | Invalid percentages can create negative invoices. | Ignore percentages outside 0-100. |
| Coupon expiry boundary | Bug | 31 | Coupon is rejected on its expiry day. | Compare with `>` rather than `>=`. |
| Trial off by one | Bug | 24-25 | A trial remains active after 14 elapsed days. | Use `>= TRIAL_DAYS`. |
| Month overflow | Bug | 40-41 | December and day 31 can produce an invalid date. | Roll the year and clamp to month end. |
| Proration divisor | Bug | 43-49 | Proration always divides by 30. | Use the actual number of days in the billing month. |
| Retry loop | Bug | 50-56 | `<=` allows four attempts when the maximum is three. | Use `< MAX_ATTEMPTS`. |
| Refund ignores usage | Bug | 58-65 | The full price is refunded and `finally` hides errors. | Refund only unused days and remove the `finally` return. |
| Style and maintainability | Pylint/Flake8 | Whole file | Naming, docstrings, import, literal, spacing, and entry-point issues reduce quality. | Apply Pylint and Flake8 recommendations. |
