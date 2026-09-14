# Architecture Analysis: Legacy Enrollment Processor

## 1. Execution Flow of the Legacy Program

`legacy_enrollment_processor.py` runs everything inside a single function,
`run_legacy_enrollment()`, in this order:

1. **Database setup.** Opens (or creates) `university_enrollment.db` and
   runs `CREATE TABLE IF NOT EXISTS enrollments` right at startup.
2. **HTML report setup.** Immediately starts building an HTML string
   (`html_report = f"<html>..."`) before a single row of data has even
   been read.
3. **CSV existence check.** If `students.csv` is missing, it prints an
   error and returns — no exception, no partial cleanup of the DB
   connection it already opened.
4. **CSV read + god loop.** Opens the CSV, skips the header, and for
   *every row* does all of the following in one iteration:
   - Parses the row into `student_id`, `student_name`, `course_code`,
     `credits`, `has_prereqs`, `override_code`.
   - Queries SQLite for the student's current `SUM(credits)` where
     `status='ENROLLED'`.
   - Runs the enrollment decision (credit limit → prereqs → Dean
     override → failure).
   - Prints a "simulated email" line describing the outcome.
   - Inserts the result into the `enrollments` table.
   - Appends a `<tr>` to the HTML string, red if the status contains
     `"FAILED"`.
5. **Teardown.** Commits and closes the DB connection, closes the HTML
   `<table>`/`<body>`/`<html>` tags, and writes `enrollment_report.html`.

## 2. Identified Code Smells (with evidence)

### Smell 1 — God Function / mixed responsibilities
`run_legacy_enrollment()` is one function that does database setup, HTML
setup, file I/O, business-rule evaluation, "email" side effects, database
writes, and HTML string-building — all in one 60-line block with no
sub-functions. There is no way to test the credit-limit rule, for
example, without also touching SQLite, the CSV file, and stdout.

### Smell 2 — Global / hardcoded configuration
```python
DB_PATH = "university_enrollment.db"
CSV_PATH = "students.csv"
MAX_CREDITS = 18
```
These are module-level constants baked into the file. There is no way to
point the same logic at a different database, a different CSV, or a
different credit cap (e.g. for a different program) without editing the
source file itself.

### Smell 3 — Business logic coupled directly to the database
The credit-limit check is not a pure calculation — it is a live SQL
query run *inside* the decision logic:
```python
cursor.execute("SELECT SUM(credits) FROM enrollments WHERE student_id=? AND status='ENROLLED'", (student_id,))
result = cursor.fetchone()[0]
current_credits = result if result else 0
if current_credits + credits > MAX_CREDITS:
```
This means the enrollment rule (a domain concept) cannot be evaluated,
reasoned about, or unit-tested without a live SQLite connection.

### Smell 4 — Hidden side effects inside business logic
Each branch of the if/else chain both decides the outcome *and* performs
a `print()` that simulates sending an email:
```python
status = "FAILED - CREDIT LIMIT EXCEEDED"
print(f"SENDING EMAIL TO: {student_name} -> Registration failed for {course_code} (Credit limit).")
```
A reader (or a unit test) evaluating "what status does this student
get?" has no way to do so without also triggering the "email" side
effect — the two are inseparable in the current code.

### Smell 5 — Presentation logic mixed into the processing loop
HTML string concatenation happens in the same loop, using the same
`status` variable the database just consumed:
```python
if "FAILED" in status:
    html_report += f"<tr style='color:red;'>..."
```
Changing the report's look (e.g. switching to a different HTML
structure or output format) requires editing the same function that
also parses CSV rows and talks to SQLite.

### Smell 6 — Fragile CSV / input handling
```python
if not os.path.exists(CSV_PATH):
    print("ERROR: CSV file not found!")
    return
```
A missing file is handled with a `print` + silent `return` rather than
a raised, catchable error, and a malformed row (wrong column count, a
non-integer `credits` value) would raise an uncaught `IndexError` or
`ValueError` deep inside the loop, after the DB table has already been
created and mid-way through writing other rows.

## 3. Clean Architecture Blueprint

| Layer | Responsibility | Files |
|---|---|---|
| **Domain** | Enrollment decision rules only — credit limit, prereqs, Dean override. No I/O. | `domain/enrollment.py` |
| **Infrastructure** | CSV reading, SQLite access, simulated email. All I/O, no decisions. | `infrastructure/csv_reader.py`, `infrastructure/db_manager.py`, `infrastructure/email_service.py` |
| **Presentation** | HTML report building/writing only. | `presentation/html_report.py` |
| **Orchestrator** | Wires the layers together in the original order. No business rules. | `main.py` |

## 4. Filename Discrepancy: `enrollment_report.html` vs. `report.html`

The assignment prompt's sample directory tree does not list a report
output filename explicitly, but the supplied legacy code writes
`enrollment_report.html`. To preserve external behavior exactly (as the
assignment requires), the refactored `presentation/html_report.py` and
`main.py` also write to `enrollment_report.html`, not `report.html`.
No other filename change was made.

## 5. Preserved Behavior (verified — see below)

- Max credit limit: `18`, checked as `current_credits + new_credits > 18`.
- Current-credit lookup only sums rows where `status == 'ENROLLED'`
  (literally — **not** `'ENROLLED (OVERRIDE)'`). This is a real quirk of
  the original SQL: a student's Dean-override enrollments do not count
  toward their running credit total in later rows. This was preserved
  as-is, since the assignment explicitly forbids "fixing" existing
  business-rule behavior.
- Exact status strings: `"ENROLLED"`, `"ENROLLED (OVERRIDE)"`,
  `"FAILED - CREDIT LIMIT EXCEEDED"`, `"FAILED - MISSING PREREQS"`.
- Exact simulated email wording for all four outcomes.
- HTML structure, `<table border='1'>`, header row, and
  `style='color:red;'` on any row whose status contains `"FAILED"`.

## 6. Behavioral Verification Results

The legacy script and the refactored `main.py` were both run against the
same `students.csv`. Results:

- **Console ("email") output:** identical, line for line.
- **SQLite rows** (`student_id, student_name, course_code, credits,
  status`): identical, row for row, in the same order.
- **HTML report:** identical except for the timestamp in the `<h1>`
  (both call `datetime.now()` at write time, so an exact match is not
  expected there — everything else, including per-row styling, matches
  exactly).

No discrepancies were found between the legacy and refactored outputs.
