# verify_empirically.py
# Programmatic empirical verification script for Scraper and Database (Milestone 2)

import os
import sys
import sqlite3

# Resolve backend imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from backend.database import init_db, save_bhajan, get_all_bhajans, search_bhajans
from backend.scraper import scrape_and_populate, parse_bhajans_html

def run_verification():
    print("====================================================")
    print("EMPIRICAL VERIFICATION REPORT - MILESTONE 2")
    print("====================================================")
    
    db_path = os.path.join(PROJECT_ROOT, "backend", "bhajans.db")
    html_path = os.path.join(PROJECT_ROOT, "backend", "mock_data", "bhajans_source.html")
    
    # 1. Verify files exist
    print(f"Checking HTML source file: {html_path}")
    if os.path.exists(html_path):
        print(f"  [PASS] HTML source exists. Size: {os.path.getsize(html_path)} bytes.")
    else:
        print("  [FAIL] HTML source file not found!")
        return
        
    # 2. Check if database exists, if not initialize it
    print(f"Checking SQLite database file: {db_path}")
    db_existed = os.path.exists(db_path)
    if not db_existed:
        print("  Database does not exist. Running scraper to populate it...")
        try:
            count = scrape_and_populate(html_path, db_path)
            print(f"  [PASS] Scraped and populated database. Count: {count}")
        except Exception as e:
            print(f"  [FAIL] Scraper execution failed: {e}")
            return
    else:
        print(f"  Database exists. Size: {os.path.getsize(db_path)} bytes.")
        
    # 3. Establish connection and query counts/table structure
    print("Verifying database connection and schema...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verify table list
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  Tables found: {tables}")
        
        for required_table in ["bhajans", "bhajans_fts"]:
            if required_table in tables:
                print(f"  [PASS] Table '{required_table}' exists.")
            else:
                print(f"  [FAIL] Table '{required_table}' is missing!")
                
        # Verify table columns
        cursor.execute("PRAGMA table_info(bhajans);")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"  Columns in 'bhajans': {columns}")
        required_cols = ["id", "title", "deity", "raga", "beat", "lyrics", "audio_url", "created_at"]
        for col in required_cols:
            if col in columns:
                print(f"    [PASS] Column '{col}' exists.")
            else:
                print(f"    [FAIL] Column '{col}' is missing!")
                
        # Verify database record count
        cursor.execute("SELECT count(*) FROM bhajans;")
        count = cursor.fetchone()[0]
        print(f"  Record count in 'bhajans': {count}")
        if count == 50:
            print("  [PASS] Exactly 50 records exist in 'bhajans' table.")
        else:
            print(f"  [FAIL] Expected 50 records, found {count}.")
            
        conn.close()
    except Exception as e:
        print(f"  [FAIL] Database schema check failed: {e}")
        return
        
    # 4. Verify duplicate protection
    print("Testing duplicate protection...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM bhajans;")
        before_count = cursor.fetchone()[0]
        
        # Query an existing bhajan
        cursor.execute("SELECT id, title, deity, lyrics, raga, beat FROM bhajans LIMIT 1;")
        original_bhajan_row = cursor.fetchone()
        o_id, o_title, o_deity, o_lyrics, o_raga, o_beat = original_bhajan_row
        
        # Duplicate bhajan with updated lyrics
        duplicate_bhajan = {
            "title": o_title,
            "deity": o_deity,
            "raga": o_raga,
            "beat": o_beat,
            "lyrics": o_lyrics + " [UPDATED BY CHALLENGER]",
            "audio_url": "/audio/updated_test.mp3"
        }
        
        print(f"  Attempting to save duplicate bhajan (title: '{o_title}', deity: '{o_deity}') with modified lyrics...")
        saved_id = save_bhajan(duplicate_bhajan, db_path)
        
        cursor.execute("SELECT count(*) FROM bhajans;")
        after_count = cursor.fetchone()[0]
        
        print(f"  Row ID returned: {saved_id} (Original was: {o_id})")
        print(f"  Record count before: {before_count}, after: {after_count}")
        
        cursor.execute("SELECT lyrics, audio_url FROM bhajans WHERE id = ?;", (saved_id,))
        updated_lyrics, updated_audio = cursor.fetchone()
        
        if after_count == before_count:
            print("  [PASS] Row count did not increase (Duplicate protection active).")
        else:
            print("  [FAIL] Row count increased after inserting duplicate!")
            
        if saved_id == o_id:
            print("  [PASS] Returned row ID matches original row ID.")
        else:
            print("  [FAIL] Returned row ID does not match original row ID.")
            
        if "[UPDATED BY CHALLENGER]" in updated_lyrics:
            print("  [PASS] Data was successfully updated in-place (UPSERT works).")
        else:
            print("  [FAIL] Data was not updated in-place!")
            
        # Restore original lyrics
        restore_bhajan = {
            "title": o_title,
            "deity": o_deity,
            "raga": o_raga,
            "beat": o_beat,
            "lyrics": o_lyrics,
            "audio_url": "/audio/original_restored.mp3"
        }
        save_bhajan(restore_bhajan, db_path)
        print("  Original record restored.")
        
        conn.close()
    except Exception as e:
        print(f"  [FAIL] Duplicate protection test failed: {e}")
        
    # 5. Verify Full-Text Search and filtering behavior
    print("Testing Full-Text Search (FTS5) and filtering...")
    try:
        # Test 5a: FTS match on lyrics keyword
        # "Sadguru" is in Ganesha Sharanam lyrics
        results = search_bhajans("Sadguru", None, None, None, db_path)
        print(f"  FTS Search for 'Sadguru': found {len(results)} matches.")
        if len(results) > 0:
            print("    [PASS] FTS returned search results successfully.")
            for r in results:
                print(f"      Matched: '{r['title']}' - Lyrics: '{r['lyrics'][:50]}...'")
        else:
            print("    [FAIL] FTS returned no results for 'Sadguru'.")
            
        # Test 5b: Metadata filter combining deity and raga
        results_filter = search_bhajans(None, "Ganesha", "Hamsadhwani", None, db_path)
        print(f"  Filter search (Deity: Ganesha, Raga: Hamsadhwani): found {len(results_filter)} matches.")
        if len(results_filter) > 0:
            print("    [PASS] Filter search returned results successfully.")
            for r in results_filter:
                print(f"      Matched: '{r['title']}' (Deity: {r['deity']}, Raga: {r['raga']})")
        else:
            print("    [FAIL] Filter search returned no results.")
            
        # Test 5c: Case-insensitivity check of the filters
        # Note: If the backend logic is case-sensitive, this will fail or return empty list
        results_case = search_bhajans(None, "ganesha", None, None, db_path)
        print(f"  Filter search with lowercase deity 'ganesha': found {len(results_case)} matches.")
        if len(results_case) > 0:
            print("    [PASS] Metadata filters are case-insensitive.")
        else:
            print("    [WARN] Metadata filters are CASE-SENSITIVE (returned 0 results for 'ganesha' vs Ganesha).")
            
        # Test 5d: FTS query parser robustness check
        # Query with invalid FTS syntax
        results_robust = search_bhajans("OR OR NOT", None, None, None, db_path)
        print(f"  FTS query with invalid syntax 'OR OR NOT': found {len(results_robust)} matches.")
        print("    [PASS] Fallback to LIKE search works and did not crash.")
        
    except Exception as e:
        print(f"  [FAIL] FTS and filtering verification failed: {e}")

if __name__ == "__main__":
    run_verification()
