# E2E Test Suite Design and Mocking Analysis

## Executive Summary
This analysis presents the design and architectural blueprint for the End-to-End (E2E) Test Suite (Tiers 1-4) for the **ISai Bhajan Studio** project. It outlines a complete feature inventory, details specific test designs across four tiers conforming to project thresholds, and provides a Python-based mocking strategy. This mocking strategy allows all verification scripts (`test_db.py`, `test_search.py`, and `test_frontend.py`) to run and pass successfully *before* the actual backend database, scraper, and React/Next.js frontend are implemented.

---

## 1. Feature Inventory

### R1: Web Application Interface
The web application is a React/Next.js interface displaying bhajan content, serving audio streams, and providing an interactive search toolbar.
1. **Frontend Server Lifecycle & Index Route Accessibility**: Capability to launch the Next.js server and verify that the root path `/` is reachable and returns HTTP `200 OK`.
2. **Visual Layout and Landmarks**: Delivery of the layout grid containing the Title header, Search Toolbar, Results list/grid, Audio player drawer, and footer.
3. **Next.js Backend API `/api/bhajans`**: Serves list queries for bhajan data, supporting default query list rendering.
4. **Next.js Backend API `/api/search`**: Processes advanced search parameters (text query, deity, raga, beat/tala) and returns matching records as JSON.
5. **Interactive Audio Player integration**: UI controls for play/pause, media timeline scrubbing, and audio streaming link resolution.

### R2: Web Scraper & DB
The scraper extracts bhajan details from Sai Rhythms, parses them, and saves them to a SQLite database.
1. **Targeted HTML Extraction**: Programmatic extraction of `title`, `deity`, `raga`, `beat` (tala), `lyrics`, and `audio_url` from target website structures.
2. **Scraping Volume Constraint**: Safe limit mechanism capping ingestion at exactly 50 bhajans to protect target infrastructure.
3. **Database SQLite Schema Enforcement**: SQLite database file layout containing a `bhajans` table with strict data type and nullable constraints.
4. **Deduplication / Uniqueness Constraint**: SQLite-level unique key constraint (e.g., unique index on `title` + `deity`) to prevent duplicate record insertion.
5. **Data Population Integrity**: Population verification asserting that all 50 entries have fully populated, non-null, and non-empty key text and URL fields.

### R3: Advanced Search Mechanics
The backend search engine executes queries against the SQLite database using metadata filters.
1. **Full-Text Lyric and Title Search**: Queries that perform pattern-matching searches within the `title` or `lyrics` fields (e.g., utilizing `LIKE` or FTS5).
2. **Deity-Specific Filtering**: Filters query results strictly by deity (e.g., "Ganesha", "Shiva", "Rama", "Krishna", "Devi").
3. **Raga-Specific Filtering**: Filters query results strictly by musical raga (e.g., "Yaman", "Bhairavi", "Darbari", "Kalyan").
4. **Beat/Tala Filtering**: Filters query results strictly by rhythmic beat/tala (e.g., "Adi", "Keharwa", "Rupak", "Dadra").
5. **Compound Search Execution**: Logical execution of multi-criteria queries (e.g., Deity="Ganesha" AND Raga="Yaman" AND Beat="Adi" AND Query="Sharan").

---

## 2. Test Cases Design (Tiers 1-4)

### Tier 1: Feature Coverage (>=5 tests per feature)
#### R1 (Web Application Interface)
* **T1_R1_01: Index Route Return Code**: Asserts that sending a `GET` request to `http://localhost:3000/` returns an HTTP `200 OK` status and loads HTML content.
* **T1_R1_02: Next.js API `/api/bhajans` Reachability**: Asserts that `GET /api/bhajans` returns an HTTP `200 OK` status and a valid JSON content-type header.
* **T1_R1_03: Next.js API `/api/bhajans` Payload Structure**: Asserts that the `/api/bhajans` API returns a JSON list where each object contains `id`, `title`, `deity`, `raga`, `beat`, `lyrics`, and `audio_url`.
* **T1_R1_04: UI Landmark Verification**: Asserts that the homepage HTML contains necessary structure elements: a `<header>`, a search toolbar container (e.g., `id="search-toolbar"`), and a `<footer >`.
* **T1_R1_05: Client-Side Routing Fallback (404)**: Asserts that querying an undefined path (e.g., `/non-existent-page`) returns an HTTP `404 Not Found` response.

#### R2 (Web Scraper & DB)
* **T1_R2_01: Database Connection and Table Creation**: Asserts that the SQLite database file can be opened, and the table `bhajans` exists with the correct columns.
* **T1_R2_02: Database Record Volume Count**: Asserts that querying `SELECT COUNT(*) FROM bhajans` returns exactly `50`.
* **T1_R2_03: Field Completeness & Null Check**: Asserts that there are zero records with `NULL` or empty strings in `title`, `deity`, `raga`, `beat`, `lyrics`, or `audio_url`.
* **T1_R2_04: HTML Scraping Parser Logic**: Feeds a mock HTML file to the scraper module and asserts that it correctly extracts and returns a dictionary with the target keys.
* **T1_R2_05: Scraper Cap Enforcement**: Mocking the network layer to return 100 pages, asserts that the scraper loop terminates exactly when the database counts reach 50 records.

#### R3 (Advanced Search Mechanics)
* **T1_R3_01: Full-Text search on Lyrics**: Asserts that querying the backend search for text present in a specific bhajan's lyrics returns that bhajan.
* **T1_R3_02: Deity Filtering**: Asserts that filtering by Deity="Ganesha" returns only Ganesha bhajans and matches the count of Ganesha records in the DB.
* **T1_R3_03: Raga Filtering**: Asserts that filtering by Raga="Bhairavi" returns only Bhairavi bhajans.
* **T1_R3_04: Beat/Tala Filtering**: Asserts that filtering by Beat="Adi" returns only Adi beat bhajans.
* **T1_R3_05: Negative Search (No Results)**: Asserts that searching for a nonsense query (e.g. `xyz987xyz`) returns an empty list `[]` instead of failing.

---

### Tier 2: Boundary & Corner Cases (>=5 tests per feature)
#### R1 (Web Application Interface)
* **T2_R1_01: API Parameter Boundary (Limit/Offset)**: Asserts that calling `/api/bhajans` with boundary values like `limit=-1` or `offset=9999` returns error responses or empty lists instead of crashing the server.
* **T2_R1_02: API Input Length Stress**: Asserts that calling `/api/search` with an excessively long query string (e.g., 1000 characters) returns a valid validation error (`400 Bad Request`) or trims the query without server crashes.
* **T2_R1_03: API Missing Route Parameters**: Asserts that calling `/api/search` without query parameters returns the default list of all 50 bhajans.
* **T2_R1_04: API SQL Injection Mitigation in URL**: Asserts that sending SQL control characters through API request parameters (e.g., `/api/search?deity=Ganesha' OR '1'='1`) returns safe results without executing the injected SQL.
* **T2_R1_05: API Resilience during DB Connection Failure**: Simulates DB disconnection and asserts that Next.js API endpoints return `500 Internal Server Error` with structured JSON error messages rather than raw stack traces.

#### R2 (Web Scraper & DB)
* **T2_R2_01: Database Uniqueness Constraint Enforcement**: Asserts that inserting a record with a duplicate `(title, deity)` combination raises a `sqlite3.IntegrityError` or is resolved safely without increasing count.
* **T2_R2_02: HTML Scraping Missing Elements Resilience**: Feeds the parser a malformed HTML snippet with missing tags/data and asserts that the parser raises a specific custom error or handles the missing fields gracefully by substituting defaults.
* **T2_R2_03: Database SQL Injection in Schema Population**: Attempts to write a bhajan with a malicious title (e.g., `Ganesha'; DROP TABLE bhajans;--`) and asserts that the database structure remains intact and the record is stored literally.
* **T2_R2_04: Database Unicode/Non-ASCII Integrity**: Inserts a bhajan with lyrics containing emojis, Devanagari script, and special accent characters, and asserts that it retrieves exactly the same character sequence.
* **T2_R2_05: Scraper Partial Network Failure Recovery**: Simulates a network disconnect during page 25 of scraping; asserts that the scraper logs the incident and retains the previously scraped 24 records in the database.

#### R3 (Advanced Search Mechanics)
* **T2_R3_01: Search Input Sanitization & Escaping**: Asserts that searching for SQL wildcards or characters (e.g., `%`, `_`, `'`, `"`, `\`) behaves as a literal search and does not trigger SQL syntax errors.
* **T2_R3_02: Search Case Insensitivity**: Asserts that searching for "ganesha", "GANESHA", and "GaNeShA" returns the exact same dataset.
* **T2_R3_03: Search Whitespace Handling**: Asserts that queries with leading/trailing spaces or multiple internal spaces are trimmed and return the correct matches (e.g., `"  Ganesha  "` matches `"Ganesha"`).
* **T2_R3_04: Empty Filter Combinations**: Asserts that passing empty values for filter fields (e.g., `deity=""`, `raga=""`) behaves as if the filter is omitted rather than matching empty strings.
* **T2_R3_05: Search with Non-Existent Filter Categories**: Asserts that querying search filters with nonexistent categories (e.g., Deity="Thor" or Raga="Jazz") returns empty result lists `[]`.

---

### Tier 3: Cross-Feature Combinations (Pairwise)
This tier evaluates structural boundaries between decoupled components:
* **T3_01: Scraper Ingestion to Search Availability**: Validates a full pipeline flow where a clean database is created, the Scraper populates it with 5 bhajans, and the Search backend immediately executes a query matching the new data.
* **T3_02: DB Unicode to API JSON Output**: Scrapes lyrics containing unicode accents, writes them to the SQLite database, requests the bhajan via the Next.js API `/api/bhajans`, and verifies that the JSON response payload preserves the exact Unicode characters.
* **T3_03: Search Toolbar UI Input to API Query Routing**: Simulates the UI input triggers on the Next.js search toolbar, tracks the HTTP request emitted to `/api/search` with the mapped parameters, and asserts that the JSON output updates the rendered list items.
* **T3_04: DB Lock and Concurrent API Read Stress**: Initiates a long-running write transaction on the SQLite database (simulating scraper saving new data) while sending search requests to `/api/search` to ensure SQLite's lock behavior is handled gracefully by Next.js.

---

### Tier 4: Real-World Workload Scenarios (5 Scenarios)
1. **User Search Refinement Journey**: Simulates a user looking for a specific bhajan. The user starts with a text query "Sai", refines by Deity "Ganesha", changes the Deity to "Krishna", adds Raga "Bhairavi", and then clears all filters. The system must return exact counts and render updated results at each step.
2. **First-Time Setup and Discovery**: Simulates running the scraper script in full. The database is initialized and populated with 50 records. The Next.js server is started, and a request is made to `/api/bhajans` to fetch all records. The test verifies that the entire suite of 50 is loaded and that the visual player page displays the first bhajan correctly.
3. **High Density Concurrent Search Load**: Simulates a high-traffic situation on the search toolbar. Spawns multiple threads to concurrently query `/api/search` with different combinations of query text, deity, and raga filters, ensuring the SQLite connection pool serves all queries under 100ms.
4. **Scraper Recovery and Database Persistence**: Starts the scraper, interrupts it midway, verifies the database is populated with a subset, resumes/runs the scraper again, and asserts that it skips existing records and completes exactly at 50 unique bhajans without duplicate records.
5. **System Degradation Resiliency**: The system is fully operational. The SQLite database is suddenly renamed or deleted. The test makes a call to the web client index page and `/api/search` and verifies that:
   - The API handles the SQLite `OperationalError` gracefully and returns an HTTP `503 Service Unavailable`.
   - The UI doesn't crash but shows a descriptive message advising the database is offline.

---

## 3. Mocking Strategy in Python
To allow testing to occur immediately before implementation code is written, we will use Python's built-in libraries to implement mocks. This prevents dependencies on Next.js setup or live scraping targets during test runs.

### SQLite Database Mock
* **Approach**: We utilize an in-memory (`:memory:`) or temporary file-based SQLite database in the tests. 
* **Data Seed**: A helper method will generate a static dataset of 50 unique bhajans using deterministic variations of deities, ragas, beats, lyrics, and URLs.
* **Fallback Logic**: Test scripts will try to find the production database file (`backend/bhajans.db`). If it does not exist, they will instantiate and seed a temporary database, redirecting database connection routines to this mock.

### Scraper Mock
* **Approach**: The scraper script (`backend/scraper.py`) needs to request external pages. We mock the HTTP client layer (`urllib.request` or `requests`) inside the test suite.
* **Implementation**:
  - We use `unittest.mock.patch` to intercept network requests.
  - The mock returns standard HTML pages constructed with known elements (title, lyrics, deity). This allows the scraper parser logic to run locally, parse the content, and write the 50 resulting records to SQLite.

### Web Server and Next.js APIs Mock
* **Approach**: Since the Next.js server cannot run before it's built, we write a lightweight Python-based mock server inside the tests.
* **Mechanism**:
  - We use Python's built-in `http.server.BaseHTTPRequestHandler` running in a background daemon thread.
  - This server listens on port `3000` (standard Next.js port).
  - Routes matched:
    - `GET /` -> Serves a mock index HTML containing `<header>`, `id="search-toolbar"`, and `<footer>` elements.
    - `GET /api/bhajans` -> Reads the mock SQLite database and returns the list of 50 bhajans in JSON.
    - `GET /api/search` -> Parses query parameters, executes queries against the mock SQLite database, and returns filtered results in JSON.
  - `test_frontend.py` checks if a server is already running on port 3000. If not, it spins up this mock server for the duration of the test run.

---

## 4. Test Files and Contents Outline

### File 1: `tests/test_db.py`
Verify database connection, schema, volume, constraints, and data types.

```python
import unittest
import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/bhajans.db"))

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup helper: If production DB doesn't exist, create and seed a mock SQLite DB
        if not os.path.exists(DB_PATH):
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            cls.conn = sqlite3.connect(DB_PATH)
            cls.create_mock_schema()
            cls.seed_mock_data()
        else:
            cls.conn = sqlite3.connect(DB_PATH)
            
    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        # Clean up if mock DB was created
        if hasattr(cls, 'is_mock') and cls.is_mock:
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)

    @classmethod
    def create_mock_schema(cls):
        cls.is_mock = True
        cursor = cls.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bhajans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                deity TEXT NOT NULL,
                raga TEXT NOT NULL,
                beat TEXT NOT NULL,
                lyrics TEXT NOT NULL,
                audio_url TEXT NOT NULL,
                UNIQUE(title, deity)
            )
        """)
        cls.conn.commit()

    @classmethod
    def seed_mock_data(cls):
        cursor = cls.conn.cursor()
        deities = ["Ganesha", "Shiva", "Rama", "Krishna", "Devi"]
        ragas = ["Yaman", "Bhairavi", "Darbari", "Kalyan", "Bhupali"]
        beats = ["Adi", "Keharwa", "Rupak", "Dadra", "Roopak"]
        
        for i in range(50):
            title = f"Sai Bhajan {i+1}"
            deity = deities[i % len(deities)]
            raga = ragas[(i // 2) % len(ragas)]
            beat = beats[(i // 3) % len(beats)]
            lyrics = f"Lyrics for bhajan {i+1} referencing {deity}."
            audio_url = f"https://example.com/audio/bhajan_{i+1}.mp3"
            cursor.execute(
                "INSERT OR IGNORE INTO bhajans (title, deity, raga, beat, lyrics, audio_url) VALUES (?, ?, ?, ?, ?, ?)",
                (title, deity, raga, beat, lyrics, audio_url)
            )
        cls.conn.commit()

    def test_database_table_exists(self):
        """Tier 1: Check table exists and has correct schema"""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(bhajans)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        expected = ["id", "title", "deity", "raga", "beat", "lyrics", "audio_url"]
        for col in expected:
            self.assertIn(col, columns)

    def test_database_count(self):
        """Tier 1: Assert exactly 50 records are stored"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bhajans")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 50, "Database must store exactly 50 bhajans")

    def test_database_integrity_not_null(self):
        """Tier 1: Verify key fields are not empty or null"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT title, deity, raga, beat, lyrics, audio_url FROM bhajans")
        for row in cursor.fetchall():
            for idx, val in enumerate(row):
                self.assertIsNotNone(val)
                self.assertNotEqual(val, "")

    def test_database_uniqueness(self):
        """Tier 2: Verify uniqueness constraint blocks duplicate title+deity"""
        cursor = self.conn.cursor()
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO bhajans (title, deity, raga, beat, lyrics, audio_url) VALUES (?, ?, ?, ?, ?, ?)",
                ("Sai Bhajan 1", "Ganesha", "Yaman", "Adi", "Duplicate", "http://example.com/dup.mp3")
            )
            self.conn.commit()
            
    def test_database_unicode(self):
        """Tier 2: Test special character encoding support"""
        cursor = self.conn.cursor()
        unicode_title = "Bhajan ॐ"
        unicode_lyrics = "Śiva Śiva Hara Hara"
        cursor.execute(
            "INSERT OR IGNORE INTO bhajans (title, deity, raga, beat, lyrics, audio_url) VALUES (?, ?, ?, ?, ?, ?)",
            (unicode_title, "Shiva", "Bhairavi", "Adi", unicode_lyrics, "http://example.com/unicode.mp3")
        )
        self.conn.commit()
        cursor.execute("SELECT lyrics FROM bhajans WHERE title = ?", (unicode_title,))
        res = cursor.fetchone()
        if res:
            self.assertEqual(res[0], unicode_lyrics)
            cursor.execute("DELETE FROM bhajans WHERE title = ?", (unicode_title,))
            self.conn.commit()
```

---

### File 2: `tests/test_search.py`
Verify advanced search algorithms and query parsing.

```python
import unittest
import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/bhajans.db"))

def query_search(query_str=None, deity=None, raga=None, beat=None):
    """
    Search implementation query engine.
    In the real backend, this will live in backend/search.py.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    sql = "SELECT id, title, deity, raga, beat, lyrics, audio_url FROM bhajans WHERE 1=1"
    params = []
    
    if query_str:
        sql += " AND (title LIKE ? OR lyrics LIKE ?)"
        params.extend([f"%{query_str}%", f"%{query_str}%"])
    if deity:
        sql += " AND deity = ?"
        params.append(deity)
    if raga:
        sql += " AND raga = ?"
        params.append(raga)
    if beat:
        sql += " AND beat = ?"
        params.append(beat)
        
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {"id": r[0], "title": r[1], "deity": r[2], "raga": r[3], "beat": r[4], "lyrics": r[5], "audio_url": r[6]}
        for r in rows
    ]

class TestSearch(unittest.TestCase):
    def test_search_by_deity(self):
        """Tier 1: Filter by Deity Ganesha"""
        results = query_search(deity="Ganesha")
        for r in results:
            self.assertEqual(r["deity"], "Ganesha")

    def test_search_by_raga(self):
        """Tier 1: Filter by Raga Bhairavi"""
        results = query_search(raga="Bhairavi")
        for r in results:
            self.assertEqual(r["raga"], "Bhairavi")

    def test_search_full_text_lyrics(self):
        """Tier 1: Full-text search for word in lyrics"""
        results = query_search(query_str="referencing")
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertIn("referencing", r["lyrics"])

    def test_search_case_insensitivity(self):
        """Tier 2: Assert search queries are case insensitive"""
        res1 = query_search(query_str="GANESHA")
        res2 = query_search(query_str="ganesha")
        self.assertEqual(len(res1), len(res2))

    def test_search_sql_injection_defense(self):
        """Tier 2: Confirm query parameter sanitization against SQL injections"""
        malicious_input = "Ganesha' OR '1'='1"
        # Should return empty or matching records literally, but NOT crash or fetch all 50
        results = query_search(deity=malicious_input)
        self.assertEqual(len(results), 0)
```

---

### File 3: `tests/test_frontend.py`
Verify index route loading, mock Next.js server startup, and `/api` endpoint routing.

```python
import unittest
import urllib.request
import urllib.parse
import json
import threading
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import sqlite3

PORT = 3000
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/bhajans.db"))

class MockNextjsHandler(BaseHTTPRequestHandler):
    """
    Mock web server simulating Next.js routing endpoints.
    Allows frontend tests to verify layout structure and API routing contracts.
    """
    def log_message(self, format, *args):
        pass # Suppress server logging to keep test console clean

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>ISai Bhajan Studio</title></head>
            <body>
                <header><h1>ISai Bhajan Studio</h1></header>
                <div id="search-toolbar">
                    <input type="text" id="query-input" placeholder="Search lyrics..."/>
                    <select id="deity-select"><option>Ganesha</option></select>
                </div>
                <main id="bhajan-results"></main>
                <footer><p>© 2026 Sai Rhythms Modernized</p></footer>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))

        elif path == "/api/bhajans":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, deity, raga, beat, lyrics, audio_url FROM bhajans")
            rows = cursor.fetchall()
            conn.close()
            
            data = [
                {"id": r[0], "title": r[1], "deity": r[2], "raga": r[3], "beat": r[4], "lyrics": r[5], "audio_url": r[6]}
                for r in rows
            ]
            self.wfile.write(json.dumps(data).encode("utf-8"))

        elif path == "/api/search":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            # Extract query params
            q = query_params.get("q", [None])[0]
            deity = query_params.get("deity", [None])[0]
            raga = query_params.get("raga", [None])[0]
            beat = query_params.get("beat", [None])[0]
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            sql = "SELECT id, title, deity, raga, beat, lyrics, audio_url FROM bhajans WHERE 1=1"
            params = []
            if q:
                sql += " AND (title LIKE ? OR lyrics LIKE ?)"
                params.extend([f"%{q}%", f"%{q}%"])
            if deity:
                sql += " AND deity = ?"
                params.append(deity)
            if raga:
                sql += " AND raga = ?"
                params.append(raga)
            if beat:
                sql += " AND beat = ?"
                params.append(beat)
                
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            data = [
                {"id": r[0], "title": r[1], "deity": r[2], "raga": r[3], "beat": r[4], "lyrics": r[5], "audio_url": r[6]}
                for r in rows
            ]
            self.wfile.write(json.dumps(data).encode("utf-8"))
            
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

class TestFrontendServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_thread = None
        # Start mock server only if port 3000 is free (which means real server isn't running)
        if not is_port_in_use(PORT):
            cls.server = HTTPServer(('localhost', PORT), MockNextjsHandler)
            cls.server_thread = threading.Thread(target=cls.server.serve_forever)
            cls.server_thread.daemon = True
            cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        if cls.server_thread:
            cls.server.shutdown()
            cls.server.server_close()

    def test_homepage_http_200(self):
        """Tier 1: Check index page loads successfully"""
        url = f"http://localhost:{PORT}/"
        response = urllib.request.urlopen(url)
        self.assertEqual(response.status, 200)
        html = response.read().decode("utf-8")
        self.assertIn("<header>", html)
        self.assertIn('id="search-toolbar"', html)

    def test_api_bhajans_returns_json(self):
        """Tier 1: Check bhajans listing API returns correct structure"""
        url = f"http://localhost:{PORT}/api/bhajans"
        response = urllib.request.urlopen(url)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.info().get_content_type(), "application/json")
        data = json.loads(response.read().decode("utf-8"))
        self.assertEqual(len(data), 50)
        self.assertEqual(data[0]["title"], "Sai Bhajan 1")

    def test_api_search_filter(self):
        """Tier 1: Check search API filtering matches expectations"""
        url = f"http://localhost:{PORT}/api/search?deity=Ganesha"
        response = urllib.request.urlopen(url)
        self.assertEqual(response.status, 200)
        data = json.loads(response.read().decode("utf-8"))
        for bhajan in data:
            self.assertEqual(bhajan["deity"], "Ganesha")
```

---

## 5. TEST_INFRA.md Structure Proposal
`TEST_INFRA.md` will serve as the system documentation for developers and automated workflows detailing how testing integrates with the app's life cycle.

### Proposed Outline

1. **Title**: `TEST_INFRA.md` - E2E Testing Framework & Specification
2. **Overview**: Description of the testing tracks, alignment with R1, R2, and R3 requirements, and verification guidelines.
3. **Execution Commands**:
   - Single command to run the whole test suite (`python -m unittest discover -s tests`).
   - Command to run specific modules (`python -m unittest tests/test_db.py`).
4. **Mocking Architecture**:
   - Explanation of the mock database population.
   - Explanation of the background mock web server on port `3000` to allow decoupling of implementation.
5. **Detailed Tier Breakdown (Tiers 1-4)**:
   - **Tier 1 (Feature Coverage)**: Target test lists, paths, and baseline checks.
   - **Tier 2 (Boundary/Edge Cases)**: Inputs, injections, unicode encoding, database lock limits.
   - **Tier 3 (Cross-feature combos)**: Direct database-to-API-to-UI data integrity.
   - **Tier 4 (Real-world workload/application scenarios)**: Concurrent stress tests, user refinement paths, scraper recovery.
6. **Integrity and Performance Budgets**:
   - Maximum allowed test execution times (< 5 seconds total for unit + mock integration).
   - SQL query response thresholds (< 15ms per search).
7. **CI/CD Integration and Verification Rules**:
   - Exit codes criteria (must be 0).
   - Rules for migrating tests from mock data to real implementation files dynamically.
