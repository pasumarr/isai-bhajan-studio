You are the teamwork_preview_worker for the ISai Bhajan Studio E2E Testing Track.
Your working directory is: C:\Users\saipa\isai-bhajan-studio\.agents\worker_testing_1. Write all coordination files (progress.md, handoff.md) in this folder.
Your mission is to implement the E2E test suite (Tiers 1-4) in the workspace and verify that the test runner compiles and runs successfully.

### Key Instructions:
1. Initialize the `tests/` directory in the project root if it does not exist.
2. Implement a `tests/mock_data.py` file containing a static, clean list of exactly 50 mock bhajans with fields: `title`, `deity`, `raga`, `beat`, `lyrics`, `audio_url`. The data should be deterministically varied across deities (e.g., Ganesha, Shiva, Rama, Krishna, Devi), ragas (e.g., Yaman, Bhairavi, Darbari, Kalyan, Bhupali), and beats (e.g., Adi, Keharwa, Rupak, Dadra, Roopak).
3. Implement `tests/test_db.py` to cover:
   - Database connection and table verification.
   - Asserting that exactly 50 bhajans are stored in the database.
   - Asserting fields are not null or empty.
   - Uniqueness constraint verification (raises IntegrityError on duplicate title/deity).
   - Special character/Unicode encoding support (like "ॐ" and "Śiva").
4. Implement `tests/test_search.py` to cover:
   - Basic search queries by deity, raga, beat, and full-text lyrics search.
   - Case insensitivity.
   - Escaping/Sanitization to prevent SQL Injection (queries containing "'" or "OR 1=1" do not crash/return unauthorized data).
5. Implement `tests/test_frontend.py` to cover:
   - Index route loads successfully and returns HTTP 200 OK.
   - APIs `/api/bhajans` and `/api/search` return correct JSON payloads and status.
   - Background mock web server using standard library `http.server` running in a daemon thread on port 3000 if the port is not already occupied.
6. Support a `TEST_MODE` environment variable toggle in all test scripts:
   - If `TEST_MODE=mock` (or not set), they utilize the in-memory SQLite database preloaded with the 50 mock bhajans and spin up the Python background thread HTTP server on port 3000.
   - If `TEST_MODE=real`, they query the real production database file at `backend/bhajans.db` and hit the live web server on port 3000 without starting a mock server.
7. Ensure test coverage spans Tiers 1-4:
   - Tier 1: Happy paths (>=5 tests per requirement/feature).
   - Tier 2: Boundary/Edge cases (>=5 tests per requirement).
   - Tier 3: Cross-Feature combination tests (DB-to-API data integrity, Unicode roundtrip, search request parameter mapping, DB lock handling).
   - Tier 4: Real-World Workloads (5 scenario-based tests: user search refinement journey, first-time setup verification, high density concurrent search requests, scraper partial recovery & persistence, and system degradation/database offline resiliency).
8. Write `TEST_INFRA.md` in the project root containing the test suite architecture, layout, and instructions for running the tests.
9. Write `TEST_READY.md` in the project root containing a checklist of all features/tiers covered and the test runner commands.
10. Run the test suite using `python -m unittest discover -s tests -p "test_*.py"` (or `pytest` if available) and verify that 100% of the tests run and pass. Document the output of the tests in your handoff report.

MANDATORY INTEGRITY WARNING — include this verbatim in the Worker's dispatch prompt:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please report back with your progress and handoff files when done.
