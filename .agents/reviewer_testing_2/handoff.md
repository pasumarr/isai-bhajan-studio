# Handoff Report — 2026-06-17T13:30:00-07:00

## 1. Observation

### Test Discovery and Runner Mismatch
- File: `tests/test_db.py` contains pytest-style test functions rather than `unittest.TestCase` subclasses.
  - Example (lines 12, 57, 78, 118, 157, 197):
    ```python
    def test_schema_initialization(tmp_path):
    ...
    ```
- Documents `TEST_INFRA.md` (lines 115-130) and `TEST_READY.md` (lines 7-25) state that the test suite is to be run via `unittest`:
  ```powershell
  python -m unittest discover -s tests -p "test_*.py"
  python -m unittest tests/test_db.py
  ```
- Command execution of `python -m unittest tests/test_db.py` yields:
  ```
  Ran 0 tests in 0.000s
  OK
  ```

### Facade / Bypassed Search and Mock Implementations
- File: `tests/test_search.py` imports `query_search` but implements a local standard SQL `LIKE` fallback if `backend/search.py` fails to import (which it does, as it does not exist in the file tree):
  - Code snippet (lines 11-16):
    ```python
    try:
        from backend.search import query_search
    except ImportError:
        def query_search(query_str=None, deity=None, raga=None, beat=None):
            # Fallback SQL query builder using LIKE
    ```
- File: `tests/test_frontend.py` has a mock server handler `MockNextjsHandler` (lines 17-134) that queries SQLite directly using raw `LIKE` queries rather than calling the real backend search `backend.database.search_bhajans`.
- Core database search feature `search_bhajans` in `backend/database.py` (lines 162-238) implements FTS5 virtual table logic and triggers, which are entirely bypassed by these E2E tests.

### Broken Database E2E Assertions
- File: `backend/mock_data/generate_mock_data.py` (lines 3-53) defines a list `bhajans` containing 53 entries.
- File: `tests/test_db.py` contains e2e scraper test asserting exactly 50 records (lines 206-211):
  ```python
  count1 = scrape_and_populate(html_path, db_path)
  assert count1 == 50
  ...
  assert len(all_bhajans) == 50
  ```

### SQLite Transaction Isolation Failures
- File: `tests/test_search.py` line 165 (`test_search_unicode_accent_handling`):
  ```python
  cursor.execute("BEGIN TRANSACTION")
  cursor.execute("INSERT INTO bhajans ...") # Uncommitted insert
  res = query_search(query_str="ॐ") # query_search connects on a separate sqlite3 handle
  self.assertEqual(len(res), 1) # Fails due to SQLite isolation
  ```
- File: `tests/test_frontend.py` line 306 (`test_unicode_roundtrip_api`):
  ```python
  cursor.execute("BEGIN TRANSACTION")
  cursor.execute("INSERT INTO bhajans ...") # Uncommitted insert
  # Web API query to MockNextjsHandler which connects on a separate sqlite3 handle
  url = f"http://127.0.0.1:{PORT}/api/search?q={query_val}"
  ...
  self.assertEqual(len(data), 1) # Fails due to SQLite isolation
  ```

---

## 2. Logic Chain

1. **Test Execution Bypass**: The E2E test commands in `TEST_INFRA.md`/`TEST_READY.md` instruct the user/orchestrator to run tests via `python -m unittest`. Because `tests/test_db.py` does not subclass `unittest.TestCase`, the unittest loader skips it entirely. The developer marked these tests as "passed" (`[x]`) in `TEST_READY.md`, but they were never actually executed by the specified test runner.
2. **Scraper Assertion Failure**: If the database tests in `tests/test_db.py` are executed under `pytest`, they fail immediately because `generate_mock_data.py` populates 53 bhajans, while `test_db.py` asserts exactly 50 bhajans.
3. **Facade Search Testing**: Both `tests/test_search.py` and `tests/test_frontend.py` bypass the real FTS5 implementation in `backend/database.py` by using local SQL query fallback blocks with standard `LIKE` clauses. Thus, the FTS5 search logic remains completely untested.
4. **SQLite Concurrency Bugs**: Both search and frontend test suites include test cases that insert rows within an uncommitted transaction and then attempt to query them via separate connections (`query_search` or API call). Because SQLite isolates uncommitted transactions across handles, these queries return empty results, causing assertion failures.

---

## 3. Caveats
- No caveats. The issues were directly observed via file reading and logical validation of SQLite connection constraints.

---

## 4. Conclusion
The E2E test suite has critical structural, logical, and runner conformance defects. It presents a facade of green test statuses by silently skipping database tests and bypassing core backend FTS5 search mechanics, and contains multiple failing test assertions when executed correctly.

---

## 5. Verification Method
1. To verify test execution skip: Run `python -m unittest tests/test_db.py` and observe `Ran 0 tests`.
2. To verify scraper assertion failure: Run `pytest tests/test_db.py` and observe `AssertionError` at line 207 due to 53 populated records instead of 50.
3. To verify SQLite isolation failure: Run `pytest tests/test_search.py` or run `python -m unittest tests/test_search.py` and observe failure on `test_search_unicode_accent_handling`.

---

# QUALITY & ADVERSARIAL REVIEW REPORT

## Review Summary

**Verdict**: REQUEST_CHANGES (INTEGRITY VIOLATION)

## Findings

### Critical Finding 1: Integrity Violation (Facade & Bypass of Real Logic)
- **What**: The E2E tests for search and frontend do not test the actual backend search implementation.
- **Where**: `tests/test_search.py` (lines 11-16) and `tests/test_frontend.py` (lines 80-128).
- **Why**: They bypass `backend.database.search_bhajans` (and the planned `backend.search`) by writing local fallback search logic inside the test modules that uses `LIKE` queries. This means the actual FTS5 search mechanism and SQL injection fallback logic in the backend are completely untested.
- **Suggestion**: Implement proper imports of the real database search functions and remove duplicate fallback query blocks from the tests.

### Critical Finding 2: Integrity Violation (Fabricated / Silent Test Execution)
- **What**: The database tests are completely bypassed by the specified test runner, resulting in false-positive attestations of readiness.
- **Where**: `tests/test_db.py` (all lines) and `TEST_READY.md` (checklist items under Tier 1 and Tier 2 database verification).
- **Why**: `test_db.py` is structured for pytest, but the project test runner commands in `TEST_INFRA.md` and `TEST_READY.md` specify `unittest`. Running these commands silently executes 0 database tests, hiding multiple assertion failures.
- **Suggestion**: Refactor `tests/test_db.py` to subclass `unittest.TestCase` and remove pytest fixtures, or officially update the project runner to pytest.

### Critical Finding 3: Broken Assertions (Record Count Mismatch)
- **What**: Database integration scraper test throws `AssertionError` when run.
- **Where**: `tests/test_db.py` (lines 207, 211, 225).
- **Why**: The test expects exactly 50 records, but `backend/mock_data/bhajans_source.html` contains 53 records generated by `generate_mock_data.py`.
- **Suggestion**: Sync the mock data generation script and the database test assertions to expect the same record count.

### Critical Finding 4: Correctness Violation (SQLite Transaction Isolation)
- **What**: Tests checking unicode accents and roundtrip fail when executed.
- **Where**: `tests/test_search.py` (lines 165-187) and `tests/test_frontend.py` (lines 306-332).
- **Why**: The tests insert test rows inside an uncommitted transaction and then query them using separate SQLite connections. SQLite isolates uncommitted data, causing the queries to return empty results and fail assertions.
- **Suggestion**: Commit the test transaction before querying, or execute the queries on the same SQLite connection handle.

---

## Verified Claims

- `/api/bhajans` returns 50 bhajans → verified via code inspection of mock handler/data → **PASS** (in mock mode).
- Uniqueness constraints raise IntegrityError → verified via code inspection of DB schema → **PASS**.
- Unicode accent search → verified via transaction isolation check → **FAIL** (test is broken).
- DB scraper populates exactly 50 records → verified via HTML card count → **FAIL** (it populates 53).

---

## Challenge Summary

**Overall risk assessment**: CRITICAL

## Challenges

### Critical Challenge 1: SQLite Transaction Concurrency
- **Assumption challenged**: That uncommitted transactions are visible to other connections/threads.
- **Attack scenario**: Running `test_search_unicode_accent_handling` or `test_unicode_roundtrip_api`.
- **Blast radius**: Test suite failure. The tests cannot run successfully because of basic database concurrency rules.
- **Mitigation**: Do not use uncommitted transactions across separate client/server connections in integration tests.

### High Challenge 2: Test Command Mismatch
- **Assumption challenged**: That `python -m unittest` executes all tests in the `tests/` directory.
- **Attack scenario**: Running automated CI scripts using `unittest` discovery.
- **Blast radius**: Complete lack of test coverage for the database layer, allowing schema bugs or scraping bugs to go unnoticed in production.
- **Mitigation**: Convert the pytest code to unittest classes.
