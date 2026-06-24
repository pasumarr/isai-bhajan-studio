import sys
import json
import os
from database import get_all_bhajans, search_bhajans

def main():
    if len(sys.argv) < 2:
        return
    
    # Path to db relative to this script
    db_path = os.path.join(os.path.dirname(__file__), 'bhajans.db')
    command = sys.argv[1]
    
    if command == "all":
        results = get_all_bhajans(db_path)
        print(json.dumps(results))
    elif command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        deity = sys.argv[3] if len(sys.argv) > 3 else ""
        raga = sys.argv[4] if len(sys.argv) > 4 else ""
        beat = sys.argv[5] if len(sys.argv) > 5 else ""
        tempo = sys.argv[6] if len(sys.argv) > 6 else ""
        level = sys.argv[7] if len(sys.argv) > 7 else ""
        language = sys.argv[8] if len(sys.argv) > 8 else ""
        songtags = sys.argv[9] if len(sys.argv) > 9 else ""
        results = search_bhajans(query, deity, raga, beat, tempo, level, language, songtags, db_path)
        print(json.dumps(results))

if __name__ == "__main__":
    main()
