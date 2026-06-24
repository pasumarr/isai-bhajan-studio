# Original User Request

## Initial Request — 2026-06-17T12:52:54-07:00

A production-ready web application (ISai Bhajan Studio) that modernizes "Sai Rhythms". It includes an automated web scraper to populate a multi-database architecture with audio and lyrics sourced from a representative sample of Sai Rhythms, replicating their advanced search toolbar mechanics but within a highly modern, responsive UI.

Working directory: C:\Users\saipa\isai-bhajan-studio
Integrity mode: development

[Design Document Reference: https://docs.google.com/document/d/1P5OXgTe2sX3rjwJwGYjZd56q9ybQH5FDhXPEYIyoyUE]

## Requirements

### R1. Web Application Interface
Build a modern Web Application (React/Next.js) incorporating the design aesthetics described in the ISai Bhajan Studio design document. The app must run from the working directory.

### R2. Web Scraper and Backend Database
Develop an automated web scraper to extract audio links and lyrics from Sai Rhythms. The scraper should populate a multi-database system. Limit the scraping to a representative sample of 50 bhajans to avoid rate limits.

### R3. Advanced Search Mechanics
Replicate the specific search toolbar functionality found on Sai Rhythms (e.g., filtering by Deity, Raga, etc.) and wire it to the scraped database.

## Acceptance Criteria

### R1 Verification (Web App)
- [ ] A programmatic test script (`test_frontend.py` or similar) can start the web server and verify it returns a 200 OK status on the main index route, confirming the app builds and runs.

### R2 Verification (Scraper & DB)
- [ ] A programmatic verification script (`test_db.py` or similar) successfully queries the database and asserts that exactly 50 bhajans have been stored, complete with populated lyrics and audio URLs.

### R3 Verification (Search)
- [ ] An automated test (`test_search.py` or similar) demonstrates that searching/filtering by specific metadata (like a specific Deity or Raga) returns the correctly filtered subset of the 50 scraped bhajans from the database.
