# Stratus

Stratus is a technology job aggregation site. It pulls listings from several job APIs, cleans and de-duplicates them, and presents them in one searchable place.

The site was hosted at stratusjobs.com on Railway and has since been taken down, so it is no longer publicly available. The code is kept here as a record of the project.

It started as my independent internship project for the Master of Science in Information Technology at Arkansas Tech University. It was first planned as a veteran-only job board. Testing showed the APIs return too few positions that are clearly veteran-preferred, so I changed the scope to general technology jobs. Veteran features remain as optional extras (profile fields, a veteran-friendly filter, security clearance tagging).

## State at last deployment

- About 516 validated technology jobs from 740+ companies
- Sources: Adzuna, USAJobs, JSearch (RapidAPI)
- Data cleanup removed 482 duplicates and 535 expired listings
- Was hosted on Railway with PostgreSQL, deployed from GitHub on push to main

## Stack

- Python, Django 4.2.7
- PostgreSQL 15
- Bootstrap 5, Django templates
- Gunicorn, WhiteNoise
- Railway (hosting), GoDaddy (domain)

## Features

- Job search and filtering by keyword, location, salary and employment type
- User accounts and profiles, with optional military service fields
- Saved jobs and application tracking
- Contact form with spam protection
- Admin panel for jobs, companies and users

## Import pipeline

1. Query each API across a set of technology search terms
2. Parse responses and normalize location, salary and employment type
3. Filter out non-technology roles with include and exclude keywords
4. Skip duplicates by import hash and by title plus company
5. Create or match the company record
6. Insert in atomic transactions
7. Check that each application URL still works, so expired listings can be removed
8. Log counts and errors for each run

While it was live, scheduled jobs refreshed listings daily, backed up the database with 7-day retention, and sent health alerts by email.

## Security

- Credentials are read from environment variables and never committed
- Least-privilege database user
- Rate limiting on login, registration and contact submissions
- HTTPS-only cookies, session timeout, HSTS and other security headers
- Password validation and a custom admin URL

## Repository layout

- `accounts/`: authentication and user profiles
- `companies/`, `jobs/`, `application/`: core data models
- `public_site/`: public pages and templates
- `contact/`: contact form
- `import_jobs_advanced.py`: main multi-API importer
- `archive/veteran_experiment/`: the original veteran-only import scripts, kept as a record of the scope change

## Diagrams

Generated from the code in this repository by the scripts in `docs/diagrams/` (Graphviz and the Python `diagrams` package):

- `docs/diagrams/01_system_architecture.png`: components, deployment path and security controls
- `docs/diagrams/02_database_erd.png`: tables and relationships, taken from the Django models
- `docs/diagrams/03_import_pipeline.png`: how listings are fetched, de-duplicated and stored

## Running locally

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # then fill in your own values
python manage.py migrate
python manage.py runserver
```

## Author

Richard Oliver, Arkansas Tech University, December 2025.
