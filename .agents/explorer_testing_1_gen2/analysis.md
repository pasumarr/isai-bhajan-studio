# Forensic Analysis and Compatibility Report: E2E Test Suite Integrity Violation

This document provides a comprehensive analysis of the E2E Test Suite integrity violation in the database testing codebase (`tests/test_db.py`) and outlines the concrete refactoring strategy to resolve it using Python's standard `unittest` framework.

---

## 1. Forensic Audit Analysis & Root Cause

### The Integrity Violation
The forensic auditor identified an **INTEGRITY VIOLATION** under the **Build and run** phase. The E2E Test Suite is mandated to run with the following command:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

However, `tests/test_db.py` was implemented using **pytest-style bare function tests** and relied on the external package `pytest`. This results in two failure modes:
1. **Crash due to Missing Dependency**: If `pytest` is not installed in the testing environment, importing `test_db.py` fails with a `ModuleNotFoundError: No module named 'pytest'` exception. This halts the entire test execution process.
2. **Silent Skipping / False Positives**: If `pytest` is present in the environment, standard Python `unittest discover` does not detect any tests in `test_db.py` because they are written as bare functions (`def test_*`) rather than members of a class subclassing `unittest.TestCase`. The runner finishes with `OK`, reporting only the search and frontend tests as run, silently bypassing database schema, volume, constraints, and scraper integration verifications.

### Incompatible Elements in `tests/test_db.py`
1. **Pytest Imports**: `import pytest` on Line 4.
2. **Bare Test Functions**: 6 test entry points declared as global-scope functions:
   - Line 12: `def test_schema_initialization(tmp_path):`
   - Line 57: `def test_parser_with_snippet():`
   - Line 78: `def test_database_insertion_and_validation(tmp_path):`
   - Line 118: `def test_duplicate_protection_and_upsert(tmp_path):`
   - Line 157: `def test_search_fts_and_filters(tmp_path):`
   - Line 197: `def test_e2e_integration_and_idempotency(tmp_path):`
3. **Fixture Arguments**: Five of the test functions declare a parameter `tmp_path`, which is a pytest-specific fixture for injecting temporary directory paths. Standard `unittest` does not support parameter injection in test methods and fails with a `TypeError` if run.
4. **Pytest Assertion Blocks**: Using `with pytest.raises(...)` for validating that errors (like `ValueError` for invalid schema values) are raised.
5. **Bare Assertions**: Standard Python `assert` statements were used throughout the file. While functional, they lack the informative diagnostics of `unittest` assertion helpers.

---

## 2. Refactoring & Compatibility Strategy

To ensure 100% compliance with `unittest discover` while maintaining all test verifications, `tests/test_db.py` must be refactored as follows:

### Class-Based Structure
Encapsulate all database tests within a new test case class inheriting from `unittest.TestCase`:
```python
class TestDatabase(unittest.TestCase):
    # Test methods defined here...
```

### Eliminating the `pytest` Dependency
1. Remove `import pytest` from the file header.
2. Replace `with pytest.raises(ExceptionClass, match="...")` with `with self.assertRaisesRegex(ExceptionClass, "...")`.

### Standard Temporary Directory Replacement (`tmp_path`)
The pytest `tmp_path` fixture provides an isolated `pathlib.Path` directory for each test run. Under Python's standard `unittest` framework, we can achieve identical isolation and cleanup by using a context manager around `tempfile.TemporaryDirectory()` within each test:
```python
import tempfile
import pathlib

# Inside test methods:
with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = pathlib.Path(tmpdir)
    # The remainder of the test body can run unmodified
```
Using the context manager approach is superior to using `setUp` / `tearDown` because:
- It maintains the exact same local variable scoping (`tmp_path`) as the original code, reducing the risk of code rewrite errors.
- It guarantees automatic directory removal on context exit, even if the test fails or raises an exception.
- It ensures strict file system isolation between tests without sharing state on `self`.

### Standardizing Assertions
Convert all bare `assert` statements to standard `unittest` methods to capture meaningful failure outputs:
- `assert a in b` $\rightarrow$ `self.assertIn(a, b)`
- `assert a == b` $\rightarrow$ `self.assertEqual(a, b)`
- `assert a is not None` $\rightarrow$ `self.assertIsNotNone(a)`
- `assert a > b` $\rightarrow$ `self.assertGreater(a, b)`
- `assert a != b` $\rightarrow$ `self.assertNotEqual(a, b)`

---

## 3. Preservation of Tier 1-4 Boundaries and Features

Every test function and boundary condition originally implemented in `tests/test_db.py` is fully preserved in the refactored structure:

| original Test Function | Target Tier / Feature | Verification Maintained |
|---|---|---|
| `test_schema_initialization` | **Tier 1 (Happy Paths)**: Database connection validation & database table schema confirmation | Verifies database creation, `bhajans` and `bhajans_fts` tables, all 8 required column names, indexes on metadata fields (`idx_bhajans_deity`, `idx_bhajans_raga`, `idx_bhajans_beat`), and FTS sync triggers (`bhajans_ai`, `bhajans_ad`, `bhajans_au`). |
| `test_parser_with_snippet` | **Tier 2 (Boundary & Edge)**: Web scraping parser logic | Validates parser extracts 1 bhajan card HTML snippet and maps title, deity, raga, beat, multiline lyrics, and audio URL correctly. |
| `test_database_insertion_and_validation` | **Tier 1 (Happy Paths)**: Field insertion verification.<br>**Tier 2 (Boundary & Edge)**: `NOT NULL` constraint violations | Inserts a valid bhajan record, reads it back to assert field fidelity, and tests validation raises `ValueError` on missing `title` or `lyrics`. |
| `test_duplicate_protection_and_upsert` | **Tier 2 (Boundary & Edge)**: Uniqueness constraints & duplicate protection | Validates database executes an `UPSERT` on conflicts on `(title, deity)`, updating metadata columns while maintaining exactly 1 row. |
| `test_search_fts_and_filters` | **Tier 1 (Happy Paths)**: Deity search, Raga search, Beat search, Full-text lyrics query, compound filters | Validates that keyword queries, deity filters, compound searches (query + deity + raga + beat), and invalid filters behave identically inside SQLite. |
| `test_e2e_integration_and_idempotency` | **Tier 1 (Happy Paths)**: Database record volume (exactly 50 items).<br>**Tier 4 (Real-World)**: First-Time Setup Scenario & Scraper Idempotency | Simulates setup verification by scraping the mock HTML, asserting exactly 50 records are written, confirming zero empty values, and running the scraper again to assert volume remains at 50 (idempotency). |

---

## 4. Verification & Implementation Artifacts

To facilitate the immediate resolution of the integrity violation, the following helper files have been generated:
1. **Replacement File**: `proposed_test_db.py` — A complete drop-in replacement file containing the refactored code.
2. **Diff Patch File**: `test_db_compatibility.patch` — A machine-applicable diff that can be applied to the existing `tests/test_db.py` file using standard patching mechanisms (e.g. `git apply` or `patch`).
