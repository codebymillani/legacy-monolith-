"""
Domain layer: enrollment business rules.

This module contains ONLY decision logic. It has no knowledge of SQLite,
CSV files, HTML, or email. It receives plain data (a student's requested
course info + their current enrolled credit total) and returns a decision.

Extracted from the "5. BUSINESS LOGIC" section of the legacy
legacy_enrollment_processor.py god-loop, with behavior preserved exactly,
including the exact status strings.
"""

from dataclasses import dataclass

MAX_CREDITS = 18  # same hardcoded limit as the legacy script

# Status strings are preserved character-for-character from the legacy
# implementation because other layers (DB, HTML) match against them
# (e.g. presentation checks for the substring "FAILED").
STATUS_ENROLLED = "ENROLLED"
STATUS_ENROLLED_OVERRIDE = "ENROLLED (OVERRIDE)"
STATUS_FAILED_CREDIT_LIMIT = "FAILED - CREDIT LIMIT EXCEEDED"
STATUS_FAILED_MISSING_PREREQS = "FAILED - MISSING PREREQS"

DEAN_OVERRIDE_CODE = "DEAN_APPROVED"


@dataclass
class EnrollmentRequest:
    """One row of enrollment input, already parsed from the CSV."""
    student_id: str
    student_name: str
    course_code: str
    credits: int
    has_prereqs: bool
    override_code: str


@dataclass
class EnrollmentDecision:
    """Result of evaluating an EnrollmentRequest."""
    status: str

    @property
    def failed(self) -> bool:
        return "FAILED" in self.status


def evaluate_enrollment(request: EnrollmentRequest, current_credits: int) -> EnrollmentDecision:
    """
    Decide whether a student can enroll in a course.

    This mirrors the legacy if/else chain exactly:
      1. Credit limit is checked first, before anything else.
      2. If prereqs are satisfied, the student is enrolled.
      3. If prereqs are missing, a Dean override code enrolls the student
         with an "(OVERRIDE)" status.
      4. Otherwise, enrollment fails for missing prerequisites.
    """
    if current_credits + request.credits > MAX_CREDITS:
        return EnrollmentDecision(status=STATUS_FAILED_CREDIT_LIMIT)

    if request.has_prereqs:
        return EnrollmentDecision(status=STATUS_ENROLLED)

    if request.override_code == DEAN_OVERRIDE_CODE:
        return EnrollmentDecision(status=STATUS_ENROLLED_OVERRIDE)

    return EnrollmentDecision(status=STATUS_FAILED_MISSING_PREREQS)
