"""
Presentation layer: HTML report generation.

Responsible only for building and writing the enrollment report. Takes
plain (student_id, student_name, course_code, status) rows and has no
knowledge of the database or business rules.
"""

from datetime import datetime


class HtmlReportBuilder:
    def __init__(self):
        self._rows_html = ""

    def add_row(self, student_id: str, student_name: str, course_code: str, status: str):
        """Add one table row. Failed rows are styled red, same as legacy."""
        if "FAILED" in status:
            self._rows_html += (
                f"<tr style='color:red;'><td>{student_id}</td><td>{student_name}</td>"
                f"<td>{course_code}</td><td>{status}</td></tr>"
            )
        else:
            self._rows_html += (
                f"<tr><td>{student_id}</td><td>{student_name}</td>"
                f"<td>{course_code}</td><td>{status}</td></tr>"
            )

    def build(self) -> str:
        html = f"<html><body><h1>Enrollment Run: {datetime.now()}</h1><table border='1'>"
        html += "<tr><th>ID</th><th>Name</th><th>Course</th><th>Status</th></tr>"
        html += self._rows_html
        html += "</table></body></html>"
        return html

    def write(self, output_path: str):
        with open(output_path, "w") as report_file:
            report_file.write(self.build())
