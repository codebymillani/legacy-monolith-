"""
Infrastructure layer: CSV reading.

Responsible only for reading the input file and turning each row into a
domain.enrollment.EnrollmentRequest. Contains no business rules and no
knowledge of the database, email, or HTML.
"""

import csv

from domain.enrollment import EnrollmentRequest


def read_enrollment_requests(csv_path: str) -> list[EnrollmentRequest]:
    """
    Read the enrollment CSV and return a list of EnrollmentRequest objects.

    Column order matches the legacy script exactly:
    student_id, student_name, course_code, credits, has_prereqs, override_code
    """
    requests = []
    with open(csv_path, "r") as file:
        reader = csv.reader(file)
        next(reader)  # skip header, same as legacy

        for row in reader:
            requests.append(
                EnrollmentRequest(
                    student_id=row[0],
                    student_name=row[1],
                    course_code=row[2],
                    credits=int(row[3]),
                    has_prereqs=row[4].strip().lower() == "true",
                    override_code=row[5],
                )
            )
    return requests
