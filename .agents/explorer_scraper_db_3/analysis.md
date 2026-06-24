# SQLite Database & Offline Scraper Design Analysis

This report proposes a complete database schema, offline scraper strategy, database interface module, and testing/verification suite for the ISai Bhajan Studio backend.

---

## 1. SQLite Database Schema Proposal

For a collection of 50 bhajans (and scaling upward to thousands), SQLite is an ideal, lightweight, zero-configuration relational database. We propose a robust schema designed for data integrity, efficiency, and future search performance.

### Table: `bhajans`
This table stores the core metadata and lyrics for each bhajan.

| Column Name | SQLite Data Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique identifier for internal references. |
| `title` | `TEXT` | `NOT NULL UNIQUE` | Title of the bhajan. Enforces uniqueness to prevent duplicates. |
| `deity` | `TEXT` | `NOT NULL` | The deity addressed (e.g., Ganesha, Shiva, Krishna). |
| `raga` | `TEXT` | `NOT NULL` | The musical raga/scale of the bhajan (e.g., Hamsadhwani, Bhairavi). |
| `beat` | `TEXT` | `NOT NULL` | The rhythm cycle/tala (e.g., Adi, Rupak, Keherwa). |
| `lyrics` | `TEXT` | `NOT NULL` | Full text lyrics of the bhajan (newlines preserved). |
| `audio_url` | `TEXT` | `NOT NULL` | URL pointing to the bhajan's audio file (simulated/mocked). |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Audit timestamp of insertion. |

### Indexes
To optimize searching by filtering on deity, raga, and beat (which are core parameters for Milestone 3's advanced search), we define the following indexes:
- `idx_bhajans_deity` on `bhajans(deity)`
- `idx_bhajans_raga` on `bhajans(raga)`
- `idx_bhajans_beat` on `bhajans(beat)`
*(Note: A unique index on `title` is automatically created by SQLite due to the `UNIQUE` constraint.)*

### Full-Text Search (FTS5) Support
To support fast, fuzzy, and snippet-based text searches across lyrics and titles, we propose setting up an FTS5 virtual table. SQLite's FTS5 extension allows full-text querying without slow SQL `LIKE %query%` statements.

- **FTS Table**: `bhajans_fts` (columns: `title`, `lyrics`, content mapping to `bhajans` table via `rowid`)
- **Triggers**: Automated triggers (`bhajans_ai`, `bhajans_ad`, `bhajans_au`) will keep `bhajans_fts` in sync whenever rows are inserted, deleted, or updated in the main `bhajans` table.

---

## 2. Offline Scraper Strategy (CODE_ONLY)

Under `CODE_ONLY` network restrictions, the scraper cannot query live websites. However, the system must simulate an automated web scraper parsing and populating data. We propose storing mock HTML or JSON data containing **50 representative bhajans** locally in the workspace.

### Proposal: Raw Data Storage Location & Format

We propose storing the mock data in **`backend/mock_data/bhajans_source.html`**. 

Using a static HTML file (instead of a clean JSON file) is highly recommended because it **preserves the crawler/scraper parsing logic**. The scraper can use `BeautifulSoup` to parse HTML structures (e.g., tags, class names, and attributes). This validates CSS selectors and parsing logic, allowing a seamless transition to a live web-scraping script later.

#### HTML Structure Example (`backend/mock_data/bhajans_source.html`):
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sai Bhajans Mock Directory</title>
</head>
<body>
    <div id="bhajan-container">
        <!-- Bhajan 1 -->
        <div class="bhajan-card" data-bhajan-id="1">
            <h2 class="bhajan-title">Ganesha Sharanam</h2>
            <div class="bhajan-metadata">
                <span class="meta-label">Deity:</span> <span class="deity-name">Ganesha</span>
                <span class="meta-label">Raga:</span> <span class="raga-name">Hamsadhwani</span>
                <span class="meta-label">Tala/Beat:</span> <span class="beat-name">Adi</span>
            </div>
            <div class="bhajan-lyrics">
                Ganesha Sharanam Parama Pavanam<br/>
                Sadguru Sharanam Bhava Bhaya Haranam<br/>
                Ganesha Sharanam Parama Pavanam
            </div>
            <div class="bhajan-media">
                <audio class="audio-player" src="https://www.saibhajans.org/audio/ganesha_sharanam.mp3"></audio>
            </div>
        </div>
        
        <!-- Bhajan 2 -->
        <div class="bhajan-card" data-bhajan-id="2">
            <h2 class="bhajan-title">Shiva Shambho Mahadeva</h2>
            <div class="bhajan-metadata">
                <span class="meta-label">Deity:</span> <span class="deity-name">Shiva</span>
                <span class="meta-label">Raga:</span> <span class="raga-name">Bhairavi</span>
                <span class="meta-label">Tala/Beat:</span> <span class="beat-name">Keherwa</span>
            </div>
            <div class="bhajan-lyrics">
                Shiva Shambho Mahadeva Shambo Mahadeva<br/>
                Hara Hara Shambho Mahadeva Shambo Mahadeva
            </div>
            <div class="bhajan-media">
                <audio class="audio-player" src="https://www.saibhajans.org/audio/shiva_shambho.mp3"></audio>
            </div>
        </div>
        
        <!-- Additional 48 bhajans populated similarly -->
    </div>
</body>
</html>
```

### Alternative Proposal: JSON Mock Data (`backend/mock_data/bhajans_source.json`)
If the team prefers to bypass HTML parsing entirely, a simple JSON file can be stored. This avoids dependencies on HTML parsers:
```json
[
  {
    "title": "Ganesha Sharanam",
    "deity": "Ganesha",
    "raga": "Hamsadhwani",
    "beat": "Adi",
    "lyrics": "Ganesha Sharanam Parama Pavanam\nSadguru Sharanam Bhava Bhaya Haranam",
    "audio_url": "https://www.saibhajans.org/audio/ganesha_sharanam.mp3"
  },
  ...
]
```

### Offline Scraper Parsing Logic
The python scraper (`backend/scraper.py`) will open and read this local file directly from the filesystem using relative paths, preventing any HTTP network requests.

#### Parsing Implementation Concept (HTML parsing via BeautifulSoup):
```python
import os
from bs4 import BeautifulSoup

def parse_offline_bhajans(file_path: str) -> list:
    """Parses local mock HTML containing bhajans and extracts structured dicts."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Mock data file not found at {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    bhajans = []
    cards = soup.find_all(class_="bhajan-card")
    for card in cards:
        # Extract title
        title_el = card.find(class_="bhajan-title")
        title = title_el.text.strip() if title_el else ""
        
        # Extract metadata
        deity_el = card.find(class_="deity-name")
        deity = deity_el.text.strip() if deity_el else ""
        
        raga_el = card.find(class_="raga-name")
        raga = raga_el.text.strip() if raga_el else ""
        
        beat_el = card.find(class_="beat-name")
        beat = beat_el.text.strip() if beat_el else ""
        
        # Extract lyrics and format line breaks
        lyrics_el = card.find(class_="bhajan-lyrics")
        if lyrics_el:
            # Replace br tags with newlines
            for br in lyrics_el.find_all("br"):
                br.replace_with("\n")
            lyrics = lyrics_el.text.strip()
        else:
            lyrics = ""
            
        # Extract audio URL
        audio_el = card.find("audio", class_="audio-player")
        audio_url = audio_el["src"].strip() if (audio_el and audio_el.has_attr("src")) else ""
        
        if title and deity: # Basic validation
            bhajans.append({
                "title": title,
                "deity": deity,
                "raga": raga,
                "beat": beat,
                "lyrics": lyrics,
                "audio_url": audio_url
            })
            
    return bhajans
```

---

## 3. Database Interface Functions

In `backend/database.py`, we implement the database operations. We enforce duplicate protection at the SQLite query level using **UPSERT (`ON CONFLICT`)** syntax. This ensures that:
1. Re-running the scraper updates existing records if fields have changed.
2. The total count remains at 50, preventing duplicate rows.
3. Operations are idempotent and safe.

### Recommended `backend/database.py` Code Structure

```python
import sqlite3
import os
from typing import Dict, List, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "bhajans.db")

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Helper function to get a sqlite connection with dict factory."""
    conn = sqlite3.connect(db_path)
    # Return rows as dict-like objects for easier JSON serialization downstream
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH) -> None:
    """Initializes the database schema and indexes."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Main Bhajans Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bhajans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            deity TEXT NOT NULL,
            raga TEXT NOT NULL,
            beat TEXT NOT NULL,
            lyrics TEXT NOT NULL,
            audio_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 2. Performance Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_deity ON bhajans(deity);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_raga ON bhajans(raga);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_beat ON bhajans(beat);")
    
    # 3. FTS5 Virtual Table for advanced text search
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS bhajans_fts USING fts5(
            title,
            lyrics,
            content='bhajans',
            content_rowid='id'
        );
    """)
    
    # 4. Triggers to keep FTS virtual table in sync
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS bhajans_ai AFTER INSERT ON bhajans BEGIN
            INSERT INTO bhajans_fts(rowid, title, lyrics) VALUES (new.id, new.title, new.lyrics);
        END;
    """)
    
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS bhajans_ad AFTER DELETE ON bhajans BEGIN
            INSERT INTO bhajans_fts(bhajans_fts, rowid, title, lyrics) VALUES('delete', old.id, old.title, old.lyrics);
        END;
    """)
    
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS bhajans_au AFTER UPDATE ON bhajans BEGIN
            INSERT INTO bhajans_fts(bhajans_fts, rowid, title, lyrics) VALUES('delete', old.id, old.title, old.lyrics);
            INSERT INTO bhajans_fts(rowid, title, lyrics) VALUES (new.id, new.title, new.lyrics);
        END;
    """)
    
    conn.commit()
    conn.close()

def save_bhajan(bhajan_data: Dict[str, Any], db_path: str = DB_PATH) -> bool:
    """
    Saves a bhajan dict to the database.
    If a record with the same title exists, it performs an UPSERT (updates fields).
    Ensures duplicate protection. Returns True on success, False on error.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    success = False
    
    # Validate required fields
    required_fields = ["title", "deity", "raga", "beat", "lyrics", "audio_url"]
    for field in required_fields:
        if field not in bhajan_data or bhajan_data[field] is None:
            conn.close()
            raise ValueError(f"Missing required field: '{field}' in bhajan data.")

    try:
        # UPSERT implementation: INSERT OR UPDATE ON CONFLICT
        cursor.execute("""
            INSERT INTO bhajans (title, deity, raga, beat, lyrics, audio_url)
            VALUES (:title, :deity, :raga, :beat, :lyrics, :audio_url)
            ON CONFLICT(title) DO UPDATE SET
                deity = EXCLUDED.deity,
                raga = EXCLUDED.raga,
                beat = EXCLUDED.beat,
                lyrics = EXCLUDED.lyrics,
                audio_url = EXCLUDED.audio_url;
        """, bhajan_data)
        conn.commit()
        success = True
    except sqlite3.Error as e:
        print(f"SQLite Error in save_bhajan: {e}")
        conn.rollback()
    finally:
        conn.close()
        
    return success

def get_bhajan_by_title(title: str, db_path: str = DB_PATH) -> Dict[str, Any] or None:
    """Retrieves a single bhajan by title. Returns None if not found."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM bhajans WHERE title = ?;", (title,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_bhajans(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves all bhajans stored in the database."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM bhajans ORDER BY title ASC;").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_db(db_path: str = DB_PATH) -> None:
    """Clears all records in the database (useful for test setup)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bhajans;")
    # Reset AUTOINCREMENT sequence
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='bhajans';")
    # Empty FTS table
    cursor.execute("INSERT INTO bhajans_fts(bhajans_fts) VALUES('rebuild');")
    conn.commit()
    conn.close()
```

---

## 4. Programmatic Unit Test and Verification Plan (`tests/test_db.py`)

A comprehensive, automated unit testing framework using `pytest` will be implemented under `tests/test_db.py` to verify the database implementation, duplicate protection, parsing correctness, and final 50-bhajan population constraints.

### Test Structure & Coverage (Tiers 1-5)

#### Tier 1: Core Database Schema Verification
- Assert that database initialization creates the `bhajans` table.
- Verify expected columns (`id`, `title`, `deity`, `raga`, `beat`, `lyrics`, `audio_url`, `created_at`) and their types/constraints.
- Verify that performance indexes (`idx_bhajans_deity`, etc.) are successfully registered in sqlite.

#### Tier 2: Scraper Parser Verification
- Feed the scraper function a tiny offline HTML slice (e.g. 2 bhajans) and verify the extracted structured dict values are 100% accurate.
- Verify that HTML formatting tags (like `<br/>` in lyrics) are converted correctly to newlines (`\n`) and leading/trailing whitespace is trimmed.

#### Tier 3: Database Interface & Constraint Verification
- Test `save_bhajan` inserts a valid record successfully.
- Test that trying to insert a bhajan missing a required field (e.g., empty `title` or missing `lyrics`) raises a `ValueError` or database constraint failure.

#### Tier 4: Duplicate Protection Verification (UPSERT)
- Insert a bhajan "Ganesha Sharanam".
- Insert the same bhajan "Ganesha Sharanam" with updated lyrics and audio URL.
- Assert that the database contains exactly **1** row (no duplication).
- Assert that the fields (lyrics, audio URL) are updated with the new values.

#### Tier 5: Complete E2E Integration (50 Bhajans)
- Point the scraper to `backend/mock_data/bhajans_source.html`.
- Run the scraper population script to populate the database.
- Assert that exactly **50** unique bhajans are inserted.
- Assert that no fields are empty or null.
- Run the scraper population a second time and assert that the count remains exactly **50**.

---

### Code Blueprint: `tests/test_db.py`

This code structure uses pytest fixtures to set up and tear down a isolated database environment for each test.

```python
import os
import pytest
import sqlite3
from backend.database import init_db, save_bhajan, get_bhajan_by_title, get_all_bhajans, clear_db
from backend.scraper import parse_offline_bhajans # Assuming parse method exists here

# Set up isolated temp DB for unit tests
@pytest.fixture
def temp_db(tmp_path):
    """Creates a temporary, isolated SQLite database file for the test run."""
    db_file = tmp_path / "test_bhajans.db"
    db_path = str(db_file)
    init_db(db_path)
    yield db_path
    # Clean up file after tests
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass

@pytest.fixture
def mock_html_path(tmp_path):
    """Creates a mock HTML file containing exactly 2 bhajans for parsing tests."""
    html_content = """
    <html>
        <body>
            <div id="bhajan-container">
                <div class="bhajan-card">
                    <h2 class="bhajan-title">Ganesha Sharanam</h2>
                    <div class="bhajan-metadata">
                        <span class="deity-name">Ganesha</span>
                        <span class="raga-name">Hamsadhwani</span>
                        <span class="beat-name">Adi</span>
                    </div>
                    <div class="bhajan-lyrics">
                        Line 1<br/>Line 2
                    </div>
                    <audio class="audio-player" src="http://mock.com/ganesha.mp3"></audio>
                </div>
                <div class="bhajan-card">
                    <h2 class="bhajan-title">Shiva Shambho</h2>
                    <div class="bhajan-metadata">
                        <span class="deity-name">Shiva</span>
                        <span class="raga-name">Bhairavi</span>
                        <span class="beat-name">Keherwa</span>
                    </div>
                    <div class="bhajan-lyrics">
                        Line A<br/>Line B
                    </div>
                    <audio class="audio-player" src="http://mock.com/shiva.mp3"></audio>
                </div>
            </div>
        </body>
    </html>
    """
    file_path = tmp_path / "test_bhajans.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return str(file_path)

# ----------------- TIER 1: SCHEMA TESTS -----------------

def test_database_schema_initialization(temp_db):
    """Verifies table, columns, and indexes are created correctly."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Check that bhajans table exists
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table_names = [t[0] for t in tables]
    assert "bhajans" in table_names
    assert "bhajans_fts" in table_names
    
    # Check column definitions
    columns_info = cursor.execute("PRAGMA table_info(bhajans);").fetchall()
    columns = {col[1]: col[2] for col in columns_info}
    expected_cols = ["id", "title", "deity", "raga", "beat", "lyrics", "audio_url", "created_at"]
    for col in expected_cols:
        assert col in columns
        
    # Check that title column is marked unique (or has index)
    indexes = cursor.execute("PRAGMA index_list(bhajans);").fetchall()
    idx_names = [idx[1] for idx in indexes]
    assert any("idx_bhajans_deity" in name for name in idx_names if name)
    assert any("idx_bhajans_raga" in name for name in idx_names if name)
    assert any("idx_bhajans_beat" in name for name in idx_names if name)
    
    conn.close()

# ----------------- TIER 2: PARSER TESTS -----------------

def test_offline_html_parsing(mock_html_path):
    """Verifies that the scraper correctly parses local HTML structured data."""
    bhajans = parse_offline_bhajans(mock_html_path)
    assert len(bhajans) == 2
    
    # Check structure
    ganesha = bhajans[0]
    assert ganesha["title"] == "Ganesha Sharanam"
    assert ganesha["deity"] == "Ganesha"
    assert ganesha["raga"] == "Hamsadhwani"
    assert ganesha["beat"] == "Adi"
    assert ganesha["lyrics"] == "Line 1\nLine 2"
    assert ganesha["audio_url"] == "http://mock.com/ganesha.mp3"
    
    shiva = bhajans[1]
    assert shiva["title"] == "Shiva Shambho"
    assert shiva["deity"] == "Shiva"
    assert shiva["lyrics"] == "Line A\nLine B"

# ----------------- TIER 3: INTERFACE & CONSTRAINTS -----------------

def test_save_bhajan_basic_insert(temp_db):
    """Verifies basic write function creates a record successfully."""
    bhajan_data = {
        "title": "Ganesha Sharanam",
        "deity": "Ganesha",
        "raga": "Hamsadhwani",
        "beat": "Adi",
        "lyrics": "Lyrics here",
        "audio_url": "http://mock.com/ganesha.mp3"
    }
    
    success = save_bhajan(bhajan_data, db_path=temp_db)
    assert success is True
    
    # Verify values in DB
    record = get_bhajan_by_title("Ganesha Sharanam", db_path=temp_db)
    assert record is not None
    assert record["deity"] == "Ganesha"
    assert record["raga"] == "Hamsadhwani"

def test_save_bhajan_validation(temp_db):
    """Verifies that missing required fields raises a ValueError."""
    invalid_data = {
        "title": "Missing Fields Bhajan",
        # deity is missing
        "raga": "Bhairavi",
        "beat": "Adi",
        "lyrics": "Lyrics",
        "audio_url": "http://mock.com/missing.mp3"
    }
    with pytest.raises(ValueError):
        save_bhajan(invalid_data, db_path=temp_db)

# ----------------- TIER 4: DUPLICATE PROTECTION -----------------

def test_save_bhajan_duplicate_protection_upsert(temp_db):
    """Verifies duplicate protection (UPSERT) keeps count at 1 and updates fields."""
    bhajan_initial = {
        "title": "Unique Bhajan",
        "deity": "Devi",
        "raga": "Kalyani",
        "beat": "Rupak",
        "lyrics": "Original Lyrics",
        "audio_url": "http://mock.com/orig.mp3"
    }
    
    # First save
    assert save_bhajan(bhajan_initial, db_path=temp_db) is True
    assert len(get_all_bhajans(db_path=temp_db)) == 1
    
    # Save duplicate with modified lyrics and audio
    bhajan_update = {
        "title": "Unique Bhajan",
        "deity": "Devi",
        "raga": "Kalyani",
        "beat": "Rupak",
        "lyrics": "Updated Lyrics!",
        "audio_url": "http://mock.com/new_updated.mp3"
    }
    assert save_bhajan(bhajan_update, db_path=temp_db) is True
    
    # Check that count remains 1 (No duplicate row was added)
    all_bhajans = get_all_bhajans(db_path=temp_db)
    assert len(all_bhajans) == 1
    
    # Verify that the record was updated with the new lyrics and audio URL
    record = all_bhajans[0]
    assert record["lyrics"] == "Updated Lyrics!"
    assert record["audio_url"] == "http://mock.com/new_updated.mp3"

# ----------------- TIER 5: POPULATION VERIFICATION -----------------

def test_full_offline_population(temp_db):
    """
    Simulates the actual execution task:
    1. Reads actual mock file containing 50 bhajans
    2. Runs offline scraper to extract metadata
    3. Saves all records to the temp database
    4. Verifies exactly 50 unique, complete records are stored.
    """
    # Locate actual mock source data file
    # (Assuming placed in workspace 'backend/mock_data/bhajans_source.html')
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mock_file_path = os.path.join(base_dir, "backend", "mock_data", "bhajans_source.html")
    
    # Check if mock file is present (skip if not created yet)
    if not os.path.exists(mock_file_path):
        pytest.skip(f"Mock source file {mock_file_path} not created yet.")
        
    # 1. Parse all 50 bhajans
    bhajans = parse_offline_bhajans(mock_file_path)
    assert len(bhajans) == 50, f"Expected mock data file to contain exactly 50 bhajans, got {len(bhajans)}"
    
    # 2. Populate DB
    for b in bhajans:
        assert save_bhajan(b, db_path=temp_db) is True
        
    # 3. Verify counts & completeness
    db_bhajans = get_all_bhajans(db_path=temp_db)
    assert len(db_bhajans) == 50
    
    for row in db_bhajans:
        assert row["title"] != ""
        assert row["deity"] != ""
        assert row["raga"] != ""
        assert row["beat"] != ""
        assert row["lyrics"] != ""
        assert row["audio_url"] != ""
        assert row["audio_url"].startswith("http")
        
    # 4. Verify Idempotence (re-run population does not change count or corrupt data)
    for b in bhajans:
        assert save_bhajan(b, db_path=temp_db) is True
        
    assert len(get_all_bhajans(db_path=temp_db)) == 50
```
