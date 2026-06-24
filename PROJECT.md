# Project: ISai Bhajan Studio

## Architecture
ISai Bhajan Studio is a web application designed to search and play Sai bhajans.
- **Backend**: Python-based scraper and SQLite database. The backend handles data scraping, structured storage of bhajans, and search querying.
- **Frontend**: React/Next.js web application providing a responsive UI and an advanced search toolbar.
- **Data Flow**:
  1. The Scraper extracts bhajan metadata (title, deity, raga, lyrics, audio link) and stores it in the multi-database architecture.
  2. The Search Toolbar queries the database to filter and present results.
  3. The Frontend displays the bhajan details and plays the audio.

## Code Layout
```
C:\Users\saipa\isai-bhajan-studio\
├── backend/                 # Scraper and database scripts
│   ├── scraper.py           # Automated web scraper
│   ├── database.py          # Database schema and population code
│   └── search.py            # Advanced search backend logic
├── frontend/                # Next.js / React application
├── tests/                   # Programmatic test scripts
│   ├── test_db.py           # Verification for R2 (50 bhajans stored)
│   ├── test_search.py       # Verification for R3 (Advanced Search)
│   └── test_frontend.py     # Verification for R1 (Web Server startup and status)
└── PROJECT.md               # Global project index (this file)
```

## Milestones
| # | Name | Scope | Dependencies | Status | Conversation ID |
|---|------|-------|-------------|--------|-----------------|
| 1 | E2E Testing Track | Define test infra and create automated test cases (Tiers 1-4) | None | COMPLETED | af82128f-c6ad-4af5-af7c-3250940b42b0 |
| 2 | Scraper & DB (R2) | Implement web scraper and multi-database storing 50 bhajans | None | COMPLETED | 78fa64de-70fc-4549-b4c9-d2ec830af9db |
| 3 | Search Mechanics (R3) | Implement advanced search mechanics & wire to DB | M2 | COMPLETED | 154e082f-7173-48b3-b5a3-1be6716fc079 |
| 4 | Web App Interface (R1) | Build Next.js app with modern aesthetics and search UI | M2, M3 | COMPLETED | 154e082f-7173-48b3-b5a3-1be6716fc079 |
| 5 | Integration & E2E Pass | Run E2E test suite (Tiers 1-4) and Phase 2 Adversarial Hardening (Tier 5) | M1, M4 | COMPLETED | 154e082f-7173-48b3-b5a3-1be6716fc079 |

## Interface Contracts
### Scraper ↔ Database
- The scraper must output bhajan objects structured with: `title`, `deity`, `raga`, `beat` (tala), `lyrics`, `audio_url`, and other metadata.
- Database must expose a write method: `save_bhajan(bhajan_data)` ensuring unique records.

### Database ↔ Search API
- The search function/endpoint must accept filter arguments: `query` (text search in lyrics/title), `deity`, `raga`, `tempo`, etc.
- Return format: JSON array of bhajans matching the criteria.

### Backend ↔ Frontend
- Next.js API route `/api/bhajans` and `/api/search` routing queries to the Python backend/SQLite database.
