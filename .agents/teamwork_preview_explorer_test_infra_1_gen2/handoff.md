# Handoff Report — E2E Test Infrastructure Setup (Milestone 1)

This report details the architectural design and recommendations for the End-to-End (E2E) test infrastructure for AgriTrace.

---

## 1. Observation

During read-only investigation, the following codebase details were observed:

- **Root Directory Layout**: Contains separate `backend` (FastAPI REST API) and `frontend` (React + Vite + Tailwind CSS) directories.
- **Backend Stack**: FastAPI framework, SQLAlchemy ORM with async PostgreSQL database connection (configured in `backend/app/database.py` and `backend/app/config.py` using `postgresql+asyncpg://postgres:Gibbs@localhost:5432/agritrace_db`).
- **Frontend Stack**: React 18 with Vite and Axios. Uses standard routing and authentication with JWT stored in local storage (observed in `frontend/src/services/api.js` line 9: `localStorage.getItem('agritrace_token')`).
- **Forgot Password Contracts**: `PROJECT.md` defines three endpoints for dual-path password recovery:
  1. `POST /api/auth/forgot-password/initiate`
  2. `POST /api/auth/forgot-password/reset-otp`
  3. `POST /api/auth/forgot-password/reset-question`
- **OTP Storage**: The backend stores generated 6-digit OTP passcodes in a database-backed table (`OTPStore`/`otp_stores`) containing `email` (PK), `otp`, and `expires_at` (observed in `backend/app/routers/auth.py` line 185: `otp_record = OTPStore(...)`).
- **Location & Boundary Controls**: 
  - Latitude must be in range `[-90, 90]`, and longitude in `[-180, 180]`.
  - Coordinates validation fails with HTTP 400 and detail `"wrong location"` (observed in `PROJECT.md` line 76 and backend design).
  - Exact coordinates (`exact_location`) must be returned for Farmers (`/api/farmer/profile`) and Admins (`/api/admin/farmers/{id}`), but fuzzed (rounded to 2 decimal places, giving ~1.1km approximation) for Buyers (`/api/buyer/farmers/{id}/crops`) and anonymous scans (`/api/verify/{batch_id}`).
- **Local Runtimes**: The command execution check (`python --version`, `node --version`) timed out waiting for user response, which means we must proceed by designing the test runner environment configuration statically and verifying standard setup.

---

## 2. Logic Chain

To satisfy the **Dual Track: E2E Testing Track** principles of **opaque-box**, **requirement-driven**, and **progressive testability**, the following reasoning is established:

1. **Opaque-Box Requirement**: The testing framework must execute test cases using HTTP requests (API testing) or browser-driven automation (UI testing) against public interfaces, without directly calling backend code modules.
2. **Progressive Testability**: Since backend endpoints are implemented prior to frontend UI screens, the test suite must be capable of executing **API-only E2E tests first** (Tiers 1 & 2), and then easily scaling to include **browser-based E2E UI tests** (Tiers 3 & 4) once Vite/React components are deployed.
3. **Database Integration for Supporting Actions**: E2E tests require a mechanism to:
   - Read the OTP bypass (since SMTP is simulated and printed to stdout).
   - Clean up test records (e.g. users registered under test domains).
   - Seed pre-verified farmers (since newly registered farmers are unverified by default and cannot add crops).
4. **Framework Choice (Python pytest + Playwright)**:
   - Given the backend is entirely Python-based, using a **Python-based pytest + pytest-playwright** suite is highly integrated. It allows E2E test files to reuse PostgreSQL connection variables and SQLAlchemy models (directly importing `database.py` and database credentials) for setup/teardown and OTP retrieval while keeping test execution strictly opaque-box (executing HTTP calls via `httpx` or driving browsers via `playwright`).
   - A Node-based Playwright framework (using JS/TS) is also feasible but would duplicate SQL/database connection configurations and models in Javascript, adding setup complexity.
   - Therefore, a Python-based **pytest + Playwright** suite is recommended.

---

## 3. Caveats

- **System Runtimes**: Since terminal commands could not run due to user confirmation timeouts, we assume standard Node.js (18+) and Python (3.10+) are installed. If Node or Python versions are outdated on the target system, it will block E2E script execution.
- **Smart Contract Offline Mocks**: Polygon Amoy integration (`blockchain/deploy.py`) requires a private key and RPC node. E2E tests should have options to run against the backend's local database fallback mode if the blockchain RPC network is offline or unconfigured.
- **OpenRouter (Gemini) Mocks**: Image verification on scan uses OpenRouter API (`backend/app/services/verify_service.py` line 96). E2E tests must handle mock or placeholder image analysis responses to prevent external API calls and latency during automated test runs.

---

## 4. Conclusion & Recommendations

We propose establishing a new E2E test infrastructure under a root directory `tests/e2e`.

### E2E Test Suite Directory Structure

```
tests/e2e/
├── conftest.py             # Global pytest fixtures (DB sessions, playwright setup, HTTP clients)
├── requirements-e2e.txt    # E2E test dependencies (pytest, playwright, httpx, asyncpg)
├── test_auth.py            # Login, registration, forgot-password recovery paths tests
├── test_farmer.py          # Coordinates validation, profile updates, crop registration tests
├── test_buyer.py           # Location fuzzing, crop list, purchase inquiry tests
└── test_admin.py           # Farmer verification approval/rejection/suspension tests
```

### E2E Test Runner Setup (`requirements-e2e.txt`)
```text
pytest==8.0.0
pytest-playwright==0.4.4
pytest-asyncio==0.23.5
httpx==0.27.0
asyncpg==0.29.0
sqlalchemy==2.0.31
```

### Interaction Specifications

1. **Authentication**:
   - **API Level**: Tests authenticate using `/api/auth/login`, `/api/auth/buyer/login`, or `/api/auth/admin/login`, and capture the returned `access_token` in headers: `Authorization: Bearer <token>`.
   - **UI Level**: Playwright automates inputting email and password into the forms and logs in. Using the Playwright `browser_context`'s `storage_state`, we save session tokens to disk, reusing authentication states across tests.

2. **Test Data Setup**:
   - A `db_session` fixture in `conftest.py` connects to the PostgreSQL database using settings parsed from `backend/app/config.py`.
   - Before running tests, standard accounts (e.g. a pre-verified farmer `farmer_active@e2e.test` and an admin `admin@agritrace.com`) are verified/seeded in the database to allow subsequent operations like registering crops.

3. **Test Data Cleanup**:
   - E2E tests register and manipulate records using emails ending with `@e2e.test` (e.g., `test_farmer_1@e2e.test`).
   - A global `autouse` teardown fixture executes SQL deletions:
     ```sql
     DELETE FROM farmers WHERE email LIKE '%@e2e.test';
     DELETE FROM buyers WHERE email LIKE '%@e2e.test';
     DELETE FROM crop_batches WHERE farmer_id NOT IN (SELECT id FROM farmers);
     DELETE FROM otp_stores WHERE email LIKE '%@e2e.test';
     ```

4. **Mocking Email OTP Verification**:
   - When `/forgot-password/initiate` is triggered, the backend stores a 6-digit OTP code in the database `otp_stores` table.
   - The test script queries this table directly using the user's email:
     ```python
     async def get_test_otp(db_session, email: str) -> str:
         result = await db_session.execute(
             select(OTPStore.otp).where(OTPStore.email == email.lower())
         )
         return result.scalar_one_or_none()
     ```
   - The test runner submits this retrieved OTP to `/forgot-password/reset-otp` to complete the password reset flow.

5. **Verifying Coordinate Validation and Fuzzing**:
   - **Input Validation**: Submit invalid formats or out-of-bounds latitude/longitude coordinates (e.g., `"100.0, 77.0"`) to `/api/auth/register` and `/api/farmer/profile`. Verify that the backend returns HTTP 400 Bad Request with details `{"detail": "wrong location"}`.
   - **Exact Coordinates**: Authenticate as the Farmer or Admin, retrieve profile/farmer details, and assert that the returned `exact_location` is exact (e.g., `"12.9716, 77.5946"`).
   - **Fuzzed Coordinates**: Access the same crop or farmer resource as an authenticated Buyer or an anonymous consumer (e.g., `/api/verify/{batch_id}`). Verify that the returned location details are fuzzed/rounded to 2 decimal places (e.g., `"12.97, 77.59"`).

---

## 5. Verification Method

To verify the test setup once implemented:
1. Ensure the PostgreSQL database is running and `backend/.env` is correctly populated.
2. Install E2E requirements:
   ```bash
   pip install -r tests/e2e/requirements-e2e.txt
   playwright install chromium
   ```
3. Run backend and frontend servers.
4. Execute the test suite using `pytest`:
   ```bash
   pytest tests/e2e -v
   ```
5. Check that tests pass against the backend endpoints (progressive API testing), and check the test logs to confirm fuzzed vs exact coordinate matching.
