# LEARMS - Learner Assessment & Resource Management System

Sprints capstone (AI & Machine Learning - Beginner). Python standard library + SQLite, deployed on Linux with least-privilege permissions.

## Run
python3 code/main.py            # reads data/raw_cohort_data.csv, writes data/sprints_learners.db and logs/application_activity.log
python3 code/main.py --hold 12  # keep the process alive 12 s so it can be watched with: ps aux | grep main.py

## Layout
- code/main.py - ingestion application (csv parsing, float cast, every-10th audit flag, parameterised SQLite, logging, try/except)
- code/models.py - User base class with Learner and Instructor subclasses (polymorphism)
- data/raw_cohort_data.csv - starter data (45 learners)
- logs/linux_operations.log - real terminal log of package install, service account, chmod/chown, ps monitoring
- docs/ - project charter, architecture and schema (the report PDF, presentation PDF, generated database and demo video are in the submission bundle)

## Results on the starter data
45 learners parsed, 45 inserted, 0 rejected, 5 cohorts, 4 flagged for audit (SP-L-1010, 1020, 1030, 1040).
