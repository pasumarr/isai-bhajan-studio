# ISai Bhajan Studio — Mark 2 Implementation Plan

## Overview
Mark 2 transforms ISai Bhajan Studio from a static search repository into a **community-driven platform** with authentication, playlists, real-time coordination, AI-powered search, and a mobile-ready architecture.

---

## Implementation Phases

### Phase 2A — Backend Migration & Core Infrastructure
> **Goal:** Replace the SQLite/script architecture with a production-grade backend.

| # | Task | Tech | Status |
|---|------|------|--------|
| 1 | Migrate to **FastAPI** backend with proper REST endpoints | Python, FastAPI, Pydantic | ⬜ |
| 2 | Migrate database from SQLite → **PostgreSQL** with full schema | PostgreSQL, SQLAlchemy | ⬜ |
| 3 | Re-import all 3,609 bhajans with expanded metadata (keys, sentiment) | Python | ⬜ |
| 4 | Add **Redis** caching layer for popular queries | Redis | ⬜ |
| 5 | Set up **Celery** background worker for scrubber/normalization tasks | Celery + Redis | ⬜ |
| 6 | Containerize with **Docker** (backend + db + redis + worker) | Docker, docker-compose | ⬜ |

### Phase 2B — Authentication & User System
> **Goal:** Users can sign in, have profiles, save favorites, and manage roles.

| # | Task | Tech | Status |
|---|------|------|--------|
| 1 | **Firebase Auth** integration (Google, Apple, Email) | Firebase SDK | ⬜ |
| 2 | User profiles table (recently played, favorites, contribution history) | PostgreSQL | ⬜ |
| 3 | **RBAC** system: Guest / Member / Coordinator / Admin | FastAPI middleware | ⬜ |
| 4 | Personalized dashboard (recently played, recommendations, playlists) | React/Next.js | ⬜ |

### Phase 2C — Enhanced Player & Playlist System
> **Goal:** A premium "Now Playing" experience with playlist management.

| # | Task | Tech | Status |
|---|------|------|--------|
| 1 | **"Now Playing" view** — synced lyrics, raga info, key signature | React | ⬜ |
| 2 | **Mini-Player** overlay that persists across navigation | React, CSS | ⬜ |
| 3 | **Playlist CRUD** — create, save, reorder, delete playlists | FastAPI + React | ⬜ |
| 4 | **Offline downloads** — save bhajans for offline playback | Service Worker / IndexedDB | ⬜ |
| 5 | Gapless audio playback engine | Web Audio API | ⬜ |

### Phase 2D — AI Services Layer
> **Goal:** Intelligent search, auto-tagging, and transliteration.

| # | Task | Tech | Status |
|---|------|------|--------|
| 1 | **pgvector** embeddings for semantic/vibe search | PostgreSQL + pgvector | ⬜ |
| 2 | **Smart Search** — "easy evening bhajans" natural language queries | Gemini API | ⬜ |
| 3 | **AI Avatar** interface (Antigravity SDK) for conversational search | Antigravity SDK | ⬜ |
| 4 | **Auto-transliteration** — Romanized Sanskrit/Hindi/Telugu lyrics | Gemini API | ⬜ |
| 5 | **Raga detection** — AI audio analysis for untagged recordings | Gemini Audio | ⬜ |
| 6 | **Lyric alignment** — karaoke-style timestamp sync | AI + Web Audio | ⬜ |

### Phase 2E — Community & Contribution Engine
> **Goal:** Users can contribute, correct, and collaborate.

| # | Task | Tech | Status |
|---|------|------|--------|
| 1 | **Contribution form** — upload sheets, karaoke, correct lyrics | React + S3 | ⬜ |
| 2 | **Staging pipeline** — pending_submissions → moderator review → production | PostgreSQL | ⬜ |
| 3 | **Version history** for lyrics with diff view and revert | PostgreSQL | ⬜ |
| 4 | **Admin dashboard** — content approval, user management, analytics | React | ⬜ |

### Phase 2F — Real-Time Coordination & Chat
> **Goal:** Live coordination for bhajan sessions at Sai Centers.

| # | Task | Tech | Status |
|---|------|------|--------|
| 1 | **Chat server** with event-based rooms ("Thursday Samithi Bhajan") | Node.js + Socket.io | ⬜ |
| 2 | **Center Groups** — create/manage Sai Centers and Samithis | FastAPI + PostgreSQL | ⬜ |
| 3 | **Setlist planning** — drag-and-drop bhajan ordering for sessions | React | ⬜ |
| 4 | **AI setlist suggestions** — balanced setlist based on singers present | Gemini API | ⬜ |
| 5 | **Singer scheduling** — assign singers by key preference/history | FastAPI | ⬜ |

### Phase 2G — Gamification & Social
> **Goal:** Drive engagement through streaks, badges, and social features.

| # | Task | Tech | Status |
|---|------|------|--------|
| 1 | **Like/Reaction engine** with heart + emoji animations | React + Lottie | ⬜ |
| 2 | **Practice Streaks** — daily engagement tracking | PostgreSQL + React | ⬜ |
| 3 | **Listen Together** — synchronized playback with reactions | Socket.io + Web Audio | ⬜ |
| 4 | **Contribution Badges** — digital rewards for community contributions | PostgreSQL + React | ⬜ |

### Phase 2H — Mobile App
> **Goal:** Native iOS + Android experience.

| # | Task | Tech | Status |
|---|------|------|--------|
| 1 | Initialize **Flutter** project with Riverpod state management | Flutter, Dart | ⬜ |
| 2 | Bottom navigation (Home, Search, Coordinate, Contribute, Profile) | Flutter | ⬜ |
| 3 | Now Playing view with `just_audio` engine | Flutter | ⬜ |
| 4 | Connect to FastAPI backend | Dart HTTP | ⬜ |
| 5 | Firebase Auth + Push Notifications | Firebase | ⬜ |
| 6 | Offline sync with local database | SQLite/Hive | ⬜ |

### Phase 2I — Infrastructure & Operations
> **Goal:** Production-grade deployment, monitoring, and CI/CD.

| # | Task | Tech | Status |
|---|------|------|--------|
| 1 | **Audio pipeline** — loudness normalization (-14 LUFS), ABS transcoding | FFmpeg + Celery | ⬜ |
| 2 | **CDN** setup for media assets | AWS CloudFront / GCS | ⬜ |
| 3 | **Sentry** error tracking (frontend + backend) | Sentry SDK | ⬜ |
| 4 | **CI/CD** via GitHub Actions (test → build → deploy) | GitHub Actions | ⬜ |
| 5 | **Firebase Remote Config** + kill-switch capability | Firebase | ⬜ |
| 6 | **Analytics** — DAU, completion rate, zero-result query tracking | Mixpanel/Firebase | ⬜ |

---

## Recommended Build Order

```
Phase 2A (Backend) ──→ Phase 2B (Auth) ──→ Phase 2C (Player/Playlists)
                                                    │
                                          Phase 2D (AI) ──→ Phase 2E (Community)
                                                    │
                                          Phase 2F (Chat) ──→ Phase 2G (Social)
                                                    │
                                          Phase 2H (Mobile) ──→ Phase 2I (Ops)
```

**Critical Path:** 2A → 2B → 2C (these unlock everything else)
