# BRIEFING — 2026-07-18T09:36:00Z

## Mission
Restore and extend backend core components for AgriTrace, including restoring models, validating schemas, updating registration, password reset endpoints, coordinate validation, and location fuzzing.

## 🔒 My Identity
- Archetype: teamwork_preview_worker
- Roles: implementer, qa, specialist
- Working directory: d:\Agriculture project\.agents\teamwork_preview_worker_backend_core_1
- Original parent: d33d933f-93b7-4f0a-bb4c-bf046adf7d62
- Milestone: Milestone 2 (Backend Core)

## 🔒 Key Constraints
- CODE_ONLY network mode: No external internet access or http requests.
- No dummy/facade implementations or hardcoded values.
- Do not modify files outside specified scope unnecessarily.
- Maintain real state and produce real behavior.

## Current Parent
- Conversation ID: d33d933f-93b7-4f0a-bb4c-bf046adf7d62
- Updated: not yet

## Task Summary
- **What to build**: 
  1. Restore models.py from backup, add security_question and security_question_answer columns.
  2. Require phone_number, address, security_question, and security_question_answer in registration schemas.
  3. Validate security_question list, hash answer, and save in register endpoints.
  4. Implement forgot password endpoints: initiate (send OTP via OTPStore), reset-otp, and reset-question.
  5. Validate latitude/longitude coordinates format and range.
  6. Location fuzzing helper (rounding coordinates to 2 decimal places), fuzz location fields for buyers and verify_batch if role is not admin/farmer.
- **Success criteria**: Functional tests and syntax checks passing, real security fields saved/verified.
- **Interface contracts**: Standard REST APIs, schemas and models matching SQLite database structure.
- **Code layout**: Python FastAPI application in `backend/app/`

## Key Decisions Made
- [TBD]

## Artifact Index
- [TBD]
