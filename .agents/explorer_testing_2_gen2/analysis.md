# Analysis Report: E2E Test Suite Integrity Refactoring

## 1. Problem Incompatibility Details
The Forensic Auditor identified an `INTEGRITY VIOLATION` in the E2E Test Suite because `tests/test_db.py` uses pytest-style bare function tests and depends on pytest. 

When the project's designated test runner command is run:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```
The following issues occur:
1. **Runner Incompatibility**: `unittest discover` scans the `tests/` folder for files matching `test_*.py`. It imports `test_db.py` but skips it entirely or runs `0` tests from it, because `unittest` requires test classes to inherit from `unittest.TestCase` and test methods to start with `test_`.
2. **Crash on Missing Dependencies**: If `pytest` is not installed, the test runner crashes with `ModuleNotFoundError: No module named 'pytest'` at the very beginning of the test suite execution.
3. **Silent Skips**: If `pytest` is installed in the python environment, the runner will start but skip all 6 tests in `test_db.py` without warning, reporting that `Ran 0 tests` or omitting them from execution logs.

## 2. Refactoring Strategy

### Fix Strategy 1: Migrate to standard Python `unittest.TestCase`
We must refactor all test functions in `tests/test_db.py` to be methods inside a test class `TestDatabase` inheriting from `unittest.TestCase`.

Before:
```python
import pytest

def test_schema_initialization(tmp_path):
    ...
```

After:
```python
import unittest

class TestDatabase(unittest.TestCase):
    def test_schema_initialization(self):
        ...
```

### Fix Strategy 2: Replacing the `tmp_path` Fixture
Pytest automatically passes a pathlib `Path` object to `tmp_path`. To replicate this cleanly in Python's standard library `unittest`:
- We can define `setUp()` and `tearDown()` methods inside `TestDatabase`.
- `setUp()` instantiates `tempfile.TemporaryDirectory()`.
- We extract the path of the temporary directory and convert it to a `pathlib.Path` object stored in `self.tmp_path`.
- `tearDown()` automatically calls `.cleanup()` on the temporary directory object to clean up disk space after each test execution.

This is highly robust and requires minimal edits inside the actual test bodies because we can still reference `self.tmp_path / "filename"`.

Implementation:
```python
import tempfile
from pathlib import Path

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._temp_dir.name)

    def tearDown(self):
        self._temp_dir.cleanup()
```

### Fix Strategy 3: Replacing `pytest.raises` Exception Checking
We replace pytest's `with pytest.raises(...)` context manager with standard library's `with self.assertRaisesRegex(...)`.

Before:
```python
    with pytest.raises(ValueError, match="Missing required field: title"):
        save_bhajan(missing_title, db_path)
```

After:
```python
        with self.assertRaisesRegex(ValueError, "Missing required field: title"):
            save_bhajan(missing_title, db_path)
```

## 3. Preserving Tiers 1-4 Features & Boundaries
We verified that the refactored structure preserves all features, boundaries, and logic defined in Tiers 1-4:

- **Tier 1: Feature Coverage / Happy Paths**:
  - `test_schema_initialization`: Verifies correct initialization of table structures (`bhajans`, `bhajans_fts`), columns, and database indexes/triggers.
  - `test_parser_with_snippet`: Happy-path check verifying HTML parser accurately extracts values from structured markup snippets.
- **Tier 2: Boundary & Edge Cases**:
  - `test_database_insertion_and_validation`: Verifies validator throws errors on missing required fields (`title`, `lyrics`) using standard exception assertion.
  - `test_duplicate_protection_and_upsert`: Validates UPSERT conflict resolution when writing a record with matching unique keys.
- **Tier 3: Cross-Feature Combination Tests**:
  - `test_search_fts_and_filters`: Exercises combination filters (FTS search string + Deity + Raga + Beat) against the virtual and physical database tables.
- **Tier 4: Scenarios**:
  - `test_e2e_integration_and_idempotency`: Runs the end-to-end HTML file scraper and populator, verifying schema attributes and database idempotency (ensuring 50 records are written and duplicates do not duplicate rows).
