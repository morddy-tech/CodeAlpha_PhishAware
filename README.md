# PhishAware

**CodeAlpha Cybersecurity Internship - Task 2 (Phishing Awareness Training)**

> Learn to Detect. Learn to Defend.

[![CI](https://github.com/morddy-tech/CodeAlpha_PhishAware/actions/workflows/ci.yml/badge.svg)](https://github.com/morddy-tech/CodeAlpha_PhishAware/actions/workflows/ci.yml)

PhishAware is a defensive, educational phishing-awareness training platform. It
teaches users to recognise phishing emails, fake websites, social engineering,
smishing, and vishing through modules, safe simulations, quizzes, scoring, and
progress tracking.

**This is an educational, defensive application. It cannot and does not conduct
real phishing, collect real credentials, or attack anyone.**

---

## Overview

Phishing remains one of the most common initial access vectors because it
targets human trust. PhishAware builds human defence with:

- Structured training modules and lessons
- Safe, fictional phishing email and fake-website simulations
- Social-engineering scenarios with "what should you do?" decisions
- Server-scored quizzes with explanations and retries
- Progress tracking, achievements, notifications, and an awareness score
- A staff/admin dashboard with analytics

## Features

- **8 training modules / 32 lessons** covering phishing fundamentals, email
  phishing, fake websites, social engineering, smishing/vishing, BEC, incident
  response, and security habits
- **8 interactive simulation scenarios** (email, fake website, SMS, phone, and
  social engineering) where learners identify red flags and choose a response
- **9 quizzes / 50 questions** with server-side scoring, passing thresholds,
  explanations, retry support, and a best-attempt summary
- **9 achievements** awarded automatically
- **Security Awareness Score** combining training, quizzes, and simulations
- **Custom staff dashboard** with user management, content links, feedback
  triage, and analytics
- **Responsive, accessible UI** with dark/light/system themes and keyboard-friendly
  navigation
- **Defensive security controls** including CSRF, authorization checks,
  rate-limited login and feedback, trusted-proxy support, CSP, secure cookies,
  upload validation, and server-side quiz time enforcement

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ (CI targets 3.13) |
| Framework | Django 6.1.x (`>=6.0,<6.2`) |
| Database | SQLite for local development, PostgreSQL for production |
| Static files | WhiteNoise + `collectstatic` |
| Cache / rate limits | LocMemCache locally, Redis when `REDIS_URL` is set |
| Images | Pillow |
| WSGI server | Gunicorn |
| Frontend | Django templates, vanilla JavaScript, custom CSS |

## Architecture

```text
config/         Django project settings, URLs, WSGI entry point
accounts/       Authentication, registration, profiles, avatars, security backend
training/       Training modules and lessons
simulations/    Scenario content, scoring, and post-submit feedback
quizzes/        Quiz engine, attempts, answers, and results
progress/       Completion tracking, achievements, notifications, awareness score
dashboard/      Learner dashboard and staff/admin analytics
core/           Landing page, feedback, error pages, security middleware/decorators
templates/      Shared and app-specific templates
static/         CSS, JavaScript, images, and SVGs
tests/          Regression and security test suite
```

## Database

The main models are:

- `accounts.UserProfile` (one-to-one with Django's user model; automatic
  creation via a `post_save` signal plus a backfill migration)
- `training.TrainingModule`, `training.TrainingLesson`
- `simulations.PhishingScenario`, `ScenarioIndicator`, `ScenarioResponse`,
  `ScenarioAttempt`
- `quizzes.Quiz`, `Question`, `Answer`, `QuizAttempt`, `UserAnswer`
- `progress.ModuleProgress`, `LessonCompletion`, `Achievement`,
  `UserAchievement`, `Notification`
- `core.Feedback`

The custom user-facing identity remains Django's `auth.User`. Non-empty emails
are protected by a case-insensitive unique index, and
`accounts.backends.EmailOrUsernameModelBackend` accepts either a username or an
email at login.

## Security Controls

| Boundary | Control |
|----------|---------|
| Authentication | Django password hashing, session cookies with `HttpOnly` and `SameSite=Lax`, optional secure cookies via `USE_HTTPS`, login rate limiting |
| Authorization | Server-side `login_required` and staff checks; attempts and results are scoped to the authenticated user |
| CSRF | Enabled for all state-changing forms; no view disables it |
| Input validation | Django forms, image content validation with Pillow, feedback length limits |
| Output safety | Django template auto-escaping; no user-controlled HTML is rendered unescaped |
| Uploads | PNG/JPEG only, 2 MB maximum, dimensions checked, generated filenames |
| Quiz integrity | Scores and timers are authoritative on the server; attempt start time comes from the database |
| Simulation privacy | Demo username/password fields are not successful form controls; submissions use Post-Redirect-Get |
| Rate limits | Cache-backed limits return HTTP 429 with `Retry-After` |
| Proxy headers | `X-Forwarded-*` is trusted only when `TRUST_PROXY_HEADERS=True` |
| Headers | CSP, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy` |
| Secrets | Environment variables only; `.env` is ignored and never committed |

## Installation

### 1. Clone and enter the project

```bash
git clone https://github.com/morddy-tech/CodeAlpha_PhishAware.git
cd CodeAlpha_PhishAware
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Python 3.12 or newer is required by Django 6.x. CI uses Python 3.13 (see
`.python-version`).

### 4. Create `.env`

```bash
cp .env.example .env
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Put it in `.env` as `SECRET_KEY=...` and keep `DEBUG=True` for local work.

### 5. Apply migrations

```bash
python manage.py migrate
```

The migrations create the schema, backfill profiles for existing users, and add
the case-insensitive email index. If your database already contains duplicate
emails, the email migration stops with an actionable error. Audit first:

```bash
python manage.py audit_duplicate_emails
```

The command is read-only; resolve duplicates manually, then migrate.

### 6. Create an admin user

```bash
python manage.py createsuperuser
```

### 7. Seed training content

```bash
python manage.py seed_training
```

This loads the modules, lessons, scenarios, questions, and achievements used by the application.

### 8. Run tests

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

### 9. Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Environment Variables

| Variable | Purpose | Local default |
|----------|---------|---------------|
| `SECRET_KEY` | Django signing key; required | — |
| `DEBUG` | Debug mode; never `True` in production | `False` |
| `ALLOWED_HOSTS` | Comma-separated host names | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins | empty |
| `DATABASE_URL` | PostgreSQL URL; SQLite when empty | empty |
| `DB_CONN_MAX_AGE` | Persistent DB connection age | `60` |
| `USE_HTTPS` | Secure cookies and HTTPS defaults | `False` |
| `SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS | `False` |
| `SECURE_HSTS_SECONDS` | HSTS lifetime; `0` disables | `0` |
| `TRUST_PROXY_HEADERS` | Trust `X-Forwarded-*` from a sanitising proxy | `False` |
| `REDIS_URL` | Shared cache for rate limits | empty (LocMem) |
| `RATE_LIMIT_ATTEMPTS` | Attempts per window | `5` |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate-limit window | `300` |
| `RATE_LIMIT_LOCKOUT_SECONDS` | Lockout duration | `900` |
| `QUIZ_CLOCK_TOLERANCE_SECONDS` | Server clock/network grace for quiz submission | `5` |
| `SERVE_STATIC_FILES` | Serve static files through Django | `DEBUG` |
| `SERVE_MEDIA_FILES` | Serve user media through Django | `DEBUG` |
| `LOG_TO_STDOUT` | Log to stdout instead of rotating files | `not DEBUG` |
| `EMAIL_BACKEND` | Email backend | console backend |

See `.env.example` for a copyable template.

## Production Deployment

### Build and start

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

The included `Procfile` uses the same Gunicorn command.

### Production environment example

```text
DEBUG=False
SECRET_KEY=<fresh random value>
ALLOWED_HOSTS=your-domain.example
CSRF_TRUSTED_ORIGINS=https://your-domain.example
DATABASE_URL=postgres://user:password@host:5432/phishaware
DB_CONN_MAX_AGE=60
USE_HTTPS=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=False
TRUST_PROXY_HEADERS=False
REDIS_URL=redis://cache-host:6379/1
SERVE_STATIC_FILES=False
SERVE_MEDIA_FILES=False
LOG_TO_STDOUT=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=...
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@your-domain.example
```

Set `TRUST_PROXY_HEADERS=True` **only** when a trusted edge proxy overwrites
client-supplied `X-Forwarded-For` / `X-Forwarded-Proto` headers. Django must not
be directly exposed to the internet when this is enabled.

### Static and media files

- WhiteNoise serves collected static files from `STATIC_ROOT` (`staticfiles/`).
- User media (`media/`, including avatars) is never served by WhiteNoise in
  production. Serve it from Nginx, a CDN, or an object-storage service.

Example Nginx location:

```nginx
location /media/ {
    alias /srv/phishaware/media/;
    add_header X-Content-Type-Options nosniff;
    location ~* \.(php|phtml|py|sh)$ {
        deny all;
    }
}
```

For object storage, place the bucket/CDN in front of `MEDIA_ROOT` and keep
`SERVE_MEDIA_FILES=False`. Never expose the media directory for script
execution.

### Database and cache

- PostgreSQL is recommended for production. SQLite is suitable for local
  development and small single-user demonstrations only.
- Set `REDIS_URL` whenever more than one Gunicorn worker handles requests.
  Otherwise each worker has an independent rate-limit counter.
- The project supports PostgreSQL via `DATABASE_URL`; `sslmode=require` can be
  supplied as a query parameter, for example
  `postgres://user:pass@host/db?sslmode=require`.

### Operations checklist

```bash
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py audit_duplicate_emails
python manage.py test
```

Also:

- Back up PostgreSQL and `media/` together.
- Keep `.env`, database files, logs, and user media out of Git.
- Rotate `SECRET_KEY` only with a planned session/password-reset impact.
- Use a TLS-terminating proxy and set `USE_HTTPS=True`.
- Review `logs/` access if file logging is enabled; production defaults to
  stdout via `LOG_TO_STDOUT=True`.
- Run the app with a non-root user and a read-only filesystem except for media
  and log paths.

### Render / Railway / Heroku

1. Connect the repository.
2. Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
3. Start: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
4. Add PostgreSQL and Redis, then set the environment variables above.
5. Run one-time commands: `migrate`, `seed_training`, `createsuperuser`.

## Project Structure Notes

- `accounts/signals.py` creates a profile for every user, including users made
  with `createsuperuser` or Django admin. `accounts/migrations/0002` backfills
  profiles for existing accounts.
- `quizzes/views.py` binds an attempt to the session and enforces the time limit
  from `QuizAttempt.started_at`, not from a browser timer.
- `simulations/views.py` uses Post-Redirect-Get so refreshing feedback cannot
  create duplicate attempts or re-score a scenario.
- `core/decorators.py` is a small cache-backed rate limiter used for login,
  registration, and feedback.

## Testing

The suite covers authentication, authorization, quiz scoring and timing,
simulation privacy, dashboard analytics, uploads, rate limiting, CSRF, headers,
and error pages.

```bash
python manage.py test -v 2
```

Run the same commands in CI on every push and pull request.

## Known Limitations

- SQLite is not a production database for concurrent multi-worker deployments.
- LocMemCache is per-process; production rate limiting requires Redis or another
  shared cache.
- The default avatar storage is local `MEDIA_ROOT`; production should use a
  proper media server or object storage.
- Log files are rotated locally when `LOG_TO_STDOUT=False`; container platforms
  should collect stdout instead.
- No real screenshots are committed. Add genuine screenshots of the running UI
  if you want them in the README; do not use fabricated images.
- Email uniqueness is enforced for non-empty addresses with a partial index
  supported by SQLite and PostgreSQL.

## Security Disclaimer

PhishAware is for education and defensive awareness only. All organisations,
domains, messages, and scenarios are fictional. The application does not send
email, contact third parties, collect real credentials, or perform any
offensive action.

Do not use this project to conduct real phishing, harvest credentials, attack
systems, or impersonate real people or organisations.

## Ethical Use

Use this project only where you have permission to train users, and only with
fictional content. Follow your organisation's policies and applicable law. See
`SECURITY.md` for vulnerability reporting and disclosure expectations.

## CodeAlpha Task Mapping

| Requirement | Implementation |
|-------------|----------------|
| Phishing awareness content | Training modules, lessons, simulations, quizzes |
| Interactive learning | Red-flag selection, response choices, explanations |
| Progress tracking | Module/lesson completion, attempts, achievements, awareness score |
| Safe demonstrations | Fictional content and non-submitting demo credential fields |
| Professional presentation | Responsive UI, themes, accessibility, admin analytics |
| Security-conscious engineering | Server-side scoring/timing, authorization, rate limits, CSP, upload validation |

## Future Improvements

- Add genuine UI screenshots and a short demo video.
- Add optional object-storage backend for media.
- Add email verification and MFA for staff accounts.
- Add richer cohort reporting and CSV export for administrators.
- Add background jobs for notification delivery and reminder emails.

## Author

**Ifedayo Matthew**
GitHub: [morddy-tech](https://github.com/morddy-tech)

## License

MIT License. See `LICENSE`.
