# Explorer Synthesis Report: Milestone 2 — Scraper & DB

This document synthesizes the designs, strategies, and verification plans proposed by the three Explorer subagents. It defines the final specification for implementing the database, offline scraper, and test suite.

---

## 1. SQLite Database Schema Specification

The database will be implemented in `backend/database.py` using SQLite (typically saved as `backend/bhajans.db`).

### 1.1 The `bhajans` Table
Stores the structured metadata, lyrics, and audio URLs.
- **Table Name**: `bhajans`
- **Columns**:
  - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
  - `title`: `TEXT NOT NULL`
  - `deity`: `TEXT NOT NULL`
  - `raga`: `TEXT DEFAULT 'Unknown'`
  - `beat`: `TEXT DEFAULT 'Unknown'` (Tala, e.g., Adi, Keherwa)
  - `lyrics`: `TEXT NOT NULL`
  - `audio_url`: `TEXT NOT NULL`
  - `created_at`: `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- **Constraints**:
  - `CONSTRAINT unique_title_deity UNIQUE (title, deity)`
  This constraint protects against duplicate records of the same bhajan under the same deity, while allowing different bhajans that might share a title.

### 1.2 Indexes for Performance
To optimize filtering for Milestone 3 (Advanced Search), create these indexes:
- `CREATE INDEX IF NOT EXISTS idx_bhajans_deity ON bhajans(deity);`
- `CREATE INDEX IF NOT EXISTS idx_bhajans_raga ON bhajans(raga);`
- `CREATE INDEX IF NOT EXISTS idx_bhajans_beat ON bhajans(beat);`

### 1.3 Full-Text Search (FTS5) Support
To support high-performance text search on titles and lyrics:
- **FTS Table**: `bhajans_fts` virtual table using FTS5:
  ```sql
  CREATE VIRTUAL TABLE IF NOT EXISTS bhajans_fts USING fts5(
      title,
      lyrics,
      content='bhajans',
      content_rowid='id'
  );
  ```
- **Sync Triggers**:
  ```sql
  CREATE TRIGGER IF NOT EXISTS bhajans_ai AFTER INSERT ON bhajans BEGIN
      INSERT INTO bhajans_fts(rowid, title, lyrics) VALUES (new.id, new.title, new.lyrics);
  END;

  CREATE TRIGGER IF NOT EXISTS bhajans_ad AFTER DELETE ON bhajans BEGIN
      INSERT INTO bhajans_fts(bhajans_fts, rowid, title, lyrics) VALUES('delete', old.id, old.title, old.lyrics);
  END;

  CREATE TRIGGER IF NOT EXISTS bhajans_au AFTER UPDATE ON bhajans BEGIN
      INSERT INTO bhajans_fts(bhajans_fts, rowid, title, lyrics) VALUES('delete', old.id, old.title, old.lyrics);
      INSERT INTO bhajans_fts(rowid, title, lyrics) VALUES (new.id, new.title, new.lyrics);
  END;
  ```

---

## 2. Offline Scraper Strategy (CODE_ONLY)

Under `CODE_ONLY` network restrictions, the scraper cannot access external websites.
- **Mock Data Source File**: A single HTML file located at `backend/mock_data/bhajans_source.html`.
- **Parser**: `backend/scraper.py` parses this local HTML file using `BeautifulSoup` (or falls back to standard library `html.parser` if BeautifulSoup is unavailable, though BeautifulSoup is preferred).
- **Selector Mapping**:
  - Cards: `div` with class `bhajan-card`
  - Title: `h2` with class `bhajan-title`
  - Deity: `span` with class `deity-name`
  - Raga: `span` with class `raga-name`
  - Beat: `span` with class `beat-name`
  - Lyrics: `div` with class `bhajan-lyrics` (replace `<br/>` with `\n` and trim whitespace)
  - Audio URL: `audio` tag with class `audio-player`, using the `src` attribute.

---

## 3. Database Interface API

In `backend/database.py`, expose these APIs:
1. `init_db(db_path: str)`: Initializes the database schema, indexes, and triggers.
2. `save_bhajan(bhajan_data: dict, db_path: str) -> int`: Saves a bhajan dictionary using SQLite `UPSERT` to implement duplicate protection:
   ```sql
   INSERT INTO bhajans (title, deity, raga, beat, lyrics, audio_url)
   VALUES (:title, :deity, :raga, :beat, :lyrics, :audio_url)
   ON CONFLICT(title, deity) DO UPDATE SET
       raga = excluded.raga,
       beat = excluded.beat,
       lyrics = excluded.lyrics,
       audio_url = excluded.audio_url
   RETURNING id;
   ```
3. `get_all_bhajans(db_path: str) -> list`: Queries all bhajans.
4. `search_bhajans(query: str, deity: str, raga: str, beat: str, db_path: str) -> list`: Implements the search combining FTS5 and structured metadata filtering.

---

## 4. Test and Verification Plan (`tests/test_db.py`)

Create `tests/test_db.py` using `pytest`. The test suite must cover:
1. **Schema Check**: Table creation, column properties, indexes, and triggers.
2. **Parser Check**: Parsing a snippet of HTML to ensure BeautifulSoup extraction works correctly.
3. **Database Insertion & Validation**: Verifying fields are stored, and missing fields raise errors.
4. **Duplicate Protection**: Inserting the same bhajan title/deity with updated lyrics, asserting that the record count remains 1 and the lyrics are updated.
5. **E2E Integration & Idempotency**: Parsing the full mock HTML data of 50 bhajans, populating the database, verifying exactly 50 records exist with no empty fields, and verifying that rerunning the scraper keeps the count at exactly 50.

---

## 5. Seed Dataset: 50 Representative Bhajans

The worker should generate `backend/mock_data/bhajans_source.html` containing these 50 bhajans:

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
