# Security Policy

## Security Philosophy

PhishAware is a **defensive security education platform**. Its entire purpose
is to teach people how to recognize and resist phishing. It is built on the
principle that the application itself must never be usable as an offensive
tool.

- **Simulated only** — every phishing example uses clearly fictional
  organizations and domains.
- **No credential collection** — simulated login fields are decorative; input
  is discarded and never stored, logged, or transmitted.
- **No real targets** — the application never sends email, contacts external
  systems, or initiates contact with anyone.
- **Defense in depth** — auth controls, access controls, validation, and
  rate limiting are applied throughout.

## Security Boundaries

| Boundary | Guarantee |
|----------|-----------|
| Authentication | Passwords hashed (PBKDF2/Argon2); session cookies HttpOnly + SameSite; rate-limited login |
| Authorization | Staff/admin endpoints require `is_staff`; enforced server-side |
| User data | Users can only read/modify their own records (IDOR protected) |
| Input | All user input validated by Django forms; no raw SQL |
| Output | Template auto-escaping (XSS-safe) |
| Uploads | File type + size validation; served from `media/` only |
| Secrets | Loaded from environment variables; `.env` never committed |

## Prohibited Use

This software must **not** be used to:

- Conduct real phishing or credential harvesting
- Send phishing emails to real users
- Collect or store real passwords, banking data, or MFA codes
- Attack, exploit, or impersonate real organizations or individuals
- Repurpose its simulation features into any credential-theft system

Any such use is a violation of the project's ethical guidelines and may be
illegal.

## Reporting Vulnerabilities

If you find a security issue in PhishAware:

1. **Do not** disclose it publicly until it is fixed.
2. Report it privately by email or private issue to the project maintainer
   with:
   - A description of the issue
   - Steps to reproduce
   - The affected version/commit
   - Proposed impact and (optionally) a fix

We aim to acknowledge reports within **72 hours** and to coordinate a fix and
disclosure with you.

## Responsible Disclosure

Please allow a reasonable period (default **90 days**) before public
disclosure of any confirmed issue, so a fix can be released.

## Supported Versions

Only the current `main` branch is actively supported. Older tags/commits
receive fixes on a best-effort basis.
