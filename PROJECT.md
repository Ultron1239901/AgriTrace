# Project: AgriTrace Enhancements

## Architecture
AgriTrace follows a decoupled layout with:
- **Backend**: FastAPI web framework, SQLAlchemy ORM with async connection to PostgreSQL.
- **Frontend**: React + Vite + Tailwind CSS.
- **Database**: PostgreSQL storing credentials, farm profiles, crop batches, and audit logs.
- **Blockchain**: Polygon Amoy Integration (Solidity smart contracts).

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | E2E Test Track | Design and implement opaque-box E2E test suite (Tiers 1-4); publish `TEST_READY.md`. | None | PLANNED |
| 2 | Backend Core | DB models, registration schemas, forgot password dual-recovery routes, farmer profile coordinates verification, location fuzzing API. | None | PLANNED |
| 3 | Frontend Auth & Recovery UI | Phone/address/security question registration forms, forgot password portal UI, and API integration. | M2 | PLANNED |
| 4 | Frontend Maps & Onboarding | Interactive Leaflet maps (exact for Farmer/Admin, fuzzed for Buyer), Guideline Manual terms pop-up locking dashboard, static PDF in assets, About page manual, onboarding tour, theme accessibility audit. | M2 | PLANNED |
| 5 | E2E Test Pass & Hardening | Run all E2E tests, pass 100%, execute Tier 5 adversarial testing, final security and integrity audit. | M1, M3, M4 | PLANNED |

## Interface Contracts
### Auth Dual Password Recovery
#### 1. Initiate Recovery
- **Endpoint**: `POST /api/auth/forgot-password/initiate`
- **Request**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "email": "user@example.com",
    "security_question": "What was your childhood nickname?",
    "message": "Dual recovery paths available."
  }
  ```

#### 2. Reset via OTP
- **Endpoint**: `POST /api/auth/forgot-password/reset-otp`
- **Request**:
  ```json
  {
    "email": "user@example.com",
    "otp": "123456",
    "new_password": "NewPassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Password reset successful.",
    "success": true
  }
  ```

#### 3. Reset via Security Question
- **Endpoint**: `POST /api/auth/forgot-password/reset-question`
- **Request**:
  ```json
  {
    "email": "user@example.com",
    "answer": "Nickname",
    "new_password": "NewPassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Password reset successful.",
    "success": true
  }
  ```

### Geospatial Boundaries
- Farmer profile exact coordinate validation pattern: Latitude must be in range `[-90, 90]`, Longitude in `[-180, 180]`. Can accept coordinate strings like `"13.13, 78.13"`.
- If coords are un-parseable or out of bounds, returns HTTP 400 with exact detail `"wrong location"`.
- Buyer viewing crop details: API filters `exact_location` to only output village/district, or fuzzes exact coordinates in response payload.
