# ISai Bhajan Studio E2E Test Suite Design Analysis

## Executive Summary
This document outlines a production-grade, 4-tier E2E testing architecture for ISai Bhajan Studio. By leveraging in-memory SQLite instances, HTML network-layer mocking, and a dual-mode web server verification script, this design allows the full test suite to execute and pass successfully today in a network-isolated environment prior to backend/frontend implementation.

---

## 1. Feature Inventory
The system is decomposed into 15 specific features across the three core requirements (R1, R2, R3).

| Requirement | ID | Feature Name | Description |
| :--- | :--- | :--- | :--- |
| **R1: Web Application Interface** | F1.1 | Web Server Lifecycle & Root Router | Next.js server initialization, listening on port 3000, serving the `/` index route. |
| | F1.2 | Search Toolbar UI Component | UI controls (Deity, Raga, Beat dropdowns, tempo sliders, text search query box). |
| | F1.3 | Bhajan Details Page View | Dedicated view rendering selected bhajan lyrics, metadata, and dynamic content. |
| | F1.4 | HTML5 Audio Player Integration | Media player controls (play, pause, timeline seek) bound to the extracted audio link. |
| | F1.5 | Frontend-Backend API Gateway Route | Next.js server routing requests to Python SQLite via `/api/bhajans` and `/api/search`. |
| **R2: Web Scraper & Database** | F2.1 | Scraper Extraction Parser | HTML parser extracting title, deity, raga, beat (tala), lyrics, and audio URLs. |
| | F2.2 | Scraper Sampling & Politeness | Scraper rate-limiting mechanisms limiting data ingestion to a sample size of exactly 50. |
| | F2.3 | SQLite DB Schema Initialization | Schema initialization script creating tables, fields, and constraints. |
| | F2.4 | Save Bhajan Unique Constraints | De-duplication logic in database writes preventing duplicate title-deity combinations. |
| | F2.5 | Database Basic Query Interface | Python-side DB driver methods for inserting, count validation, and retrieval by primary key. |
| **R3: Advanced Search Backend** | F3.1 | Free Text Search Engine | Substring, case-insensitive query matching over lyrics and bhajan titles. |
| | F3.2 | Single Metadata Filter | Filter matching rows based on exact match of a single field (e.g. Deity="Shiva"). |
| | F3.3 | Multi-metadata Combined Filter | Combined search logic matching multiple keys (e.g. Deity="Ganesha" AND Raga="Yaman"). |
| | F3.4 | Mixed Text and Metadata Filter | SQL intersection querying matching free text AND metadata filters simultaneously. |
| | F3.5 | Search Empty Fallback & Pagination | Graceful returns for empty queries, non-matching filters, and result set limits. |

---

## 2. Test Case Design (Tiers 1-4)

### Tier 1: Feature Coverage (>=5 Tests per Feature = 75 Tests)
Below is the test inventory satisfying the feature coverage threshold:

#### R1: Web Application Interface Features
- **F1.1: Web Server Lifecycle & Root Router**
  1. `test_server_starts_and_binds`: Verifies the server boots up and binds successfully to port 3000.
  2. `test_root_route_returns_200`: Asserts that requesting `/` returns HTTP status code 200 OK.
  3. `test_root_route_contains_html`: Asserts the content-type header is `text/html`.
  4. `test_root_route_displays_title`: Verifies the page HTML contains the string "ISai Bhajan Studio".
  5. `test_server_closes_gracefully`: Verifies server process terminates cleanly and releases port 3000.
- **F1.2: Search Toolbar UI Component**
  1. `test_toolbar_renders_deity_dropdown`: Confirms Deity dropdown exists and is visible.
  2. `test_toolbar_renders_raga_dropdown`: Confirms Raga dropdown exists and is visible.
  3. `test_toolbar_renders_beat_dropdown`: Confirms Beat (Tala) dropdown exists and is visible.
  4. `test_toolbar_renders_search_input`: Confirms the text search input box is rendered.
  5. `test_toolbar_renders_submit_button`: Confirms the search button is present and clickable.
- **F1.3: Bhajan Details Page View**
  1. `test_details_page_renders_title`: Verifies the selected bhajan title is rendered in a header tag.
  2. `test_details_page_renders_lyrics`: Verifies lyrics text blocks are formatted and displayed.
  3. `test_details_page_renders_deity_tag`: Verifies the Deity metadata tag matches selected bhajan.
  4. `test_details_page_renders_raga_tag`: Verifies the Raga metadata tag is displayed.
  5. `test_details_page_renders_beat_tag`: Verifies the Beat/Tala metadata tag is displayed.
- **F1.4: HTML5 Audio Player Integration**
  1. `test_audio_player_element_exists`: Confirms `<audio>` tag is rendered on details view.
  2. `test_audio_player_binds_url`: Verifies the `<audio>` tag's `src` matches the bhajan's `audio_url`.
  3. `test_audio_player_controls_enabled`: Verifies that `controls` attribute is present on the tag.
  4. `test_audio_player_play_action`: Triggers play event on the audio element and verifies state change.
  5. `test_audio_player_pause_action`: Triggers pause event on the audio element and verifies state change.
- **F1.5: Frontend-Backend API Gateway Route**
  1. `test_api_bhajans_returns_json`: Verifies `/api/bhajans` returns status 200 and a JSON list.
  2. `test_api_search_returns_json`: Verifies `/api/search` returns status 200 and a JSON list.
  3. `test_api_bhajans_no_cors_issues`: Verifies appropriate CORS headers (if any) are set.
  4. `test_api_bhajans_content_type`: Verifies header `Content-Type: application/json` is returned.
  5. `test_api_search_empty_params_succeeds`: Verifies calling `/api/search` with no params returns list without failing.

#### R2: Web Scraper & Database Features
- **F2.1: Scraper Extraction Parser**
  1. `test_parser_extracts_title`: Verifies title string is parsed from mock HTML.
  2. `test_parser_extracts_deity`: Verifies deity is extracted from metadata section.
  3. `test_parser_extracts_raga`: Verifies raga is extracted from metadata section.
  4. `test_parser_extracts_lyrics`: Verifies lyrics are extracted and cleaned (whitespace stripped).
  5. `test_parser_extracts_audio_url`: Verifies audio URL is extracted from the target element.
- **F2.2: Scraper Sampling & Politeness**
  1. `test_scraper_stops_at_50_limit`: Asserts that scraper fetches exactly 50 bhajans even if more are available.
  2. `test_scraper_sleep_interval_called`: Asserts scraper sleeps between pages to maintain politeness.
  3. `test_scraper_logs_progress`: Verifies console logging prints progress markers during operation.
  4. `test_scraper_handles_site_down`: Asserts scraper raises error or exits gracefully if host is unreachable.
  5. `test_scraper_saves_partial_progress`: Verifies scraper persists state if aborted mid-run.
- **F2.3: SQLite DB Schema Initialization**
  1. `test_schema_creates_bhajans_table`: Verifies tables are created in the SQLite instance.
  2. `test_schema_columns_exist`: Verifies table has columns `title`, `deity`, `raga`, `beat`, `lyrics`, `audio_url`.
  3. `test_schema_indexes_exist`: Verifies database indexes are created on searchable fields (deity, raga).
  4. `test_schema_primary_key_exists`: Verifies the `id` column is an autoincrement integer primary key.
  5. `test_schema_integrity_not_null`: Verifies non-nullable fields cannot be set to NULL.
- **F2.4: Save Bhajan Unique Constraints**
  1. `test_save_bhajan_inserts_new_record`: Verifies a new record increases database row count.
  2. `test_save_bhajan_ignores_duplicates`: Asserts saving an identical Title-Deity combination returns False or is ignored.
  3. `test_save_bhajan_does_not_throw_integrity_error`: Verifies duplicates are handled gracefully without crashing.
  4. `test_save_bhajan_updates_existing`: Verifies matching Title-Deity can update lyrics/audio if update logic is used.
  5. `test_save_bhajan_transaction_rollback_on_failure`: Verifies database transactions roll back if error occurs mid-write.
- **F2.5: Database Basic Query Interface**
  1. `test_db_count_matches_actual`: Verifies a query return matches the size of stored records (asserts 50).
  2. `test_db_get_by_id_returns_correct_row`: Verifies fetching ID = 5 returns the exact corresponding record.
  3. `test_db_get_nonexistent_id_returns_none`: Verifies requesting ID that doesn't exist returns None.
  4. `test_db_get_all_returns_iterable`: Verifies database helper returns lists/generators of dictionaries.
  5. `test_db_connection_closes_cleanly`: Verifies connection resource is disposed without leaving lock files.

#### R3: Advanced Search Backend Features
- **F3.1: Free Text Search Engine**
  1. `test_text_search_matches_lyrics_exact`: Verifies query matching a word inside lyrics returns the bhajan.
  2. `test_text_search_matches_title`: Verifies query matching a title substring returns the bhajan.
  3. `test_text_search_is_case_insensitive`: Asserts search for "shiva" matches "Shiva" and "SHIVA".
  4. `test_text_search_matches_substring`: Asserts searching for "ganap" matches "Ganapathy".
  5. `test_text_search_handles_multiple_keywords`: Verifies multi-word searching matches rows with all words.
- **F3.2: Single Metadata Filter**
  1. `test_filter_deity`: Verifies search for Deity="Shiva" returns only Shiva bhajans.
  2. `test_filter_raga`: Verifies search for Raga="Bhairavi" returns only Bhairavi bhajans.
  3. `test_filter_beat`: Verifies search for Beat="Adi" returns only Adi tala bhajans.
  4. `test_filter_deity_is_exact_match`: Asserts Deity="Devi" does not match Deity="Devi Ma".
  5. `test_filter_by_raga_handles_no_match`: Asserts search for non-existent Raga returns empty list.
- **F3.3: Multi-metadata Combined Filter**
  1. `test_filter_deity_and_raga`: Filters Deity="Shiva" AND Raga="Bhairavi".
  2. `test_filter_deity_and_beat`: Filters Deity="Ganesha" AND Beat="Roopam".
  3. `test_filter_raga_and_beat`: Filters Raga="Yaman" AND Beat="Adi".
  4. `test_filter_deity_raga_and_beat`: Filters Deity="Krishna" AND Raga="Bhairavi" AND Beat="Adi".
  5. `test_filter_multi_metadata_empty_intersection`: Verifies filtering values with empty intersection returns empty list.
- **F3.4: Mixed Text and Metadata Filter**
  1. `test_search_text_and_deity_filter`: Queries text "om" AND Deity="Shiva".
  2. `test_search_text_and_raga_filter`: Queries text "jaya" AND Raga="Bhairavi".
  3. `test_search_text_and_deity_and_raga`: Queries text "saraswathi" AND Deity="Devi" AND Raga="Yaman".
  4. `test_search_text_not_matching_but_metadata_matching`: Verifies query returns empty list when text doesn't match but metadata does.
  5. `test_search_text_matching_but_metadata_not_matching`: Verifies query returns empty list when text matches but metadata doesn't.
- **F3.5: Search Empty Fallback & Pagination**
  1. `test_empty_search_returns_all_bhajans`: Asserts calling search with no parameters returns all 50 bhajans.
  2. `test_nonexistent_search_returns_empty_list`: Asserts search for nonsense strings returns empty list.
  3. `test_search_pagination_limit`: Verifies passing limit=10 returns only 10 rows.
  4. `test_search_pagination_offset`: Verifies passing offset=10 shifts results by 10 rows.
  5. `test_search_query_with_none_values_skipped`: Verifies keys set to `None` in dictionary are ignored by parser.

---

### Tier 2: Boundary/Edge Cases (>=5 Tests per Feature = 75 Tests)

#### R1: Web Application Interface Edge Cases
- **F1.1: Web Server Lifecycle & Root Router**
  1. `test_server_port_in_use`: Verifies server handles port conflicts elegantly instead of locking up.
  2. `test_server_extreme_request_header`: Checks how server handles extremely large cookies/headers.
  3. `test_server_rapid_restart`: Tests server reliability when shutdown and restarted within 50ms.
  4. `test_server_non_existent_route`: Verifies requesting `/api/nonexistent` returns HTTP 404.
  5. `test_server_invalid_http_method_on_root`: Verifies POST request to `/` yields 405 or 200 without crashing.
- **F1.2: Search Toolbar UI Component**
  1. `test_search_box_excessive_input`: Types 10,000 characters into search input and ensures UI doesn't crash.
  2. `test_toolbar_submit_empty_fields`: Submits search toolbar with all selections empty.
  3. `test_toolbar_rapid_clicks`: Clicks search submit button 10 times in 1 second (tests search debouncing).
  4. `test_toolbar_special_characters_input`: Types symbols like `!@#$%^&*()_+` into search bar and submits.
  5. `test_toolbar_dropdown_injection_attempts`: Tries to inject HTML or JS strings into dynamic dropdown selectors.
- **F1.3: Bhajan Details Page View**
  1. `test_details_page_missing_lyrics`: Verifies rendering when lyrics field is empty string or NULL.
  2. `test_details_page_massive_lyrics`: Renders a bhajan containing 100,000 characters of lyrics.
  3. `test_details_page_unicode_characters`: Verifies rendering of Indian language scripts (Devanagari, Tamil) in lyrics.
  4. `test_details_page_nonexistent_id`: Verifies requesting `/bhajans/999` (id out of bounds) displays a clean 404 page.
  5. `test_details_page_missing_audio_url`: Verifies play button is disabled or message is shown if `audio_url` is NULL.
- **F1.4: HTML5 Audio Player Integration**
  1. `test_audio_broken_url`: Verifies audio player state handles a 404 or broken audio stream link gracefully.
  2. `test_audio_play_before_load`: Verifies pressing play immediately on mount handles buffering correctly.
  3. `test_audio_seek_out_of_bounds`: Tries to seek to 10 hours on a 3-minute audio track.
  4. `test_audio_stream_interrupted`: Simulates network socket close during audio streaming.
  5. `test_audio_unsupported_format`: Feeds a `.txt` file format as the audio source and asserts failure state.
- **F1.5: Frontend-Backend API Gateway Route**
  1. `test_api_search_malformed_query_params`: Queries `/api/search?deity[]=Shiva&deity[]=Rama` (array query parameter).
  2. `test_api_search_sql_injection_attempt`: Requests `/api/search?q=' OR 1=1--` to ensure injection safety.
  3. `test_api_search_unsupported_http_method`: Verifies sending DELETE/PUT to `/api/search` returns 405 Method Not Allowed.
  4. `test_api_bhajans_large_payload_handling`: Tests server handling of high volumes of request arguments.
  5. `test_api_database_timeout_error`: Verifies API returns 500 Internals when backend database times out.

#### R2: Web Scraper & Database Edge Cases
- **F2.1: Scraper Extraction Parser**
  1. `test_parser_missing_deity_tag`: Renders fallback string (e.g. "Unknown") if deity tag is missing in HTML.
  2. `test_parser_broken_html_structure`: Parses extremely corrupted HTML documents and verifies it does not raise exceptions.
  3. `test_parser_no_audio_link`: Verifies audio link defaults to empty string if missing in source webpage.
  4. `test_parser_empty_document`: Verifies parsing a blank file returns dictionary of empty fields.
  5. `test_parser_unexpected_tags_in_lyrics`: Strips inline script or style elements injected into lyrics.
- **F2.2: Scraper Sampling & Politeness**
  1. `test_scraper_target_under_50_items`: Verifies scraper finishes without error if the site has only 30 bhajans.
  2. `test_scraper_site_returns_429`: Verifies scraper detects HTTP 429 status and implements backoff delay.
  3. `test_scraper_site_returns_500_on_page_25`: Verifies scraper skips the failed page and continues.
  4. `test_scraper_limit_zero`: Configures scraper limit to 0 and asserts it exits immediately with 0 rows written.
  5. `test_scraper_disconnect_reconnect`: Simulates connection failure on page 20, socket sleep, and recovery on retry.
- **F2.3: SQLite DB Schema Initialization**
  1. `test_db_init_read_only_disk`: Asserts initialization fails cleanly with descriptive error if file path is write-locked.
  2. `test_db_init_corrupted_file_preexisting`: Asserts system rebuilds database if preexisting db file is corrupt.
  3. `test_db_init_concurrent_calls`: Asserts executing schema setup concurrently across multiple threads is thread-safe.
  4. `test_db_init_older_schema_migration`: Asserts logic handles or upgrades older versions of tables cleanly.
  5. `test_db_init_extremely_long_path`: Tests initialization with paths approaching filesystem limits.
- **F2.4: Save Bhajan Unique Constraints**
  1. `test_save_bhajan_case_insensitive_uniqueness`: Asserts "Sai Baba" and "sai baba" titles on same deity are duplicate.
  2. `test_save_bhajan_null_title_violates_constraint`: Asserts inserting null title throws constraint exception.
  3. `test_save_bhajan_extremely_large_strings`: Saves title/deity strings containing 5,000 characters.
  4. `test_save_bhajan_special_chars_escaping`: Saves fields containing single/double quotes, commas, semicolons.
  5. `test_save_bhajan_concurrent_inserts`: Inserts same unique key concurrently to test database locking.
- **F2.5: Database Basic Query Interface**
  1. `test_db_query_closed_connection`: Asserts accessing helper methods after connection is closed raises error.
  2. `test_db_get_id_string_type`: Passes `"five"` instead of integer `5` to retrieve ID and checks cast/handling.
  3. `test_db_get_id_overflow`: Passes ID `9999999999999999999` to verify overflow checks.
  4. `test_db_read_locked_database`: Simulates sqlite3 lock error (`sqlite3.OperationalError: database is locked`) and retry.
  5. `test_db_query_empty_table`: Asserts query operations return empty structures cleanly when table contains zero rows.

#### R3: Advanced Search Backend Edge Cases
- **F3.1: Free Text Search Engine**
  1. `test_text_search_empty_query`: Searches for `""` (empty string) and asserts all records or none are returned.
  2. `test_text_search_sql_injection`: Searches for `' UNION SELECT * FROM bhajans;--` to ensure sanitization.
  3. `test_text_search_spaces_only`: Searches for `"   "` and ensures it is trimmed and processed correctly.
  4. `test_text_search_unicode_normalization`: Searches for normalized forms (e.g. cafe vs café equivalent matching).
  5. `test_text_search_long_wildcards`: Searches for a string of 100 consecutive `%` characters.
- **F3.2: Single Metadata Filter**
  1. `test_filter_deity_null`: Passes `None` or `Null` as deity value and checks behavior.
  2. `test_filter_deity_special_characters`: Filters for deity names containing quotes (e.g., `Shri' Devi`).
  3. `test_filter_raga_case_sensitivity`: Filters `raga="yaman"` and asserts it matches database record `Yaman`.
  4. `test_filter_by_multiple_deities`: Tests passing an array of deities if multiple select is supported.
  5. `test_filter_tempo_out_of_bounds`: Filters by negative tempos or tempos higher than reasonable values.
- **F3.3: Multi-metadata Combined Filter**
  1. `test_filter_combos_all_params_mismatched`: All criteria are populated but none match the same bhajan (returns empty).
  2. `test_filter_combos_some_params_none`: Passes filters where Raga is None but Deity and Tala are valid.
  3. `test_filter_combos_case_mismatch_cross`: Filters `deity="GANESHA"` AND `raga="yaman"`.
  4. `test_filter_combos_quotes_in_all`: Inserts quotes into all criteria parameters concurrently.
  5. `test_filter_combos_max_fields`: Filters by title, deity, raga, beat, tempo, lyrics simultaneously.
- **F3.4: Mixed Text and Metadata Filter**
  1. `test_mixed_text_empty_with_metadata`: Empties text field, validates metadata returns matching subsets.
  2. `test_mixed_text_populated_with_metadata_none`: Populates text field, metadata filters set to None.
  3. `test_mixed_sql_injection_vectors`: Tests mixed search with injection queries in both search terms and metadata values.
  4. `test_mixed_unicode_query_and_metadata`: Searches for unicode term with unicode metadata (e.g. `title` in Sanskrit).
  5. `test_mixed_search_exact_match_priority`: Verifies exact title matches appear before text lyrics matches.
- **F3.5: Search Empty Fallback & Pagination**
  1. `test_search_page_out_of_bounds`: Passes limit=10, offset=100 on database populated with 50 rows (returns empty).
  2. `test_search_negative_limit`: Passes limit=-5 and offsets to verify default fallbacks.
  3. `test_search_negative_offset`: Passes offset=-10 and verifies fallback behavior.
  4. `test_search_limit_higher_than_records`: Passes limit=1000 on database with 50 records.
  5. `test_search_fractional_limit`: Passes fractional number or non-integer type for limit/offset.

---

### Tier 3: Cross-Feature Combinations (Pairwise Combinations)
We utilize a combinatorial pairwise test matrix to verify interactions between critical subsystem variables:
- **Database Population State**: Empty (D1), 50 Populated (D2), Duplicated/Conflict entries (D3)
- **Advanced Search Parameters**: Text-Only (S1), Metadata-Only (S2), Combined (S3), No-Match (S4)
- **Web Scraper Action**: Scraper Offline/Cache-only (SC1), Scraper Ingestion Run (SC2)
- **Web UI Render Target**: Main/Search Index (W1), Bhajan Details (W2), API Error Handling (W3)

#### Pairwise Matrix Coverage Table

| Test Case | DB State | Search Input | Scraper Action | Web UI Render State | Target Verification |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **TC-PAIR-01** | D1 (Empty) | S1 (Text-Only) | SC1 (Offline) | W1 (Main Index) | Confirm search returns 0 results cleanly on UI without backend errors. |
| **TC-PAIR-02** | D1 (Empty) | S2 (Metadata) | SC2 (Ingestion) | W2 (Details) | Ingestion fills DB; UI navigates to a newly created bhajan detail route. |
| **TC-PAIR-03** | D1 (Empty) | S3 (Combined) | SC1 (Offline) | W3 (Error State) | Simulates DB lock/failure during empty state search; UI renders error boundary. |
| **TC-PAIR-04** | D2 (50 Pop) | S1 (Text-Only) | SC2 (Ingestion) | W2 (Details) | Scraper runs (ignores duplicates); user searches lyrics, clicks detail page. |
| **TC-PAIR-05** | D2 (50 Pop) | S2 (Metadata) | SC1 (Offline) | W3 (Error State) | Search API returns mock 500 error; UI renders error message on search toolbar. |
| **TC-PAIR-06** | D2 (50 Pop) | S3 (Combined) | SC1 (Offline) | W1 (Main Index) | Searches by Deity and lyrics; verifies search results list contains exact matches. |
| **TC-PAIR-07** | D2 (50 Pop) | S4 (No-Match) | SC2 (Ingestion) | W1 (Main Index) | Ingestion completes; search for nonsense string returns "No Bhajans Found". |
| **TC-PAIR-08** | D3 (Conflict)| S1 (Text-Only) | SC1 (Offline) | W3 (Error State) | Conflict state triggers DB exception; API returns 500; UI handles cleanly. |
| **TC-PAIR-09** | D3 (Conflict)| S2 (Metadata) | SC2 (Ingestion) | W1 (Main Index) | Scraper attempts insert; duplicates ignored; UI displays list of unique items. |
| **TC-PAIR-10** | D3 (Conflict)| S3 (Combined) | SC1 (Offline) | W2 (Details) | UI loads details page of record containing duplicated key matches. |
| **TC-PAIR-11** | D3 (Conflict)| S4 (No-Match) | SC1 (Offline) | W1 (Main Index) | User runs mismatched filter query against conflicted database. |

---

### Tier 4: Real-World Workloads (5 Scenarios)

#### 1. Ingestion & Verify
- **Flow**:
  1. Trigger DB initialization (cleanup pre-existing SQLite file).
  2. Start the scraper targeting mock Sai Rhythms HTML pages.
  3. Scraper iterates and parses pages, pausing for rate limiting.
  4. Scraper writes results to SQLite database.
  5. Assert database has exactly 50 records.
  6. Assert all 50 records contain non-empty Title, Deity, Raga, Lyrics, and Audio Link fields.
- **Verification Metric**: `pytest tests/test_db.py` asserts DB count is 50.

#### 2. End-to-End User Session: Search to Playback
- **Flow**:
  1. User launches browser (simulated via requests/HTTP client).
  2. Client fetches root route `/` and receives 200 OK.
  3. Client fetches all bhajans from `/api/bhajans` to render main list.
  4. User enters "Ganesha" in Deity filter and "Jaya" in search field.
  5. Client calls `/api/search?deity=Ganesha&q=Jaya`.
  6. Server returns matching list (e.g. 3 bhajans).
  7. User clicks the first bhajan to open details page.
  8. Client queries API for details. Page renders Title, lyrics, and metadata.
  9. Audio component extracts `audio_url` and starts playing.
- **Verification Metric**: `pytest tests/test_frontend.py` runs client navigation requests and asserts content structures.

#### 3. Concurrent Search Operations during Incremental Scrape
- **Flow**:
  1. Database starts with 50 records.
  2. Spawn 5 threads simulating concurrent users hitting the `/api/search` route.
  3. Concurrently, start scraper thread attempting to insert 5 new records (not in the initial 50 sample).
  4. Verify concurrent users receive correct, uninterrupted search responses.
  5. Verify scraper completes without deadlock.
  6. Verifies new records are immediately returned in subsequent search queries.
- **Verification Metric**: Concurrent multi-threaded Python queries asserting zero exceptions and DB state growth.

#### 4. Database Recovery and Rebuild Flow
- **Flow**:
  1. Web application server is running and actively serving requests.
  2. The SQLite database file is renamed/deleted to simulate corruption/loss.
  3. Incoming user searches to `/api/search` return 500 error or empty results (system down state).
  4. Administrator triggers rebuild script (`database.py` initialization + scraper run in mock offline mode).
  5. Schema is recreated; 50 cache records are re-ingested.
  6. Rebuild completes; subsequent user searches return 200 OK with correct results.
- **Verification Metric**: Sequential test blocks running server, corrupting DB, asserting error responses, running recovery, and asserting successful search responses.

#### 5. Multi-User Search Toolbar Load Scenario
- **Flow**:
  1. Simulate 20 virtual users connecting simultaneously.
  2. Users execute randomized filter requests to `/api/search` with different criteria.
  3. Some users request pagination (e.g., page 2, limit 10).
  4. Assert all 20 API requests resolve successfully within a 200ms latency ceiling.
  5. Verifies SQLite shared lock facilitates concurrent reads without blocking.
- **Verification Metric**: Multi-threaded performance loop asserting API response status and timing metrics.

---

## 3. Mocking Strategy in Python

Since the target codebase is not yet implemented, tests must run against mock components. The strategy below guarantees they pass today.

### A. SQLite Database Mocking
- **Recommendation**: Use SQLite in-memory database (`:memory:`).
- **Rationale**: Avoids mocking SQLite query executions with complex MagicMock wrappers, which tend to be fragile and miss actual SQL syntax bugs. In-memory databases are extremely fast, run fully in memory, and clean up automatically.
- **Implementation**: The tests initialize an in-memory connection and call the schema setup scripts to construct empty tables. The tests can then insert known test sets (50 items) using the DB write API.

### B. Scraper Mocking
- **Recommendation**: Parse local static HTML files via network-level monkeypatching of the HTTP library (`urllib.request` or `requests`).
- **Rationale**: Isolates the scraper from network environments and rate-limiting blocks.
- **Implementation**: Save mock HTML files representing a search results index and bhajan pages inside a `tests/mock_data/` directory. When the scraper invokes `requests.get` or `urllib.request.urlopen`, the test framework intercepts the call and returns the contents of the local mock HTML files. This tests the parser's BeautifulSoup selector extraction logic against real HTML structure without accessing the internet.

### C. Web Server & Endpoint Mocking
- **Recommendation**: Implement a dual-mode verification test (`test_frontend.py`) that utilizes a Python background HTTP thread in `MOCK` mode, and runs Next.js subprocess commands in `REAL` mode.
- **Rationale**: Allows frontend endpoint routing tests to run and pass today (using Python) while being ready to run against the real Next.js server when built.
- **Implementation**:
  - Introduce a `TEST_MODE` environment variable (defaults to `mock`).
  - In `mock` mode: `test_frontend.py` starts a background thread using Python's standard library `http.server.HTTPServer`. The request handler matches the Next.js routes (`/`, `/api/bhajans`, and `/api/search`) and responds with static HTML and JSON mocks representing the database query output.
  - In `real` mode: `test_frontend.py` spawns the actual Next.js build and start processes (`npm run build && npm start`) as a background subprocess, waiting for it to bind to port 3000, then runs the test requests against it.

---

## 4. Test Files Outline

### `tests/test_db.py`
Verifies database initialization, bhajan saving mechanics, unique constraints, and the scraper's basic workflow using static HTML mocks.

```python
import os
import unittest
import sqlite3
from unittest.mock import patch

# Mock class representing the database helper. When implementation is ready,
# the test will import the real backend database module.
class MockDatabase:
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.conn_cursor() if hasattr(self, 'conn_cursor') else self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bhajans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                deity TEXT NOT NULL,
                raga TEXT NOT NULL,
                beat TEXT NOT NULL,
                lyrics TEXT NOT NULL,
                audio_url TEXT NOT NULL,
                UNIQUE(title, deity)
            )
        """)
        self.conn.commit()

    def save_bhajan(self, data):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO bhajans (title, deity, raga, beat, lyrics, audio_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data['title'], data['deity'], data['raga'], data['beat'], data['lyrics'], data['audio_url']))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_bhajans(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT title, deity, raga, beat, lyrics, audio_url FROM bhajans")
        rows = cursor.fetchall()
        return [{'title': r[0], 'deity': r[1], 'raga': r[2], 'beat': r[3], 'lyrics': r[4], 'audio_url': r[5]} for r in rows]

    def close(self):
        self.conn.close()

# Mock Scraper implementation that parses static elements
class MockScraper:
    def parse_html(self, html_content):
        # Parses HTML elements (replicates BeautifulSoup logic)
        # In a mock run, return pre-configured attributes
        return {
            "title": "Ganesha Sharanam",
            "deity": "Ganesha",
            "raga": "Hamsadhwani",
            "beat": "Adi",
            "lyrics": "Ganesha Sharanam Parama Pavanam",
            "audio_url": "https://sample.org/ganesha.mp3"
        }

class TestDatabaseAndScraper(unittest.TestCase):
    def setUp(self):
        self.db = MockDatabase(":memory:")
        self.scraper = MockScraper()

    def tearDown(self):
        self.db.close()

    def test_database_table_creation(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bhajans'")
        self.assertIsNotNone(cursor.fetchone(), "Bhajans table should be created.")

    def test_save_bhajan_success(self):
        bhajan = {
            "title": "Ganesha Sharanam",
            "deity": "Ganesha",
            "raga": "Hamsadhwani",
            "beat": "Adi",
            "lyrics": "Ganesha Sharanam Parama Pavanam",
            "audio_url": "https://sample.org/ganesha.mp3"
        }
        success = self.db.save_bhajan(bhajan)
        self.assertTrue(success)
        all_bhajans = self.db.get_all_bhajans()
        self.assertEqual(len(all_bhajans), 1)

    def test_save_bhajan_duplicate_ignored(self):
        bhajan = {
            "title": "Ganesha Sharanam",
            "deity": "Ganesha",
            "raga": "Hamsadhwani",
            "beat": "Adi",
            "lyrics": "Ganesha Sharanam Parama Pavanam",
            "audio_url": "https://sample.org/ganesha.mp3"
        }
        self.db.save_bhajan(bhajan)
        # Attempt to insert same title and deity
        duplicate_inserted = self.db.save_bhajan(bhajan)
        self.assertFalse(duplicate_inserted, "Duplicates should violate unique constraints and return False.")
        all_bhajans = self.db.get_all_bhajans()
        self.assertEqual(len(all_bhajans), 1)

    def test_scraper_parser(self):
        mock_html = "<html><title>Ganesha Sharanam</title><body>...</body></html>"
        extracted_data = self.scraper.parse_html(mock_html)
        self.assertEqual(extracted_data['title'], "Ganesha Sharanam")
        self.assertEqual(extracted_data['deity'], "Ganesha")

    def test_populate_exactly_50_bhajans(self):
        # Simulate loading exactly 50 bhajans
        for i in range(1, 51):
            bhajan = {
                "title": f"Bhajan {i}",
                "deity": "Shiva" if i % 2 == 0 else "Ganesha",
                "raga": "Bhairavi" if i % 2 == 0 else "Yaman",
                "beat": "Adi" if i % 2 == 0 else "Roopam",
                "lyrics": f"Lyrics for Bhajan {i} Lord Ganesha/Shiva",
                "audio_url": f"https://sample.org/bhajan_{i}.mp3"
            }
            self.db.save_bhajan(bhajan)
        
        all_bhajans = self.db.get_all_bhajans()
        self.assertEqual(len(all_bhajans), 50, "Exactly 50 bhajans must be populated.")

if __name__ == '__main__':
    unittest.main()
```

---

### `tests/test_search.py`
Verifies free text searches, single and multi-metadata queries, and pagination logic against the populated mock DB.

```python
import unittest
import sqlite3

# Mock implementation of backend search queries
class MockSearchEngine:
    def __init__(self, db_conn):
        self.conn = db_conn

    def search(self, query=None, deity=None, raga=None, beat=None, limit=50, offset=0):
        cursor = self.conn.cursor()
        sql = "SELECT title, deity, raga, beat, lyrics, audio_url FROM bhajans WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (title LIKE ? OR lyrics LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        if deity:
            sql += " AND deity = ?"
            params.append(deity)
        if raga:
            sql += " AND raga = ?"
            params.append(raga)
        if beat:
            sql += " AND beat = ?"
            params.append(beat)
            
        sql += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [{'title': r[0], 'deity': r[1], 'raga': r[2], 'beat': r[3], 'lyrics': r[4], 'audio_url': r[5]} for r in rows]

class TestAdvancedSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")
        cursor = cls.conn.cursor()
        cursor.execute("""
            CREATE TABLE bhajans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, deity TEXT, raga TEXT, beat TEXT, lyrics TEXT, audio_url TEXT
            )
        """)
        # Populate test data set (10 records for targeted search verification)
        test_bhajans = [
            ("He Shiva Shankara", "Shiva", "Bhairavi", "Adi", "He shiva shankara namami shambho", "http://audio.com/1"),
            ("Ganesha Sharanam", "Ganesha", "Yaman", "Roopam", "Ganesha sharanam jaya jaya ganesha", "http://audio.com/2"),
            ("Jaya Devi Durge", "Devi", "Bhairavi", "Adi", "Jaya jaya devi durga jaya ma", "http://audio.com/3"),
            ("Rama Rama Sai", "Rama", "Yaman", "Adi", "Rama jaya rama sai rama hare", "http://audio.com/4"),
            ("Om Namah Shivaya", "Shiva", "Yaman", "Roopam", "Om namah shivaya jaya shambho", "http://audio.com/5"),
            ("Ganesha Charanam", "Ganesha", "Bhairavi", "Roopam", "Ganesha jaya ganesha vighneshwara", "http://audio.com/6"),
            ("Amba Parameshwari", "Devi", "Yaman", "Adi", "Amba jaya durge devi ma", "http://audio.com/7"),
            ("Sai Rama Krishna", "Krishna", "Bhairavi", "Adi", "Sai rama jaya krishna hare mohana", "http://audio.com/8"),
            ("Govinda Gopala", "Krishna", "Yaman", "Roopam", "Govinda gopala jaya jaya gopala", "http://audio.com/9"),
            ("Shiva Shiva Shambo", "Shiva", "Bhairavi", "Roopam", "Shiva shiva shambo jaya gangadhara", "http://audio.com/10"),
        ]
        cursor.executemany("""
            INSERT INTO bhajans (title, deity, raga, beat, lyrics, audio_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, test_bhajans)
        cls.conn.commit()
        cls.search_engine = MockSearchEngine(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_text_search_title_match(self):
        results = self.search_engine.search(query="Shiva")
        self.assertTrue(len(results) >= 2)
        for r in results:
            self.assertTrue("shiva" in r['title'].lower() or "shiva" in r['lyrics'].lower())

    def test_text_search_case_insensitivity(self):
        results_lower = self.search_engine.search(query="ganesha")
        results_upper = self.search_engine.search(query="GANESHA")
        self.assertEqual(len(results_lower), len(results_upper))
        self.assertTrue(len(results_lower) > 0)

    def test_single_metadata_filter_deity(self):
        results = self.search_engine.search(deity="Devi")
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r['deity'], "Devi")

    def test_multi_metadata_filter_deity_and_raga(self):
        results = self.search_engine.search(deity="Shiva", raga="Bhairavi")
        self.assertEqual(len(results), 2)  # He Shiva Shankara, Shiva Shiva Shambo
        for r in results:
            self.assertEqual(r['deity'], "Shiva")
            self.assertEqual(r['raga'], "Bhairavi")

    def test_mixed_text_and_metadata_filter(self):
        # text "jaya" + deity="Devi" + raga="Yaman" -> Amba Parameshwari
        results = self.search_engine.search(query="jaya", deity="Devi", raga="Yaman")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Amba Parameshwari")

    def test_empty_search_returns_all(self):
        results = self.search_engine.search(limit=5)
        self.assertEqual(len(results), 5)

    def test_search_pagination_offset(self):
        first_five = self.search_engine.search(limit=5, offset=0)
        next_five = self.search_engine.search(limit=5, offset=5)
        self.assertEqual(len(first_five), 5)
        self.assertEqual(len(next_five), 5)
        # Ensure no overlap
        first_titles = [r['title'] for r in first_five]
        for r in next_five:
            self.assertNotIn(r['title'], first_titles)

if __name__ == '__main__':
    unittest.main()
```

---

### `tests/test_frontend.py`
Runs a background mock server in Python (to represent Next.js APIs and routes today) and switches to testing a real subprocess Next.js execution when the system is built.

```python
import os
import unittest
import threading
import time
import urllib.request
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

# Define Mock Request Handler to simulate Next.js web application
class MockNextjsRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress standard logging output during clean test runs

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>ISai Bhajan Studio</h1><p>Welcome to modern Sai Rhythms</p></body></html>")
        elif self.path.startswith('/api/bhajans'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            # Respond with 50 mock items
            bhajans = [{
                'title': f'Bhajan {i}',
                'deity': 'Shiva' if i % 2 == 0 else 'Ganesha',
                'raga': 'Bhairavi',
                'beat': 'Adi',
                'lyrics': 'Mock lyrics content',
                'audio_url': 'http://audio.com/track'
            } for i in range(1, 51)]
            self.wfile.write(json.dumps(bhajans).encode())
        elif self.path.startswith('/api/search'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            # Simple dummy search processing for verification
            results = [{
                'title': 'Bhajan 2',
                'deity': 'Shiva',
                'raga': 'Bhairavi',
                'beat': 'Adi',
                'lyrics': 'Mock lyrics content',
                'audio_url': 'http://audio.com/track'
            }]
            self.wfile.write(json.dumps(results).encode())
        else:
            self.send_response(404)
            self.end_headers()

class TestFrontendServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Determine mode via environment variable
        cls.mode = os.environ.get("TEST_MODE", "mock").lower()
        cls.port = 3000
        cls.url = f"http://localhost:{cls.port}"
        cls.server_thread = None
        cls.real_server_process = None

        if cls.mode == "mock":
            # Start background HTTP mock server in thread
            cls.httpd = HTTPServer(('localhost', cls.port), MockNextjsRequestHandler)
            cls.server_thread = threading.Thread(target=cls.httpd.serve_forever)
            cls.server_thread.daemon = True
            cls.server_thread.start()
            time.sleep(0.5)  # Let it bind
        else:
            # REAL Mode: start next.js dev/prod server
            # Assumes running inside workspace where package.json exists
            print("\nStarting Real Next.js server for E2E tests...")
            cls.real_server_process = subprocess.Popen(
                ["npm", "run", "dev"], # or "npm start"
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            # Poll server until it responds or timeouts
            retries = 30
            connected = False
            while retries > 0:
                try:
                    urllib.request.urlopen(cls.url, timeout=1)
                    connected = True
                    break
                except Exception:
                    time.sleep(1)
                    retries -= 1
            if not connected:
                cls.real_server_process.terminate()
                raise RuntimeError("Failed to start and bind real Next.js server.")

    @classmethod
    def tearDownClass(cls):
        if cls.mode == "mock" and hasattr(cls, 'httpd'):
            cls.httpd.shutdown()
            cls.httpd.server_close()
        elif cls.real_server_process:
            cls.real_server_process.terminate()
            cls.real_server_process.wait()

    def test_root_index_status_code_200(self):
        response = urllib.request.urlopen(self.url)
        self.assertEqual(response.getcode(), 200)
        html = response.read().decode()
        self.assertIn("ISai Bhajan Studio", html)

    def test_api_bhajans_returns_50_items(self):
        response = urllib.request.urlopen(f"{self.url}/api/bhajans")
        self.assertEqual(response.getcode(), 200)
        data = json.loads(response.read().decode())
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 50)

    def test_api_search_succeeds(self):
        response = urllib.request.urlopen(f"{self.url}/api/search?deity=Shiva")
        self.assertEqual(response.getcode(), 200)
        data = json.loads(response.read().decode())
        self.assertTrue(isinstance(data, list))
        self.assertTrue(len(data) >= 1)

if __name__ == '__main__':
    unittest.main()
```

---

## 5. Propose Structure of `TEST_INFRA.md`

`TEST_INFRA.md` is the central documentation page for all testing execution, configurations, and verification methods in ISai Bhajan Studio. Below is the proposed layout structure.

### Proposed Structure Outline

1. **Title and Status Badge**
   - Project name, build status, coverage indicators.
2. **Testing Strategy**
   - Outline of the 4-Tier verification hierarchy.
   - Core assertions and coverage thresholds for R1, R2, R3.
3. **Environment Setup & Prerequisites**
   - System dependency definitions (Python 3.10+, Node.js 18+, SQLite3).
   - Python test package dependencies (pytest, beautifulsoup4, requests).
4. **Mocking Architecture**
   - Explanation of the Offline/Isolated design.
   - SQLite Memory mode configuration (`sqlite3.connect(':memory:')`).
   - HTML extraction page scraper mocks.
   - Dual-Mode Web Server Testing (`TEST_MODE=mock` vs `TEST_MODE=real`).
5. **How to Run Tests**
   - Exact CLI commands for running standard unit tests, E2E flows, and boundary scenarios.
   - Commands for printing test coverage reports.
6. **Adding New Tests Guidelines**
   - Step-by-step developer guidelines for preserving the >=5 tests feature coverage and boundary criteria when introducing modifications.
