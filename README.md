# PhishAware

**CodeAlpha Cybersecurity Internship — Task 2 (Phishing Awareness Training)**

> Learn to Detect. Learn to Defend.

PhishAware is a professional, production-quality **defensive cybersecurity
awareness training platform**. It teaches users to recognize phishing emails,
fake websites, social engineering, smishing, and vishing through interactive
modules, safe simulations, quizzes, scoring, and progress tracking.

**This is an educational, defensive application. It cannot and does not
conduct real phishing, collect real credentials, or attack anyone.**

---

## Overview

Phishing remains the #1 entry vector for breaches because it targets human
trust. PhishAware builds that human defense with:

- Structured training modules and lessons
- Safe, fictional phishing email and fake-website simulations
- Social engineering scenario training with "what should you do?" decisions
- Server-scored quizzes with explanations and retries
- Progress tracking, achievements, notifications, and a security awareness score
- A custom staff/admin dashboard with analytics

## Objectives

- Educate users about phishing, fake websites, and social engineering
- Provide realistic but **completely safe** practice
- Reinforce learning through quizzes and immediate feedback
- Track progress and motivate with achievements
- Deliver a professional, accessible, responsive experience

## Features

- **8 training modules / 32 lessons** covering phishing fundamentals, email
  phishing, fake websites, social engineering, smishing/vishing, BEC, incident
  response, and security habits
- **8 interactive simulation scenarios** (email, fake website, SMS, phone,
  social engineering) where learners click red flags and choose the right action
- **9 quizzes / 50 questions** with server-side scoring, passing thresholds,
  explanations, and retry
- **9 achievements** awarded automatically
- **Security Awareness Score** combining training, quizzes, and simulations
- **Custom admin dashboard**: overview, users, content, analytics, feedback
- **Notifications**, feedback, search and filtering
- **Light / dark / system** themes, responsive, accessible
- **Rate limiting** on authentication endpoints
- **Security headers**, CSRF protection, IDOR protection, hashed passwords

## Technology Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3, Django 6, Gunicorn (prod)  |
| Database   | SQLite (dev) / PostgreSQL (prod)     |
| Static     | Whitenoise (prod)                    |
| Auth       | Django auth + custom email/username backend |
| Frontend   | HTML5, CSS3 (custom design system), vanilla JS |
| Icons      | Inline Lucide-style SVG set          |
| Charts     | Pure CSS bar charts (no dependencies) |

No frontend frameworks or CDNs are required — everything is self-contained.

## Architecture

```text
CodeAlpha_PhishAware/
├── manage.py
├── config/                  # project settings, urls, asgi/wsgi
├── accounts/                # auth, profiles, password reset
├── training/                # modules & lessons
├── simulations/             # phishing scenarios, indicators, attempts
├── quizzes/                 # quiz engine, attempts, user answers
├── progress/                # progress, achievements, notifications
├── dashboard/               # user dashboard + admin dashboard
├── core/                    # landing, about, tips, feedback, errors, middleware
├── templates/               # Django templates
├── static/                  # CSS, JS, images
├── media/                   # uploads (avatars)
├── tests/                   # automated test suite
├── requirements.txt
├── .env.example
├── README.md
└── SECURITY.md
```

## Database

Key models (Django ORM, all in `*/models.py`):

- `User` (Django auth) + `UserProfile` (accounts)
- `TrainingModule`, `TrainingLesson` (training)
- `PhishingScenario`, `ScenarioIndicator`, `ScenarioResponseOption`,
  `ScenarioAttempt` (simulations)
- `Quiz`, `Question`, `AnswerOption`, `QuizAttempt`, `UserAnswer` (quizzes)
- `ModuleProgress`, `LessonCompletion`, `Achievement`, `UserAchievement`,
  `Notification` (progress)
- `Feedback` (core)

Design rules applied: foreign keys, indexes, unique constraints, slugs,
choices, timestamps, duplicate-progress/achievement prevention, transactions,
`select_related`/`prefetch_related` where useful.

## Security Controls

- CSRF protection enabled on all forms
- Server-side quiz/simulation scoring (clients cannot set scores)
- IDOR protection: every user-scoped lookup filters by the requesting user
- Staff-only admin dashboard enforced server-side
- Session cookies `HttpOnly` + `SameSite=Lax`; secure cookies off in DEBUG
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
  plus HSTS/SSL settings available for production
- Password hashing via Django defaults (PBKDF2/Argon2)
- Application-level rate limiting on login/registration/password reset
- Input validation via Django forms; upload validation (type + size)
- Custom 400/403/404/500 pages — no stack traces in production
- Logging for auth events and permission failures (no secrets logged)
- Simulated login fields never store or transmit anything

## Installation

Requirements: Python 3.10+ (developed on 3.14), pip.

```bash
# 1. Clone and enter the project
git clone https://github.com/morddy-tech/CodeAlpha_PhishAware.git
cd CodeAlpha_PhishAware

# 2. (Recommended) create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and edit:

```bash
cp .env.example .env   # Windows:  copy .env.example .env
```

The most important variables:

```text
SECRET_KEY=            # generate one (see below)
DEBUG=True             # must be False in production
ALLOWED_HOSTS=localhost,127.0.0.1
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Never commit your `.env` file.**

## Database Setup

```bash
python manage.py migrate
```

SQLite is used by default. For PostgreSQL (production), set
`DATABASE_URL` in `.env`:

```text
DATABASE_URL=postgres://user:password@host:5432/phishaware
```

The `DATABASES` block switches automatically when the URL is present.

## Creating Admin User

```bash
python manage.py createsuperuser
```

There is **no default admin password** — you create the account yourself, as
you should.

## Seeding Training Content

```bash
python manage.py seed_training
```

The command is idempotent — running it twice creates no duplicates. It seeds
the 8 modules, 32 lessons, 8 scenarios, 9 quizzes, and 9 achievements.

## Running Tests

```bash
python manage.py test
```

The suite (72 tests) covers authentication, authorization/IDOR, training,
quizzes, simulations, security headers/CSRF/rate limiting, and model
constraints.

## Running Development Server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

> **Styling looks broken / "only HTML"?** Keep `DEBUG=True` in `.env` for local
> development (Django's dev server serves CSS/JS automatically in DEBUG mode),
> or keep `SERVE_STATIC_FILES=True` and it will also work with `DEBUG=False`.
> Never set both `DEBUG=False` and `SERVE_STATIC_FILES=False` on a local
> machine unless you have run `python manage.py collectstatic` and configured a
> real web server to serve `staticfiles/`.

## Deployment (Live Use)

The project is deployment-ready: `whitenoise` serves static files, `gunicorn`
runs the WSGI app (see `Procfile`), and the database switches to PostgreSQL
via `DATABASE_URL`.

### Environment variables (production)

```text
DEBUG=False
SECRET_KEY=<a fresh, random key>
ALLOWED_HOSTS=your-app-domain.com,www.your-app-domain.com
CSRF_TRUSTED_ORIGINS=https://your-app-domain.com
DATABASE_URL=postgres://user:password@host:5432/phishaware
SERVE_STATIC_FILES=False
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=...            # your mail provider
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@your-domain.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
```

### On Render (recommended — free tier available)

1. Push the repository to GitHub (see "GitHub" below).
2. In Render, create a **New → Web Service** and connect the repo.
3. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. Start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
5. Add a PostgreSQL database in Render and copy its URL into `DATABASE_URL`.
6. Set the remaining environment variables above.
7. Deploy, then run one-time commands in the Render shell:
   ```bash
   python manage.py migrate
   python manage.py seed_training
   python manage.py createsuperuser
   ```

### On Railway / Heroku

- Same build and start commands (the `Procfile` is used by Heroku and Railway).
- Railway: add the PostgreSQL plugin, set `DATABASE_URL` automatically.
- Run `migrate`, `seed_training`, and `createsuperuser` once after deploy.

### On PythonAnywhere / a VPS

```bash
python manage.py collectstatic --noinput   # served by Nginx/Apache from staticfiles/
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Before going live — checklist

- [ ] `DEBUG=False` and a fresh `SECRET_KEY`
- [ ] `ALLOWED_HOSTS` + `CSRF_TRUSTED_ORIGINS` set to your real domain
- [ ] `SERVE_STATIC_FILES=False` and `collectstatic` ran
- [ ] PostgreSQL configured via `DATABASE_URL`
- [ ] Real SMTP credentials configured
- [ ] `python manage.py check --deploy` shows no blocking warnings
- [ ] `migrate`, `seed_training`, `createsuperuser` executed

## GitHub

The repository is ready to push. Before committing:

- Verify `.env` is **not** tracked (it is in `.gitignore`).
- Generate a fresh `SECRET_KEY` for any shared environment.
- Replace the placeholder GitHub URL in `core/context_processors.py`
  (`GITHUB_URL`) and the Author section of this README with your profile.

```bash
git init
git add .
git commit -m "PhishAware: phishing awareness training platform (CodeAlpha Task 2)"
git branch -M main
git remote add origin https://github.com/<your-username>/CodeAlpha_PhishAware.git
git push -u origin main
```

## Project Screenshots

| Page | Screenshot |
|------|------------|
| Landing page | _(add screenshot here)_ |
| Training modules | _(add screenshot here)_ |
| Phishing email simulation | _(add screenshot here)_ |
| Quiz result | _(add screenshot here)_ |
| User dashboard | _(add screenshot here)_ |
| Admin analytics | _(add screenshot here)_ |

To add a screenshot: capture the page, save it in `docs/screenshots/`, and
insert `![alt text](docs/screenshots/name.png)` in the table above.

## Security Disclaimer

PhishAware is **educational and defensive only**. All simulations use clearly
fictional organizations and domains (e.g. `example.com`). Simulated login
pages are decorative: any text typed into them is discarded instantly and is
**never stored, logged, or transmitted**. The platform does not send email,
does not contact external targets, and cannot be used to conduct real
phishing.

## Ethical Use

- Do **not** use this project or its content to perform real phishing,
  credential harvesting, or social engineering against real people.
- This software is provided for **security awareness and education**.
- Never repurpose the simulated login/simulation features into a real
  credential-collection system.

## CodeAlpha Task Mapping

| Requirement                        | Implementation                                   |
|------------------------------------|--------------------------------------------------|
| Phishing education                 | Training modules & lessons                        |
| Fake website recognition           | Website simulation scenario                       |
| Social engineering education       | Scenario training with response decisions         |
| Best practices                     | Security tips page + security habits module       |
| Real-world examples                | Realistic (fictional) scenario content            |
| Interactive quizzes                | Server-scored quiz engine with explanations       |
| Progress tracking                  | Module progress, achievements, awareness score    |

## Future Improvements

- Scheduled email reminders (e.g. via Celery + a mail provider)
- Export learner analytics for admins (CSV)
- Gamified leaderboards and streaks
- Admin content editor UI (beyond Django admin)
- API endpoints with Django REST Framework for LMS integration
- Localization (i18n) support
- Optional organization/group management for team training

## Author

**Ifedayo Matthew**

- GitHub: [your-github-username](https://github.com/morddy-tech/)
- Project: [CodeAlpha_PhishAware](https://github.com/morddy-tech/CodeAlpha_PhishAware)
