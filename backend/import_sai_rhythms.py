import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from database import init_db, save_bhajan

DB_PATH = os.path.join(os.path.dirname(__file__), "bhajans.db")
JSON_PATH = os.path.join(os.path.dirname(__file__), "mock_data", "sai_rhythms.json")

def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Deleted old database.")
    
    init_db(DB_PATH)
    print("Initialized new database schema.")
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        songs = json.load(f)
        
    print(f"Processing {len(songs)} songs from JSON...")
    count = 0
    skipped = 0
    errors = 0
    
    for song in songs:
        title = song.get("title2") or song.get("title")
        deity = song.get("deity", "")
        lyrics = song.get("lyrics", "")
        
        if not title or not lyrics.strip():
            skipped += 1
            continue
        
        # Normalize deity: take first value if comma-separated, title-case it
        deity_clean = deity.strip() if deity else "Unknown"
            
        audio_link = song.get("audio_link", [])
        video_link = song.get("video_link", [])
        
        audio_url = audio_link[0] if audio_link else ""
        video_url = video_link[0] if video_link else ""
        
        bhajan_data = {
            "title": title.strip(),
            "deity": deity_clean,
            "raga": song.get("raga", ""),
            "beat": song.get("beat", ""),
            "tempo": song.get("tempo", ""),
            "level": song.get("level", ""),
            "language": song.get("language", ""),
            "songtags": song.get("songtags", ""),
            "lyrics": lyrics,
            "audio_url": audio_url,
            "video_url": video_url
        }
        
        try:
            save_bhajan(bhajan_data, DB_PATH)
            count += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error saving '{title}': {e}")
            
    print(f"\nImport complete!")
    print(f"  Successfully imported: {count}")
    print(f"  Skipped (no lyrics/title): {skipped}")
    print(f"  Errors: {errors}")
    print(f"  Total in JSON: {len(songs)}")

if __name__ == "__main__":
    main()
