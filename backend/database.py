import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

def get_connection(db_path: str) -> sqlite3.Connection:
    """Helper function to get a sqlite3 connection with Row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str):
    """Initializes the database schema, indexes, and triggers."""
    # Ensure directory exists
    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    conn = get_connection(db_path)
    cursor = conn.cursor()

    try:
        # Create base table with all Sai Rhythms fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bhajans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                deity TEXT NOT NULL COLLATE NOCASE,
                raga TEXT COLLATE NOCASE DEFAULT '',
                beat TEXT COLLATE NOCASE DEFAULT '',
                tempo TEXT COLLATE NOCASE DEFAULT '',
                level TEXT COLLATE NOCASE DEFAULT '',
                language TEXT COLLATE NOCASE DEFAULT '',
                songtags TEXT COLLATE NOCASE DEFAULT '',
                lyrics TEXT NOT NULL,
                audio_url TEXT DEFAULT '',
                video_url TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_title_deity UNIQUE (title, deity)
            );
        """)

        # Create indexes for metadata fields
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_deity ON bhajans(deity);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_raga ON bhajans(raga);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_beat ON bhajans(beat);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_tempo ON bhajans(tempo);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_level ON bhajans(level);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_language ON bhajans(language);")

        # Create FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS bhajans_fts USING fts5(
                title,
                lyrics,
                content='bhajans',
                content_rowid='id'
            );
        """)

        # Create Triggers to sync with FTS5
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

        # --- Playlist tables ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlist_bhajans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL,
                bhajan_id INTEGER NOT NULL,
                position INTEGER NOT NULL DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (bhajan_id) REFERENCES bhajans(id) ON DELETE CASCADE,
                CONSTRAINT unique_playlist_bhajan UNIQUE (playlist_id, bhajan_id)
            );
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_playlist_bhajans_playlist ON playlist_bhajans(playlist_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_playlist_bhajans_bhajan ON playlist_bhajans(bhajan_id);")

        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        raise e
    finally:
        conn.close()

def save_bhajan(bhajan_data: dict, db_path: str) -> int:
    """
    Saves a bhajan dictionary using SQLite UPSERT to implement duplicate protection.
    Returns the id of the saved record.
    """
    # Validation
    required_fields = ["title", "deity", "lyrics"]
    for field in required_fields:
        if not bhajan_data.get(field):
            raise ValueError(f"Missing required field: {field}")

    conn = get_connection(db_path)
    cursor = conn.cursor()

    title = bhajan_data["title"]
    deity = bhajan_data["deity"]
    raga = bhajan_data.get("raga", "") or ""
    beat = bhajan_data.get("beat", "") or ""
    tempo = bhajan_data.get("tempo", "") or ""
    level = bhajan_data.get("level", "") or ""
    language = bhajan_data.get("language", "") or ""
    songtags = bhajan_data.get("songtags", "") or ""
    lyrics = bhajan_data["lyrics"]
    audio_url = bhajan_data.get("audio_url", "") or ""
    video_url = bhajan_data.get("video_url", "") or ""

    try:
        try:
            cursor.execute("""
                INSERT INTO bhajans (title, deity, raga, beat, tempo, level, language, songtags, lyrics, audio_url, video_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(title, deity) DO UPDATE SET
                    raga = excluded.raga,
                    beat = excluded.beat,
                    tempo = excluded.tempo,
                    level = excluded.level,
                    language = excluded.language,
                    songtags = excluded.songtags,
                    lyrics = excluded.lyrics,
                    audio_url = excluded.audio_url,
                    video_url = excluded.video_url
                RETURNING id;
            """, (title, deity, raga, beat, tempo, level, language, songtags, lyrics, audio_url, video_url))
            row = cursor.fetchone()
            if row:
                record_id = row[0]
            else:
                cursor.execute("SELECT id FROM bhajans WHERE title = ? AND deity = ?;", (title, deity))
                record_id = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            cursor.execute("""
                INSERT INTO bhajans (title, deity, raga, beat, tempo, level, language, songtags, lyrics, audio_url, video_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(title, deity) DO UPDATE SET
                    raga = excluded.raga,
                    beat = excluded.beat,
                    tempo = excluded.tempo,
                    level = excluded.level,
                    language = excluded.language,
                    songtags = excluded.songtags,
                    lyrics = excluded.lyrics,
                    audio_url = excluded.audio_url,
                    video_url = excluded.video_url;
            """, (title, deity, raga, beat, tempo, level, language, songtags, lyrics, audio_url, video_url))
            cursor.execute("SELECT id FROM bhajans WHERE title = ? AND deity = ?;", (title, deity))
            record_id = cursor.fetchone()[0]

        conn.commit()
        return record_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving bhajan: {e}")
        raise e
    finally:
        conn.close()

def get_all_bhajans(db_path: str) -> list:
    """Queries all bhajans from the database and returns them as a list of dicts."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM bhajans ORDER BY title ASC;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error querying all bhajans: {e}")
        return []
    finally:
        conn.close()

def expand_query(q: str) -> str:
    """Expands query to match common Sanskrit/Sai bhajan spelling/phonetic variants."""
    if not q:
        return ""
    
    words = q.strip().split()
    if not words:
        return ""
        
    expanded_words = []
    
    PHONETIC_VARIANTS = {
        "shambo": ["shambho", "shambo"],
        "shambho": ["shambo", "shambho"],
        "shiva": ["siva", "shiva"],
        "siva": ["shiva", "siva"],
        "sathya": ["satya", "sathya"],
        "satya": ["sathya", "satya"],
        "ganesha": ["ganesa", "ganesha"],
        "ganesa": ["ganesha", "ganesa"],
        "he": ["hey", "he"],
        "hey": ["he", "hey"],
        "om": ["aum", "om"],
        "aum": ["om", "aum"],
        "murali": ["murli", "murali"],
        "murli": ["murali", "murli"],
        "dharma": ["darma", "dharma"],
        "darma": ["dharma", "darma"],
        "sharanam": ["saranam", "sharanam"],
        "saranam": ["sharanam", "saranam"],
        "eeswara": ["eshwara", "ishwara", "iswara", "eeswara"],
        "eshwara": ["eshwara", "ishwara", "iswara", "eeswara"],
        "ishwara": ["eshwara", "ishwara", "iswara", "eeswara"],
        "iswara": ["eshwara", "ishwara", "iswara", "eeswara"],
        "giridhara": ["giridhar", "giridhara"],
        "giridhar": ["giridhara", "giridhar"],
        "gopala": ["gopal", "gopala"],
        "gopal": ["gopala", "gopal"],
        "govinda": ["govind", "govinda"],
        "govind": ["govinda", "govind"],
        "parvathi": ["parvati", "parvathi"],
        "parvati": ["parvathi", "parvati"],
        "jaya": ["jai", "jaya"],
        "jai": ["jaya", "jai"],
        "ram": ["rama", "ram"],
        "rama": ["ram", "rama"],
        "shyam": ["shyama", "shyam"],
        "shyama": ["shyam", "shyama"],
        "ganapathi": ["ganapati", "ganapathy", "ganapathi"],
        "ganapati": ["ganapathi", "ganapathy", "ganapati"],
        "ganapathy": ["ganapathi", "ganapati", "ganapathy"],
        "charanam": ["caranam", "charanam"],
        "caranam": ["charanam", "caranam"],
    }
    
    for w in words:
        w_lower = w.lower()
        if w_lower in ["and", "or", "not", "near", "*", "-"]:
            expanded_words.append(w)
            continue
            
        cleaned_w = w_lower.strip("\"'.,()[]{}!?;:")
        if cleaned_w in PHONETIC_VARIANTS:
            variants = PHONETIC_VARIANTS[cleaned_w]
            expanded_w = "(" + " OR ".join(variants) + ")"
            expanded_words.append(expanded_w)
        else:
            expanded_words.append(w)
            
    # Join terms with explicit AND if the query doesn't already contain operators
    has_operator = any(op in [w.lower() for w in words] for op in ["and", "or", "not"])
    if has_operator:
        return " ".join(expanded_words)
    else:
        return " AND ".join(expanded_words)

def search_bhajans(query: str, deity: str, raga: str, beat: str, 
                   tempo: str = "", level: str = "", language: str = "", songtags: str = "",
                   db_path: str = None) -> list:
    """
    Implements search combining FTS5 (for query matching title or lyrics) 
    and structured metadata filters (deity, raga, beat, tempo, level, language, songtags).
    Returns a list of dicts representing the matching bhajans.
    """
    if db_path is None:
        # Support legacy 5-argument calls: search_bhajans(query, deity, raga, beat, db_path)
        db_path = tempo
        tempo = ""

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cleaned_query = query.strip() if query else ""
    deity = deity.strip() if deity else ""
    raga = raga.strip() if raga else ""
    beat = beat.strip() if beat else ""
    tempo = tempo.strip() if tempo else ""
    level = level.strip() if level else ""
    language = language.strip() if language else ""
    songtags = songtags.strip() if songtags else ""
    
    params = []
    
    def add_filters(sql):
        """Append all active filter clauses to the SQL string."""
        nonlocal params
        if deity:
            # Deity field can contain comma-separated values like "sai, guru"
            # Use LIKE for partial matching
            sql += " AND b.deity LIKE ? COLLATE NOCASE"
            params.append(f"%{deity}%")
        if raga:
            sql += " AND b.raga LIKE ? COLLATE NOCASE"
            params.append(f"%{raga}%")
        if beat:
            sql += " AND b.beat LIKE ? COLLATE NOCASE"
            params.append(f"%{beat}%")
        if tempo:
            sql += " AND b.tempo LIKE ? COLLATE NOCASE"
            params.append(f"%{tempo}%")
        if level:
            sql += " AND b.level LIKE ? COLLATE NOCASE"
            params.append(f"%{level}%")
        if language:
            sql += " AND b.language LIKE ? COLLATE NOCASE"
            params.append(f"%{language}%")
        if songtags:
            sql += " AND b.songtags LIKE ? COLLATE NOCASE"
            params.append(f"%{songtags}%")
        return sql
    
    try:
        if cleaned_query:
            sql = "SELECT b.* FROM bhajans b JOIN bhajans_fts f ON b.id = f.rowid WHERE bhajans_fts MATCH ?"
            params.append(expand_query(cleaned_query))
        else:
            sql = "SELECT b.* FROM bhajans b WHERE 1=1"

        sql = add_filters(sql)
        sql += " ORDER BY b.title ASC;"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except sqlite3.OperationalError as e:
        # Fallback to LIKE query in case of FTS5 parser errors
        logger.warning(f"FTS5 query failed: {e}. Falling back to LIKE search.")
        params = []
        sql = "SELECT b.* FROM bhajans b WHERE 1=1"
        
        if cleaned_query:
            sql += " AND (b.title LIKE ? OR b.lyrics LIKE ?)"
            like_pat = f"%{cleaned_query}%"
            params.extend([like_pat, like_pat])

        sql = add_filters(sql)
        sql += " ORDER BY b.title ASC;"
        
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as ex:
            logger.error(f"Fallback search also failed: {ex}")
            return []
    finally:
        conn.close()
