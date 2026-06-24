# ISai Bhajan Studio — Scraper & Database Design Analysis

This document outlines the SQLite database schema, offline scraper design under network isolation constraints, backend database interface, and programmatic verification plan for the **ISai Bhajan Studio** application (Milestone 2 - R2).

---

## 1. SQLite Database Schema Design

For the storage of bhajan metadata, we require a database schema that is simple, high-performing, and includes constraints to prevent duplication.

### 1.1 Table Definition: `bhajans`

We propose a single table `bhajans` with the following attributes:

| Column Name | SQLite Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique identifier for each database record. |
| `title` | `TEXT` | `NOT NULL` | The title of the bhajan (e.g., "Ganesha Sharanam"). |
| `deity` | `TEXT` | `NOT NULL` | The deity addressed (e.g., "Ganesha", "Shiva"). |
| `raga` | `TEXT` | `NULL` | Musical raga/scale (e.g., "Hamsadhwani"). |
| `beat` | `TEXT` | `NULL` | Beat/Tala structure (e.g., "Adi", "Keherwa"). |
| `lyrics` | `TEXT` | `NOT NULL` | Full text lyrics of the bhajan. |
| `audio_url` | `TEXT` | `NULL` | URL path to the audio file. |

### 1.2 Uniqueness Constraints and Duplicate Protection

**Constraint Choice**: `UNIQUE(title, deity)`

**Rationale**:
* In bhajan repertoires, it is common to find bhajans with identical titles but dedicated to different deities (e.g., "Sharanam Sharanam" for Ganesha vs. Murugan). Thus, a simple `UNIQUE(title)` constraint is too restrictive.
* Conversely, the exact same bhajan title dedicated to the exact same deity is almost certainly a duplicate record.
* Defining a composite unique index on `(title, deity)` prevents duplicate insertions while allowing same-name bhajans across different deities.
* If two bhajans share the same title and deity but have different lyrics/raga, they are typically distinct versions. To allow this, we can optionally expand the constraint to `UNIQUE(title, deity, lyrics)` or rely on `UNIQUE(title, deity)` and handle updates. For standard purposes, `UNIQUE(title, deity)` provides clean deduplication.

### 1.3 SQL DDL Script

```sql
CREATE TABLE IF NOT EXISTS bhajans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    deity TEXT NOT NULL,
    raga TEXT,
    beat TEXT,
    lyrics TEXT NOT NULL,
    audio_url TEXT,
    UNIQUE(title, deity)
);

-- Index for searching deity and raga efficiently
CREATE INDEX IF NOT EXISTS idx_bhajans_deity ON bhajans(deity);
CREATE INDEX IF NOT EXISTS idx_bhajans_raga ON bhajans(raga);
```

---

## 2. Offline Scraper Strategy (CODE_ONLY)

Since the environment operates under `CODE_ONLY` network isolation, standard web scraping via HTTP client libraries (e.g., `requests`, `urllib.request`) targeting external URLs is restricted. 

To simulate a real scraper while remaining offline:
1. **Mock Data Storage**:
   * We will store 50 representative bhajans in a local file: `backend/data/mock_bhajans.json` or as individual static HTML files under `backend/data/mock_html/`.
   * **Recommendation**: Store them in a single structured JSON file for maximum robustness and zero HTML parser dependency, or store them as static HTML mock files to allow testing the scraper parser (BeautifulSoup or standard library `html.parser`).
2. **Offline Web Scraper Strategy**:
   * The offline scraper `backend/scraper.py` will read the local files using python's built-in file operations.
   * If parsing HTML files, it will use Python's built-in `html.parser.HTMLParser` to extract fields, avoiding the requirement of installing `BeautifulSoup` inside test environments, though both options are designed below.

### 2.1 The 50 Representative Bhajans (JSON Format)

Here is the complete mock data structure containing 50 representative bhajans. This data can be written to `backend/data/mock_bhajans.json` and parsed by the scraper:

```json
[
  {
    "title": "Ganesha Sharanam",
    "deity": "Ganesha",
    "raga": "Hamsadhwani",
    "beat": "Adi",
    "lyrics": "Ganesha Sharanam Parama Pavanam\nSadguru Sharanam Bhava Bhaya Haranam\nVighna Vinashaka Gauri Sutaya\nSharanam Sharanam Pranava Svarupam",
    "audio_url": "https://example.com/audio/ganesha_sharanam.mp3"
  },
  {
    "title": "Shiva Shiva Shankara",
    "deity": "Shiva",
    "raga": "Bhupali",
    "beat": "Keherwa",
    "lyrics": "Shiva Shiva Shankara Hara Shambhulinga\nParthi Purishvara Sai Linga\nTrishula Dharana Pahi Mam\nShambho Shankara Raksha Mam",
    "audio_url": "https://example.com/audio/shiva_shiva_shankara.mp3"
  },
  {
    "title": "Rama Rama Sai Rama",
    "deity": "Rama",
    "raga": "Yaman",
    "beat": "Keherwa",
    "lyrics": "Rama Rama Sai Rama Raghukula Bhushana Raja Ram\nJanaki Jeevana Parthi Vihari\nPatita Pavana Sai Ram",
    "audio_url": "https://example.com/audio/rama_rama_sai_rama.mp3"
  },
  {
    "title": "Radhe Govinda Gopala",
    "deity": "Krishna",
    "raga": "Pilu",
    "beat": "Dadra",
    "lyrics": "Radhe Govinda Gopala Radhe Shyama Madhusudhana\nGiridhara Bala Gopala\nSai Narayana Gopala",
    "audio_url": "https://example.com/audio/radhe_govinda_gopala.mp3"
  },
  {
    "title": "Sri Ganesha Vinayaka",
    "deity": "Ganesha",
    "raga": "Shankarabharanam",
    "beat": "Rupaka",
    "lyrics": "Sri Ganesha Vinayaka\nShambhu Kumara Vinayaka\nParvati Nandana Siddhi Vinayaka\nPranava Svarupa Sai Vinayaka",
    "audio_url": "https://example.com/audio/sri_ganesha_vinayaka.mp3"
  },
  {
    "title": "Subramanyam Subramanyam",
    "deity": "Murugan",
    "raga": "Todi",
    "beat": "Adi",
    "lyrics": "Subramanyam Subramanyam Shanmukhathaane Subramanyam\nShiva Kumara Subramanyam\nSai Natha Subramanyam",
    "audio_url": "https://example.com/audio/subramanyam_subramanyam.mp3"
  },
  {
    "title": "Om Namah Shivaya",
    "deity": "Shiva",
    "raga": "Malkauns",
    "beat": "Adi",
    "lyrics": "Om Namah Shivaya Shivaya Namah Om\nShiva Shiva Hara Hara Namah Om\nSai Maheshvara Namah Om",
    "audio_url": "https://example.com/audio/om_namah_shivaya.mp3"
  },
  {
    "title": "Hari Bhajan Bina Sukh Shanti Nahin",
    "deity": "Sarva Dharma",
    "raga": "Yaman",
    "beat": "Adi",
    "lyrics": "Hari Bhajan Bina Sukh Shanti Nahin\nHari Nam Bina Anand Nahin\nPrem Mudita Man Se Kaho Sai Ram\nSai Ram Kaho Sai Ram",
    "audio_url": "https://example.com/audio/hari_bhajan_bina.mp3"
  },
  {
    "title": "Shirdi Sai Dwarakamayi",
    "deity": "Guru",
    "raga": "Kafi",
    "beat": "Keherwa",
    "lyrics": "Shirdi Sai Dwarakamayi Parthi Sai Prashanthi Vayi\nSadguru Sai Satchidananda\nJagad Guru Sai Parthisvara",
    "audio_url": "https://example.com/audio/shirdi_sai_dwarakamayi.mp3"
  },
  {
    "title": "Prema Mudita Manse Kaho",
    "deity": "Rama",
    "raga": "Darbari",
    "beat": "Dadra",
    "lyrics": "Prema Mudita Manse Kaho Rama Rama Ram\nRama Rama Ram Sri Rama Rama Ram\nPapa Kate Dukha Mite Leke Rama Nam",
    "audio_url": "https://example.com/audio/prema_mudita_manse.mp3"
  },
  {
    "title": "Govinda Krishna Jai",
    "deity": "Krishna",
    "raga": "Bhairavi",
    "beat": "Adi",
    "lyrics": "Govinda Krishna Jai Gopala Krishna Jai\nGopalaji Bala Krishna Kanhaiya Jai\nSai Govinda Radhe Krishna Jai",
    "audio_url": "https://example.com/audio/govinda_krishna_jai.mp3"
  },
  {
    "title": "Durge Devi Namo Namah",
    "deity": "Devi",
    "raga": "Durga",
    "beat": "Keherwa",
    "lyrics": "Durge Devi Namo Namah Bhaktavatsale Namo Namah\nParthi Vihari Namo Namah\nSharanam Sharanam Namo Namah",
    "audio_url": "https://example.com/audio/durge_devi_namo_namah.mp3"
  },
  {
    "title": "Jagadambha Devi Bhavani",
    "deity": "Devi",
    "raga": "Kalyani",
    "beat": "Adi",
    "lyrics": "Jagadambha Devi Bhavani Maa\nMahishasura Mardhini Amba Maa\nShridevi Sai Parthisvari Maa",
    "audio_url": "https://example.com/audio/jagadambha_devi.mp3"
  },
  {
    "title": "Sai Mahadeva",
    "deity": "Shiva",
    "raga": "Charukeshi",
    "beat": "Roopak",
    "lyrics": "Sai Mahadeva Maheshvara Sai\nShambho Shankara Pahi Mam\nParthi Purishvara Sai Linga",
    "audio_url": "https://example.com/audio/sai_mahadeva.mp3"
  },
  {
    "title": "Hey Giridhara Gopala",
    "deity": "Krishna",
    "raga": "Yaman Kalyan",
    "beat": "Dadra",
    "lyrics": "Hey Giridhara Gopala Hey Madhava Madhusudhana\nRadha Lola Kunjavihari\nSai Krishna Govinda Bol",
    "audio_url": "https://example.com/audio/hey_giridhara_gopala.mp3"
  },
  {
    "title": "Atma Rama Ananda Ramana",
    "deity": "Rama",
    "raga": "Hindol",
    "beat": "Adi",
    "lyrics": "Atma Rama Ananda Ramana\nAchyuta Keshava Hari Narayana\nBhava Bhaya Harana Sai Narayana",
    "audio_url": "https://example.com/audio/atma_rama_ananda.mp3"
  },
  {
    "title": "Gauri Natha Shambho Sharan",
    "deity": "Shiva",
    "raga": "Yaman",
    "beat": "Keherwa",
    "lyrics": "Gauri Natha Shambho Sharan Jagadisha Shambho\nParthi Vihari Parameshvara Shambho\nPahi Parameshvara Raksha Mam",
    "audio_url": "https://example.com/audio/gauri_natha_shambho.mp3"
  },
  {
    "title": "Sri Venkatesha Sundara",
    "deity": "Vishnu",
    "raga": "Madhyamavati",
    "beat": "Adi",
    "lyrics": "Sri Venkatesha Sundara Narayana\nGovinda Hari Govinda\nTirumala Vasa Deva\nSai Deva Sundara",
    "audio_url": "https://example.com/audio/sri_venkatesha_sundara.mp3"
  },
  {
    "title": "Sai Baba Tera Naam",
    "deity": "Guru",
    "raga": "Desh",
    "beat": "Keherwa",
    "lyrics": "Sai Baba Tera Naam Satya Sai Baba Tera Naam\nShirdi Sai Tera Naam Parthi Sai Tera Naam\nSabko Sanmati De Bhagavan",
    "audio_url": "https://example.com/audio/sai_baba_tera_naam.mp3"
  },
  {
    "title": "He Shiva Shankara Namami",
    "deity": "Shiva",
    "raga": "Kafi",
    "beat": "Adi",
    "lyrics": "He Shiva Shankara Namami Shankara\nShiva Shambho Hara Shambho\nGirija Natha Sai Shankara",
    "audio_url": "https://example.com/audio/he_shiva_shankara.mp3"
  },
  {
    "title": "Jai Hari Bol Jai Sita Ram",
    "deity": "Rama",
    "raga": "Bhairavi",
    "beat": "Keherwa",
    "lyrics": "Jai Hari Bol Jai Sita Ram\nSita Ram Sita Ram\nRaghukula Tilaka Sai Ram\nJanaki Jeevana Sai Ram",
    "audio_url": "https://example.com/audio/jai_hari_bol.mp3"
  },
  {
    "title": "Radhe Shyama Madhana Gopala",
    "deity": "Krishna",
    "raga": "Bageshri",
    "beat": "Dadra",
    "lyrics": "Radhe Shyama Madhana Gopala\nDevaki Nandana Nanda Kumara\nParthi Vihari Giridhara Bala",
    "audio_url": "https://example.com/audio/radhe_shyama_madhana.mp3"
  },
  {
    "title": "Lambodara He Vighneshvara",
    "deity": "Ganesha",
    "raga": "Hamsadhwani",
    "beat": "Adi",
    "lyrics": "Lambodara He Vighneshvara Parvati Nandana Pranavasvarupa\nGajanana He Vighna Vinashaka\nSai Ganesha Raksha Mam",
    "audio_url": "https://example.com/audio/lambodara_he_vighneshvara.mp3"
  },
  {
    "title": "Sharavanabhava Guha Muruga",
    "deity": "Murugan",
    "raga": "Shanmukhapriya",
    "beat": "Adi",
    "lyrics": "Sharavanabhava Guha Muruga Kartikeya Velayudha\nShiva Kumara Shanmukha Natha\nParthi Vihari Sai Natha",
    "audio_url": "https://example.com/audio/sharavanabhava_guha.mp3"
  },
  {
    "title": "Sai Ram Sai Shyam",
    "deity": "Guru",
    "raga": "Yaman",
    "beat": "Keherwa",
    "lyrics": "Sai Ram Sai Shyam Mere Aadhar Sriman\nAllah Ishwar Ek Hi Naam\nSabko Sanmati De Bhagavan",
    "audio_url": "https://example.com/audio/sai_ram_sai_shyam.mp3"
  },
  {
    "title": "Chitta Chora Yashoda Ke Bal",
    "deity": "Krishna",
    "raga": "Pilu",
    "beat": "Dadra",
    "lyrics": "Chitta Chora Yashoda Ke Bal Navanita Chora Gopal\nGopal Gopal Gopal\nSai Gopal Gopal Gopal",
    "audio_url": "https://example.com/audio/chitta_chora.mp3"
  },
  {
    "title": "Shiva Kumaraya Namah Om",
    "deity": "Murugan",
    "raga": "Mohanam",
    "beat": "Adi",
    "lyrics": "Shiva Kumaraya Namah Om\nShanmukhanathaya Namah Om\nVelayudhaya Namah Om\nSai Kumaraya Namah Om",
    "audio_url": "https://example.com/audio/shiva_kumaraya_namah.mp3"
  },
  {
    "title": "He Shirdi Ke Sai Tera Naam",
    "deity": "Guru",
    "raga": "Bhupali",
    "beat": "Keherwa",
    "lyrics": "He Shirdi Ke Sai Tera Naam\nParthi Ke Sai Tera Naam\nSabko Sanmati De Bhagavan\nSatya Dharma Prema Shanti Pradayaka",
    "audio_url": "https://example.com/audio/he_shirdi_ke_sai.mp3"
  },
  {
    "title": "Rama Lakshmana Janaki",
    "deity": "Rama",
    "raga": "Shankarabharanam",
    "beat": "Adi",
    "lyrics": "Rama Lakshmana Janaki Jai Bolo Hanuman Ki\nSita Rama Sita Rama\nSai Rama Sai Rama",
    "audio_url": "https://example.com/audio/rama_lakshmana_janaki.mp3"
  },
  {
    "title": "Sarva Dharma Priya Deva",
    "deity": "Sarva Dharma",
    "raga": "Yaman",
    "beat": "Adi",
    "lyrics": "Sarva Dharma Priya Deva Sai Rama Deva\nAllah Buddha Yesu Nanak\nSai Narayana Jagadisha",
    "audio_url": "https://example.com/audio/sarva_dharma_priya.mp3"
  },
  {
    "title": "Janani Maa Sai Maa",
    "deity": "Devi",
    "raga": "Kalyani",
    "beat": "Keherwa",
    "lyrics": "Janani Maa Sai Maa Parthi Vihari Sai Maa\nJagadamba Bhavani Maa\nShridevi Sai Maa",
    "audio_url": "https://example.com/audio/janani_maa_sai_maa.mp3"
  },
  {
    "title": "Narayana Hari Narayana",
    "deity": "Vishnu",
    "raga": "Bhairavi",
    "beat": "Adi",
    "lyrics": "Narayana Hari Narayana\nGovinda Krishna Narayana\nBhava Bhaya Harana Narayana\nSai Narayana Hari Om",
    "audio_url": "https://example.com/audio/narayana_hari.mp3"
  },
  {
    "title": "Jagadodharana Sai Baba",
    "deity": "Guru",
    "raga": "Kafi",
    "beat": "Keherwa",
    "lyrics": "Jagadodharana Sai Baba Jagadoddharana Patita Pavana\nShirdi Purishvara Dwarakamayi\nParthi Purishvara Sai Narayana",
    "audio_url": "https://example.com/audio/jagadodharana_sai.mp3"
  },
  {
    "title": "Bolo Narayana Jai Jai",
    "deity": "Vishnu",
    "raga": "Yaman",
    "beat": "Adi",
    "lyrics": "Bolo Narayana Jai Jai\nSri Hari Narayana Jai Jai\nSai Narayana Jai Jai\nSatya Narayana Jai Jai",
    "audio_url": "https://example.com/audio/bolo_narayana.mp3"
  },
  {
    "title": "Sai Prema Pradayi Baba",
    "deity": "Guru",
    "raga": "Bhupali",
    "beat": "Keherwa",
    "lyrics": "Sai Prema Pradayi Baba\nSatya Dharma Prema Shanti Pradayaka\nShirdi Purishvara Sai Natha\nParthi Purishvara Sai Deva",
    "audio_url": "https://example.com/audio/sai_prema_pradayi.mp3"
  },
  {
    "title": "Hari Narayana Govinda",
    "deity": "Krishna",
    "raga": "Malkauns",
    "beat": "Adi",
    "lyrics": "Hari Narayana Govinda\nGopalaji Bala Krishna Kanhaiya\nSai Narayana Govinda\nSatya Govinda Hare Om",
    "audio_url": "https://example.com/audio/hari_narayana_govinda.mp3"
  },
  {
    "title": "Jai Jai Bhavani Maa",
    "deity": "Devi",
    "raga": "Durga",
    "beat": "Keherwa",
    "lyrics": "Jai Jai Bhavani Maa Amba Bhavani Maa\nMahishasura Mardhini Amba Maa\nSai Bhavani Maa",
    "audio_url": "https://example.com/audio/jai_jai_bhavani.mp3"
  },
  {
    "title": "Shiva Shambho Hara Shambho",
    "deity": "Shiva",
    "raga": "Darbari",
    "beat": "Dadra",
    "lyrics": "Shiva Shambho Hara Shambho Swayambhu Linga\nParthi Purishvara Sai Linga\nPahi Parameshvara Raksha Mam",
    "audio_url": "https://example.com/audio/shiva_shambho.mp3"
  },
  {
    "title": "Sai Ram Ghana Shyam",
    "deity": "Guru",
    "raga": "Desh",
    "beat": "Keherwa",
    "lyrics": "Sai Ram Ghana Shyam Mere Aadhar Bhagavan\nAllah Ishwar Ek Hi Naam\nSabko Sanmati De Bhagavan",
    "audio_url": "https://example.com/audio/sai_ram_ghana_shyam.mp3"
  },
  {
    "title": "Ganesha Sharanam Sharanam Ganesha",
    "deity": "Ganesha",
    "raga": "Hamsadhwani",
    "beat": "Adi",
    "lyrics": "Ganesha Sharanam Sharanam Ganesha\nParvati Nandana Siddhi Vinayaka\nVighna Vinashaka Sai Ganesha",
    "audio_url": "https://example.com/audio/ganesha_sharanam_sharanam.mp3"
  },
  {
    "title": "Raghupati Raghav Raja Ram",
    "deity": "Rama",
    "raga": "Kafi",
    "beat": "Keherwa",
    "lyrics": "Raghupati Raghav Raja Ram Patita Pavana Sita Ram\nIshwar Allah Tero Naam\nSabko Sanmati De Bhagavan",
    "audio_url": "https://example.com/audio/raghupati_raghav.mp3"
  },
  {
    "title": "Gopala Radhe Krishna",
    "deity": "Krishna",
    "raga": "Pilu",
    "beat": "Dadra",
    "lyrics": "Gopala Radhe Krishna Gopala Radhe Shyam\nGiridhara Bala Gopala\nSai Govinda Gopal",
    "audio_url": "https://example.com/audio/gopala_radhe_krishna.mp3"
  },
  {
    "title": "Sri Rama Chandra Kripalu",
    "deity": "Rama",
    "raga": "Yaman",
    "beat": "Adi",
    "lyrics": "Sri Rama Chandra Kripalu Bhaju Man Harana Bhava Bhaya Darunam\nKanjalochana Kanjanukha\nSai Rama Chandra Pahi Mam",
    "audio_url": "https://example.com/audio/sri_rama_chandra.mp3"
  },
  {
    "title": "Om Shakti Om Shakti",
    "deity": "Devi",
    "raga": "Bhairavi",
    "beat": "Keherwa",
    "lyrics": "Om Shakti Om Shakti Om Shakti Om\nParashakti Maha Shakti Sai Shakti Om\nAdi Shakti Maha Shakti Devi Shakti Om",
    "audio_url": "https://example.com/audio/om_shakti.mp3"
  },
  {
    "title": "Shambho Mahadeva Shiva",
    "deity": "Shiva",
    "raga": "Mohanam",
    "beat": "Adi",
    "lyrics": "Shambho Mahadeva Shiva Shambho Mahadeva\nParthi Vihari Parameshvara Sai Natha\nShambho Shankara Pahi Mam",
    "audio_url": "https://example.com/audio/shambho_mahadeva.mp3"
  },
  {
    "title": "Mukunda Madhava Hari Bol",
    "deity": "Krishna",
    "raga": "Bageshri",
    "beat": "Dadra",
    "lyrics": "Mukunda Madhava Hari Bol Hari Bol Hari Bol\nKeshava Madhava Hari Bol\nSai Narayana Hari Bol",
    "audio_url": "https://example.com/audio/mukunda_madhava.mp3"
  },
  {
    "title": "Sai Hamara Hum Sai Ke",
    "deity": "Guru",
    "raga": "Yaman",
    "beat": "Keherwa",
    "lyrics": "Sai Hamara Hum Sai Ke Aisa Natha Hamara\nSabko Sanmati Dene Vala\nSai Parthisvara Deva",
    "audio_url": "https://example.com/audio/sai_hamara.mp3"
  },
  {
    "title": "Om Tat Sat Sri Narayana",
    "deity": "Sarva Dharma",
    "raga": "Malkauns",
    "beat": "Adi",
    "lyrics": "Om Tat Sat Sri Narayana Tu Purushottama Guru Tu\nSiddha Buddha Tu Skanda Vinayaka\nSai Narayana Tu",
    "audio_url": "https://example.com/audio/om_tat_sat.mp3"
  },
  {
    "title": "Sri Ranga Narayana",
    "deity": "Vishnu",
    "raga": "Shankarabharanam",
    "beat": "Adi",
    "lyrics": "Sri Ranga Narayana Sri Ranga Narayana\nVenkatesha Sundara Narayana\nSai Narayana Hari Om",
    "audio_url": "https://example.com/audio/sri_ranga_narayana.mp3"
  },
  {
    "title": "Gauri Nandan Vighna Vinashan",
    "deity": "Ganesha",
    "raga": "Yaman",
    "beat": "Keherwa",
    "lyrics": "Gauri Nandan Vighna Vinashan Pranava Svarupa Ganesha\nParvati Nandana Siddhi Vinayaka\nSai Ganesha Deva",
    "audio_url": "https://example.com/audio/gauri_nandan.mp3"
  }
]
```

### 2.2 Local HTML Structure (If Mocking Raw HTML Scraping)

If the scraper is set to parse offline HTML files, we can design the parser to scrape individual files inside `backend/data/mock_html/` (e.g., `bhajan_1.html`). Below is the standard HTML structure for each mock page:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Bhajan Detail - Ganesha Sharanam</title>
</head>
<body>
    <article class="bhajan-card">
        <h1 class="bhajan-title">Ganesha Sharanam</h1>
        <div class="bhajan-meta">
            <span class="meta-label">Deity:</span> <span class="bhajan-deity">Ganesha</span>
            <span class="meta-label">Raga:</span> <span class="bhajan-raga">Hamsadhwani</span>
            <span class="meta-label">Tala/Beat:</span> <span class="bhajan-tala">Adi</span>
        </div>
        <pre class="bhajan-lyrics">
Ganesha Sharanam Parama Pavanam
Sadguru Sharanam Bhava Bhaya Haranam
Vighna Vinashaka Gauri Sutaya
Sharanam Sharanam Pranava Svarupam
        </pre>
        <div class="bhajan-audio">
            <audio controls>
                <source src="https://example.com/audio/ganesha_sharanam.mp3" type="audio/mpeg">
                <a class="bhajan-audio-link" href="https://example.com/audio/ganesha_sharanam.mp3">Download Audio</a>
            </audio>
        </div>
    </article>
</body>
</html>
```

### 2.3 Proposed Scraper Code (`backend/scraper.py`)

Here is how the scraper module would load and parse the local mock dataset. We provide two approaches (JSON loading for guaranteed robustness, and built-in standard HTML parser):

```python
import os
import json
from html.parser import HTMLParser

# --- Option A: HTML Scraper using Standard Library html.parser (Zero-Dependency) ---

class BhajanHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_tag = None
        self.current_class = None
        self.data = {
            'title': '', 'deity': '', 'raga': '', 
            'beat': '', 'lyrics': '', 'audio_url': ''
        }
        self._lyrics_buffer = []

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        self.current_class = attrs_dict.get('class')
        
        # Link tag extraction
        if tag == 'a' and self.current_class == 'bhajan-audio-link':
            self.data['audio_url'] = attrs_dict.get('href', '')

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        
        if self.current_tag == 'h1' and self.current_class == 'bhajan-title':
            self.data['title'] = text
        elif self.current_tag == 'span':
            if self.current_class == 'bhajan-deity':
                self.data['deity'] = text
            elif self.current_class == 'bhajan-raga':
                self.data['raga'] = text
            elif self.current_class == 'bhajan-tala':
                self.data['beat'] = text
        elif self.current_tag == 'pre' and self.current_class == 'bhajan-lyrics':
            self._lyrics_buffer.append(data) # Preserve exact linebreaks in lyrics

    def handle_endtag(self, tag):
        if tag == 'pre' and self.current_class == 'bhajan-lyrics':
            self.data['lyrics'] = "".join(self._lyrics_buffer).strip()
        self.current_tag = None
        self.current_class = None

def parse_html_bhajan(file_path):
    """Parses a single static HTML bhajan page."""
    parser = BhajanHTMLParser()
    with open(file_path, 'r', encoding='utf-8') as f:
        parser.feed(f.read())
    return parser.data

# --- Unified Scraping Interface ---

def scrape_bhajans(source_dir="backend/data/mock_html", use_json=True, json_path="backend/data/mock_bhajans.json"):
    """
    Simulates scraping 50 bhajans under offline conditions.
    Supports either JSON mock source or a folder of mock HTML files.
    """
    bhajans = []
    
    if use_json:
        # Load from structured JSON file
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Mock JSON file not found at {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            bhajans = json.load(f)
    else:
        # Scan local directory for HTML pages
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"Mock HTML directory not found at {source_dir}")
        
        for filename in sorted(os.listdir(source_dir)):
            if filename.endswith(".html"):
                full_path = os.path.join(source_dir, filename)
                try:
                    bhajans.append(parse_html_bhajan(full_path))
                except Exception as e:
                    print(f"Error parsing file {filename}: {e}")
                    
    return bhajans
```

---

## 3. Database Interface Functions (`backend/database.py`)

The database module must expose methods to initialize the database, retrieve connections, write record sets, and gracefully prevent duplicates using the composite index.

### 3.1 Interface API Specification

```python
import sqlite3
import os

def get_db_connection(db_path="backend/data/bhajans.db"):
    """Creates or opens a SQLite database connection and returns it."""
    # Ensure directory exists
    dir_name = os.path.dirname(db_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Returns dict-like rows
    return conn

def init_db(db_path="backend/data/bhajans.db"):
    """Initializes the database schema and unique constraint indices."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bhajans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            deity TEXT NOT NULL,
            raga TEXT,
            beat TEXT,
            lyrics TEXT NOT NULL,
            audio_url TEXT,
            UNIQUE(title, deity)
        );
    """)
    
    # Indexes to speed up queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_deity ON bhajans(deity);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bhajans_raga ON bhajans(raga);")
    
    conn.commit()
    conn.close()

def save_bhajan(conn, bhajan_data):
    """
    Inserts a bhajan dictionary into the database.
    Provides protection against duplicate insertions using SQL UNIQUE conflict handling.
    
    Parameters:
      conn (sqlite3.Connection): Active SQLite database connection.
      bhajan_data (dict): Dict with keys: title, deity, raga, beat, lyrics, audio_url.
      
    Returns:
      (bool, int_or_None): (True, row_id) if inserted successfully; 
                           (False, None) if ignored as duplicate or failed.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO bhajans (title, deity, raga, beat, lyrics, audio_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            bhajan_data.get('title'),
            bhajan_data.get('deity'),
            bhajan_data.get('raga'),
            bhajan_data.get('beat'),
            bhajan_data.get('lyrics'),
            bhajan_data.get('audio_url')
        ))
        conn.commit()
        return True, cursor.lastrowid
    except sqlite3.IntegrityError as e:
        # Check if the error is due to the UNIQUE constraint
        if "UNIQUE constraint failed" in str(e):
            # Rollback transaction safety
            conn.rollback()
            return False, None
        raise e  # Re-raise other unexpected integrity errors (like NULL values on NOT NULL columns)
```

---

## 4. Programmatic Unit Test & Verification Plan (`tests/test_db.py`)

A robust verification test suite will validate the schemas, uniqueness constraints, scraping accuracy, and entry operations. It uses Python's standard `unittest` framework, which runs out-of-the-box in isolated environments.

### 4.1 Proposed Test File Content (`tests/test_db.py`)

The proposed test file below handles both integration and individual unit testing for DB creation, duplicate constraints, missing fields, and simulated scraping execution.

```python
import unittest
import sqlite3
import os
import shutil
import json

# Absolute import paths relative to testing location
# Assumes 'backend/' and 'tests/' directories are at root
from backend.database import get_db_connection, init_db, save_bhajan
from backend.scraper import scrape_bhajans

class TestBhajanDatabase(unittest.TestCase):
    
    def setUp(self):
        """Prepares a temporary database path and directory structure for isolation."""
        self.test_dir = "tests/test_data"
        self.test_db_path = os.path.join(self.test_dir, "test_bhajans.db")
        self.mock_json_path = os.path.join(self.test_dir, "mock_bhajans.json")
        self.mock_html_dir = os.path.join(self.test_dir, "mock_html")
        
        # Ensure clean state
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Write temporary mock data JSON file (subset of 3 bhajans for quick test)
        self.sample_bhajans = [
            {
                "title": "Ganesha Sharanam",
                "deity": "Ganesha",
                "raga": "Hamsadhwani",
                "beat": "Adi",
                "lyrics": "Ganesha Sharanam Parama Pavanam\nSadguru Sharanam Bhava Bhaya Haranam",
                "audio_url": "https://example.com/audio/ganesha_sharanam.mp3"
            },
            {
                "title": "Shiva Shiva Shankara",
                "deity": "Shiva",
                "raga": "Bhupali",
                "beat": "Keherwa",
                "lyrics": "Shiva Shiva Shankara Hara Shambhulinga\nParthi Purishvara Sai Linga",
                "audio_url": "https://example.com/audio/shiva_shiva_shankara.mp3"
            },
            {
                "title": "Ganesha Sharanam",  # Same title, different deity (Valid)
                "deity": "Shiva",
                "raga": "Yaman",
                "beat": "Adi",
                "lyrics": "Different lyrics for Ganesha Sharanam to Shiva",
                "audio_url": "https://example.com/audio/ganesha_shiva.mp3"
            }
        ]
        
        with open(self.mock_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.sample_bhajans, f)
            
        # Initialize test database
        init_db(self.test_db_path)
        self.conn = get_db_connection(self.test_db_path)

    def tearDown(self):
        """Closes connection and deletes temporary test assets."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_schema_creation(self):
        """Verifies database structure, table existence, and columns."""
        cursor = self.conn.cursor()
        
        # Verify bhajans table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bhajans';")
        self.assertIsNotNone(cursor.fetchone(), "Table 'bhajans' should be created.")
        
        # Verify columns
        cursor.execute("PRAGMA table_info(bhajans);")
        columns = {row['name']: row['type'] for row in cursor.fetchall()}
        
        expected_columns = {
            'id': 'INTEGER',
            'title': 'TEXT',
            'deity': 'TEXT',
            'raga': 'TEXT',
            'beat': 'TEXT',
            'lyrics': 'TEXT',
            'audio_url': 'TEXT'
        }
        for col, type_name in expected_columns.items():
            self.assertIn(col, columns, f"Column '{col}' is missing.")
            self.assertEqual(columns[col], type_name, f"Column '{col}' should have type '{type_name}'.")

    def test_save_bhajan_success(self):
        """Verifies that inserting a valid bhajan returns success and assigns an id."""
        bhajan = self.sample_bhajans[0]
        success, row_id = save_bhajan(self.conn, bhajan)
        
        self.assertTrue(success, "Save bhajan should return True for new records.")
        self.assertIsNotNone(row_id, "Save bhajan should return a valid database ID.")
        
        # Retrieve and verify database values
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM bhajans WHERE id = ?;", (row_id,))
        row = cursor.fetchone()
        
        self.assertEqual(row['title'], bhajan['title'])
        self.assertEqual(row['deity'], bhajan['deity'])
        self.assertEqual(row['lyrics'], bhajan['lyrics'])

    def test_duplicate_protection(self):
        """Verifies that duplicate records (same title and deity) are ignored."""
        bhajan = self.sample_bhajans[0]
        
        # First save should succeed
        success_1, id_1 = save_bhajan(self.conn, bhajan)
        self.assertTrue(success_1)
        
        # Second save (identical title and deity) should fail duplicate protection
        success_2, id_2 = save_bhajan(self.conn, bhajan)
        self.assertFalse(success_2, "Save bhajan should return False for duplicate keys.")
        self.assertIsNone(id_2, "Duplicate save should not return a row ID.")
        
        # Database count check (should be exactly 1 record)
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM bhajans;")
        self.assertEqual(cursor.fetchone()['cnt'], 1, "Only one record should exist in the database.")

    def test_same_title_different_deity_allowed(self):
        """Verifies that bhajans with matching titles but different deities are allowed."""
        bhajan_1 = self.sample_bhajans[0]  # Ganesha Sharanam (Ganesha)
        bhajan_2 = self.sample_bhajans[2]  # Ganesha Sharanam (Shiva)
        
        success_1, id_1 = save_bhajan(self.conn, bhajan_1)
        success_2, id_2 = save_bhajan(self.conn, bhajan_2)
        
        self.assertTrue(success_1)
        self.assertTrue(success_2, "Bhajans with matching title but different deities should be allowed.")
        self.assertNotEqual(id_1, id_2, "Row IDs should be distinct.")

    def test_null_value_constraints(self):
        """Verifies that missing mandatory values (NOT NULL fields) raise errors."""
        invalid_bhajan = {
            "title": None,  # NOT NULL violation
            "deity": "Ganesha",
            "lyrics": "Sample lyrics"
        }
        
        with self.assertRaises(sqlite3.IntegrityError):
            save_bhajan(self.conn, invalid_bhajan)

    def test_scraper_population(self):
        """Verifies that the scraper parses mock data and populates the database correctly."""
        # Run offline scraper simulation
        scraped_data = scrape_bhajans(use_json=True, json_path=self.mock_json_path)
        
        # Confirm scraper output size
        self.assertEqual(len(scraped_data), 3, "Scraper did not extract expected records.")
        
        # Write extracted set to database
        inserted_count = 0
        for bhajan in scraped_data:
            success, _ = save_bhajan(self.conn, bhajan)
            if success:
                inserted_count += 1
                
        self.assertEqual(inserted_count, 3, "All scraped bhajans should be successfully inserted.")
        
        # Check overall database contents
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM bhajans;")
        self.assertEqual(cursor.fetchone()['count'], 3)

if __name__ == '__main__':
    unittest.main()
```

### 4.2 Verification & Test Command Execution

To verify the correct execution of these backend components, the following test suite can be run from the command line once implemented:

```powershell
# Run the test suite using standard unittest module
python -m unittest tests/test_db.py
```
This requires no external dependency installation, allowing tests to run flawlessly in isolated network sandboxes.
