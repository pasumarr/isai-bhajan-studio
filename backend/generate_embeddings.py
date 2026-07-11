import os
import sys
import sqlite3
import struct
import time
import google.generativeai as genai

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
    # Check for --mock flag
    mock_mode = "--mock" in sys.argv

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        if mock_mode:
            print("Notice: GEMINI_API_KEY is not set. Running in MOCK mode (generating random 768-dim vectors).")
        else:
            print("ERROR: GEMINI_API_KEY environment variable is not set.")
            print("To test the pipeline without an API key, run with the --mock flag:")
            print("  python3 backend/generate_embeddings.py --mock")
            print("\nOtherwise, please run: export GEMINI_API_KEY='your-key'")
            sys.exit(1)
    else:
        genai.configure(api_key=api_key)

    conn = sqlite3.connect(DB_PATH)
    init_embedding_table(conn)

    # Fetch all bhajans that don't have embeddings yet
    cursor = conn.cursor()
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

    count = 0
    start_time = time.time()

    for row in rows:
        bhajan_id, title, deity, raga, lyrics = row
        
        # Prepare text representation for semantic embedding
        text_to_embed = f"Title: {title or ''} | Deity: {deity or ''} | Raga: {raga or ''} | Lyrics: {lyrics or ''}"
        
        try:
            if not api_key and mock_mode:
                # Generate a mock 768-dim normalized vector
                import random
                import math
                vec = [random.gauss(0, 1) for _ in range(768)]
                norm = math.sqrt(sum(x*x for x in vec))
                embedding = [x / norm for x in vec]
            else:
                # Generate embedding vector (768 dimensions for models/text-embedding-004)
                response = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text_to_embed,
                    task_type="retrieval_document"
                )
                embedding = response.get("embedding")
                
            if not embedding:
                print(f"Warning: No embedding returned for bhajan ID {bhajan_id}")
                continue
                
            # Pack float list to binary BLOB (768 floats * 4 bytes = 3072 bytes)
            embedding_blob = struct.pack(f"{len(embedding)}f", *embedding)
            
            cursor.execute(
                "INSERT INTO bhajan_embeddings (bhajan_id, embedding) VALUES (?, ?)",
                (bhajan_id, embedding_blob)
            )
            
            count += 1
            if count % 50 == 0 or count == total_to_embed:
                conn.commit()
                elapsed = time.time() - start_time
                rate = count / elapsed if elapsed > 0 else 0
                print(f"Embedded {count}/{total_to_embed} bhajans ({rate:.2f} songs/sec)...")
                
            # Respect rate limits (1500 RPM for free tier Gemini API)
            if not mock_mode:
                time.sleep(0.05)
            
        except Exception as e:
            print(f"Error embedding bhajan ID {bhajan_id}: {e}")
            print("Stopping. Progress is saved.")
            conn.commit()
            conn.close()
            sys.exit(1)

    conn.commit()
    conn.close()
    print(f"Finished! Successfully generated and saved {count} embeddings.")

if __name__ == "__main__":
    generate_embeddings()
