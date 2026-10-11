import os
import sys
import sqlite3
import struct
import time
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bhajans.db")

def init_embedding_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bhajan_embeddings (
            bhajan_id INTEGER PRIMARY KEY,
            embedding BLOB,
            FOREIGN KEY (bhajan_id) REFERENCES bhajans (id) ON DELETE CASCADE
        )
    """)
    conn.commit()

def generate_embeddings():
    # Check for flags
    mock_mode = "--mock" in sys.argv
    regenerate = "--regenerate" in sys.argv

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        if mock_mode:
            print("Notice: GEMINI_API_KEY is not set. Running in MOCK mode (generating random 3072-dim vectors).")
        else:
            print("ERROR: GEMINI_API_KEY environment variable is not set.")
            print("To test the pipeline without an API key, run with the --mock flag:")
            print("  python3 backend/generate_embeddings.py --mock")
            print("\nOtherwise, please run: export GEMINI_API_KEY='your-key'")
            sys.exit(1)
    else:
        from google import genai
        client = genai.Client(api_key=api_key)

    conn = sqlite3.connect(DB_PATH)
    init_embedding_table(conn)
    cursor = conn.cursor()

    # If regenerating, clear all old embeddings first
    if regenerate:
        print("Regenerating all embeddings (clearing old ones)...")
        cursor.execute("DELETE FROM bhajan_embeddings")
        conn.commit()

    # Fetch all bhajans that don't have embeddings yet
    cursor.execute("""
        SELECT b.id, b.title, b.deity, b.raga, b.lyrics 
        FROM bhajans b
        LEFT JOIN bhajan_embeddings e ON b.id = e.bhajan_id
        WHERE e.bhajan_id IS NULL
    """)
    rows = cursor.fetchall()
    total_to_embed = len(rows)

    if total_to_embed == 0:
        print("All bhajans are already embedded!")
        conn.close()
        return

    print(f"Found {total_to_embed} bhajans to embed. Starting generation...")

    # Process in batches for efficiency
    BATCH_SIZE = 20
    count = 0
    start_time = time.time()

    for batch_start in range(0, len(rows), BATCH_SIZE):
        batch = rows[batch_start:batch_start + BATCH_SIZE]
        
        texts = []
        ids = []
        for row in batch:
            bhajan_id, title, deity, raga, lyrics = row
            text_to_embed = f"Title: {title or ''} | Deity: {deity or ''} | Raga: {raga or ''} | Lyrics: {lyrics or ''}"
            texts.append(text_to_embed)
            ids.append(bhajan_id)
        
        try:
            if not api_key and mock_mode:
                # Generate mock 3072-dim normalized vectors
                import random
                import math
                embeddings = []
                for _ in texts:
                    vec = [random.gauss(0, 1) for _ in range(3072)]
                    norm = math.sqrt(sum(x*x for x in vec))
                    embeddings.append([x / norm for x in vec])
            else:
                # Batch embed using new SDK
                response = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=texts,
                )
                embeddings = [e.values for e in response.embeddings]
                
            for i, embedding in enumerate(embeddings):
                if not embedding:
                    print(f"Warning: No embedding returned for bhajan ID {ids[i]}")
                    continue
                    
                # Pack float list to binary BLOB
                embedding_blob = struct.pack(f"{len(embedding)}f", *embedding)
                
                cursor.execute(
                    "INSERT OR REPLACE INTO bhajan_embeddings (bhajan_id, embedding) VALUES (?, ?)",
                    (ids[i], embedding_blob)
                )
                count += 1
            
            conn.commit()
            elapsed = time.time() - start_time
            rate = count / elapsed if elapsed > 0 else 0
            print(f"Embedded {count}/{total_to_embed} bhajans ({rate:.1f} songs/sec)...")
                
            # Respect rate limits
            if not mock_mode:
                time.sleep(0.1)
            
        except Exception as e:
            print(f"Error embedding batch starting at ID {ids[0]}: {e}")
            print("Stopping. Progress is saved.")
            conn.commit()
            conn.close()
            sys.exit(1)

    conn.commit()
    conn.close()
    print(f"Finished! Successfully generated and saved {count} embeddings.")

if __name__ == "__main__":
    generate_embeddings()

