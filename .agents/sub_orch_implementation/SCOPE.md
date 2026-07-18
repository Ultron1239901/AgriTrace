# Scope: Implementation Track

## Architecture
Decoupled frontend/backend setup with:
- **Backend**: FastAPI (Python), SQLAlchemy ORM with async connections to PostgreSQL.
- **Frontend**: React + Vite + Tailwind CSS.
- **Database**: PostgreSQL storing user roles, profiles, and analytics.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 2 | Backend Core | DB models, registration schemas, forgot password dual-recovery routes, farmer profile coordinates verification, location fuzzing API. | None | IN_PROGRESS (Conv ID: d33d933f-93b7-4f0a-bb4c-bf046adf7d62) |
| 3 | Frontend Auth & Recovery UI | Phone/address/security question registration forms, forgot password portal UI, and API integration. | M2 | PLANNED |
| 4 | Frontend Maps & Onboarding | Interactive Leaflet maps (exact for Farmer/Admin, fuzzed for Buyer), Guideline Manual terms pop-up locking dashboard, static PDF in assets, About page manual, onboarding tour, theme accessibility audit. | M2 | PLANNED |
| 5 | E2E Test Pass & Hardening | Run all E2E tests, pass 100%, execute Tier 5 adversarial testing, final security and integrity audit. | M1, M3, M4 | PLANNED |

## Interface Contracts
Defined in PROJECT.md at project root.
- Recovery Initiation: `POST /api/auth/forgot-password/initiate`
- Reset via OTP: `POST /api/auth/forgot-password/reset-otp`
- Reset via Security Question: `POST /api/auth/forgot-password/reset-question`
- Coordinate verification: Latitude `[-90, 90]`, Longitude `[-180, 180]` validation returning 400 `"wrong location"`.
- Coordinate fuzzing: buyer response client-payload filters exact coordinate details.
