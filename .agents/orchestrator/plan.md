# Orchestration Plan - ISai Bhajan Studio

This document outlines the detailed orchestration plan for implementing the ISai Bhajan Studio project.

## Strategy and Topology
We will run a Dual Track project pattern:
1. **E2E Testing Track**: An E2E Testing Orchestrator (spawned as a sub-orchestrator) will build the test infrastructure, design the test suite (Tiers 1-4), and verify criteria. It will produce `TEST_READY.md`.
2. **Implementation Track**: A sequence of milestones, each handled by a sub-orchestrator or the orchestrator itself:
   - **Milestone 1**: Scraper & Database (R2)
   - **Milestone 2**: Search Mechanics (R3)
   - **Milestone 3**: Web Application Interface (R1)
   - **Milestone 4**: Final Integration & E2E Verification (Phase 1 E2E tests, Phase 2 Adversarial Hardening)

## Subagent Roles
We will spawn:
- **E2E Testing Orchestrator** (using `self` archetype): to manage test suite generation.
- **Milestone Sub-orchestrators** (using `self` archetype): to handle each implementation milestone.
- Inside each milestone track, the sub-orchestrator will spawn:
  - `teamwork_preview_explorer` to analyze context, check site/scraper mechanics, and plan implementation.
  - `teamwork_preview_worker` to write code, set up databases, implement UI, and run local tests.
  - `teamwork_preview_reviewer` to review code against the project specifications and ensure it's not a dummy implementation.
  - `teamwork_preview_challenger` to write adversarial tests and verify correctness.
  - `teamwork_preview_auditor` to audit the code for compliance, integrity, and anti-cheating rules.

## Step-by-Step Execution Plan

### Step 1: Initialization and Setup
- Create global `PROJECT.md`, internal `plan.md` and `progress.md`.
- Set up the liveness heartbeat cron.

### Step 2: Spawn E2E Testing Track
- Spawn E2E Testing Orchestrator to define the test architecture in `TEST_INFRA.md` and implement test scripts (`test_db.py`, `test_search.py`, `test_frontend.py`) based on requirements.
- The test suite must cover 4 tiers:
  - Tier 1: Feature Coverage (>=5 per feature)
  - Tier 2: Boundary & Corner cases (>=5 per feature)
  - Tier 3: Cross-Feature combinations (pairwise)
  - Tier 4: Real-world workloads

### Step 3: Spawn Milestone 1 (Scraper & DB)
- Spawn Milestone 1 Sub-orchestrator.
- Explorer analyzes scraper targets and proposes SQLite schema and scraping strategy (using mock offline files if online is blocked by network mode).
- Worker implements backend database setup, scraping script, and populates with 50 bhajans.
- Reviewer, Challenger, and Auditor verify.

### Step 4: Spawn Milestone 2 (Search Mechanics)
- Spawn Milestone 2 Sub-orchestrator.
- Worker implements backend search functions (deity, raga, beat, etc.) querying the populated database.
- Verification via `test_search.py` (created by the E2E Testing Track).

### Step 5: Spawn Milestone 3 (Web App)
- Spawn Milestone 3 Sub-orchestrator.
- Worker builds React/Next.js UI. Incorporates search toolbar, bhajan display, and audio playing features.
- Verification via `test_frontend.py`.

### Step 6: Spawn Final Integration and Verification
- Run all test suites against the combined system.
- Run Phase 2: Adversarial Coverage Hardening (Tier 5) using Challengers to generate additional edge cases, identify coverage gaps, and fix them.
- Final Forensic Audit.

### Step 7: Completion & Human Report
- Synthesize all subagent results.
- Write `handoff.md` and send completion notification to Sentinel.
