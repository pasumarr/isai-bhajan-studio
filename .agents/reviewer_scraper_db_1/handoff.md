# Handoff Report: Reviewer Scraper & DB 1

## 1. Observation
- **Observation A**: In `backend/database.py`, the metadata query filters in `search_bhajans` are constructed as follows:
  ```python
  187:         if deity and deity != "All":
  188:             sql += " AND b.deity = ?"
  189:             params.append(deity)
  190: 
  191:         if raga and raga != "All":
  192:             sql += " AND b.raga = ?"
  193:             params.append(raga)
  194: 
  195:         if beat and beat != "All":
  196:             sql += " AND b.beat = ?"
  197:             params.append(beat)
  ```
  Neither the query constructed nor the database schema uses `COLLATE NOCASE`.
- **Observation B**: In `tests/test_search.py` and `tests/test_frontend.py`, the mock/fallback query implementations use `COLLATE NOCASE` for metadata matching. For example, in `tests/test_search.py`:
  ```python
  33:                 sql += " AND deity = ? COLLATE NOCASE"
  ```
- **Observation C**: In `backend/scraper.py`, the `FallbackBhajanParser` defines the end tag handling for `div` tags as:
  ```python
  131:             elif tag == "div" and tag == "div" and not self.in_lyrics:
  132:                 # If we closed the bhajan-card div
  ```
- **Observation D**: In `tests/mock_data.py`, the mock database creation does not match the production table schema:
  ```python
  43:     cursor.execute("""
  44:         CREATE TABLE IF NOT EXISTS bhajans (
  45:             id INTEGER PRIMARY KEY AUTOINCREMENT,
  ...
  52:             UNIQUE(title, deity)
  53:         )
  54:     """)
  ```
  It lacks FTS5 tables, triggers, and indices present in `backend/database.py`.
- **Observation E**: The execution of pytest command timed out waiting for permission:
  ```
  Encountered error in step execution: Permission prompt for action 'command' on target 'python -m pytest -v tests/test_db.py' timed out waiting for user response.
  ```

## 2. Logic Chain
1. SQLite's `=` operator performs case-sensitive matching by default unless `COLLATE NOCASE` is specified in the schema or the query (Observation A).
2. The mock search tests check case-insensitivity on mock endpoints that manually add `COLLATE NOCASE` (Observation B), which masks the fact that the real backend logic (`search_bhajans` in `backend/database.py`) is case-sensitive.
3. Therefore, executing case-insensitive search queries against the real database engine using the backend database API will fail to match records with different case styling (such as `"ganesha"` searching for `"Ganesha"`).
4. The fallback scraper relies on `tag == "div" and tag == "div"` which contains a redundant check (Observation C) and closes the bhajan-card parser state whenever a non-lyrics `div` closing tag is encountered.
5. In a real-world scenario, any nested `div` within the card structure (other than lyrics) will cause the fallback parser to close the card prematurely, leading to corrupt or truncated parsed outputs.
6. The test database setup helper `tests/mock_data.py` sets up a simplified version of the schema that does not match the actual backend schema (Observation D), causing test databases initialized via mock data to lack the FTS virtual tables and sync triggers.
7. Running the test suite could not be verified programmatically due to user approval timeout (Observation E).

## 3. Caveats
- No test runs were completed successfully due to command execution timeout.
- The reviewer assumed python environment has `pytest` and SQLite version supporting `RETURNING` clauses based on project design documents.

## 4. Conclusion
The database schema and scraper logic correctly address the core requirements for data ingestion, duplicate protection (via UPSERT), and search indexing. However, the verdict is **REQUEST_CHANGES** due to:
1. Case-sensitivity mismatch in the real database search queries compared to mock tests.
2. Fragility in the fallback scraper's HTML parsing logic.
3. Structural discrepancies in the test database initialization schema.

## 5. Verification Method
- Execute the test suite using pytest to verify basic functionality:
  ```powershell
  python -m pytest -v tests/test_db.py
  ```
- Run search queries through `search_bhajans` in `backend/database.py` with case mismatches (e.g. `deity="ganesha"`) to verify that the query fails to return records, and confirm that it resolves once `COLLATE NOCASE` is appended.
- Modify `backend/mock_data/bhajans_source.html` by adding a wrapper `div` inside a card and running the parser script to trigger the fallback parsing failure.
