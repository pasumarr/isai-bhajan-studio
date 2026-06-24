import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add workspace path to sys.path to resolve backend imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import save_bhajan, init_db

try:
    from bs4 import BeautifulSoup
    USE_BS4 = True
except ImportError:
    from html.parser import HTMLParser
    USE_BS4 = False
    logger.warning("BeautifulSoup not found. Falling back to native html.parser.")

def parse_bhajans_html_bs4(html_content: str) -> list:
    """Parses HTML using BeautifulSoup."""
    soup = BeautifulSoup(html_content, "html.parser")
    bhajans = []
    
    cards = soup.find_all("div", class_="bhajan-card")
    for card in cards:
        # Title
        title_el = card.find("h2", class_="bhajan-title")
        title = title_el.get_text().strip() if title_el else ""
        
        # Deity
        deity_el = card.find("span", class_="deity-name")
        deity = deity_el.get_text().strip() if deity_el else ""
        
        # Raga
        raga_el = card.find("span", class_="raga-name")
        raga = raga_el.get_text().strip() if raga_el else "Unknown"
        
        # Beat
        beat_el = card.find("span", class_="beat-name")
        beat = beat_el.get_text().strip() if beat_el else "Unknown"
        
        # Lyrics
        lyrics_el = card.find("div", class_="bhajan-lyrics")
        if lyrics_el:
            # Create a copy/work inline to replace <br/> with \n
            for br in lyrics_el.find_all("br"):
                br.replace_with("\n")
            lyrics = lyrics_el.get_text().strip()
        else:
            lyrics = ""
            
        # Audio URL
        audio_el = card.find("audio", class_="audio-player")
        audio_url = audio_el.get("src", "").strip() if audio_el else ""
        
        if title and deity:
            bhajans.append({
                "title": title,
                "deity": deity,
                "raga": raga,
                "beat": beat,
                "lyrics": lyrics,
                "audio_url": audio_url
            })
            
    return bhajans

if not USE_BS4:
    from html.parser import HTMLParser

    class FallbackBhajanParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.bhajans = []
            self.current_bhajan = None
            self.current_field = None
            self.field_opening_tag = None
            self.field_tag_depth = 0
            self.in_lyrics = False
            self.lyrics_div_depth = None
            self.div_depth = 0
            self.lyrics_buffer = []

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)
            class_name = attrs_dict.get("class", "")
            
            if tag == "div" and class_name == "bhajan-card" and self.current_bhajan is None:
                self.current_bhajan = {
                    "title": "",
                    "deity": "",
                    "raga": "Unknown",
                    "beat": "Unknown",
                    "lyrics": "",
                    "audio_url": ""
                }
                self.lyrics_buffer = []
                self.in_lyrics = False
                self.div_depth = 1
                self.lyrics_div_depth = None
                self.current_field = None
                self.field_opening_tag = None
                self.field_tag_depth = 0
                
            elif self.current_bhajan is not None:
                if tag == "div":
                    self.div_depth += 1
                    if class_name == "bhajan-lyrics":
                        self.in_lyrics = True
                        self.lyrics_div_depth = self.div_depth
                elif tag == "h2" and class_name == "bhajan-title":
                    self.current_field = "title"
                    self.field_opening_tag = "h2"
                    self.field_tag_depth = 1
                elif tag == "span" and class_name == "deity-name":
                    self.current_field = "deity"
                    self.field_opening_tag = "span"
                    self.field_tag_depth = 1
                elif tag == "span" and class_name == "raga-name":
                    self.current_field = "raga"
                    self.current_bhajan["raga"] = ""  # Clear default for appending
                    self.field_opening_tag = "span"
                    self.field_tag_depth = 1
                elif tag == "span" and class_name == "beat-name":
                    self.current_field = "beat"
                    self.current_bhajan["beat"] = ""  # Clear default for appending
                    self.field_opening_tag = "span"
                    self.field_tag_depth = 1
                elif tag == "audio" and class_name == "audio-player":
                    self.current_bhajan["audio_url"] = attrs_dict.get("src", "").strip()
                elif tag == "br" and self.in_lyrics:
                    self.lyrics_buffer.append("\n")
                elif self.current_field is not None and tag == self.field_opening_tag:
                    self.field_tag_depth += 1

        def handle_data(self, data):
            if not self.current_bhajan:
                return
            if self.in_lyrics:
                self.lyrics_buffer.append(data)
            elif self.current_field:
                self.current_bhajan[self.current_field] += data

        def handle_endtag(self, tag):
            if self.current_bhajan is None:
                return
                
            if tag == "div":
                if self.in_lyrics and self.div_depth == self.lyrics_div_depth:
                    self.in_lyrics = False
                    self.lyrics_div_depth = None
                
                self.div_depth -= 1
                if self.div_depth == 0:
                    self.current_bhajan["lyrics"] = "".join(self.lyrics_buffer).strip()
                    self.current_bhajan["title"] = self.current_bhajan["title"].strip()
                    self.current_bhajan["deity"] = self.current_bhajan["deity"].strip()
                    self.current_bhajan["raga"] = self.current_bhajan["raga"].strip() or "Unknown"
                    self.current_bhajan["beat"] = self.current_bhajan["beat"].strip() or "Unknown"
                    
                    if self.current_bhajan["title"] and self.current_bhajan["deity"]:
                        self.bhajans.append(self.current_bhajan)
                    self.current_bhajan = None
                    self.lyrics_buffer = []
                    
            elif self.current_field is not None and tag == self.field_opening_tag:
                self.field_tag_depth -= 1
                if self.field_tag_depth == 0:
                    self.current_field = None
                    self.field_opening_tag = None

def parse_bhajans_html(html_content: str) -> list:
    """Parses HTML content using the appropriate parser (BeautifulSoup or HTMLParser fallback)."""
    if USE_BS4:
        return parse_bhajans_html_bs4(html_content)
    else:
        parser = FallbackBhajanParser()
        parser.feed(html_content)
        return parser.bhajans

def scrape_and_populate(html_path: str, db_path: str) -> int:
    """Reads html_path, parses it, initializes db, saves bhajans, and returns success count."""
    logger.info(f"Reading mock source from: {html_path}")
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"Mock source file not found at {html_path}")
        
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    bhajans = parse_bhajans_html(html_content)
    logger.info(f"Parsed {len(bhajans)} bhajans from HTML.")
    
    # Initialize the database
    init_db(db_path)
    
    success_count = 0
    for bhajan in bhajans:
        try:
            save_bhajan(bhajan, db_path)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to save bhajan '{bhajan.get('title')}': {e}")
            
    logger.info(f"Successfully populated {success_count} bhajans into database.")
    return success_count

if __name__ == "__main__":
    # Locate project root and set defaults
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_html = os.path.join(base_dir, "backend", "mock_data", "bhajans_source.html")
    default_db = os.path.join(base_dir, "backend", "bhajans.db")
    
    try:
        scrape_and_populate(default_html, default_db)
    except Exception as e:
        logger.error(f"Scraper execution failed: {e}")
        sys.exit(1)
