# AgriTrace End-to-End (E2E) Test Infrastructure

This document details the architecture, directory structure, configurations, and database utilities of the E2E testing framework for AgriTrace.

---

## 1. Architectural Overview & Test Strategy

AgriTrace E2E tests follow **opaque-box**, **requirement-driven**, and **progressive testability** principles:
1. **Opaque-box Execution**: Tests interact with the application strictly via public interfaces (the REST API endpoints or browser-driven UI automation) without calling backend code internals.
2. **Progressive Testability**: To support development flow, the infrastructure enables **API-level E2E tests** (Tier 1 & 2) to run first (validating routes, inputs, and business rules), and subsequently scales to **UI-level browser-based tests** (Tier 3 & 4) via Playwright once frontend views are compiled.
3. **Database-assisted Verification**: E2E tests leverage direct database access as a supporting action (e.g., seeding prerequisite data, inspecting generated email OTPs directly to bypass SMTP, and executing thorough cleanup post-test).

---

## 2. Directory Structure

The E2E test framework is isolated under the `tests/e2e/` directory at the project root:

```text
tests/e2e/
├── conftest.py             # Global pytest fixtures (DB session, async setup, API client)
├── requirements-e2e.txt    # Python dependencies for the E2E framework
├── test_auth.py            # Registration, login, and forgot-password recovery tests
├── test_farmer.py          # Coordinate validation, profile updates, and crop registration tests
├── test_buyer.py           # Location fuzzing, crop list viewing, and purchase inquiries tests
└── test_admin.py           # Verification approvals, suspension, and auditing tests
```

---

## 3. Testing Stack & Setup

The test runner utilizes a Python-based stack:
- **Pytest (v8.0.0)**: Main test run orchestrator.
- **pytest-asyncio (v0.23.5)**: Support for async pytest fixtures and async test functions.
- **pytest-playwright (v0.4.4)**: Browser automation engine for UI-level E2E testing.
- **HTTPX (v0.27.0)**: Asynchronous HTTP client for API-level E2E testing.
- **SQLAlchemy (v2.0.31) & Asyncpg (v0.29.0)**: Async database integration to read credentials from the backend configuration and interact directly with PostgreSQL.

---

## 4. Database Integration & Utility Functions

The `conftest.py` file reads PostgreSQL connection strings dynamically from the backend configuration (`backend/app/config.py`). It provides several key helpers:

### 4.1 Automated Cleanup (`cleanup_e2e_data`)
An autouse fixture cleans the database before and after every test. To prevent test isolation leakages, all E2E test accounts are created with email addresses matching the pattern `%@e2e.test`. 
The cleanup runner deletes records across the schema in the correct topological order to satisfy foreign key constraints:
1. Deletes dependent records in `crop_batches`, `ai_fraud_reports`, `vision_analyses`, and `purchase_requests` referencing E2E Farmers.
2. Deletes dependent records in `purchase_requests` and `verification_logs` referencing E2E Buyers.
3. Clears verification tokens from `otps` (the OTP store).
4. Deletes core `farmers` and `buyers` records.

### 4.2 Direct Database Utilities
- **`get_otp_from_db(db_session, email)`**: Directly queries the `otps` table to retrieve 6-digit email OTPs. This enables password-recovery and email-login tests to verify OTP-based workflows without mock mail catchers or external SMTP servers.
- **`seed_verified_farmer(db_session, email)`**: Seeds a pre-verified Farmer user in PostgreSQL. Because newly registered farmers are unverified and cannot register crop batches, this utility lets tests bypass the verification approval step to verify crop and transaction flows.

---

## 5. Feature Inventory & Mapping

The 10 core features are mapped into the E2E test inventory as follows:

### F1: Registration Fields & Validation
- **Requirement**: Registration must require `phone_number` and `address` (non-null, non-empty), as well as predefined `security_question` and `security_question_answer`. Empty/invalid inputs must be rejected.
- **E2E Strategy**: 
  - Submit registration payloads to `/api/auth/register` (Farmer) and `/api/auth/buyer/register` (Buyer) missing required fields or containing empty strings. Validate that the API returns HTTP 422 (Unprocessable Entity) or HTTP 400 (Bad Request).
  - Submit invalid security questions (not in the predefined list of questions). Validate that registration is blocked.
  - Verify that a valid payload returns HTTP 200/201 with JWT token and correctly hashes the password and security answer in the database.

### F2: Forgot Password Primary Path (Email OTP Reset)
- **Requirement**: Allow password reset by verifying email OTP.
- **E2E Strategy**: 
  - Initiate recovery via `POST /api/auth/forgot-password/initiate` for a registered test email.
  - Query the PostgreSQL database using `get_otp_from_db` to retrieve the active OTP.
  - Submit the OTP and new password to `POST /api/auth/forgot-password/reset-otp`. Assert return status 200 OK.
  - Attempt login using `/api/auth/login` with the new password and verify success.

### F3: Forgot Password Secondary Path (Security Question Challenge Reset)
- **Requirement**: Allow password reset by answering the profile's security question.
- **E2E Strategy**: 
  - Initiate recovery using `POST /api/auth/forgot-password/initiate`.
  - Assert that the response contains the exact security question selected by the user during registration.
  - Submit the correct answer and new password to `POST /api/auth/forgot-password/reset-question`. Assert 200 OK.
  - Verify that submiting an incorrect answer returns HTTP 400 Bad Request.

### F4: Farmer Coordinates Validation Check
- **Requirement**: Latitude must be within `[-90, 90]`, and Longitude within `[-180, 180]`. Format should be `latitude,longitude`. Return HTTP 400 `"wrong location"` on violation.
- **E2E Strategy**: 
  - Submit out-of-bounds coordinates (e.g. `"105.0, 77.0"` or `"12.0, 200.0"`) or invalid formats (e.g. `"xyz,abc"`) to farmer registration and profile update endpoints.
  - Assert that the server responds with HTTP 400 and the exact error body `{"detail": "wrong location"}`.

### F5: Exact Coordinate View on Map (Farmer and Admin access)
- **Requirement**: Farmers viewing their own profile and Admins viewing farmer profiles must get exact coordinate location strings.
- **E2E Strategy**: 
  - Seed a farmer with exact location `"12.9716, 77.5946"`.
  - Log in as that Farmer; fetch `/api/farmer/profile` and verify the coordinates are returned exactly.
  - Log in as Admin; fetch `/api/admin/farmers/{id}` and assert that coordinates are exact.

### F6: Fuzzed Coordinate View on Map (Buyer Crop List / Scan access)
- **Requirement**: Buyers and anonymous consumers scanning QR codes must receive fuzzed locations (rounded to 2 decimal places, representing ~1.1km approximation) to protect farmer privacy.
- **E2E Strategy**: 
  - Seed a farmer with coordinates `"12.971638, 77.594621"`.
  - Log in as Buyer; query `/api/buyer/farmers` or `/api/verify/{batch_id}`.
  - Verify that the coordinates returned are rounded to 2 decimal places: `"12.97, 77.59"`.

### F7: Onboarding Guideline Manual Pop-up Interceptor
- **Requirement**: UI dashboard is locked by a popup modal on first-time login until the user checks the "OK" checkbox and acknowledges the guidelines.
- **E2E Strategy**: 
  - Drive Playwright browser to log in with a new user.
  - Assert that the pop-up modal is present on the DOM and viewport interactions with the dashboard are blocked.
  - Attempt to dismiss the popup without checking the "OK" checkbox and verify that the dashboard remains locked.
  - Check the "OK" checkbox, click dismiss, and verify that the modal is removed and the dashboard becomes interactive.

### F8: Guideline Manual PDF Assets & About Page Rendering
- **Requirement**: Static PDF manuals are served, and About page displays terms.
- **E2E Strategy**: 
  - Use Playwright to navigate to the About page and assert that the layout and texts render correctly.
  - Request the PDF manual assets URL (e.g., `/assets/guideline_manual.pdf` or `/uploads/manual.pdf`). Assert that the asset is loaded successfully with HTTP 200 and the content-type is `application/pdf`.

### F9: Interactive Walkthrough Onboarding Tour
- **Requirement**: Onboarding tour must guide users using "Next", "Back", "Skip", and "Finish".
- **E2E Strategy**: 
  - Log in via Playwright and trigger the onboarding tour.
  - Assert the first tour step modal is visible.
  - Click "Next", assert navigation to the second step element.
  - Click "Back", assert navigation returns to the first step.
  - Click "Skip" or "Finish", assert that the tour closes and the user's dashboard is fully visible without any tour overlays.

### F10: Theme Accessibility Contrast Legibility Audit
- **Requirement**: Contrast ratios must meet WCAG AA standards across dark/light accessibility themes.
- **E2E Strategy**: 
  - Toggle light and dark accessibility contrast themes via Playwright.
  - Run `axe-core` accessibility audits (`playwright-axe`) on active views.
  - Verify that there are zero violations of the contrast rules (`color-contrast` WCAG AA guidelines).

---

## 6. Running Tests

### 6.1 Installation
Install E2E dependencies in the environment:
```bash
pip install -r tests/e2e/requirements-e2e.txt
playwright install chromium
```

### 6.2 Executing the E2E Test Suite
To run the full suite:
```bash
pytest tests/e2e -v
```

To run API-only tests:
```bash
pytest tests/e2e -v -k "api_"
```

To run UI-only tests:
```bash
pytest tests/e2e -v -k "ui_"
```
