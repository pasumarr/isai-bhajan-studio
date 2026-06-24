# Scraper & Database Design Proposal — ISai Bhajan Studio

This document contains the detailed proposal for the SQLite Database Schema, offline scraper strategy under CODE_ONLY constraints, database interface API, and programmatic unit test plan for the ISai Bhajan Studio application.

---

## 1. SQLite Database Schema

To support advanced searching (by deity, raga, beat/tala, and free-text queries matching titles or lyrics), we propose a database design leveraging a main structured relational table combined with an **FTS5 Virtual Table** for high-performance full-text search.

### 1.1 The `bhajans` Table
This table stores the primary metadata and lyrics of the bhajans.

```sql
CREATE TABLE IF NOT EXISTS bhajans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    deity TEXT NOT NULL,
    raga TEXT DEFAULT 'Unknown',
    beat TEXT DEFAULT 'Unknown', -- Tala (e.g. Adi, Keherwa)
    lyrics TEXT NOT NULL,
    audio_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_title_deity UNIQUE (title, deity)
);
```

#### Key Constraints and Rationale:
- **`id`**: Autoincremented integer primary key.
- **`unique_title_deity` UNIQUE CONSTRAINT**: Combines `title` and `deity` to define record uniqueness. This ensures duplicate prevention during ingestion (e.g., preventing two entries of "Ganesha Sharanam" associated with "Ganesha", while allowing another deity's song if titled similarly).
- **`lyrics` and `title`**: Marked `NOT NULL` to ensure data integrity, since a bhajan requires lyrics and a name.
- **Indexes**:
  - `CREATE INDEX IF NOT EXISTS idx_bhajans_deity ON bhajans(deity);`
  - `CREATE INDEX IF NOT EXISTS idx_bhajans_raga ON bhajans(raga);`
  - `CREATE INDEX IF NOT EXISTS idx_bhajans_beat ON bhajans(beat);`
  These single-column indexes speed up queries filtered by deity, raga, or beat.

### 1.2 The `bhajans_fts` Virtual Table
SQLite's built-in **FTS5** extension allows indexing of text columns for fast search. We create an external content virtual table that indexes the `title` and `lyrics` columns of our primary `bhajans` table.

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS bhajans_fts USING fts5(
    title,
    lyrics,
    content='bhajans',
    content_rowid='id'
);
```

#### FTS5 Sync Triggers:
To ensure the search index automatically updates when records are inserted, updated, or deleted in the main `bhajans` table, we define the following triggers:

```sql
-- Trigger: Keep FTS updated on insert
CREATE TRIGGER IF NOT EXISTS bhajans_ai AFTER INSERT ON bhajans BEGIN
    INSERT INTO bhajans_fts(rowid, title, lyrics) VALUES (new.id, new.title, new.lyrics);
END;

-- Trigger: Keep FTS updated on delete
CREATE TRIGGER IF NOT EXISTS bhajans_ad AFTER DELETE ON bhajans BEGIN
    INSERT INTO bhajans_fts(bhajans_fts, rowid, title, lyrics) VALUES('delete', old.id, old.title, old.lyrics);
END;

-- Trigger: Keep FTS updated on update
CREATE TRIGGER IF NOT EXISTS bhajans_au AFTER UPDATE ON bhajans BEGIN
    INSERT INTO bhajans_fts(bhajans_fts, rowid, title, lyrics) VALUES('delete', old.id, old.title, old.lyrics);
    INSERT INTO bhajans_fts(rowid, title, lyrics) VALUES (new.id, new.title, new.lyrics);
END;
```

---

## 2. Offline Scraper Strategy (CODE_ONLY)

Under CODE_ONLY network constraints, external internet access is disabled. To verify the scraper's HTML parsing logic instead of just loading pre-formatted JSON, we propose an offline filesystem-based scraping strategy that mirrors web scraping.

### 2.1 File Storage Structure
We propose placing mock data inside the `backend/mock_data/` directory:
- `backend/mock_data/index.html`: Contains links to the detail pages of all 50 bhajans.
- `backend/mock_data/bhajans/bhajan_1.html` to `bhajan_50.html`: Detail pages containing structured elements for each of the 50 bhajans.

### 2.2 Representative HTML Layout for detail pages (`bhajan_1.html`)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Ganesha Sharanam</title>
</head>
<body>
    <div class="bhajan-container">
        <h1 class="bhajan-title">Ganesha Sharanam</h1>
        <div class="bhajan-metadata">
            <span class="meta-label">Deity:</span> <span class="bhajan-deity">Ganesha</span><br/>
            <span class="meta-label">Raga:</span> <span class="bhajan-raga">Hamsadhwani</span><br/>
            <span class="meta-label">Beat:</span> <span class="bhajan-beat">Adi</span>
        </div>
        <div class="bhajan-lyrics-section">
            <h2>Lyrics</h2>
            <pre class="bhajan-lyrics">
Ganesha Sharanam Parama Pavanam
Sadguru Sharanam Bhava Bhaya Haranam
Vighna Vinashaka Harana Gajanana
Prathama Vandana Sri Gajanana
            </pre>
        </div>
        <div class="bhajan-audio-section">
            <audio id="bhajan-player" src="https://example.com/audio/ganesha_sharanam.mp3"></audio>
        </div>
    </div>
</body>
</html>
```

### 2.3 Scraper Parsing Strategy (`backend/scraper.py`)
The scraper reads the offline HTML index, compiles a list of local file links, reads each file from the disk, and parses the HTML using BeautifulSoup (`bs4`).

```python
import os
from pathlib import Path
from bs4 import BeautifulSoup

def scrape_offline_bhajans(mock_data_dir: str) -> list:
    """
    Simulates scraping by parsing local mock HTML files.
    Returns a list of bhajan data dictionaries.
    """
    mock_path = Path(mock_data_dir)
    index_file = mock_path / "index.html"
    
    if not index_file.exists():
        raise FileNotFoundError(f"Mock index file not found at {index_file}")
        
    with open(index_file, "r", encoding="utf-8") as f:
        index_soup = BeautifulSoup(f.read(), "html.parser")
        
    # Find all links pointing to details pages
    links = [a['href'] for a in index_soup.find_all('a') if 'href' in a.attrs]
    
    bhajans = []
    for link in links:
        # Resolve path relative to index file
        file_path = mock_path / link
        if not file_path.exists():
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            detail_soup = BeautifulSoup(f.read(), "html.parser")
            
        title = detail_soup.find("h1", class_="bhajan-title").text.strip()
        deity = detail_soup.find("span", class_="bhajan-deity").text.strip()
        
        # Optional fields
        raga_elem = detail_soup.find("span", class_="bhajan-raga")
        raga = raga_elem.text.strip() if raga_elem else "Unknown"
        
        beat_elem = detail_soup.find("span", class_="bhajan-beat")
        beat = beat_elem.text.strip() if beat_elem else "Unknown"
        
        lyrics = detail_soup.find("pre", class_="bhajan-lyrics").text.strip()
        
        audio_elem = detail_soup.find("audio")
        audio_url = audio_elem['src'].strip() if (audio_elem and 'src' in audio_elem.attrs) else ""
        
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

## 3. Database Interface API (`backend/database.py`)

To communicate between the scraper/search modules and the database, the `backend/database.py` module exposes three primary functions: `init_db()`, `save_bhajan()`, and `search_bhajans()`.

### 3.1 `init_db`
Initializes the database, creating the main table, search index, and required triggers.

```python
import sqlite3

def init_db(db_path: str = "bhajans.db"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create Main Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bhajans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                deity TEXT NOT NULL,
                raga TEXT DEFAULT 'Unknown',
                beat TEXT DEFAULT 'Unknown',
                lyrics TEXT NOT NULL,
                audio_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_title_deity UNIQUE (title, deity)
            );
        """)
        
        # Indexes for filter fields
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_deity ON bhajans(deity);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_raga ON bhajans(raga);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_beat ON bhajans(beat);")
        
        # Create FTS5 Table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS bhajans_fts USING fts5(
                title,
                lyrics,
                content='bhajans',
                content_rowid='id'
            );
        """)
        
        # Create FTS Triggers
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
```

### 3.2 `save_bhajan` (Duplicate Protection)
Handles insertion using the SQLite **UPSERT** syntax to update records if a duplicate is found.

```python
def save_bhajan(bhajan_data: dict, db_path: str = "bhajans.db") -> int:
    """
    Saves a bhajan dict to the SQLite database.
    Prevents duplication using ON CONFLICT(title, deity) DO UPDATE.
    Returns the row ID of the inserted or updated record.
    """
    query = """
        INSERT INTO bhajans (title, deity, raga, beat, lyrics, audio_url)
        VALUES (:title, :deity, :raga, :beat, :lyrics, :audio_url)
        ON CONFLICT(title, deity) DO UPDATE SET
            raga = excluded.raga,
            beat = excluded.beat,
            lyrics = excluded.lyrics,
            audio_url = excluded.audio_url
        RETURNING id;
    """
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, bhajan_data)
        row = cursor.fetchone()
        conn.commit()
        return row[0] if row else None
```

### 3.3 `search_bhajans`
Supports combining structured filtering and full-text querying.

```python
def search_bhajans(query: str = None, deity: str = None, raga: str = None, beat: str = None, db_path: str = "bhajans.db") -> list:
    """
    Searches and filters bhajans using FTS5 for query and direct lookup for filters.
    Returns a list of matching bhajan dictionaries.
    """
    conditions = []
    params = {}
    
    if query:
        # Match using FTS5 table
        conditions.append("id IN (SELECT rowid FROM bhajans_fts WHERE bhajans_fts MATCH :query)")
        params['query'] = query
        
    if deity:
        conditions.append("deity = :deity")
        params['deity'] = deity
        
    if raga:
        conditions.append("raga = :raga")
        params['raga'] = raga
        
    if beat:
        conditions.append("beat = :beat")
        params['beat'] = beat
        
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"SELECT id, title, deity, raga, beat, lyrics, audio_url FROM bhajans{where_clause}"
    
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
```

---

## 4. Programmatic Unit Test Plan (`tests/test_db.py`)

A comprehensive pytest suite is planned to assert DB initialization, scraper extraction accuracy, duplicate protection mechanisms, and search functionality.

### 4.1 Pytest Fixtures
- `temp_db_path`: Uses pytest's `tmp_path` fixture to supply a database path isolated to each test function.
- `mock_html_dir`: Generates the mock index file and 50 mock detail HTML files in a temporary folder structure.

### 4.2 Test Suite Layout (`tests/test_db.py`)
```python
import pytest
import sqlite3
from pathlib import Path
from backend.database import init_db, save_bhajan, search_bhajans
from backend.scraper import scrape_offline_bhajans

@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test_bhajans.db"
    init_db(str(db_path))
    return str(db_path)

@pytest.fixture
def mock_html_dir(tmp_path):
    """
    Creates a temporary mock_data directory with index.html and 50 bhajan details pages.
    """
    mock_dir = tmp_path / "mock_data"
    mock_dir.mkdir()
    
    # Generate 50 mock pages
    links_html = []
    for i in range(1, 51):
        filename = f"bhajans/bhajan_{i}.html"
        (mock_dir / "bhajans").mkdir(exist_ok=True)
        
        detail_html = f"""
        <html>
        <body>
            <h1 class="bhajan-title">Bhajan Title {i}</h1>
            <span class="bhajan-deity">Deity_{ (i % 5) + 1 }</span>
            <span class="bhajan-raga">Raga_{ (i % 3) + 1 }</span>
            <span class="bhajan-beat">Beat_{ (i % 2) + 1 }</span>
            <pre class="bhajan-lyrics">Lyrics of bhajan number {i} with search_keyword_{i}. Sing praise!</pre>
            <audio src="https://example.com/audio/bhajan_{i}.mp3"></audio>
        </body>
        </html>
        """
        with open(mock_dir / filename, "w", encoding="utf-8") as f:
            f.write(detail_html)
        links_html.append(f'<li><a href="{filename}">Bhajan {i}</a></li>')
        
    index_html = f"""
    <html>
    <body>
        <ul>
            {"".join(links_html)}
        </ul>
    </body>
    </html>
    """
    with open(mock_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
        
    return str(mock_dir)

def test_db_initialization(temp_db):
    """Assert that schema elements (tables, indexes, triggers) were successfully generated."""
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        assert "bhajans" in tables
        assert "bhajans_fts" in tables
        
        # Verify triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
        triggers = [row[0] for row in cursor.fetchall()]
        assert "bhajans_ai" in triggers
        assert "bhajans_ad" in triggers
        assert "bhajans_au" in triggers

def test_save_bhajan_and_duplicate_protection(temp_db):
    """Assert that save_bhajan inserts new entries and updates on conflict instead of duplicating."""
    bhajan = {
        "title": "Ganesha Sharanam",
        "deity": "Ganesha",
        "raga": "Hamsadhwani",
        "beat": "Adi",
        "lyrics": "First set of lyrics",
        "audio_url": "https://example.com/audio1.mp3"
    }
    
    # Save first time
    id_1 = save_bhajan(bhajan, temp_db)
    assert id_1 is not None
    
    # Verify insert
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bhajans")
        assert cursor.fetchone()[0] == 1
        
    # Save duplicate with updated lyrics/url
    bhajan_duplicate = bhajan.copy()
    bhajan_duplicate["lyrics"] = "Updated lyrics"
    bhajan_duplicate["audio_url"] = "https://example.com/audio2.mp3"
    
    id_2 = save_bhajan(bhajan_duplicate, temp_db)
    assert id_2 == id_1  # Should return the same row ID
    
    # Verify count is still 1 and values updated (UPSERT check)
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*), lyrics, audio_url FROM bhajans")
        count, lyrics, audio_url = cursor.fetchone()
        assert count == 1
        assert lyrics == "Updated lyrics"
        assert audio_url == "https://example.com/audio2.mp3"

def test_scraper_population_and_idempotency(temp_db, mock_html_dir):
    """Asserts that exactly 50 records are created, populated fully, and running scraper twice doesn't duplicate."""
    # Run scraper
    scraped_bhajans = scrape_offline_bhajans(mock_html_dir)
    assert len(scraped_bhajans) == 50
    
    # Populate DB
    for b in scraped_bhajans:
        save_bhajan(b, temp_db)
        
    # Verify 50 inserted
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bhajans")
        assert cursor.fetchone()[0] == 50
        
        # Verify metadata is not null or default empty
        cursor.execute("SELECT title, deity, raga, beat, lyrics, audio_url FROM bhajans")
        rows = cursor.fetchall()
        for row in rows:
            assert all(x is not None and str(x).strip() != "" for x in row)
            
    # Run population again (Idempotency check)
    for b in scraped_bhajans:
        save_bhajan(b, temp_db)
        
    # Verify count is still 50
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bhajans")
        assert cursor.fetchone()[0] == 50

def test_fts_search_behavior(temp_db):
    """Verifies that full-text searching matching title/lyrics works correctly via search_bhajans API."""
    bhajan_1 = {
        "title": "Ganesha Sharanam",
        "deity": "Ganesha",
        "raga": "Hamsadhwani",
        "beat": "Adi",
        "lyrics": "Bhava Bhaya Haranam Sadguru Sharanam Gajanana",
        "audio_url": "https://example.com/1.mp3"
    }
    bhajan_2 = {
        "title": "Shiva Shambho",
        "deity": "Shiva",
        "raga": "Bhairavi",
        "beat": "Keherwa",
        "lyrics": "Hara Hara Shankara Mahadeva Shambho Ganga Dhara",
        "audio_url": "https://example.com/2.mp3"
    }
    
    save_bhajan(bhajan_1, temp_db)
    save_bhajan(bhajan_2, temp_db)
    
    # Match query 'Sharanam' (in bhajan 1 lyrics)
    res = search_bhajans(query="Sharanam", db_path=temp_db)
    assert len(res) == 1
    assert res[0]["title"] == "Ganesha Sharanam"
    
    # Match query 'Shambho' (in bhajan 2 title/lyrics)
    res2 = search_bhajans(query="Shambho", db_path=temp_db)
    assert len(res2) == 1
    assert res2[0]["title"] == "Shiva Shambho"
    
    # Filter by deity without query
    res3 = search_bhajans(deity="Shiva", db_path=temp_db)
    assert len(res3) == 1
    assert res3[0]["title"] == "Shiva Shambho"
```

---

## 5. Summary Index of 50 Representative Bhajans

Here is the table of the 50 representative bhajans proposed to populate the mock HTML files, ensuring a rich set of data for raga, deity, and beat filters:

| # | Title | Deity | Raga | Beat (Tala) | Lyrics Keyword (for search) |
|---|---|---|---|---|---|
| 1 | Ganesha Sharanam | Ganesha | Hamsadhwani | Adi | Parama Pavanam Sadguru Sharanam |
| 2 | He Shiva Shankara | Shiva | Bhairavi | Keherwa | Ganga Dhara Hara He Parameshvara |
| 3 | Devi Bhavani Maa | Devi | Durga | Keherwa | Jagadamba Bhavani Maa Durga |
| 4 | Rama Nama Payasam | Rama | Anandabhairavi | Adi | Krishna Nama Sakkare Vitthala |
| 5 | Govinda Krishna Jai | Krishna | Yaman | Dadra | Gopika Vallabha Roopini Jai |
| 6 | Sai Maa Jagadamba | Sai | Yaman | Keherwa | Janani Sathya Sai Maha Devi |
| 7 | Sri Ganesha Vinayaka | Ganesha | Hamsadhwani | Roopak | Parvati Nandana Siddhi Vinayaka |
| 8 | Shankara Sadashiva | Shiva | Darbari | Adi | Kailasa Vasi Chandrashekhara |
| 9 | Janani Maa Durga | Devi | Bhupali | Keherwa | Simhavahini Durga Bhavani |
| 10 | Raghupati Raghav Raja Ram | Rama | Mishra Kafi | Keherwa | Patita Pavana Sita Ram |
| 11 | Radhe Govinda Gopala | Krishna | Yaman | Dadra | Bhaja Mana Panduranga Vitthala |
| 12 | Sai Baba Bolo | Sai | Mishra Pilu | Keherwa | Sathya Sai Baba Mukunda Hare |
| 13 | Jai Jai Hanuman | Hanuman | Bhupali | Keherwa | Pavanaputra Sankat Haran |
| 14 | Ganesha Sharanam Parama Pavanam | Ganesha | Jog | Keherwa | Sadguru Sharanam Bhava Bhaya Haranam |
| 15 | Shiva Shiva Shambho | Shiva | Shivaranjani | Adi | Hara Hara Shankara Mahadeva |
| 16 | Amba Parameshwari | Devi | Kalyani | Adi | Akhilandeswari Rajeshwari |
| 17 | Sri Rama Chandra Kripalu | Rama | Yaman | Adi | Bhaju Mana Harana Bhava Bhaya |
| 18 | Hari Bolo Hare Krishna | Krishna | Bhupali | Keherwa | Gopala Hari Govinda Bolo |
| 19 | Love Is God | Sai | Mixed | Keherwa | Live In Love And Be Peaceful |
| 20 | Anjaneya Veera | Hanuman | Madhyamavati | Adi | Sankata Harana Maruthi |
| 21 | Vighneshvara Vinayaka | Ganesha | Hamsadhwani | Keherwa | Gajanana Hey Shubhanana |
| 22 | Om Namah Shivaya | Shiva | Bhairavi | Keherwa | Shiva Shiva Shankara Hara |
| 23 | Durge Devi Namo Namah | Devi | Durga | Keherwa | Mahishasura Mardini Jaya Jaya |
| 24 | Ramachandra Prabhu | Rama | Mishra Kafi | Keherwa | Raghuvira Ranadhira Janaki Ram |
| 25 | Krishna Mukunda Murari | Krishna | Yaman | Dadra | Devaki Nandana Gopala |
| 26 | Sai Ram Sai Shyam | Sai | Mishra Kafi | Keherwa | Shirdi Ke Sai Parthi Ke Sai |
| 27 | Maruti Raya Hanumanta | Hanuman | Bhupali | Keherwa | Anjani Putra Sankata Harana |
| 28 | Prathama Vandana Ganesha | Ganesha | Hamsadhwani | Adi | Gajanana Vighna Vinashaka |
| 29 | Bholenath Mogra | Shiva | Darbari | Keherwa | Gangadhara Hara Bholenath |
| 30 | Amba Bhavani Sharade | Devi | Shankarabharanam | Adi | Jagadguru Pujita Sarada Maa |
| 31 | Ayodhya Vasi Ram | Rama | Keeravani | Keherwa | Dasharatha Nandana Sai Ram |
| 32 | Radhe Shyam Gopal | Krishna | Yaman | Dadra | Govinda Murari Hari Bol |
| 33 | Sadguru Deva Sai Ram | Sai | Bhupali | Keherwa | Parthi Purishvara Shirdi Vasi |
| 34 | Veeranjaneya Jai | Hanuman | Mohanam | Adi | Maruti Raya Pavana Suta |
| 35 | Ganesha Sharanam Sharanam | Ganesha | Hamsadhwani | Keherwa | Lambodara Jaya Vighneshvara |
| 36 | Hara Hara Shankara | Shiva | Shivaranjani | Keherwa | Samba Sadashiva Bholenath |
| 37 | Sarva Mangala Mangalye | Devi | Durga | Keherwa | Shive Sarvartha Sadhike Sharanye |
| 38 | Rama Kodanda Rama | Rama | Bhairavi | Adi | Janaki Vallabha Shrita Chintamani |
| 39 | Gopala Radha Lola | Krishna | Mishra Pilu | Keherwa | Radhe Shyam Govinda Jai |
| 40 | Sai Baba Pravah | Sai | Yaman | Keherwa | Sabka Malik Ek Allah Sai |
| 41 | Maruti Stotra Snippet | Hanuman | Bhupali | Keherwa | Rama Dootha Anjani Suta |
| 42 | Gajanana He Gajanana | Ganesha | Hamsadhwani | Dadra | Vighna Vinayaka Sai Gajanana |
| 43 | Shiva Om Namah Shivaya | Shiva | Darbari | Keherwa | Om Namah Shivaya Chandrashekhara |
| 44 | Sri Lakshmi Ramana | Devi | Kalyani | Adi | Narayani Namostute Maha Lakshmi |
| 45 | Ramakrishna Govinda | Krishna | Yaman | Keherwa | Bhaja Govinda Gopala Hari |
| 46 | Sai Prem Data | Sai | Mishra Kafi | Keherwa | Prema Swaroopa Sai Ram |
| 47 | Pavanaputra Hanuman | Hanuman | Jog | Keherwa | Sankat Mochan Maruti Raya |
| 48 | Gam Ganapataye Namaha | Ganesha | Hamsadhwani | Keherwa | Ganesha Mantra Siddhi Dayaka |
| 49 | Kailasavasi Shiva | Shiva | Bhairavi | Keherwa | Kailasa Parvata Vasi Shankara |
| 50 | Shradha Saburi Sai | Sai | Bhupali | Keherwa | Sai Baba Bhakti Mukti Prada |
