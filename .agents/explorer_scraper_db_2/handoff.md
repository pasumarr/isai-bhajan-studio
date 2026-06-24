# Handoff Report — DB & Scraper Architecture Proposal

This report summarizes the design, strategy, and verification plan proposed by Scraper & DB Explorer 2.

## 1. Observation
We observed the following regarding the project workspace and requirements:
- **Project Structure**: Investigating the root directory and `PROJECT.md` shows that the project code layout is expected to be:
  ```
  backend/
    ├── scraper.py
    ├── database.py
    └── search.py
  tests/
    └── test_db.py
  ```
  No code files currently exist in these directories on disk.
- **Milestone Scope**: The file `.agents/sub_orch_scraper_db/SCOPE.md` specifies:
  - Database file name: `bhajans.db`.
  - Database contract: Expose `database.save_bhajan(bhajan_data: dict)` ensuring unique records.
  - Fields: `title`, `deity`, `raga`, `beat` (tala), `lyrics`, and `audio_url`.
  - Target: Mock offline raw data source containing details for 50 representative bhajans.
- **Constraints**: We are restricted by `CODE_ONLY` network mode, which prohibits external HTTP clients and network calls.

## 2. Logic Chain
Based on these observations, our design reasoning is as follows:
1. **Schema Design**: Since the system requires advanced searching including filtering and free-text queries (e.g., text search on lyrics or title as defined in `PROJECT.md`), a single table `bhajans` with structured columns for `deity`, `raga`, and `beat` (with indexing) is necessary. To handle text search efficiently, a SQLite FTS5 virtual table `bhajans_fts` is chosen.
2. **Duplicate Protection**: The requirement for "ensuring unique records" based on title/deity translates to a database-level `UNIQUE(title, deity)` constraint. To implement this gracefully in `save_bhajan()`, we utilize SQLite's `INSERT ... ON CONFLICT(title, deity) DO UPDATE` (UPSERT) syntax. This ensures existing records are updated rather than throwing exception errors or silently ignoring modifications.
3. **Scraper Strategy**: Due to `CODE_ONLY` constraints, parsing a remote web page is impossible. However, to ensure the parser logic uses BeautifulSoup rather than just reading a static JSON file, we propose storing 50 mock HTML pages (and an `index.html` referencing them) inside `backend/mock_data/`. The scraper will read these local files and parse them using `BeautifulSoup`. This keeps the extraction code identical to what would be run in a production/online scraper.
4. **Verification Plan**: The verification in `tests/test_db.py` must programmatically construct the mock HTML directory, invoke `init_db()`, parse/run the scraper, save the records, and assert count (exactly 50), metadata presence, duplicate protection (running scraper twice maintains count of 50), and query filtering/FTS matching.

## 3. Caveats
- **SQLite Version**: FTS5 is universally enabled in Python's standard `sqlite3` library in modern releases (Python 3.9+). If running on an extremely outdated Python environment, FTS5 triggers could fail, though this is highly unlikely in modern systems.
- **HTML Layout Sync**: The mock HTML generator in tests must match the parser selectors in `backend/scraper.py`. Any class name mismatch will fail parsing. We have documented the selector mapping clearly.
- **Audio URLs**: For simplicity, mock URLs are formatted as `https://example.com/audio/bhajan_{i}.mp3`. If real audio files are needed later, these URLs will need to point to real paths.

## 4. Conclusion
We conclude that:
- A database schema with `bhajans` and `bhajans_fts` combined with insert-update triggers is the optimal design for the search engine backend.
- Storing mock HTML files locally and reading them via standard I/O preserves BeautifulSoup parsing integrity under CODE_ONLY constraints.
- An UPSERT-based `save_bhajan` API achieves duplicate protection with minimal overhead.
- A pytest suite using standard `tmp_path` fixtures is robust and fully covers the verification criteria.

Detailed plans and code structures are fully detailed in `C:\Users\saipa\isai-bhajan-studio\.agents\explorer_scraper_db_2\analysis.md`.

## 5. Verification Method
Since this is a read-only investigation task, no source code was written or modified. However, the proposal's correctness can be verified by implementing the design proposed in `analysis.md` and running the test suite:
1. Implement `backend/database.py`, `backend/scraper.py`, and `tests/test_db.py` as detailed in `analysis.md`.
2. Generate the 50 mock HTML pages in `backend/mock_data/` using the list provided in the report.
3. Execute the tests:
   ```bash
   pytest tests/test_db.py
   ```
4. Confirm all assertions pass.
