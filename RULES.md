# Development Rules — VisionAI

This document serves as the project's development and AI operating manual.
Any agent or human contributing code must strictly adhere to these principles.

---

## 1. General Principles
- **Clarity over Cleverness**: Write readable, self-documenting code.
- **Reuse Existing Components**: Check existing modules in `app/` before adding new logic or dependencies.
- **Do Not Duplicate Logic**: Keep core logic centralized (e.g., preprocessing in `preprocessing.py`, inference in `inference.py`).
- **Keep Functions Small**: Each function should have a single, distinct responsibility.
- **Do Not Modify Unrelated Files**: Keep git diffs focused strictly on the assigned task.
- **Lightweight by Default**: Never import heavy frameworks or multi-megabyte frontend bundles when Vanilla JS and standard browser APIs suffice.

---

## 2. Before Coding Workflow
Before creating or editing any files:
1. **Read Project Context**: Inspect `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN.md`, and `TASKS.md`.
2. **Inspect Existing Code**: Understand data types, route patterns, and UI state flows.
3. **Plan First**: Formulate an implementation plan before touching code.
4. **Identify Constraints**: Never break existing inference or live streaming endpoints.

---

## 3. Frontend & UI Rules
- **Follow `docs/DESIGN.md`**: Respect the dark-first theme palette (`#0B0F14` base, `#111820` surface, `#7C3AED` accent).
- **Maintain Full Responsiveness**: Ensure mobile drawer navigation works and two-column layouts collapse cleanly to single-column on mobile (< 860px).
- **Mandatory UI States**: Every asynchronous action must have:
  - Empty state
  - Loading / Progress state
  - Success state
  - Human-friendly Error state
- **Decoupled Video Rendering**: Live camera feeds must render locally on `<canvas>` at 60 FPS while inference coordinates arrive asynchronously over WebSocket. Never block the video feed on network latency.
- **No Heavy Frontend Frameworks**: Use modular, clean Vanilla HTML5/CSS/JS.

---

## 4. Backend & Machine Learning Rules
- **FastAPI Standards**: Use Pydantic schemas for request and response modeling.
- **Non-blocking Operations**: Avoid blocking FastAPI's event loop during synchronous model inference.
- **Defensive Error Handling**: Always return appropriate HTTP status codes (e.g., 400 for bad files, 413 for oversized payloads, 500 for inference failures).
- **Model Invariance**: Keep model loading decoupled from request handlers (`lifespan` initialization).

---

## 5. Security & Input Validation
- **Never Commit Secrets**: Keep `.env` out of version control; use `.env.example`.
- **Strict File Validation**: Validate uploaded files against allowed MIME types (`image/jpeg`, `image/png`, `image/webp`, `image/bmp`).
- **Enforce Size Limits**: Reject uploads exceeding `MAX_FILE_SIZE_MB` (default 15 MB) before decoding image tensors.
- **Safe WebSocket Handling**: Safely handle abrupt WebSocket disconnections (`WebSocketDisconnect`).

---

## 6. Testing & Quality Assurance
- **Automated Verification**: Run `pytest` after backend changes.
- **Test Before Commit**: Ensure all existing unit tests in `tests/` pass before staging changes.
- **Zero Console Errors**: Ensure browser console has no unhandled exceptions in any UI tab.

---

## 7. Git Workflow
- **Atomic Commits**: Make small, cohesive commits that address one feature or bug fix.
- **Conventional Commits**: Format commit messages descriptively:
  - `feat:` for new capabilities
  - `fix:` for bug fixes
  - `docs:` for documentation updates
  - `refactor:` for code restructuring without behavior changes
  - `test:` for test additions or modifications
