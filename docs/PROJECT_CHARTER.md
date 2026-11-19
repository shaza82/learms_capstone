# LEARMS - Project Charter (1 page)

**Client:** Sprints - Technical Operations (Fatima Rashid) | **Consultant:** Shaza, Junior Solutions Consultant

**Problem.** Learner assessment data is exported to fragmented text files; sysadmins ingest it by hand, fix folder permissions manually and run disjointed scripts. No version control, security risk, slow.

**Scope.** Python (standard library only) backend that parses `raw_cohort_data.csv` into a normalised SQLite database `sprints_learners.db` (Cohorts, Learners); OOP models (User, Learner, Instructor); logging; Git; a documented, reproducible Linux deployment (apt-get, chmod/chown, ps monitoring).

**Out of scope.** Web UI, third-party frameworks (Django, Pandas), real employer-partner reporting.

**Success criteria.** (1) every CSV row parsed, scores as float, every 10th user flagged; (2) DB with normalised tables and parameterised queries; (3) no crash on bad input - invalid rows logged; (4) events appended to `application_activity.log`; (5) setup reproducible from `linux_operations.log` alone; (6) report, 8-10 slide deck and demo delivered.

**Risks.** Bad or missing CSV values (mitigated by row validation); permissions too open (group-based access, mode 750/640); package manager unavailable offline (log the real result, fall back to Python's built-in sqlite3 module).

**Assumptions.** The starter CSV in the repo is the data set (it holds 45 learners; the brief mentions 200 - the code handles any size). The discovery-call MP3 could not be transcribed in this environment, so the written kickoff deck and brief were used as the source of client expectations.
