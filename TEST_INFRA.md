# TEST_INFRA.md: E2E Test Suite Architecture & Design

This document describes the design, architecture, performance budgets, and execution procedures for the E2E Test Suite (Tiers 1-4) implemented for the **ISai Bhajan Studio** project.

---

## 1. Directory Structure and Layout

The test suite is structured within the project as follows:

```
C:\Users\saipa\isai-bhajan-studio\
├── tests/
│   ├── __init__.py           # Package marker
│   ├── mock_data.py          # 50 deterministic mock bhajans & database helper
│   ├── test_db.py            # SQLite database schema, volume, & constraints tests
│   ├── test_search.py        # Advanced search filters & SQL injection tests
│   └── test_frontend.py      # HTTP server route & API payload tests
└── TEST_INFRA.md             # This architecture documentation file
```

---

## 2. Test Suite Architecture

The test suite implements a decoupled, dual-mode testing architecture to test features end-to-end regardless of deployment stage.

### Dual Execution Modes (`TEST_MODE`)

All test modules support the `TEST_MODE` environment variable toggle:

1. **Mock Mode (`TEST_MODE=mock` or unset)**:
   - **Database**: Creates and queries a temporary SQLite database (`tests/mock_bhajans.db`) initialized and preloaded with exactly 50 mock bhajans from `tests/mock_data.py`.
   - **Frontend**: Spins up a background `http.server.HTTPServer` in a daemon thread on port 3000 to mimic Next.js route mapping and JSON API endpoints.
   - **Network**: Operates entirely offline using standard library components (complying with `CODE_ONLY` network restriction).

2. **Real Mode (`TEST_MODE=real`)**:
   - **Database**: Queries the real production database file located at `backend/bhajans.db`.
   - **Frontend**: Bypasses background mock server creation and targets the live Next.js web application running on port 3000.
   - **Writes**: Employs auto-rollback transaction protocols to ensure production/staging data remains pristine.

---

## 3. Detailed Coverage Breakdown (Tiers 1-4)

### Tier 1: Feature Coverage (Happy Paths)
Each functional requirement is tested by 5+ happy-path test cases:
* **Database (`test_db.py`)**:
  - `test_db_connection_established`: Confirms connection works.
  - `test_db_table_exists`: Confirms `bhajans` table is present.
  - `test_db_columns_match`: Confirms table structure contains all 7 required fields.
  - `test_db_exactly_50_bhajans`: Asserts count of stored records is exactly 50.
  - `test_db_fields_not_null_or_empty`: Verifies fields are not null/empty.
* **Search (`test_search.py`)**:
  - `test_search_by_deity`: Filters records correctly by deity field.
  - `test_search_by_raga`: Filters records correctly by raga field.
  - `test_search_by_beat`: Filters records correctly by beat/tala field.
  - `test_search_by_lyrics_text`: Full-text lyric search.
  - `test_search_multiple_filters`: Validates compound query logic.
* **Frontend (`test_frontend.py`)**:
  - `test_homepage_loads_successfully`: GET `/` returns HTTP 200 and loads standard layout elements.
  - `test_api_bhajans_returns_200_json`: GET `/api/bhajans` returns JSON bhajan list.
  - `test_api_search_returns_200_json`: GET `/api/search` returns JSON search results.
  - `test_api_search_with_filtering`: GET `/api/search?deity=Ganesha` returns filtered payload.
  - `test_frontend_route_not_found`: Verifies route mismatches return HTTP 404.

### Tier 2: Boundary & Edge Cases
Asserts system resiliency under erroneous or stress inputs:
* **Database (`test_db.py`)**:
  - `test_db_uniqueness_constraint`: IntegrityError on duplicate title + deity.
  - `test_db_unicode_encoding_support`: Verifies non-ASCII/Unicode roundtrip support ("ॐ", "Śiva").
  - `test_db_null_constraint_violation`: IntegrityError when trying to insert NULL title.
  - `test_db_sql_injection_defense`: Verifies malicious titles are escaped and stored as literals.
  - `test_db_extreme_input_size`: Inserts very large lyrics without database crash.
* **Search (`test_search.py`)**:
  - `test_search_case_insensitivity`: Matches `ganesha`, `GANESHA`, and `GaNeShA` identically.
  - `test_search_sql_injection_defense`: Ensures injection payload returns empty results safely.
  - `test_search_whitespace_trimming`: Padded search text gets trimmed and matched.
  - `test_search_empty_queries`: Empty parameters default to return all records.
  - `test_search_no_results`: Returns `[]` without error on missing query string.
* **Frontend (`test_frontend.py`)**:
  - `test_api_search_invalid_parameter_values`: Returns empty JSON list on missing filters.
  - `test_api_search_sql_injection_safety`: API query parameters sanitization.
  - `test_api_search_whitespace_handling`: API handles padded spaces safely.
  - `test_api_search_case_insensitivity`: Case-insensitive queries map properly to API response.
  - `test_api_search_empty_params`: Resolves empty strings to retrieve entire catalog.

### Tier 3: Cross-Feature Combinations
Tests boundaries between decoupled database, search, and frontend modules:
- **DB-to-API Data Integrity**: Directly queries SQLite database, queries `/api/bhajans` HTTP endpoint, and asserts that they match 1-to-1.
- **Unicode Roundtrip**: Writes unicode values to the DB, queries it via Next.js `/api/search`, and asserts HTTP payload preserves characters.
- **Lock Handling**: Opens multiple concurrent SQLite connection handles to assert SQLite concurrent read access works without locking.

### Tier 4: Real-World Workloads
Scenario-based tests representing end-to-end workload simulations:
1. **User Search Refinement Journey**: Simulates a search session (search "residing" -> filter Deity "Ganesha" -> filter Raga "Yaman" -> clear filters). Asserts counts update accurately.
2. **First-Time Setup Verification**: Deletes database, initializes clean schema, populates exactly 50 records, boots server, and requests `/api/bhajans` to verify page setup.
3. **High Density Concurrent Search Load**: Spawns multiple threads to concurrently query search query logic and verify connection limits.
4. **High Density Concurrent API Requests**: Spawns concurrent background threads to trigger HTTP requests targeting `/api/search` to assert concurrent socket handling on port 3000.
5. **System Degradation Resiliency**: Renames/removes database and verifies that query utilities fail gracefully with descriptive error types (OperationalError/FileNotFoundError) instead of unhandled application crashes.

---

## 4. Performance & Integrity Budgets

* **Execution Time**: The complete test suite in `mock` mode must run and complete in **under 5 seconds**.
* **SQL Query Performance**: DB search queries must resolve in **under 15 milliseconds** per request.
* **Port Conflict Policy**: The mock server attempts to bind to port 3000. If port 3000 is already in use, it dynamically binds to a free ephemeral port to avoid socket conflicts.
* **Database Isolation**: Write/modify tests write and commit their inputs so that separate connection handles (e.g. mock server threads) can query them, and use `try...finally` blocks to delete the inserted data and restore the database state.

---

## 5. Execution Commands

### Run the entire test suite:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

### Run specific test modules:
```powershell
# Database Tests only
python -m unittest tests/test_db.py

# Search Tests only
python -m unittest tests/test_search.py

# Frontend API and Mock Web Server Tests only
python -m unittest tests/test_frontend.py
```

### Force Real Database & Web Server Mode:
```powershell
$env:TEST_MODE="real"
python -m unittest discover -s tests -p "test_*.py"
```
