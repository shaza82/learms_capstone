"""LEARMS main application.

Reads ``data/raw_cohort_data.csv`` using only the standard library, validates
each row, flags every 10th learner for a random quality audit (modulus
operation), and stores everything in a normalised SQLite database
(``data/sprints_learners.db``) with the tables ``Cohorts`` and ``Learners``.

* All file and database access is wrapped in try/except so the program never
  crashes; bad CSV rows are logged and skipped.
* Every SQL statement is parameterised (no string formatting) to prevent SQL
  injection.
* Operational events are appended to ``logs/application_activity.log``.

Usage:  python3 code/main.py [--csv PATH] [--db PATH] [--hold SECONDS]
"""
import argparse
import csv
import logging
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import Instructor, Learner  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(ROOT, "logs", "application_activity.log")
AUDIT_EVERY = 10  # every 10th user is flagged for audit

SCHEMA = """
CREATE TABLE IF NOT EXISTS Cohorts (
    cohort_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    cohort_name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS Learners (
    learner_id        TEXT PRIMARY KEY,
    full_name         TEXT NOT NULL,
    assessment_score  REAL NOT NULL CHECK (assessment_score BETWEEN 0 AND 100),
    enrollment_status TEXT NOT NULL,
    audit_flag        INTEGER NOT NULL DEFAULT 0,
    cohort_id         INTEGER NOT NULL REFERENCES Cohorts(cohort_id)
);
"""


def setup_logging():
    """Configure the logger so that events are *appended* to the log file."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        logging.basicConfig(filename=LOG_PATH, filemode="a", level=logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s")
    except OSError as exc:  # e.g. read-only folder: fall back to the console
        logging.basicConfig(level=logging.INFO)
        logging.error("Cannot open log file %s: %s", LOG_PATH, exc)


def read_rows(csv_path):
    """Parse the CSV and return ``(learners, bad_rows)``.

    Each valid row becomes a ``Learner`` (score cast to float).  Invalid rows
    are logged and collected, never raised, so ingestion keeps running.
    """
    learners, bad_rows = [], []
    try:
        with open(csv_path, newline="", encoding="utf-8") as handle:
            for number, row in enumerate(csv.DictReader(handle), start=1):
                try:
                    learner = Learner(
                        row["learner_id"].strip(), row["full_name"].strip(),
                        row["cohort_name"].strip(), row["assessment_score"],
                        row["enrollment_status"].strip(),
                        audit_flag=(number % AUDIT_EVERY == 0))  # modulus operation
                    if not learner.learner_id or not learner.name:
                        raise ValueError("empty id or name")
                    learners.append(learner)
                except (KeyError, ValueError, AttributeError, TypeError) as exc:
                    bad_rows.append(number)
                    logging.warning("Row %d skipped: %s | %r", number, exc, row)
    except (OSError, csv.Error) as exc:
        logging.error("Cannot read CSV %s: %s", csv_path, exc)
    return learners, bad_rows


def store(learners, db_path):
    """Create the schema and insert all learners; return the inserted count."""
    inserted = 0
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with sqlite3.connect(db_path) as conn:
            conn.executescript(SCHEMA)
            for item in learners:
                conn.execute("INSERT OR IGNORE INTO Cohorts (cohort_name) VALUES (?)",
                             (item.cohort_name,))
                cohort_id = conn.execute(
                    "SELECT cohort_id FROM Cohorts WHERE cohort_name = ?",
                    (item.cohort_name,)).fetchone()[0]
                cur = conn.execute(
                    "INSERT OR REPLACE INTO Learners (learner_id, full_name, "
                    "assessment_score, enrollment_status, audit_flag, cohort_id) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (item.learner_id, item.name, item.assessment_score,
                     item.enrollment_status, int(item.audit_flag), cohort_id))
                inserted += cur.rowcount
    except sqlite3.Error as exc:
        logging.error("Database error: %s", exc)
    return inserted


def report(db_path):
    """Print a per-cohort summary using a parameterised query."""
    try:
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute(
                "SELECT c.cohort_name, COUNT(*), ROUND(AVG(l.assessment_score), 2) "
                "FROM Learners l JOIN Cohorts c ON c.cohort_id = l.cohort_id "
                "WHERE l.enrollment_status <> ? GROUP BY c.cohort_name "
                "ORDER BY c.cohort_name", ("Dropped",)).fetchall()
        print("Cohort summary (excluding Dropped learners):")
        for name, count, avg in rows:
            print(f"  {name:<40} learners={count:<3} avg_score={avg}")
    except sqlite3.Error as exc:
        logging.error("Report failed: %s", exc)


def main():
    """Entry point: ingest, store, summarise, and demo polymorphism."""
    parser = argparse.ArgumentParser(description="LEARMS cohort ingestion")
    parser.add_argument("--csv", default=os.path.join(ROOT, "data", "raw_cohort_data.csv"))
    parser.add_argument("--db", default=os.path.join(ROOT, "data", "sprints_learners.db"))
    parser.add_argument("--hold", type=int, default=0,
                        help="keep the process alive N seconds so it can be watched with ps")
    args = parser.parse_args()

    setup_logging()
    logging.info("LEARMS run started (pid=%d)", os.getpid())
    learners, bad_rows = read_rows(args.csv)
    inserted = store(learners, args.db)
    audited = [x.learner_id for x in learners if x.audit_flag]
    logging.info("Transaction summary: parsed=%d inserted=%d invalid_rows=%d audited=%s",
                 len(learners), inserted, len(bad_rows), ",".join(audited))
    print(f"Parsed {len(learners)} learners, inserted {inserted}, invalid rows {len(bad_rows)}")
    print(f"Flagged for audit (every {AUDIT_EVERY}th): {', '.join(audited)}")
    report(args.db)

    people = [Instructor("Dr. Laila Hassan", "laila@instructors.sprints.example",
                         ["Data Science Cohort 5", "AI & Machine Learning Cohort 2"])]
    people += learners[:2] + [x for x in learners if x.audit_flag][:1]
    print("Polymorphism demo (same call, different output):")
    for person in people:
        print("  " + person.display_profile())

    if args.hold:
        print(f"Holding process for {args.hold}s (pid {os.getpid()})...", flush=True)
        time.sleep(args.hold)
    logging.info("LEARMS run finished")


if __name__ == "__main__":
    main()
