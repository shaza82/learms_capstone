"""OOP models for LEARMS (Learner Assessment & Resource Management System).

Defines a base ``User`` class and two subclasses, ``Learner`` and
``Instructor``.  Both subclasses override ``display_profile`` so that the
caller can treat every user the same way (polymorphism) while each type
prints the information that matters for it.
"""


class User:
    """Base class for every person known to LEARMS."""

    def __init__(self, name, email, role):
        """Store the common attributes.

        Args:
            name: Full name of the user.
            email: Contact e-mail address.
            role: Human readable role, e.g. ``"Learner"``.
        """
        self.name = name
        self.email = email
        self.role = role

    def display_profile(self):
        """Return a one-line profile; subclasses override this method."""
        return f"[{self.role}] {self.name} <{self.email}>"


class Learner(User):
    """A learner enrolled in a cohort, with an assessment score."""

    def __init__(self, learner_id, name, cohort_name, assessment_score,
                 enrollment_status, audit_flag=False):
        """Create a learner.

        Args:
            learner_id: Unique id such as ``SP-L-1001``.
            name: Full name.
            cohort_name: Name of the cohort the learner belongs to.
            assessment_score: Score; always converted to ``float``.
            enrollment_status: Active, Graduated or Dropped.
            audit_flag: True when picked for the random quality audit.
        """
        email = f"{learner_id.lower()}@learners.sprints.example"
        super().__init__(name, email, "Learner")
        self.learner_id = learner_id
        self.cohort_name = cohort_name
        self.assessment_score = float(assessment_score)  # explicit float cast
        self.enrollment_status = enrollment_status
        self.audit_flag = audit_flag

    def display_profile(self):
        """Override: show the float score and the audit status."""
        audit = "AUDIT" if self.audit_flag else "no audit"
        return (f"[Learner] {self.learner_id} {self.name} | {self.cohort_name} | "
                f"score={self.assessment_score:.2f} | {self.enrollment_status} | {audit}")


class Instructor(User):
    """An instructor who teaches one or more cohorts."""

    def __init__(self, name, email, cohorts=None):
        """Create an instructor.

        Args:
            name: Full name.
            email: Contact e-mail address.
            cohorts: List of cohort names the instructor teaches.
        """
        super().__init__(name, email, "Instructor")
        self.cohorts = list(cohorts or [])

    def display_profile(self):
        """Override: show the cohorts taught by this instructor."""
        return f"[Instructor] {self.name} <{self.email}> | teaches: {', '.join(self.cohorts)}"
