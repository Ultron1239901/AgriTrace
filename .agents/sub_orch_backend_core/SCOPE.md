# Scope: Backend Core

## Architecture
- Module/package boundaries, data flow, shared interfaces:
  - **Models**: `backend/app/models/models.py` (SQLAlchemy models)
  - **Schemas**: `backend/app/schemas/schemas.py` (Pydantic validation schemas)
  - **Auth Router**: `backend/app/routers/auth.py` (Registration & Forgot Password API routes)
  - **Farmer / Crop Routers**: Coordinate validation & location fuzzing logic (Farmer profile updates & Crop details responses)

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Database & Schemas Expansion | Add phone_number, address, security_question, and security_question_answer to Farmer & Buyer models/schemas. Ensure phone & address are required (no empty/null values) during registration. | None | IN_PROGRESS |
| 2 | Registration Updates | Update `backend/app/routers/auth.py` to register user profiles with the new fields, using a predefined set of at least 3 security questions. | M1 | IN_PROGRESS |
| 3 | Forgot Password API | Implement `POST /api/auth/forgot-password/initiate`, `POST /api/auth/forgot-password/reset-otp`, and `POST /api/auth/forgot-password/reset-question`. | M2 | IN_PROGRESS |
| 4 | Coordinate Validation | Implement coordinate verification on Farmer profile location (latitude range `[-90, 90]`, longitude range `[-180, 180]`). Return HTTP 400 with detail `"wrong location"` on failure. | None | IN_PROGRESS |
| 5 | Crop Location Fuzzing | Fuzz crop coordinates in crop details API responses for Buyers, while keeping them exact for Farmers and Admins. | None | IN_PROGRESS |
| 6 | System Verification & Audit | Run all unit/integration tests and invoke Forensic Auditor to verify. | M1, M2, M3, M4, M5 | PLANNED |

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
- Farmer profile exact coordinate validation: Latitude in `[-90, 90]`, Longitude in `[-180, 180]`.
- Return HTTP 400 with exact detail `"wrong location"` if out of bounds or unparseable.
- Buyer viewing crop details: API fuzzes exact coordinates in response payload.
