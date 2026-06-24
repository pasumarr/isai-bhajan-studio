# Test Suite Refactoring Analysis & Fix Strategy

## Executive Summary
This report analyzes the E2E Test Suite codebase (specifically `tests/test_db.py`) to address a forensic audit integrity violation. By refactoring `tests/test_db.py` to subclass `unittest.TestCase`, removing the dependency on `pytest`, and utilizing standard Python `tempfile` utilities, the entire test suite becomes compatible with the mandated test runner command (`python -m unittest discover -s tests -p "test_*.py"`).

---

## 1. Problem Statement
The current E2E Test Suite has an **Integrity Violation** under Development Mode. 
- **Cause**: `tests/test_db.py` uses pytest-style bare function tests (e.g., `def test_schema_initialization(tmp_path)`) and performs `import pytest` on Line 4.
- **Impact on Mandated Runner**: 
  - The mandated test runner command `python -m unittest discover -s tests -p "test_*.py"` uses standard Python `unittest`.
  - If the third-party `pytest` package is not installed on the system, the runner command immediately crashes with `ModuleNotFoundError: No module named 'pytest'` when importing `tests/test_db.py`.
  - If `pytest` is installed, the runner completes, but standard `unittest` discovery skips all bare function tests in `tests/test_db.py` since it only discovers classes subclassing `unittest.TestCase` and method names prefixed with `test_`. As a result, 6 critical database schema, scraper, and volume tests are silently bypassed, leading to false-positive passes.

---

## 2. Refactoring Strategy

### A. Subclassing `unittest.TestCase`
To ensure compatibility with `unittest` discovery, the 6 bare test functions must be moved into a test class that inherits from `unittest.TestCase`.

1. **Remove pytest Import**: Delete `import pytest` from `tests/test_db.py`.
2. **Import unittest and tempfile**: Add standard library imports `unittest` and `tempfile`, alongside `pathlib.Path`.
3. **Class Definition**: Wrap all test functions under a class named `TestDatabaseAndScraper(unittest.TestCase)`.
4. **Main Entry Block**: Append a standard execution block at the end of the file:
   ```python
   if __name__ == "__main__":
       unittest.main()
   ```

### B. Replacing the `tmp_path` Fixture
Pytest's `tmp_path` fixture provides a temporary directory path unique to each test run. Under standard `unittest`, this is elegantly replaced using `tempfile.TemporaryDirectory` instantiated in `setUp()` and cleaned up in `tearDown()`.

- **setUp Method**:
  ```python
  def setUp(self):
      self.test_dir = tempfile.TemporaryDirectory()
      self.tmp_path = Path(self.test_dir.name)
  ```
- **tearDown Method**:
  ```python
  def tearDown(self):
      self.test_dir.cleanup()
  ```
- **Test Invocation**: Each test method receives only `self` as a parameter and references `self.tmp_path` instead of the function argument `tmp_path`. Because SQLite database connections in `backend/database.py` are properly managed and closed inside `finally` blocks, file handles will be released, allowing Windows to cleanly delete the files on `cleanup()`.

### C. Replacing Pytest Assertions
Pytest uses bare `assert` and `pytest.raises` for exception matching. These need to be converted to standard `unittest` methods for cleaner logs and runner compatibility:

| Pytest Construct | Refactored Unittest Counterpart |
| :--- | :--- |
| `assert a in b` | `self.assertIn(a, b)` |
| `assert a == b` | `self.assertEqual(a, b)` |
| `assert a is not None` | `self.assertIsNotNone(a)` |
| `assert a > b` | `self.assertGreater(a, b)` |
| `assert a != b` | `self.assertNotEqual(a, b)` |
| `with pytest.raises(ValueError, match="...")` | `with self.assertRaisesRegex(ValueError, "...")` |

---

## 3. Preservation of Tiers 1-4 Boundaries
Refactoring the test code preserves all functional boundaries and verification checks from the original suite:

1. **Tier 1: Feature Coverage (Happy Paths)**
   - **`test_schema_initialization`**: Verifies database tables (`bhajans`, `bhajans_fts`), columns (e.g. `id`, `title`, `deity`), indices (`idx_bhajans_deity`, etc.), and FTS5 triggers (`bhajans_ai`, `bhajans_ad`, `bhajans_au`) are correctly initialized.
   - **`test_parser_with_snippet`**: Verifies that standard parser functionality converts raw HTML card elements into valid Bhajan dictionaries with correct attribute mappings (title, deity, raga, beat, lyrics, audio_url).
   - **`test_database_insertion_and_validation` (Happy Path portion)**: Validates saving a clean bhajan dictionary and retrieving it back with identical attributes.
   - **`test_search_fts_and_filters`**: Evaluates FTS query lookups on titles and lyrics, as well as single/compound filtering (deity, raga, beat).

2. **Tier 2: Boundary & Edge Cases**
   - **`test_database_insertion_and_validation` (Boundary portion)**: Asserts validation constraints prevent insertions of records with missing required fields (`title`, `lyrics`) by raising `ValueError`.
   - **`test_duplicate_protection_and_upsert`**: Asserts duplicate protection via SQLite UPSERT logic. When inserting a bhajan with the same `(title, deity)` composite unique constraint key, the database performs an in-place update (UPSERT) of the remaining metadata fields instead of failing or inserting duplicate records.

3. **Tier 3: Cross-Feature Combination Tests**
   - **`test_search_fts_and_filters` (Cross-Feature portion)**: Validates interaction between FTS query matching (using `bhajans_fts`) and structured schema metadata filters combined, testing edge conditions like returning empty lists for mismatched parameters.

4. **Tier 4: Real-World Workloads (Scenarios)**
   - **`test_e2e_integration_and_idempotency`**: Executes a complete E2E scrape and populate sequence. It reads the local HTML mock data (`bhajans_source.html`), populates a test database with 50 items, verifies schema compliance across all fields (no empty properties), runs the scraper again, and checks that database record count remains exactly 50 (validating absolute population idempotency under load).

---

## 4. Integration Verification
By executing `python -m unittest discover -s tests -p "test_*.py"` after implementing this change, the test runner will discover:
- `TestDatabaseAndScraper` (6 tests in `test_db.py`)
- `TestSearch` (12 tests in `test_search.py`)
- `TestFrontend` (12 tests in `test_frontend.py`)

Total suite size will be exactly 30 tests running in a single command, verifying backend DB, search, frontend mocks, and integration workflows with 100% dependency-free compatibility with standard Python distributions.
