## 2026-06-17T20:01:47Z
You are the teamwork_preview_worker for the ISai Bhajan Studio E2E Testing Track (Generation 2).
Your working directory is: C:\Users\saipa\isai-bhajan-studio\.agents\worker_testing_2. Write all your coordination files (progress.md, handoff.md) here.
Your mission is to remediate the E2E Test Suite codebase, resolving the Forensic Audit Integrity Violation and the defects reported by the reviewers and challengers.

### Specific Defects to Remediate:
1. **Unrunnable Database Tests (Audit Failure)**:
   Refactor `tests/test_db.py` to subclass `unittest.TestCase` and remove any dependencies on `pytest` or `tmp_path`. Use `tempfile.TemporaryDirectory` and `assertRaisesRegex` (or similar standard library structures).
   Ensure the test suite can be run and discovered using:
   `python -m unittest discover -s tests -p "test_*.py"`

2. **SQLite Transaction Isolation Bugs (Correctness)**:
   In `tests/test_search.py` and `tests/test_frontend.py`, some tests (like `test_unicode_accent_handling` or other write tests) open a connection, run `BEGIN TRANSACTION`, insert data, and then call `query_search` or an API endpoint that opens a separate sqlite3 connection. Because SQLite isolates uncommitted transactions, the separate connection cannot see the inserted data, causing the tests to fail.
   Remedy this by:
   - Writing the data, executing the assertions, and then deleting the inserted data in a `try...finally` block.
   - Or utilizing a dedicated temporary database file for that specific test, initializing it, and deleting it on cleanup.
   - Do NOT use uncommitted transactions when separate connection handles are used to query that data.

3. **Bypassing Real Search Implementation (Design Defect)**:
   Ensure that search tests in `tests/test_search.py` and search endpoints in the mock Next.js server (`tests/test_frontend.py`) route queries through the real `search_bhajans` function in `backend/database.py` (which uses the FTS5 virtual table and fallback standard LIKE query), rather than duplicating/mocking the SQL search queries inline. This ensures the backend FTS5 queries are actually tested.

4. **Mock Database Schema Completeness**:
   Ensure `tests/mock_data.py` (or the database initializer) creates a SQLite database with the EXACT schema defined in `backend/database.py`, including the virtual tables (`bhajans_fts`), sync triggers (`bhajans_ai`, `bhajans_ad`, `bhajans_au`), columns (`id`, `title`, `deity`, `raga`, `beat`, `lyrics`, `audio_url`, `created_at`), and indices (`idx_bhajans_deity`, `idx_bhajans_raga`, `idx_bhajans_beat`).

5. **Test Assertions and Counts Consistency**:
   Verify that all assertions match. The mock database must store exactly 50 bhajans, and all scraper/database volume tests must assert exactly 50 records.

6. **Mock Server Port Conflict and Daemon Clean Up**:
   Ensure the mock server in `tests/test_frontend.py` starts properly, handles ports safely, and shuts down cleanly after test run execution.

Verify that the command:
`python -m unittest discover -s tests -p "test_*.py"`
runs and executes all test cases (including database, search, and frontend tests) successfully with 100% pass rate.
Update `TEST_INFRA.md` and `TEST_READY.md` in the project root to reflect these changes.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please report back when done.
