"""
Infrastructure layer: SQLite database access.

Responsible only for connecting to SQLite, creating the table, reading
current enrolled credits, inserting enrollment records, and closing the
connection. Contains no enrollment decision logic and generates no HTML.
"""

import sqlite3


class EnrollmentDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS enrollments
               (student_id TEXT, student_name TEXT, course_code TEXT,
                credits INTEGER, status TEXT)"""
        )

    def get_current_enrolled_credits(self, student_id: str) -> int:
        """
        Sum of credits for courses this student is currently ENROLLED in.

        Preserves the legacy query exactly, including that it only matches
        the literal status 'ENROLLED' — NOT 'ENROLLED (OVERRIDE)'. This
        means override-enrolled credits do not count toward a student's
        running total in later rows. That is a quirk of the original SQL,
        not a bug we are fixing here.
        """
        self.cursor.execute(
            "SELECT SUM(credits) FROM enrollments WHERE student_id=? AND status='ENROLLED'",
            (student_id,),
        )
        result = self.cursor.fetchone()[0]
        return result if result else 0

    def insert_enrollment(self, student_id: str, student_name: str,
                           course_code: str, credits: int, status: str):
        self.cursor.execute(
            "INSERT INTO enrollments VALUES (?, ?, ?, ?, ?)",
            (student_id, student_name, course_code, credits, status),
        )

    def commit_and_close(self):
        self.conn.commit()
        self.conn.close()
