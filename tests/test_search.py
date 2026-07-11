# tests/test_search.py

import os
import sys
import sqlite3
import unittest
import threading

# Add project root to path to resolve backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mock_data import MOCK_BHAJANS, get_db_path, initialize_db
from backend.database import search_bhajans, search_semantic_bhajans

TEST_MODE = os.environ.get("TEST_MODE", "mock")

def query_search(query_str=None, deity=None, raga=None, beat=None):
    db_path = get_db_path()
    return search_bhajans(query_str, deity, raga, beat, db_path)

class TestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db_path = get_db_path()
        if TEST_MODE == "mock" and not os.path.exists(db_path):
            initialize_db(db_path)

    # ==========================================
    # TIER 1: FEATURE COVERAGE / HAPPY PATHS (>= 5 tests)
    # ==========================================

    def test_search_by_deity(self):
        """Tier 1: Verify search filters correctly by deity"""
        results = query_search(deity="Ganesha")
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r["deity"], "Ganesha")

    def test_search_by_raga(self):
        """Tier 1: Verify search filters correctly by raga"""
        results = query_search(raga="Yaman")
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r["raga"], "Yaman")

    def test_search_by_beat(self):
        """Tier 1: Verify search filters correctly by beat/tala"""
        results = query_search(beat="Adi")
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r["beat"], "Adi")

    def test_search_by_lyrics_text(self):
        """Tier 1: Verify full-text search works on title"""
        first = query_search()[0]
        word = first["title"].split()[0]
        results = query_search(query_str=word)
        self.assertGreaterEqual(len(results), 1)
        for r in results:
            self.assertIn(word, r["title"])

    def test_search_multiple_filters(self):
        """Tier 1: Verify compound search using multiple filters combined"""
        first = query_search()[0]
        results = query_search(deity=first["deity"], raga=first["raga"], beat=first["beat"])
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r["deity"], first["deity"])
            self.assertEqual(r["raga"], first["raga"])
            self.assertEqual(r["beat"], first["beat"])

    # ==========================================
    # TIER 2: BOUNDARY & EDGE CASES (>= 5 tests)
    # ==========================================

    def test_search_case_insensitivity(self):
        """Tier 2: Verify search queries are case insensitive across deities, ragas, and beats"""
        first = query_search()[0]
        res_lower = query_search(deity=first["deity"].lower(), raga=first["raga"].lower(), beat=first["beat"].lower())
        res_upper = query_search(deity=first["deity"].upper(), raga=first["raga"].upper(), beat=first["beat"].upper())
        res_mixed = query_search(deity=first["deity"].capitalize(), raga=first["raga"].capitalize(), beat=first["beat"].capitalize())
        
        self.assertEqual(len(res_lower), len(res_upper))
        self.assertEqual(len(res_lower), len(res_mixed))
        self.assertGreater(len(res_lower), 0)

    def test_search_sql_injection_defense(self):
        """Tier 2: Verify queries containing malicious SQL input do not crash or return unauthorized data"""
        malicious_deity = "Ganesha' OR '1'='1"
        malicious_query = "' UNION SELECT * FROM bhajans;--"
        
        results_deity = query_search(deity=malicious_deity)
        results_query = query_search(query_str=malicious_query)
        
        # Sanitization should result in no matches (empty list) or matching the literal string (0 results)
        self.assertEqual(len(results_deity), 0)
        self.assertEqual(len(results_query), 0)

    def test_search_whitespace_trimming(self):
        """Tier 2: Verify leading, trailing, and internal whitespace is trimmed correctly"""
        results_clean = query_search(deity="Ganesha")
        results_padded = query_search(deity="   Ganesha   ")
        self.assertEqual(len(results_clean), len(results_padded))
        self.assertGreater(len(results_clean), 0)

    def test_search_empty_queries(self):
        """Tier 2: Verify empty or None filter parameters are ignored instead of matching empty strings"""
        results_empty = query_search(deity="", raga=None, beat="  ")
        # Should return all 50 since filters are effectively omitted
        self.assertEqual(len(results_empty), 50)

    def test_search_no_results(self):
        """Tier 2: Verify that searching for a non-existent term returns an empty list"""
        results = query_search(query_str="NonExistentBhajanXYZ")
        self.assertEqual(results, [])

    # ==========================================
    # TIER 3: CROSS-FEATURE COMBINATION TESTS
    # ==========================================

    def test_search_request_parameter_mapping(self):
        """Tier 3: Verify parameter mapping for combined search query arguments"""
        first = query_search()[0]
        payload = {"q": "", "deity": first["deity"], "raga": first["raga"], "beat": first["beat"]}
        results = query_search(query_str=payload["q"], deity=payload["deity"], raga=payload["raga"], beat=payload["beat"])
        for r in results:
            self.assertEqual(r["deity"], payload["deity"])
            self.assertEqual(r["raga"], payload["raga"])
            self.assertEqual(r["beat"], payload["beat"])

    def test_search_unicode_accent_handling(self):
        """Tier 3: Verify search works on unicode accents and symbols"""
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            # Temporarily insert unicode item and commit it so other connections see it
            cursor.execute("""
                INSERT INTO bhajans (title, deity, raga, beat, lyrics, audio_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("Sai Śiva Bhajan ॐ 100", "Shiva", "Bhairavi", "Adi", "Singing ॐ for Śiva", "https://example.com/siva.mp3"))
            conn.commit()
            
            # Verify searching by unicode works
            res = query_search(query_str="ॐ")
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0]["title"], "Sai Śiva Bhajan ॐ 100")
            
            res_accent = query_search(query_str="Śiva")
            self.assertEqual(len(res_accent), 1)
        finally:
            cursor.execute("DELETE FROM bhajans WHERE title = ?", ("Sai Śiva Bhajan ॐ 100",))
            conn.commit()
            conn.close()

    # ==========================================
    # TIER 4: REAL-WORLD WORKLOADS (SCENARIOS)
    # ==========================================

    def test_scenario_user_search_refinement_journey(self):
        """
        Tier 4 Scenario: User Search Refinement Journey
        """
        # Step 1: User types text query
        step1 = query_search(query_str="")
        self.assertEqual(len(step1), 50)
        
        first = step1[0]
        # Step 2: Refines by deity
        step2 = query_search(query_str="", deity=first["deity"])
        self.assertLessEqual(len(step2), len(step1))
        for r in step2:
            self.assertEqual(r["deity"], first["deity"])
            
        # Step 3: Refines further by raga
        step3 = query_search(query_str="", deity=first["deity"], raga=first["raga"])
        self.assertLessEqual(len(step3), len(step2))
        for r in step3:
            self.assertEqual(r["deity"], first["deity"])
            self.assertEqual(r["raga"], first["raga"])
            
        # Step 4: Clears filters
        step4 = query_search()
        self.assertEqual(len(step4), 50)

    def test_scenario_high_density_concurrent_search(self):
        """Tier 4 Scenario: High Density Concurrent Search Requests simulating multi-user load"""
        errors = []
        def worker():
            try:
                for _ in range(20):
                    res = query_search(deity="Ganesha", raga="Yaman")
                    for r in res:
                        if r["deity"] != "Ganesha" or r["raga"] != "Yaman":
                            errors.append("Invalid results returned under concurrent load")
            except Exception as e:
                errors.append(str(e))
                
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        self.assertEqual(len(errors), 0, f"Concurrent search errors: {errors}")

    def test_search_semantic_basic(self):
        """Test happy path for semantic search on mock database"""
        db_path = get_db_path()
        initialize_db(db_path)
        
        results = search_semantic_bhajans("peaceful morning song", limit=5, db_path=db_path)
        self.assertEqual(len(results), 5)
        for r in results:
            self.assertIn("ai_score", r)
            self.assertTrue(-1.0 <= r["ai_score"] <= 1.0)
            self.assertIn("title", r)
            self.assertIn("lyrics", r)

    def test_search_semantic_empty(self):
        """Test semantic search with empty query"""
        db_path = get_db_path()
        results = search_semantic_bhajans("", limit=5, db_path=db_path)
        self.assertEqual(len(results), 0)
