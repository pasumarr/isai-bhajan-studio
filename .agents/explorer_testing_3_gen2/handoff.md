# Handoff Report — E2E Testing Track Integrity Violation Resolution

## 1. Observation

- **Observation 1**: `tests/test_db.py` imports `pytest` on line 4:
  ```python
  import pytest
  ```
- **Observation 2**: `tests/test_db.py` contains bare function test cases that accept the pytest-specific `tmp_path` fixture as a parameter:
  - Line 12: `def test_schema_initialization(tmp_path):`
  - Line 57: `def test_parser_with_snippet():`
  - Line 78: `def test_database_insertion_and_validation(tmp_path):`
  - Line 118: `def test_duplicate_protection_and_upsert(tmp_path):`
  - Line 157: `def test_search_fts_and_filters(tmp_path):`
  - Line 197: `def test_e2e_integration_and_idempotency(tmp_path):`
- **Observation 3**: Lines 110-111 and 115-116 in `tests/test_db.py` utilize pytest exception handling:
  ```python
  with pytest.raises(ValueError, match="Missing required field: title"):
      save_bhajan(missing_title, db_path)
  ```
- **Observation 4**: The mandated runner command specified in `TEST_READY.md` (Line 11) and `TEST_INFRA.md` (Line 117) is:
  ```powershell
  python -m unittest discover -s tests -p "test_*.py"
  ```
- **Observation 5**: The other test files in the project (`tests/test_search.py` and `tests/test_frontend.py`) are structured correctly as `unittest.TestCase` classes.

---

## 2. Logic Chain

1. The mandated test runner command (Observation 4) runs the standard Python `unittest` module to discover and execute tests.
2. The `unittest` module discovers and runs tests only if they are structured as methods inside classes subclassing `unittest.TestCase` and names start with `test_`.
3. Because `tests/test_db.py` implements its tests as bare functions (Observation 2), `unittest discover` fails to identify them as executable tests.
4. Furthermore, because `tests/test_db.py` imports `pytest` (Observation 1), the standard Python `unittest` discovery process will crash with a `ModuleNotFoundError` on environments where `pytest` is not installed, or complete with false-positive green passes (running 0 tests from `test_db.py`) if `pytest` is present.
5. In addition, pytest context managers like `pytest.raises` (Observation 3) and pytest parameters like `tmp_path` (Observation 2) are not supported by the standard `unittest` framework.
6. Therefore, `tests/test_db.py` must be refactored into a `unittest.TestCase` subclass where the `pytest` import is removed, assertions are converted to `self.assert*` equivalents, `pytest.raises` is replaced by `self.assertRaisesRegex`, and the `tmp_path` fixture is replaced by a standard `tempfile.TemporaryDirectory` wrapper in the setup and teardown phases of the test class.

---

## 3. Caveats

- Interactive terminal execution of the test suite could not be performed because the user approval prompt for `run_command` timed out.
- The analysis relies on static review of the codebase and Python's standard library `unittest` and `tempfile` behavior.

---

## 4. Conclusion

`tests/test_db.py` has a critical compatibility violation with the mandated E2E test runner. To resolve the integrity violation, it must be refactored to:
1. Subclass `unittest.TestCase`.
2. Remove the `pytest` dependency.
3. Manage temporary test directories via standard library `tempfile.TemporaryDirectory()`.
4. Refactor all bare assertions and exception checking to `unittest` standards.

A fully refactored proposed implementation is provided in `proposed_test_db.py` and the patch diff in `test_db.patch` inside the agent folder.

---

## 5. Verification Method

To independently verify the resolution after implementing the proposed changes:
1. Check that `tests/test_db.py` contains no `import pytest` or references to `pytest.raises` / `tmp_path` function arguments.
2. Verify that running the command:
   ```powershell
   python -m unittest tests/test_db.py
   ```
   runs all 6 test methods successfully and outputs:
   ```
   Ran 6 tests in ...s
   OK
   ```
3. Run the mandated test suite command:
   ```powershell
   python -m unittest discover -s tests -p "test_*.py"
   ```
   Verify that all 30 tests in the suite (6 from `test_db.py`, 12 from `test_search.py`, and 12 from `test_frontend.py`) are successfully discovered and executed under a single command.
