# LEARMS - Architecture and Database Schema

## Flow
`raw_cohort_data.csv` -> `code/main.py` (csv + validation, modulus audit flag) -> `code/models.py` (Learner objects) -> `data/sprints_learners.db` (SQLite) -> console summary + `logs/application_activity.log`.

## Layout
- `code/` main.py (application), models.py (OOP)
- `data/` input CSV and generated `sprints_learners.db`
- `logs/` `linux_operations.log` (setup commands), `application_activity.log` (runtime events)
- `docs/` charter, architecture, report PDF, presentation PDF

## Database (normalised, one cohort to many learners)
**Cohorts**: `cohort_id` INTEGER PK AUTOINCREMENT, `cohort_name` TEXT UNIQUE NOT NULL
**Learners**: `learner_id` TEXT PK, `full_name` TEXT, `assessment_score` REAL (0-100 CHECK), `enrollment_status` TEXT, `audit_flag` INTEGER, `cohort_id` INTEGER FK -> Cohorts

Cohort names repeat in every row of the flat file; storing them once removes the update anomalies of the flat files.

## OOP
`User(name, email, role).display_profile()` is overridden by `Learner` (float score, audit status) and `Instructor` (cohorts taught).

## Security
Parameterised SQL only; service account with group access (no root for daily runs); DB mode 640, directories 750; try/except around all I/O.
