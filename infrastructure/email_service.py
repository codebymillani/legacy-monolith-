"""
Infrastructure layer: simulated email notifications.

The legacy script never sends real email; it prints a line pretending to.
This module preserves that exact simulated behavior (same print format)
so it's a drop-in extraction, not a real email integration.
"""

from domain.enrollment import (
    STATUS_ENROLLED,
    STATUS_ENROLLED_OVERRIDE,
    STATUS_FAILED_CREDIT_LIMIT,
    STATUS_FAILED_MISSING_PREREQS,
)


def send_enrollment_email(student_name: str, course_code: str, status: str):
    """Print a simulated email matching the legacy wording for each status."""
    if status == STATUS_FAILED_CREDIT_LIMIT:
        print(f"SENDING EMAIL TO: {student_name} -> Registration failed for {course_code} (Credit limit).")
    elif status == STATUS_ENROLLED:
        print(f"SENDING EMAIL TO: {student_name} -> Successfully enrolled in {course_code}.")
    elif status == STATUS_ENROLLED_OVERRIDE:
        print(f"SENDING EMAIL TO: {student_name} -> Enrolled in {course_code} with Dean override.")
    elif status == STATUS_FAILED_MISSING_PREREQS:
        print(f"SENDING EMAIL TO: {student_name} -> Registration failed for {course_code} (Missing Prereqs).")
