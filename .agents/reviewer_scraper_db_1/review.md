## Review Summary

**Verdict**: REQUEST_CHANGES

This review covers the Scraper and Database implementation for Milestone 2.
The core database schema is clean and correctly implements the uniqueness constraint, FTS5 virtual table, and triggers for synchronization. The duplicate protection is robustly handled via SQLite UPSERT (`ON CONFLICT(title, deity) DO UPDATE`).
However, two major findings must be addressed to ensure robustness, compatibility, and correctness under all runtime environments.

## Findings

### [Major] Finding 1: Case-Sensitive Search Filters in Database Logic

- **What**: The search filtering logic for metadata fields (`deity`, `raga`, `beat`) in `backend/database.py` is case-sensitive.
- **Where**: `backend/database.py`, lines 187–198 and 216–227 inside `search_bhajans`.
- **Why**: SQLite's `=` comparison operator is case-sensitive by default unless a `COLLATE NOCASE` clause is specified. Currently, if a user filters by `"ganesha"`, it will fail to match a database record stored with `"Ganesha"`. This violates the expectations of the other test suites (`tests/test_search.py` and `tests/test_frontend.py`), which manually append `COLLATE NOCASE` in their mock query implementations.
- **Suggestion**: Update the filter logic in `search_bhajans` to use `COLLATE NOCASE` or define columns with `COLLATE NOCASE` in the database schema. E.g.:
  ```python
  if deity and deity != "All":
      sql += " AND b.deity = ? COLLATE NOCASE"
      params.append(deity)
  ```

### [Major] Finding 2: Fragile Fallback HTML Parser Logic

- **What**: The custom `FallbackBhajanParser` closing condition is fragile and contains a redundant condition.
- **Where**: `backend/scraper.py`, lines 131–149.
- **Why**: 
  1. The code `elif tag == "div" and tag == "div" and not self.in_lyrics:` has a redundant `tag == "div"` check.
  2. The parser assumes that the end tag of any `div` when `not self.in_lyrics` must close the `bhajan-card` itself. If the HTML page is modified to contain any nested wrapper `div`s (e.g. for card headers or bootstrap styling), this parser will close the card prematurely, leading to incomplete or lost bhajan entries.
- **Suggestion**: Use a proper element stack or element attribute tracker to verify that the tag being closed corresponds directly to the `bhajan-card` container. E.g., track the nesting level of parsed tags or verify card completion using specific tag/class markers.

### [Minor] Finding 3: Missing database schema constraints in mock seed generator

- **What**: `tests/mock_data.py` defines a mock database table schema that lacks FTS5 virtual tables, indexing, triggers, and `created_at` timestamp.
- **Where**: `tests/mock_data.py`, lines 43–54.
- **Why**: If a test references `tests/mock_data.py`'s `initialize_db` to prepare a mock database, it creates a database that is structurally mismatched with the database created by `backend/database.py`'s `init_db`.
- **Suggestion**: Update `initialize_db` in `tests/mock_data.py` to match the exact schema created by `init_db(db_path)` or simply reuse `backend.database.init_db(db_path)`.

## Verified Claims

- **Database schema initialization** → verified via inspection of `init_db` in `backend/database.py` and `test_schema_initialization` in `tests/test_db.py` → **PASS**
- **Duplicate protection & SQLite UPSERT** → verified via inspection of `save_bhajan` in `backend/database.py` and `test_duplicate_protection_and_upsert` in `tests/test_db.py` → **PASS**
- **FTS5 Virtual table synchronization via triggers** → verified via inspection of triggers `bhajans_ai`, `bhajans_ad`, `bhajans_au` and `test_search_fts_and_filters` in `tests/test_db.py` → **PASS**
- **E2E HTML scraping of exactly 50 bhajans** → verified via checking `backend/mock_data/bhajans_source.html` has exactly 50 cards and `test_e2e_integration_and_idempotency` asserts the parsed count → **PASS**

## Coverage Gaps

- **Case-insensitive search tests in `tests/test_db.py`** — risk level: low — recommendation: add test cases verifying case-insensitivity of filters inside `tests/test_db.py` to catch regressions in `search_bhajans`.
- **FTS5 syntax errors handling tests in `tests/test_db.py`** — risk level: low — recommendation: verify that the FTS5 query parser operational error fallback to LIKE queries behaves correctly under tests.

## Unverified Items

- **Actual test suite execution output** — reason not verified: `run_command` timed out waiting for user approval.
