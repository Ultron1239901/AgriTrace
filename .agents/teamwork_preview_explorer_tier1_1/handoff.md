# Handoff Report — Tier 1 E2E Feature Coverage Design

This report outlines the comprehensive E2E test plan for the 10 Tier 1 features (F1 to F10), specifying 5 happy path variations per feature (total of 50 test cases), mapping them to files, verifying them against Dual Track testing principles, and documenting critical observations from the codebase.

---

## 1. Observation
We directly inspected the following files in the project workspace:
1. `ORIGINAL_REQUEST.md`: Contains the requirements for registration, forgot password recovery paths, coordinates verification, locations maps (exact/fuzzed), onboarding Guideline manuals (modal, PDF, about page), and walkthrough tour.
2. `TEST_INFRA.md`: Explains the architectural principles (opaque-box, progressive testability) and the E2E directory structure (`tests/e2e/test_auth.py`, `tests/e2e/test_farmer_buyer_location.py`, and `tests/e2e/test_ui.py`).
3. `tests/e2e/conftest.py`: Defines the async test database engine, automatically applies schema migrations (`soil_type`, `exact_location`, etc.), provides clean-up fixtures (`cleanup_e2e_data`), and helper utilities (`get_otp_from_db`, `seed_verified_farmer`).
4. `backend/app/routers/auth.py`:
   - Predefined questions are located at lines 18-22:
     ```python
     PREDEFINED_SECURITY_QUESTIONS = [
         "What was your childhood nickname?",
         "What is the name of your first school?",
         "In which city were you born?"
     ]
     ```
   - Coordinate validation range boundaries are verified at lines 48-49:
     ```python
     if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
         raise ValueError()
     ```
   - **Critical Bug Observed in Forgot Password Initialization (line 363)**:
     ```python
     buyer = (await db.execute(select(Buyer).where(Farmer.email == email_lower))).scalars().first()
     ```
     *Analysis*: This query incorrectly uses `Farmer.email` in a `select(Buyer)` query, which triggers a cross join or SQLAlchemy compiling violation, preventing buyers from initiating password recovery via `/api/auth/forgot-password/initiate`.
5. `backend/app/routers/buyer.py` (lines 25-37): Location fuzzing implementation uses `round(val, 2)` for coordinate strings:
   ```python
   def fuzz_location(location_str: str | None) -> str | None:
       ...
       return f"{round(lat, 2)},{round(lon, 2)}"
   ```

---

## 2. Logic Chain
1. To scale E2E testing to cover all 10 features with at least 5 happy path scenarios each (total >= 50 test cases), we must outline specific variations spanning different data payloads, user roles, API queries, and browser states.
2. **API-Level Coverage (F1 to F6)**: We can cover registration input configurations (soils, water access, questions), password recovery (OTP/Questions) for both roles, coordinates validations (boundary regions, formatting tolerance), and role-based maps (exact/fuzzed coordinates). 
3. **UI-Level Coverage (F7 to F10)**: We will use Playwright to drive the onboarding guideline modal interceptor, static manual PDF loading, About page rendering, step-by-step tour steps, and Axe contrast legibility audits.
4. **Dual Track: E2E Testing Track**: We verify that these proposed cases are:
   - *Opaque-box*: Run against HTTP client routes and browser DOM interactors, relying on database access only for pre-seeding or OTP verification.
   - *Requirement-driven*: Directly trace back to acceptance criteria in `ORIGINAL_REQUEST.md`.
   - *Progressive testability*: Group tests into API tests (Tier 1 & 2) and UI tests (Tier 3 & 4) so API tests can run fast without a frontend build.

---

## 3. Caveats
- **Query Bug in Auth Router**: Due to `Farmer.email` being referenced in the `select(Buyer)` query at `backend/app/routers/auth.py:363`, forgot-password tests for Buyers will fail under normal conditions. In implementing the tests, either the backend code must be corrected first by changing `Farmer.email == email_lower` to `Buyer.email == email_lower`, or the tests must mock the database query response or bypass it.
- **Frontend Running Environment**: UI tests (F7-F10) in `test_ui.py` depend on `RUN_UI_TESTS=true` and a live frontend server running at `http://localhost:3000`.

---

## 4. Conclusion
We propose the following 50 distinct happy path E2E scenarios mapped to specific files under `tests/e2e/`.

### 4.1 Feature-by-Feature Happy Path Scenarios (50 Cases)

#### F1: Registration Fields & Validation (`tests/e2e/test_auth.py`)
- **Case 1.1: Farmer Registration with Clay Soil & Question 1**
  - *Inputs*: Soil type `"Clay"`, question `"What was your childhood nickname?"`, answer `"nick"`.
  - *APIs/Steps*: POST `/api/auth/register` with valid payload.
  - *Expected Outcome*: HTTP 201, returns token, database records new farmer with hashed answer.
- **Case 1.2: Farmer Registration with Sandy Soil & Question 2**
  - *Inputs*: Soil type `"Sandy"`, question `"What is the name of your first school?"`, answer `"school"`.
  - *APIs/Steps*: POST `/api/auth/register`.
  - *Expected Outcome*: HTTP 201, returns token.
- **Case 1.3: Farmer Registration with Loam Soil & Question 3**
  - *Inputs*: Soil type `"Loam"`, question `"In which city were you born?"`, answer `"city"`.
  - *APIs/Steps*: POST `/api/auth/register`.
  - *Expected Outcome*: HTTP 201, returns token.
- **Case 1.4: Buyer Registration with Question 1**
  - *Inputs*: Valid buyer schema, question `"What was your childhood nickname?"`, answer `"buyernick"`.
  - *APIs/Steps*: POST `/api/auth/buyer/register`.
  - *Expected Outcome*: HTTP 201, returns token.
- **Case 1.5: Farmer Registration with Optional Metadata**
  - *Inputs*: Valid schema, optional fields: `water_availability="Yes"`, `previous_crops="Wheat,Rice"`, `loan_amount=50000.0`.
  - *APIs/Steps*: POST `/api/auth/register`.
  - *Expected Outcome*: HTTP 201, profile fields successfully saved to database.

#### F2: Forgot Password Primary Path (Email OTP Reset) (`tests/e2e/test_auth.py`)
- **Case 2.1: Farmer Password Reset via OTP**
  - *Inputs*: Registered farmer email.
  - *APIs/Steps*: POST `/api/auth/forgot-password/initiate` -> fetch OTP via `get_otp_from_db` -> POST `/api/auth/forgot-password/reset-otp` with new password.
  - *Expected Outcome*: HTTP 200, subsequent login with new password succeeds.
- **Case 2.2: Buyer Password Reset via OTP**
  - *Inputs*: Registered buyer email (requires fixing typo on line 363 of `auth.py` first).
  - *APIs/Steps*: POST `/api/auth/forgot-password/initiate` -> fetch OTP -> POST `/api/auth/forgot-password/reset-otp`.
  - *Expected Outcome*: HTTP 200, subsequent login with new password succeeds.
- **Case 2.3: Password Reset with 24-character Passphrase**
  - *Inputs*: Valid farmer email, complex long password `"SuperSecurePassphrase123#"`.
  - *APIs/Steps*: POST `/api/auth/forgot-password/initiate` -> fetch OTP -> POST `/api/auth/forgot-password/reset-otp`.
  - *Expected Outcome*: HTTP 200, successfully logs in with new long password.
- **Case 2.4: Password Reset with Special Characters**
  - *Inputs*: Valid buyer email, password `"P@$$w0rd_#_123!"`.
  - *APIs/Steps*: POST `/api/auth/forgot-password/initiate` -> fetch OTP -> POST `/api/auth/forgot-password/reset-otp`.
  - *Expected Outcome*: HTTP 200, successfully resets.
- **Case 2.5: OTP Re-initiate Sequence Handling**
  - *Inputs*: Valid farmer email.
  - *APIs/Steps*: Initiate recovery twice in sequence -> fetch current OTP -> reset using newest OTP.
  - *Expected Outcome*: HTTP 200, database overwrites the first OTP with the second, making only the second valid.

#### F3: Forgot Password Secondary Path (Security Question Challenge) (`tests/e2e/test_auth.py`)
- **Case 3.1: Reset for Farmer using Question 1**
  - *Inputs*: Registered farmer email, correct answer to Question 1.
  - *APIs/Steps*: POST `/api/auth/forgot-password/initiate` -> parse returned question -> POST `/api/auth/forgot-password/reset-question`.
  - *Expected Outcome*: HTTP 200, password updated successfully.
- **Case 3.2: Reset for Farmer using Question 2**
  - *Inputs*: Registered farmer email, correct answer to Question 2.
  - *APIs/Steps*: Initiate -> POST `/api/auth/forgot-password/reset-question`.
  - *Expected Outcome*: HTTP 200.
- **Case 3.3: Reset for Farmer using Question 3**
  - *Inputs*: Registered farmer email, correct answer to Question 3.
  - *APIs/Steps*: Initiate -> POST `/api/auth/forgot-password/reset-question`.
  - *Expected Outcome*: HTTP 200.
- **Case 3.4: Reset for Buyer using Question 1**
  - *Inputs*: Registered buyer email, correct answer.
  - *APIs/Steps*: Initiate -> POST `/api/auth/forgot-password/reset-question`.
  - *Expected Outcome*: HTTP 200.
- **Case 3.5: Case-insensitivity Check on Answer**
  - *Inputs*: Registered answer `"MyNickName"`, submitted answer `"mynickname"`.
  - *APIs/Steps*: Initiate -> POST `/api/auth/forgot-password/reset-question`.
  - *Expected Outcome*: HTTP 200, matching performs case-insensitive verification.

#### F4: Farmer Coordinates Validation Check (`tests/e2e/test_farmer_buyer_location.py`)
- **Case 4.1: Equatorial Coordinates Validation**
  - *Inputs*: `"0.0,0.0"`.
  - *APIs/Steps*: Farmer registration with coordinates.
  - *Expected Outcome*: HTTP 201, registration accepted.
- **Case 4.2: Northern/Eastern Hemisphere Coordinates**
  - *Inputs*: `"12.9716,77.5946"`.
  - *APIs/Steps*: Farmer registration.
  - *Expected Outcome*: HTTP 201.
- **Case 4.3: Southern/Western Hemisphere Coordinates**
  - *Inputs*: `"-33.8688,-151.2093"`.
  - *APIs/Steps*: Farmer profile update (`PUT /api/farmer/profile`).
  - *Expected Outcome*: HTTP 200, profile coordinates updated.
- **Case 4.4: Extreme Boundary Boundaries Check**
  - *Inputs*: `"90.0,180.0"`.
  - *APIs/Steps*: Farmer profile update.
  - *Expected Outcome*: HTTP 200.
- **Case 4.5: Coordinates Whitespace Padding**
  - *Inputs*: `"  12.9716  ,  77.5946  "`.
  - *APIs/Steps*: Farmer profile update.
  - *Expected Outcome*: HTTP 200, whitespaces are successfully trimmed and parsed.

#### F5: Exact Coordinate View on Map (`tests/e2e/test_farmer_buyer_location.py`)
- **Case 5.1: Farmer Profile Exact Fetch**
  - *Inputs*: Exact location `"12.971638,77.594621"` registered.
  - *APIs/Steps*: Log in as Farmer -> GET `/api/farmer/profile`.
  - *Expected Outcome*: Returns exact `location` and `exact_location` values.
- **Case 5.2: Admin Farmer Lookup Exact View**
  - *Inputs*: Exact location.
  - *APIs/Steps*: Log in as Admin -> GET `/api/admin/farmers/{id}`.
  - *Expected Outcome*: Returns exact `location` coordinate values.
- **Case 5.3: Farmer QR Scan Exact coordinates**
  - *Inputs*: Seeded crop batch.
  - *APIs/Steps*: Log in as Farmer -> GET `/api/verify/{batch_id}`.
  - *Expected Outcome*: Returns exact coordinate in `farmer_location`.
- **Case 5.4: Admin QR Scan Exact coordinates**
  - *Inputs*: Seeded crop batch.
  - *APIs/Steps*: Log in as Admin -> GET `/api/verify/{batch_id}`.
  - *Expected Outcome*: Returns exact coordinate in `farmer_location`.
- **Case 5.5: Farmer Profile Update Update Reflection**
  - *Inputs*: Update coordinates to `"13.0827,80.2707"`.
  - *APIs/Steps*: PUT `/api/farmer/profile` -> GET `/api/farmer/profile`.
  - *Expected Outcome*: Returns the newly updated exact location immediately.

#### F6: Fuzzed Coordinate View on Map (`tests/e2e/test_farmer_buyer_location.py`)
- **Case 6.1: Buyer Farmer Search Fuzzed View**
  - *Inputs*: Farmer with location `"12.9716,77.5946"`.
  - *APIs/Steps*: Log in as Buyer -> GET `/api/buyer/farmers?search=Coords`.
  - *Expected Outcome*: Coordinates returned are fuzzed: `"12.97,77.59"`.
- **Case 6.2: Buyer Favourite Farmers Fuzzed View**
  - *Inputs*: Favourited farmer.
  - *APIs/Steps*: Log in as Buyer -> GET `/api/buyer/favourites`.
  - *Expected Outcome*: Favourited farmer records contain fuzzed coordinates.
- **Case 6.3: Anonymous QR Scan Fuzzed Coordinates**
  - *Inputs*: Crop batch ID.
  - *APIs/Steps*: GET `/api/verify/{batch_id}` without auth headers.
  - *Expected Outcome*: Returns fuzzed coordinates (`"12.97,77.59"`).
- **Case 6.4: Logged-in Buyer QR Scan Fuzzed Coordinates**
  - *Inputs*: Crop batch ID.
  - *APIs/Steps*: Log in as Buyer -> GET `/api/verify/{batch_id}`.
  - *Expected Outcome*: Returns fuzzed coordinates.
- **Case 6.5: Precise Fuzzing Rounding Validation**
  - *Inputs*: Farmer exact coordinates `"12.904,77.509"`.
  - *APIs/Steps*: Log in as Buyer -> GET `/api/buyer/farmers`.
  - *Expected Outcome*: Returns rounded coordinates: `"12.9,77.51"`.

#### F7: Onboarding Guideline manual pop-up interceptor (`tests/e2e/test_ui.py`)
- **Case 7.1: New Farmer First-Time Login Modal Flow**
  - *Inputs*: Newly registered farmer.
  - *APIs/Steps*: Playwright drives login -> Guideline modal appears -> check checkbox `#guideline-ack` -> click "Acknowledge & Continue".
  - *Expected Outcome*: Dashboard unlocks and becomes interactive.
- **Case 7.2: New Buyer First-Time Login Modal Flow**
  - *Inputs*: Newly registered buyer.
  - *APIs/Steps*: Login -> Guideline modal appears -> check `#guideline-ack` -> click continue.
  - *Expected Outcome*: Buyer dashboard is unlocked.
- **Case 7.3: Click Immunity Intercept Check**
  - *Inputs*: Newly registered farmer.
  - *APIs/Steps*: Login -> Try to click backdrop or dashboard menu buttons.
  - *Expected Outcome*: Viewport events are blocked, modal remains visible.
- **Case 7.4: Guideline Content Inspection**
  - *Inputs*: First-time login user.
  - *APIs/Steps*: Inspect `.guideline-modal-overlay` text.
  - *Expected Outcome*: Confirms manual text (AI agents, Telegram rules) is visible.
- **Case 7.5: Session Persistence Interceptor Check**
  - *Inputs*: Logged in and acknowledged user.
  - *APIs/Steps*: Log out -> Log back in.
  - *Expected Outcome*: Dashboard loads directly without modal.

#### F8: Guideline manual PDF assets and About page rendering (`tests/e2e/test_ui.py`)
- **Case 8.1: Anonymous Visitor About Page Load**
  - *Inputs*: None.
  - *APIs/Steps*: Navigate to `/about`.
  - *Expected Outcome*: About page headers and text load successfully.
- **Case 8.2: Logged-in Farmer About Page Load**
  - *Inputs*: Farmer login session.
  - *APIs/Steps*: Navigate to `/about`.
  - *Expected Outcome*: About page renders beautifully.
- **Case 8.3: Direct Loading of static PDF asset**
  - *Inputs*: PDF URL `/assets/guideline_manual.pdf`.
  - *APIs/Steps*: Load asset url via page.
  - *Expected Outcome*: HTTP 200, content-type is `application/pdf`.
- **Case 8.4: Direct Loading of static PDF upload path**
  - *Inputs*: secondary path `/uploads/manual.pdf`.
  - *APIs/Steps*: Load URL.
  - *Expected Outcome*: HTTP 200, valid PDF header.
- **Case 8.5: Layout Responsiveness across Viewports**
  - *Inputs*: Screen sizes (Mobile: 375px, Tablet: 768px, Desktop: 1200px).
  - *APIs/Steps*: Navigate to `/about` with specified viewports.
  - *Expected Outcome*: Elements adapt, texts stay readable, no layout breakage.

#### F9: Interactive walkthrough onboarding tour (`tests/e2e/test_ui.py`)
- **Case 9.1: Farmer Onboarding Tour Complete Steps**
  - *Inputs*: Farmer logged in.
  - *APIs/Steps*: Click "Start Tour" -> Step 1 -> Next -> Step 2 -> Next -> Step 3 -> Next -> Step 4 -> Finish.
  - *Expected Outcome*: Tour overlay is removed, sidebar menu items highlighted correctly.
- **Case 9.2: Onboarding Tour Backwards Navigation**
  - *Inputs*: User logged in.
  - *APIs/Steps*: Click "Start Tour" -> Step 1 -> Next -> Step 2 -> Back -> Step 1 -> Skip.
  - *Expected Outcome*: Backwards movement succeeds, skip button dismisses tour.
- **Case 9.3: Onboarding Tour Immediate Skip**
  - *Inputs*: User logged in.
  - *APIs/Steps*: Click "Start Tour" -> click Skip on Step 1.
  - *Expected Outcome*: Tour overlay is removed immediately.
- **Case 9.4: Buyer Onboarding Tour Complete Steps**
  - *Inputs*: Buyer logged in.
  - *APIs/Steps*: Start Tour -> Step 1 -> Next -> Step 2 -> Next -> Step 3 -> Finish.
  - *Expected Outcome*: Tour overlay completes and exits.
- **Case 9.5: Tour Tooltip Element Alignment Check**
  - *Inputs*: Start Tour.
  - *APIs/Steps*: Inspect DOM tooltips position coordinates against targets (e.g. `#sidebar-crops`).
  - *Expected Outcome*: Tooltip is aligned properly with corresponding DOM element.

#### F10: Theme accessibility contrast legibility audit (`tests/e2e/test_ui.py`)
- **Case 10.1: Light Theme Dashboard Contrast Audit**
  - *Inputs*: Light theme.
  - *APIs/Steps*: Toggle theme -> run `playwright-axe` audit.
  - *Expected Outcome*: Zero violations under WCAG AA `color-contrast` guidelines.
- **Case 10.2: Dark Theme Dashboard Contrast Audit**
  - *Inputs*: Dark theme.
  - *APIs/Steps*: Toggle theme -> run `playwright-axe` audit.
  - *Expected Outcome*: Zero violations.
- **Case 10.3: Dark Theme Farmer Profile Contrast Audit**
  - *Inputs*: Dark theme.
  - *APIs/Steps*: Open `/profile` -> run Axe audit.
  - *Expected Outcome*: Zero violations on profile input elements.
- **Case 10.4: Light Theme About Page Contrast Audit**
  - *Inputs*: Light theme.
  - *APIs/Steps*: Open `/about` -> run Axe audit.
  - *Expected Outcome*: Zero violations on manual text.
- **Case 10.5: Dark Theme Guideline Modal Contrast Audit**
  - *Inputs*: Dark theme.
  - *APIs/Steps*: Open guideline modal popup -> run Axe audit.
  - *Expected Outcome*: Zero violations on popup overlay text, check box, and button.

---

## 5. Verification Method

### 5.1 Test Execution Command
To run all Tier 1 API-level tests (F1 to F6):
```bash
pytest tests/e2e -v -k "not test_ui"
```

To run all Tier 1 UI-level tests (F7 to F10):
```bash
# Ensure frontend dev server is running on localhost:3000
$env:RUN_UI_TESTS="true"
pytest tests/e2e/test_ui.py -v
```

### 5.2 Files to Inspect
- `tests/e2e/test_auth.py`: Inspect test registrations (F1) and recovery resets (F2, F3).
- `tests/e2e/test_farmer_buyer_location.py`: Inspect coordinates verification (F4), exact profile views (F5), and fuzzed buyer searches (F6).
- `tests/e2e/test_ui.py`: Inspect Playwright steps for modal pop-up (F7), static manual and PDF load (F8), walkthrough tour (F9), and Axe contrast audits (F10).
