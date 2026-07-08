# ISai Bhajan Studio — Mark 2: High-Level Design Document

**Project Name:** ISai Bhajan Studio  
**Vision:** A seamless, community-driven portal for Sathya Sai Bhajans that prioritizes large-scale coordination, global contribution, and localized center management.

---

## Project Structure: Two-Phased Evolution (Foundation & Community)

### 1. Mark 1 (The Foundation) ✅ COMPLETE
The primary goal of Mark 1 is to automatically scrape "Sai Rhythms" to create a robust, searchable repository. This phase focuses on delivering a cleaner, more pleasant UI/UX compared to the original site while maintaining the same basic functional features, ensuring a solid data foundation for future iterations.

### 2. Mark 2 (Community & Scale)
ISai Bhajan Studio is the definitive platform for the global Sai Bhajan community, evolving to focus on Community & Scale. It bridges the gap between repositories and active coordination through a modern UI, robust localized management tools, and scalable architecture designed for worldwide collaborative contribution.

Mark 2 explicitly defines the expansion into community collaboration. This phase introduces tools for global contribution and localized center management, bridging the gap between a static repository and an active coordination platform.

---

## 2. System Architecture Overview

The system follows a decoupled three-layer architecture with an integrated AI Services Layer:

- **Presentation Layer (Frontend):** Focuses on user experience, real-time coordination, and content contribution.
- **Data Layer (Persistence):** A multi-model database system handling rich metadata (Ragas, Keys, Sheets).
- **Backend Layer (Ingestion & Logic):** Features specialized web scrubbers and the Chat Server engine.
- **AI Services Layer (Intelligence):** Handles audio-to-text, raga recognition, and smart search capabilities.

---

## 3. Module Specifics

### 3.1 Presentation Layer (The "Studio" Experience)

The UI/UX strategy prioritizes a cleaner, easier-to-navigate interface, ensuring that the baseline experience is streamlined for simplicity and accessibility for all users.

- **UI/UX Philosophy:** Incorporate a modern, animation-heavy UI/UX philosophy to guide users seamlessly through the platform.
- **Bottom Navigation Bar:** Persistent access to Home, Search, Coordinate (Chat), Contribute (+), and Profile in a simple and concise manner with good icons.
- **The "Now Playing" View:** Shows lyrics, Raga info, and Key signature in a synchronized, scrollable interface, like Sai Rhythms.
- **Detailed Search Section:** Supporting advanced filters for Deity, Raga, Tempo, Tala, and Language.

#### Coordination Flow:
- **Chat Server Integration:** Dedicated chat rooms for specific events (e.g., "Thursday Samithi Bhajan").
- **AI-Assisted Task Management:** AI can suggest "Next Singer" based on their preferred keys or previous history within the chat.

#### Contribution Engine:
A simplified form for users to upload Western Music Sheets, Karaoke tracks, or correct existing lyrics.

#### Playlist Creation:
A feature where you can make and save playlists and download bhajans and songs for offline use, creating a platform where you can freely listen to bhajans without a subscription.

### 3.2 Data Layer (The Metadata Vault)

The data layer is structured to support complex musical queries (e.g., "Find all Bhajans in Raga Shankarabharanam with a Male Key of C#"). It explicitly integrates a "Sai Rhythms" sourced database that captures comprehensive metadata for every bhajan, including Deity, Raga, Tempo, Tala, Language, and lyrics.

#### Data Points

| Category | Data Points |
|----------|-------------|
| Core Info | Title, Deity, Type (Soorya, Devi, etc.) |
| Musicality | Raga, Beat (Tala), Typical Male/Female Key |
| Assets | Lyrics (Multi-lingual), Audio Recordings, Karaoke Tracks |
| Notation | Western Music Sheets (PDF/Image), Chord Pro |
| AI Insights | Sentiment Analysis, Vocal Range requirements, Similarity Embeddings |

#### 3.2.1 Storage Strategy for Additional/User-Contributed Content

**Two-Tier Storage Model:**
- **Staging Schema (Unverified):** All user-submitted bhajans, corrections, or new metadata entries are first routed to a `pending_submissions` table. This acts as a buffer zone where metadata is validated against the schema before moving to production.
- **Production Schema (Verified):** Once a moderator approves a submission via the Admin Dashboard, the entry is promoted to the `master_bhajan_index` (PostgreSQL).

**Asset Lifecycle:**
- Temporary uploads are initially stored in a 'quarantine' bucket (S3).
- Upon approval, the background pipeline (Celery) processes these files for loudness normalization (-14 LUFS) and transcoding.
- Verified, optimized assets are then moved to the final 'production' S3 bucket, linked via the Unique User ID for attribution.

**Versioning:** Each entry maintains a `version_history` table, allowing administrators to revert content or track the evolution of lyrics and metadata over time.

#### 3.2.2 Additional Data Sources

| Source | Purpose |
|--------|---------|
| YouTube Data API | Automated scraping of official Sathya Sai channel playlists to link video performances |
| Spotify Web API | Integration for high-quality studio album tracks and artist attribution |
| SSSO Media Archives | Deep-linking to legacy organizational portals for archival audio content |

### 3.3 Backend Layer (The Ingestion Engine)

The backend acts as an automated librarian through specialized web scrubbers.

**Modular Scrubber Design:**
- **Adapter A (Lyric Sites):** Focuses on regex-based text extraction.
- **Adapter B (Media Portals):** Focuses on scraping direct MP3/MP4 links and metadata tags.

### 3.4 AI Integration Layer

AI is integrated at various points to automate manual tasks and improve discovery:

- **Automated Metadata Tagging:** When the scrubber finds a recording without a Raga label, an AI Audio model analyzes the frequencies to suggest the most likely Raga.
- **Smart Search (LLM-Based):** Instead of exact keyword matches, users can search by vibe or context (e.g., "Bhajans about peace that are easy for beginners to sing").
- **Lyric Alignment:** AI aligns audio timestamps with lyric lines to create a "Karaoke-style" scrolling effect automatically.
- **Translation & Transliteration:** Automatically generate English transliterations (Romanized) for Sanskrit or regional language lyrics.

### 3.5 Content Sourcing & Pronunciation Strategy

- **Foundational Data Ingestion:** Sai Rhythms as primary source, augmented by SSSO Media Centre.
- **Pronunciation & Nuance Engine:** Linguistic Metadata Database storing phonetic guides, standardized transliterations, and audio pronunciation clips.
- **Database Structure:**
  - **Primary Database (Media/Metadata):** Relational mappings between audio tracks, Ragas, keys, and source links.
  - **Lyrics Database:** Multi-lingual lyrics synced with Phonetic Guides for "Original Script," "Transliterated," and "Phonetic Assistance" modes.

### 3.6 Admin & Task Management

Admin Login portal and dashboard for managing content, site configuration, and personal task tracking.

### 3.7 AI Avatar & UX

AI Avatar interface powered by the "Antigravity SDK" enabling users to converse with an AI guide that performs natural language searches across the internal database.

### 3.8 User Authentication & Personalization

- **OAuth Integration:** Google, Apple, and Email authentication flows.
- **User Profiles:** Persistent storage for 'Recently Played', 'Favorites', and 'Contribution History'.
- **Role-Based Access Control (RBAC):** Guest (read-only), Member (save playlists/contribute), Moderator/Admin (content approval), Bhajan Coordinator (center-specific management).
- **Personalized Dashboard:** "Recently Played", "Recommended Bhajans", and "Saved Playlists".

### 3.9 Moderation & Community Governance

- **Staging/Review Pipeline:** User-contributed lyrics to 'Pending' state for review.
- **Review Dashboard:** Administrative view for content verification.
- **Version History:** Trackable history for lyrics with reversion capability.

### 3.10 UI/UX & Responsive Guidelines

- **Navigation Model:** Persistent bottom nav bar + global 'Mini-Player' overlay.
- **Fluid UI Strategy:** Percentage-based sizing and relative font units (rem/sp).
- **Touch Ergonomics:** Minimum 48dp touch target size.
- **Hardware Awareness:** 'Safe Area' handling for notches/gesture indicators.
- **Micro-interactions:** Animation libraries + heart/emoji animation sets.

### 3.11 Gamification & Community Engagement

- **Reaction Engine:** "Like" button + heart/emoji animations for live sessions.
- **Practice Streaks:** Daily engagement tracking.
- **Social Sync:** 'Listen Together' feature with synchronized reactions.
- **Contribution Badges:** Digital badges for lyric corrections and phonetic guides.

### 3.12 Native Cross-Platform Strategy

Flutter or React Native for native iOS and Android experience.

### 3.13 Community & Center Management

- **Center Groups:** Authorized administrators manage Sai Centers/Samithis.
- **Localized Coordination:** Center-specific bhajan setlists, singer scheduling, event coordination.
- **Community Governance:** Localized moderators manage member access and contributions.

---

## 4. Technical Stack

| Component | Technology | Primary Purpose |
|-----------|------------|-----------------|
| Mobile Front-end | Flutter (Dart) | Cross-platform UI/UX |
| Backend API | Python (FastAPI) | Logic & Ingestion |
| Background Tasks | Celery + Redis | Scrubber/Normalization |
| Main Data Store | PostgreSQL + pgvector | AI-Search & Metadata |
| Real-time Messaging | Node.js + Socket.io | Chat & Collaboration |
| Authentication/Messaging | Firebase | Auth & Push Notifications |
| Media Hosting | AWS S3 / GCP Storage | Audio & File Assets |

### 4.1 System Scalability & Infrastructure

- **CDN:** Object storage (S3/GCS) paired with CDN for low-latency streaming.
- **Caching:** Redis for frequently queried metadata.
- **Analytics:** Track zero-result search queries for content roadmapping.
- **SEO:** Server-Side Rendering (SSR) for discoverability.

---

## 5. Interaction Sequence

1. Scrubber identifies a new bhajan audio file or lyrics.
2. AI Layer processes audio to detect BPM (tempo) and Raga.
3. Backend saves metadata and AI-generated tags to Data Layer.
4. User searches for "easy evening bhajans" → AI Search suggests entries.
5. User starts a Coordination Chat → AI suggests a "balanced setlist."

---

## 6. Privacy, Security, & Compliance

- **Data Privacy:** GDPR, COPPA, and CCPA compliance.
- **Content Moderation:** 'Report' mechanism with administrative workflow.

---

## 7. Performance & Latency Metrics

- **TTFA Target:** 300ms for playback initiation.
- **Asynchronous Processing:** AI metadata tagging as background jobs.

---

## 8. Disaster Recovery & Reliability

- **Graceful Degradation:** Fallback behaviors for AI/API outages.
- **Backup Strategy:** Regular database snapshots and recovery protocols.

---

## 9. Accessibility & Inclusivity

- **Screen Reader Support:** Comprehensive ARIA labels.
- **Visual Standards:** WCAG 2.1 AA color contrast.
- **Interface Localization:** Full i18n and L10n support.

---

## 10. Analytics & Feedback

- **Product Health:** DAU, Bhajan Completion Rate, Contribution Velocity.
- **User Feedback:** In-app 'Suggest a Feature' / 'Report a Bug' widget.

---

## 11. Rights, Legal, & Cost Management

- **Source Attribution:** Credit original providers (Radio Sai, SSSO).
- **DMCA Strategy:** Takedown and rights-management workflow.
- **Cost Management:** Batch processing (nightly) for AI tagging. Rate limiting for scrapers.

---

## 12. Audio Fidelity & Pipeline Strategy

- **Loudness Normalization:** -14 LUFS standard.
- **Adaptive Bitrate Streaming:** 64kbps / 128kbps / 256kbps tiers.
- **Optimized Formats:** Opus or HE-AAC codecs.
- **Player Engine:** Gapless playback + hardware-accelerated decoding.

---

## 13. Technical Quick Start Guide

### 13.1 Environment Setup
- **Stack:** Node.js/Python environment.
- **Key SDKs:** Firebase (Auth/Store), Gemini API (Search/Logic), Antigravity SDK (Avatar/Guide).

### 13.2 Local Development Flow
- **Initialization:** Configure environment variables and API keys.
- **Run:** Execute `npm run dev` or `python main.py` to launch local instance.

---

## 14. Operations, Observability & Deployment

### 14.1 Observability & Health Monitoring
- **Logging & Error Tracking:** Sentry for real-time crash/exception capture.
- **Metrics Monitoring:** Prometheus/Grafana or Firebase Performance Monitoring.

### 14.2 CI/CD Pipeline Strategy
- **Automated Testing:** Unit Tests (Scrubber logic) + Integration Tests (Audio Pipeline).
- **Deployment Automation:** GitHub Actions for testing, builds, and container deployment.

### 14.3 Emergency Management & Feature Flags
- **Remote Configuration:** Firebase Remote Config.
- **Kill-Switch Capability:** Remote toggling of critical features without app store updates.

---

## 15. Phase 0: Development & Prototyping Roadmap

1. **Wireframing & Low-Fi Prototyping:** Defining user journey and navigation layout.
2. **High-Fidelity UI Design:** Animation-heavy design system in Figma for "Now Playing."
3. **Core Framework Setup:** Initializing Flutter project with Riverpod state management.
4. **Alpha Testing (Internal):** Validating audio engine and local DB sync with sample dataset.
5. **Beta Testing (Closed Community):** Release to select center coordinators for feedback.
