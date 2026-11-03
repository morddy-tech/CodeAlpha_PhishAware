# Security Policy

## Security Philosophy

PhishAware is a **defensive security education platform**. Its purpose is to
teach people to recognise and resist phishing. The application itself must never
be usable as an offensive tool.

- **Simulated only** - every phishing example uses clearly fictional
  organisations and domains.
- **No credential collection** - demo login fields are not successful form
  controls; their contents are never submitted, stored, logged, or transmitted.
- **No real targets** - the application never sends email, contacts external
  systems, or initiates contact with anyone.
- **Defense in depth** - authentication controls, authorization, validation,
  rate limiting, secure headers, and server-side scoring are applied throughout.

## Security Boundaries

| Boundary | Guarantee |
|----------|-----------|
| Authentication | Django password hashing; session cookies `HttpOnly` and `SameSite=Lax`; secure cookies when `USE_HTTPS=True`; login rate-limited per identifier and per IP |
| Authorization | Staff/admin endpoints require `is_staff`; enforced server-side |
| User data | Users can only read or modify their own attempts, results, and profile |
| Input | Django forms validate all user input; no raw SQL from user input |
| Output | Template auto-escaping; CSP restricts script sources |
| Uploads | PNG/JPEG only, 2 MB maximum, content verified with Pillow, generated filenames |
| Quiz integrity | Scores and quiz deadlines are calculated from server-side state |
| Proxy trust | `X-Forwarded-*` is ignored unless `TRUST_PROXY_HEADERS=True` is explicitly configured for a sanitising proxy |
| Secrets | Loaded from environment variables; `.env` is never committed |
| Logs | Identity fields are hashed or reduced to IDs; logs are not web-accessible |

## Reporting Vulnerabilities

Please report suspected vulnerabilities privately through GitHub's **Security**
tab for this repository:

<https://github.com/morddy-tech/CodeAlpha_PhishAware/security/advisories/new>

Include:

- A description of the issue
- Steps to reproduce
- The affected version or commit
- Proposed impact and, optionally, a fix

Do not open a public issue for an unfixed vulnerability. We aim to acknowledge
reports within **72 hours** and to coordinate a fix and disclosure with you.

## Responsible Disclosure

Please allow a reasonable period (default **90 days**) before public disclosure
of any confirmed issue, so a fix can be released. We will credit reporters who
want attribution.

## Supported Versions

Only the current `main` branch is actively supported. Older tags and commits
receive fixes on a best-effort basis.

## Out of Scope

- Findings that require a compromised administrator account
- Reports against third-party hosting, DNS, or TLS configuration outside this
  repository
- Spam, social engineering of maintainers, or denial-of-service testing against
  production systems without permission
- Theoretical issues without a realistic impact on this application

## Secure Deployment Notes

- Use PostgreSQL and a shared cache (Redis) in production.
- Set `DEBUG=False`, `USE_HTTPS=True`, and `SECURE_SSL_REDIRECT=True`.
- Set `TRUST_PROXY_HEADERS=True` only behind a proxy that overwrites forwarded
  headers.
- Serve user media from a dedicated web server or object store, never from a
  script-enabled directory.
- Keep `.env`, database files, logs, and user media out of version control.
- Run `python manage.py check --deploy` before release.
