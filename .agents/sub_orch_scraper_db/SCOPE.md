# Scope: Milestone 2 — Scraper & DB (R2)

## Architecture
- **Data Source**: Offline mock data source (JSON/HTML file(s) located in `backend/` or `tests/`) containing details for 50 representative bhajans.
- **Scraper**: `backend/scraper.py` parses/reads the offline data source, simulating/extracting the audio links, lyrics, and metadata.
- **Database**: SQLite database file (e.g., `bhajans.db`). Schema and operations implemented in `backend/database.py`.
- **Verification**: `tests/test_db.py` executes the scraping and population process, then queries the database to verify that exactly 50 bhajans are successfully stored with complete metadata (lyrics, audio URLs, deities, ragas).

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Design Schema & Mock Data | Design SQLite schema, database.py interface, offline bhajan data mock | None | PLANNED |
| 2 | Implementation | Implement backend/database.py and backend/scraper.py | Milestone 1 | PLANNED |
| 3 | Verification | Write and run tests/test_db.py to verify 50 bhajans stored | Milestone 2 | PLANNED |

## Interface Contracts
### Scraper ↔ Database
- **Method**: `database.save_bhajan(bhajan_data: dict)`
- **`bhajan_data` Fields**:
  - `title` (TEXT, UNIQUE / Primary Key or part of constraints)
  - `deity` (TEXT)
  - `raga` (TEXT)
  - `beat` (TEXT) - (tala)
  - `lyrics` (TEXT)
  - `audio_url` (TEXT)
- **Behavior**: Ensures unique records (e.g. UPSERT or IGNORE if duplicate).
