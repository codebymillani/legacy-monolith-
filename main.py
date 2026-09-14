"""
Application entry point.

Wires together the CSV reader, database manager, domain enrollment logic,
email service, and HTML report builder. Contains no business rules itself
-- it only coordinates the other layers, in the same order the legacy
god-loop performed these steps.
"""

from infrastructure.csv_reader import read_enrollment_requests
from infrastructure.db_manager import EnrollmentDatabase
from infrastructure.email_service import send_enrollment_email
from presentation.html_report import HtmlReportBuilder
from domain.enrollment import evaluate_enrollment

# Same hardcoded paths as the legacy script.
DB_PATH = "university_enrollment.db"
CSV_PATH = "students.csv"
REPORT_PATH = "enrollment_report.html"


def run_enrollment():
    import os
    if not os.path.exists(CSV_PATH):
        print("ERROR: CSV file not found!")
        return

    requests = read_enrollment_requests(CSV_PATH)

    db = EnrollmentDatabase(DB_PATH)
    report = HtmlReportBuilder()

    for request in requests:
        current_credits = db.get_current_enrolled_credits(request.student_id)
        decision = evaluate_enrollment(request, current_credits)

        send_enrollment_email(request.student_name, request.course_code, decision.status)

        db.insert_enrollment(
            request.student_id,
            request.student_name,
            request.course_code,
            request.credits,
            decision.status,
        )

        report.add_row(request.student_id, request.student_name, request.course_code, decision.status)

    db.commit_and_close()
    report.write(REPORT_PATH)

    print("Enrollment processing complete. Report generated.")


if __name__ == "__main__":
    run_enrollment()
