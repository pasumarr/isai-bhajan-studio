# tests/mock_data.py

import os
import sys
import sqlite3

# Add project root to path to resolve backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db

DEITIES = ["Ganesha", "Shiva", "Rama", "Krishna", "Devi"]
RAGAS = ["Yaman", "Bhairavi", "Darbari", "Kalyan", "Bhupali"]
BEATS = ["Adi", "Keharwa", "Rupak", "Dadra", "Roopak"]

# Deterministically construct a static clean list of exactly 50 mock bhajans
MOCK_BHAJANS = [
    {
        "title": f"Sai {DEITIES[i % 5]} Bhajan {i + 1}",
        "deity": DEITIES[i % 5],
        "raga": RAGAS[(i // 2) % 5],
        "beat": BEATS[(i // 3) % 5],
        "lyrics": f"O Lord {DEITIES[i % 5]}, residing in our hearts, sung in Raga {RAGAS[(i // 2) % 5]} with Beat {BEATS[(i // 3) % 5]}. We pray to you.",
        "audio_url": f"https://example.com/audio/sai_{DEITIES[i % 5].lower()}_bhajan_{i + 1}.mp3"
    } for i in range(50)
]

def get_db_path():
    TEST_MODE = os.environ.get("TEST_MODE", "mock")
    if TEST_MODE == "real":
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/bhajans.db"))
    else:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "mock_bhajans.db"))

def initialize_db(db_path):
    """Initializes the database schema and seeds 50 mock bhajans."""
    # Ensure parent dir exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Remove file to ensure a clean start
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass
            
    # Import and call init_db to set up the exact schema, triggers, virtual tables, indexes
    from backend.database import init_db
    init_db(db_path)
            
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for bhajan in MOCK_BHAJANS:
        cursor.execute("""
            INSERT OR IGNORE INTO bhajans (title, deity, raga, beat, lyrics, audio_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            bhajan["title"],
            bhajan["deity"],
            bhajan["raga"],
            bhajan["beat"],
            bhajan["lyrics"],
            bhajan["audio_url"]
        ))
    # Seed mock embeddings for testing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bhajan_embeddings (
            bhajan_id INTEGER PRIMARY KEY,
            embedding BLOB,
            FOREIGN KEY (bhajan_id) REFERENCES bhajans (id) ON DELETE CASCADE
        )
    """)
    cursor.execute("SELECT id FROM bhajans")
    ids = [row[0] for row in cursor.fetchall()]
    import struct
    import random
    import math
    for bhajan_id in ids:
        vec = [random.gauss(0, 1) for _ in range(768)]
        norm = math.sqrt(sum(x*x for x in vec))
        embedding = [x / norm for x in vec]
        blob = struct.pack("768f", *embedding)
        cursor.execute("INSERT OR REPLACE INTO bhajan_embeddings (bhajan_id, embedding) VALUES (?, ?)", (bhajan_id, blob))

    conn.commit()
    conn.close()

