# tests/test_frontend.py

import os
import sys
import json
import socket
import sqlite3
import threading
import urllib.request
import urllib.parse
import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add project root to path to resolve backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mock_data import MOCK_BHAJANS, get_db_path, initialize_db
from backend.database import search_bhajans

PORT = 3000
TEST_MODE = os.environ.get("TEST_MODE", "mock")

class MockNextjsHandler(BaseHTTPRequestHandler):
    """
    Mock web server simulating Next.js routing endpoints and API route handlers.
    Used during 'mock' TEST_MODE to allow front-end and integration test execution.
    """
    def log_message(self, format, *args):
        pass # Suppress server logging to keep test console output clean

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        db_path = get_db_path()

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
                    <select id="deity-select">
                        <option value="">All Deities</option>
                        <option value="Ganesha">Ganesha</option>
                        <option value="Shiva">Shiva</option>
                        <option value="Rama">Rama</option>
                        <option value="Krishna">Krishna</option>
                        <option value="Devi">Devi</option>
                    </select>
                </div>
                <main id="bhajan-results">
                    <!-- Bhajan list rendered here -->
                </main>
                <footer><p>© 2026 Sai Rhythms Modernized</p></footer>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))

        elif path == "/api/bhajans":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT id, title, deity, raga, beat, lyrics, audio_url FROM bhajans")
                rows = cursor.fetchall()
                conn.close()
                data = [
                    {"id": r[0], "title": r[1], "deity": r[2], "raga": r[3], "beat": r[4], "lyrics": r[5], "audio_url": r[6]}
                    for r in rows
                ]
                self.wfile.write(json.dumps(data).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif path == "/api/search":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            
            q = query_params.get("q", [None])[0]
            deity = query_params.get("deity", [None])[0]
            raga = query_params.get("raga", [None])[0]
            beat = query_params.get("beat", [None])[0]
            
            try:
                # Route query through real search_bhajans function in backend/database.py
                data = search_bhajans(q, deity, raga, beat, db_path)
                self.wfile.write(json.dumps(data).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

class TestFrontend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global PORT
        cls.server_thread = None
        db_path = get_db_path()
        if TEST_MODE == "mock":
            if not os.path.exists(db_path):
                initialize_db(db_path)
            
            # Attempt to bind to PORT (default 3000). If in use, find a free port and try again.
            cls.server = None
            for attempt in range(5):
                try:
                    cls.server = HTTPServer(('127.0.0.1', PORT), MockNextjsHandler)
                    break
                except OSError:
                    PORT = find_free_port()
            
            if not cls.server:
                raise RuntimeError("Could not bind mock Next.js server to any port.")
                
            cls.server_thread = threading.Thread(target=cls.server.serve_forever)
            cls.server_thread.daemon = True
            cls.server_thread.start()
            # Brief sleep to allow thread socket binding
            import time
            time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        if cls.server_thread:
            cls.server.shutdown()
            cls.server.server_close()

    # ==========================================
    # TIER 1: FEATURE COVERAGE / HAPPY PATHS (>= 5 tests)
    # ==========================================

    def test_homepage_loads_successfully(self):
        """Tier 1: Verify index route loads successfully and returns HTTP 200 OK"""
        url = f"http://127.0.0.1:{PORT}/"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            html = response.read().decode("utf-8")
            self.assertIn("ISai Bhajan Studio", html)
            self.assertIn('id="search-toolbar"', html)

    def test_api_bhajans_returns_200_json(self):
        """Tier 1: Verify /api/bhajans returns HTTP 200 and a JSON list"""
        url = f"http://127.0.0.1:{PORT}/api/bhajans"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            self.assertTrue(response.info().get_content_type().startswith("application/json"))
            data = json.loads(response.read().decode("utf-8"))
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 50)

    def test_api_search_returns_200_json(self):
        """Tier 1: Verify /api/search returns HTTP 200 and a JSON list"""
        url = f"http://127.0.0.1:{PORT}/api/search"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            self.assertTrue(response.info().get_content_type().startswith("application/json"))
            data = json.loads(response.read().decode("utf-8"))
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 50)

    def test_api_search_with_filtering(self):
        """Tier 1: Verify /api/search filters by deity correctly"""
        url = f"http://127.0.0.1:{PORT}/api/search?deity=Ganesha"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertGreater(len(data), 0)
            for item in data:
                self.assertEqual(item["deity"], "Ganesha")

    def test_frontend_route_not_found(self):
        """Tier 1: Verify unmatched route returns HTTP 404"""
        url = f"http://127.0.0.1:{PORT}/api/undefined_route_xyz"
        req = urllib.request.Request(url)
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 404)

    # ==========================================
    # TIER 2: BOUNDARY & EDGE CASES (>= 5 tests)
    # ==========================================

    def test_api_search_invalid_parameter_values(self):
        """Tier 2: Verify querying a non-existent deity returns empty list instead of crashing"""
        url = f"http://127.0.0.1:{PORT}/api/search?deity=Zeus"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(data, [])

    def test_api_search_sql_injection_safety(self):
        """Tier 2: Verify SQL injection attempts on API parameters do not crash or leak data"""
        malicious_input = urllib.parse.quote("Ganesha' OR '1'='1")
        url = f"http://127.0.0.1:{PORT}/api/search?deity={malicious_input}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(data, [])

    def test_api_search_whitespace_handling(self):
        """Tier 2: Verify search API trims whitespace in request query parameter"""
        url_clean = f"http://127.0.0.1:{PORT}/api/search?deity=Ganesha"
        url_padded = f"http://127.0.0.1:{PORT}/api/search?deity=%20%20Ganesha%20%20"
        
        with urllib.request.urlopen(url_clean) as r1:
            data1 = json.loads(r1.read().decode("utf-8"))
        with urllib.request.urlopen(url_padded) as r2:
            data2 = json.loads(r2.read().decode("utf-8"))
            
        self.assertEqual(len(data1), len(data2))
        self.assertGreater(len(data1), 0)

    def test_api_search_case_insensitivity(self):
        """Tier 2: Verify search API is case insensitive for query parameters"""
        url_lower = f"http://127.0.0.1:{PORT}/api/search?deity=ganesha"
        url_upper = f"http://127.0.0.1:{PORT}/api/search?deity=GANESHA"
        
        with urllib.request.urlopen(url_lower) as r1:
            data1 = json.loads(r1.read().decode("utf-8"))
        with urllib.request.urlopen(url_upper) as r2:
            data2 = json.loads(r2.read().decode("utf-8"))
            
        self.assertEqual(len(data1), len(data2))
        self.assertGreater(len(data1), 0)

    def test_api_search_empty_params(self):
        """Tier 2: Verify search API returns all 50 bhajans if search parameters are empty strings"""
        url = f"http://127.0.0.1:{PORT}/api/search?deity=&raga=&beat="
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(len(data), 50)

    # ==========================================
    # TIER 3: CROSS-FEATURE COMBINATION TESTS
    # ==========================================

    def test_db_to_api_data_integrity(self):
        """Tier 3: Verify direct SQLite records match API response payloads exactly"""
        # Read from DB directly
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT title, deity, raga, beat, lyrics, audio_url FROM bhajans ORDER BY title ASC")
        db_records = cursor.fetchall()
        conn.close()

        # Read from API
        url = f"http://127.0.0.1:{PORT}/api/bhajans"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            api_data = json.loads(response.read().decode("utf-8"))

        self.assertEqual(len(db_records), len(api_data))
        for i in range(len(db_records)):
            self.assertEqual(db_records[i][0], api_data[i]["title"])
            self.assertEqual(db_records[i][1], api_data[i]["deity"])
            self.assertEqual(db_records[i][2], api_data[i]["raga"])
            self.assertEqual(db_records[i][3], api_data[i]["beat"])
            self.assertEqual(db_records[i][4], api_data[i]["lyrics"])
            self.assertEqual(db_records[i][5], api_data[i]["audio_url"])

    def test_unicode_roundtrip_api(self):
        """Tier 3: Verify unicode string writes to DB roundtrip successfully via search API"""
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        unicode_title = "Bhajan ॐ"
        unicode_lyrics = "Śiva Śiva Hara Hara"
        try:
            cursor.execute("""
                INSERT INTO bhajans (title, deity, raga, beat, lyrics, audio_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (unicode_title, "Shiva", "Bhairavi", "Adi", unicode_lyrics, "https://example.com/unicode.mp3"))
            conn.commit()
            
            # Verify via API query
            query_val = urllib.parse.quote("ॐ")
            url = f"http://127.0.0.1:{PORT}/api/search?q={query_val}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))
        finally:
            cursor.execute("DELETE FROM bhajans WHERE title = ?", (unicode_title,))
            conn.commit()
            conn.close()
        
        self.assertGreaterEqual(len(data), 1)
        found = next((item for item in data if item["title"] == unicode_title), None)
        self.assertIsNotNone(found)
        self.assertEqual(found["lyrics"], unicode_lyrics)

    # ==========================================
    # TIER 4: REAL-WORLD WORKLOADS (SCENARIOS)
    # ==========================================

    def test_scenario_first_time_setup_verification(self):
        """Tier 4 Scenario: First-Time Setup Verification"""
        # Asserts database is successfully created with 50 items and the API serving is active
        url = f"http://127.0.0.1:{PORT}/api/bhajans"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
        self.assertEqual(len(data), 50)
        # Verify first item matches expectations
        first = data[0]
        self.assertIsNotNone(first["title"])
        self.assertIsNotNone(first["deity"])
        self.assertIsNotNone(first["lyrics"])

    def test_scenario_user_search_refinement_api(self):
        """Tier 4 Scenario: User Search Refinement Journey via HTTP APIs"""
        # Empty search -> should return 50
        url1 = f"http://127.0.0.1:{PORT}/api/search?q="
        with urllib.request.urlopen(url1) as response:
            data1 = json.loads(response.read().decode("utf-8"))
        self.assertEqual(len(data1), 50)

        # Refine by a deity that exists (e.g., Ganesha) -> should return subset
        url2 = f"http://127.0.0.1:{PORT}/api/search?q=&deity=Ganesha"
        with urllib.request.urlopen(url2) as response:
            data2 = json.loads(response.read().decode("utf-8"))
        self.assertLessEqual(len(data2), 50)
        for bhajan in data2:
            self.assertEqual(bhajan["deity"], "Ganesha")

        # Refine by Ganesha + Yaman -> should return smaller subset
        url3 = f"http://127.0.0.1:{PORT}/api/search?q=&deity=Ganesha&raga=Yaman"
        with urllib.request.urlopen(url3) as response:
            data3 = json.loads(response.read().decode("utf-8"))
        self.assertLessEqual(len(data3), len(data2))
        for bhajan in data3:
            self.assertEqual(bhajan["deity"], "Ganesha")
            self.assertEqual(bhajan["raga"], "Yaman")

    def test_scenario_high_density_concurrent_api_requests(self):
        """Tier 4 Scenario: High Density Concurrent API Requests mimicking concurrent traffic on port 3000"""
        errors = []
        def send_request():
            url = f"http://127.0.0.1:{PORT}/api/search?deity=Ganesha"
            try:
                for _ in range(10):
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        if not all(item["deity"] == "Ganesha" for item in data):
                            errors.append("Deity mismatch in concurrent response")
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=send_request) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Concurrent request errors: {errors}")
