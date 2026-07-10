import os
import sys
import sqlite3
import unittest
import tempfile
import shutil

# Add project root to path to resolve backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, save_bhajan, get_all_bhajans, search_bhajans
from backend.scraper import parse_bhajans_html, scrape_and_populate

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        try:
            shutil.rmtree(self.test_dir)
        except Exception:
            pass

    def test_schema_initialization(self):
        db_path = os.path.join(self.test_dir, "test_bhajans.db")
        
        # Initialize the database
        init_db(db_path)
        
        # Connect and verify schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn("bhajans", tables)
        self.assertIn("bhajans_fts", tables)
        
        # Verify columns in bhajans table
        cursor.execute("PRAGMA table_info(bhajans);")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        self.assertIn("id", columns)
        self.assertIn("title", columns)
        self.assertIn("deity", columns)
        self.assertIn("raga", columns)
        self.assertIn("beat", columns)
        self.assertIn("lyrics", columns)
        self.assertIn("audio_url", columns)
        self.assertIn("created_at", columns)
        
        # Verify indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row[0] for row in cursor.fetchall()]
        self.assertIn("idx_bhajans_deity", indexes)
        self.assertIn("idx_bhajans_raga", indexes)
        self.assertIn("idx_bhajans_beat", indexes)
        
        # Verify triggers exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
        triggers = [row[0] for row in cursor.fetchall()]
        self.assertIn("bhajans_ai", triggers)
        self.assertIn("bhajans_ad", triggers)
        self.assertIn("bhajans_au", triggers)
        
        conn.close()

    def test_parser_with_snippet(self):
        html_snippet = """
        <div class="bhajan-card">
            <h2 class="bhajan-title">Test Title</h2>
            <span class="deity-name">Test Deity</span>
            <span class="raga-name">Test Raga</span>
            <span class="beat-name">Test Beat</span>
            <div class="bhajan-lyrics">Line 1<br/>Line 2</div>
            <audio class="audio-player" src="/audio/test.mp3"></audio>
        </div>
        """
        bhajans = parse_bhajans_html(html_snippet)
        self.assertEqual(len(bhajans), 1)
        b = bhajans[0]
        self.assertEqual(b["title"], "Test Title")
        self.assertEqual(b["deity"], "Test Deity")
        self.assertEqual(b["raga"], "Test Raga")
        self.assertEqual(b["beat"], "Test Beat")
        self.assertEqual(b["lyrics"], "Line 1\nLine 2")
        self.assertEqual(b["audio_url"], "/audio/test.mp3")

    def test_fallback_parser_nested_robustness(self):
        from backend.scraper import FallbackBhajanParser
        
        html_snippet = """
        <div class="bhajan-card">
            <h2 class="bhajan-title"><b>Sai</b> <i>Bhajan</i></h2>
            <span class="deity-name">Ganesha <span>(Elephant God)</span></span>
            <span class="raga-name">Bhairavi</span>
            <span class="beat-name">Keherwa</span>
            <div class="bhajan-lyrics">
                Line 1<br/>
                <div>Nested div in lyrics</div>
                Line 2
            </div>
            <audio class="audio-player" src="/audio/test.mp3"></audio>
        </div>
        """
        parser = FallbackBhajanParser()
        parser.feed(html_snippet)
        bhajans = parser.bhajans
        
        self.assertEqual(len(bhajans), 1)
        b = bhajans[0]
        self.assertEqual(b["title"], "Sai Bhajan")
        self.assertEqual(b["deity"], "Ganesha (Elephant God)")
        self.assertEqual(b["raga"], "Bhairavi")
        self.assertEqual(b["beat"], "Keherwa")
        self.assertIn("Line 1", b["lyrics"])
        self.assertIn("Nested div in lyrics", b["lyrics"])
        self.assertIn("Line 2", b["lyrics"])
        self.assertEqual(b["audio_url"], "/audio/test.mp3")

    def test_database_insertion_and_validation(self):
        db_path = os.path.join(self.test_dir, "test_insert.db")
        init_db(db_path)
        
        valid_bhajan = {
            "title": "Insert Title",
            "deity": "Insert Deity",
            "raga": "Insert Raga",
            "beat": "Insert Beat",
            "lyrics": "Insert Lyrics",
            "audio_url": "/audio/insert.mp3"
        }
        
        # Test valid insertion
        row_id = save_bhajan(valid_bhajan, db_path)
        self.assertIsNotNone(row_id)
        self.assertGreater(row_id, 0)
        
        # Verify content in database
        all_bhajans = get_all_bhajans(db_path)
        self.assertEqual(len(all_bhajans), 1)
        stored = all_bhajans[0]
        self.assertEqual(stored["title"], "Insert Title")
        self.assertEqual(stored["deity"], "Insert Deity")
        self.assertEqual(stored["raga"], "Insert Raga")
        self.assertEqual(stored["beat"], "Insert Beat")
        self.assertEqual(stored["lyrics"], "Insert Lyrics")
        self.assertEqual(stored["audio_url"], "/audio/insert.mp3")
        
        # Test missing fields validation
        missing_title = valid_bhajan.copy()
        missing_title["title"] = ""
        with self.assertRaisesRegex(ValueError, "Missing required field: title"):
            save_bhajan(missing_title, db_path)
            
        missing_lyrics = valid_bhajan.copy()
        del missing_lyrics["lyrics"]
        with self.assertRaisesRegex(ValueError, "Missing required field: lyrics"):
            save_bhajan(missing_lyrics, db_path)

    def test_duplicate_protection_and_upsert(self):
        db_path = os.path.join(self.test_dir, "test_upsert.db")
        init_db(db_path)
        
        bhajan1 = {
            "title": "Unique Title",
            "deity": "Same Deity",
            "raga": "Raga A",
            "beat": "Beat A",
            "lyrics": "Original Lyrics",
            "audio_url": "/audio/a.mp3"
        }
        
        bhajan2 = {
            "title": "Unique Title",
            "deity": "Same Deity",
            "raga": "Raga B",
            "beat": "Beat B",
            "lyrics": "Updated Lyrics",
            "audio_url": "/audio/b.mp3"
        }
        
        # First save
        id1 = save_bhajan(bhajan1, db_path)
        # Second save with same title/deity but updated other fields
        id2 = save_bhajan(bhajan2, db_path)
        
        # Row IDs should match and count should still be 1
        self.assertEqual(id1, id2)
        all_bhajans = get_all_bhajans(db_path)
        self.assertEqual(len(all_bhajans), 1)
        
        # The record should reflect the updated values (UPSERT)
        stored = all_bhajans[0]
        self.assertEqual(stored["lyrics"], "Updated Lyrics")
        self.assertEqual(stored["raga"], "Raga B")
        self.assertEqual(stored["beat"], "Beat B")
        self.assertEqual(stored["audio_url"], "/audio/b.mp3")

    def test_search_fts_and_filters(self):
        db_path = os.path.join(self.test_dir, "test_search.db")
        init_db(db_path)
        
        bhajans = [
            {"title": "Ganesha Sharanam", "deity": "Ganesha", "raga": "Hamsadhwani", "beat": "Adi", "lyrics": "Parama Pavanam Sadguru Sharanam", "audio_url": "/audio/1.mp3"},
            {"title": "He Shiva Shankara", "deity": "Shiva", "raga": "Bhairavi", "beat": "Keherwa", "lyrics": "Ganga Dhara Hara He Parameshvara", "audio_url": "/audio/2.mp3"},
            {"title": "Devi Bhavani Maa", "deity": "Devi", "raga": "Durga", "beat": "Keherwa", "lyrics": "Jagadamba Bhavani Maa Durga", "audio_url": "/audio/3.mp3"},
            {"title": "Ganesha Sharanam Sharanam", "deity": "Ganesha", "raga": "Hamsadhwani", "beat": "Keherwa", "lyrics": "Lambodara Jaya Vighneshvara", "audio_url": "/audio/4.mp3"}
        ]
        
        for b in bhajans:
            save_bhajan(b, db_path)
            
        # 1. Text search on title
        res = search_bhajans("Shankara", None, None, None, db_path)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["title"], "He Shiva Shankara")
        
        # 2. Text search on title
        res = search_bhajans("Bhavani", None, None, None, db_path)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["title"], "Devi Bhavani Maa")
        
        # 3. Filtering by deity
        res = search_bhajans(None, "Ganesha", None, None, db_path)
        self.assertEqual(len(res), 2)
        titles = [r["title"] for r in res]
        self.assertIn("Ganesha Sharanam", titles)
        self.assertIn("Ganesha Sharanam Sharanam", titles)

        # 3a. Case-insensitive filtering by deity
        res_deity_lower = search_bhajans(None, "ganesha", None, None, db_path)
        self.assertEqual(len(res_deity_lower), 2)
        
        # 3b. Case-insensitive filtering by raga
        res_raga_lower = search_bhajans(None, None, "hamsadhwani", None, db_path)
        self.assertEqual(len(res_raga_lower), 2)

        # 3c. Case-insensitive filtering by beat
        res_beat_lower = search_bhajans(None, None, None, "adi", db_path)
        self.assertEqual(len(res_beat_lower), 1)
        
        # 4. Combining query and filters
        res = search_bhajans("Sharanam", "Ganesha", "Hamsadhwani", "Adi", db_path)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["title"], "Ganesha Sharanam")

        # 4a. Combining case-insensitive query and filters
        res_combo_lower = search_bhajans("sharanam", "ganesha", "hamsadhwani", "adi", db_path)
        self.assertEqual(len(res_combo_lower), 1)
        
        # 5. Invalid filter (should yield no results)
        res = search_bhajans("Sharanam", "Shiva", None, None, db_path)
        self.assertEqual(len(res), 0)

    def test_e2e_integration_and_idempotency(self):
        db_path = os.path.join(self.test_dir, "test_e2e.db")
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        html_path = os.path.join(project_root, "backend", "mock_data", "bhajans_source.html")
        
        # 1. Verify mock file exists
        self.assertTrue(os.path.exists(html_path))
        
        # 2. Scrape and populate first time
        count1 = scrape_and_populate(html_path, db_path)
        self.assertEqual(count1, 50)
        
        # 3. Verify exactly 50 records exist in the DB
        all_bhajans = get_all_bhajans(db_path)
        self.assertEqual(len(all_bhajans), 50)
        
        # 4. Verify no empty fields for required database schema attributes
        for b in all_bhajans:
            self.assertIsNotNone(b["id"])
            self.assertNotEqual(b["title"].strip(), "")
            self.assertNotEqual(b["deity"].strip(), "")
            self.assertNotEqual(b["lyrics"].strip(), "")
            self.assertNotEqual(b["audio_url"].strip(), "")
            self.assertIsNotNone(b["raga"])
            self.assertIsNotNone(b["beat"])
            
        # 5. Run the scraper again (idempotency check)
        count2 = scrape_and_populate(html_path, db_path)
        self.assertEqual(count2, 50)
        
        # Record count must remain exactly 50
        all_bhajans_after = get_all_bhajans(db_path)
        self.assertEqual(len(all_bhajans_after), 50)
