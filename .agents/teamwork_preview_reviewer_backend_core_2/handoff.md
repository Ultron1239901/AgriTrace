# Handoff & Review Report — Milestone 2 (Backend Core)

## Quality Review Summary

**Verdict**: REQUEST_CHANGES

The implementation of Milestone 2 (Backend Core) contains the required database models, registration schemas, coordinates validation checks, and coordinates fuzzing integration. However, there are multiple critical integration mismatches between the code implementation and the specifications defined in `PROJECT.md` and `TEST_INFRA.md`.

---

## Quality Review Findings

### [Critical] Finding 1: Security Question Password Reset Payload Key Mismatch
- **Where**: `backend/app/schemas/schemas.py` (lines 387-391) and `backend/app/routers/auth.py` (lines 426-444).
- **What**: The Pydantic schema `ResetPasswordQuestionRequest` requires a field named `security_question_answer`. However, `PROJECT.md` specifies the request payload key should be `answer`:
  ```json
  {
    "email": "user@example.com",
    "answer": "Nickname",
    "new_password": "NewPassword123"
  }
  ```
- **Why**: This mismatch will cause a `422 Unprocessable Entity` validation error when the frontend or E2E tests attempt to call `POST /api/auth/forgot-password/reset-question` using the specified interface contract (`"answer"`).
- **Suggestion**: Rename `security_question_answer` to `answer` in the `ResetPasswordQuestionRequest` schema and the corresponding handler, or add a field alias.

### [Major] Finding 2: Forgot Password Response Payload Inconsistencies
- **Where**: `backend/app/routers/auth.py` (lines 395-399, 423, 443).
- **What**:
  - `POST /api/auth/forgot-password/initiate` returns `message: "Verification passcode sent to email. Answer security question to reset password."` instead of `message: "Dual recovery paths available."` as specified in `PROJECT.md`.
  - Both `/forgot-password/reset-otp` and `/forgot-password/reset-question` return `{"message": "Password updated successfully"}`. However, `PROJECT.md` specifies they must return:
    ```json
    {
      "message": "Password reset successful.",
      "success": true
    }
    ```
- **Why**: Direct violation of the interface contracts defined in `PROJECT.md`, which could break test assertions or frontend integrations.
- **Suggestion**: Standardize recovery responses to match the keys and values in `PROJECT.md`.

### [Major] Finding 3: Admin Farmer Profile Retrieval Missing Coordinates & Profile Fields
- **Where**: `backend/app/routers/admin.py` (lines 180-217, 220-237).
- **What**: The admin router endpoints `/api/admin/farmers` and `/api/admin/farmers/{id}` return a `FarmerResponse` but omit the initialization of the expanded fields (`exact_location`, `soil_type`, `land_document`, `water_availability`, `previous_crops`, and `loan_amount`).
- **Why**: Pydantic defaults `exact_location` to `None` when it is not explicitly provided. Consequently, admins will receive `exact_location: null`, failing `TEST_INFRA.md` requirement F5 which states: *"Log in as Admin; fetch `/api/admin/farmers/{id}` and assert that coordinates are exact."*
- **Suggestion**: Retrieve and pass the farmer's database columns (e.g. `exact_location`, `soil_type`, etc.) into `FarmerResponse` constructors in `admin.py`.

---

## Adversarial Review Summary

**Overall risk assessment**: MEDIUM

From an adversarial standpoint, the core cryptography (salted/PBKDF2 password and security question answer hashing) and coordinates range checks are robust. However, there are two security and privacy vulnerabilities identified in the recovery flow.

---

## Adversarial Review Challenges

### [High] Challenge 1: Absence of Rate-limiting/Lockout on Security Question Answer Verification
- **Assumption Challenged**: Users choose security question answers that are not easily guessable.
- **Attack Scenario**: Since `/api/auth/forgot-password/reset-question` performs verification against a static hash using `verify_password()` and has no rate limits, an attacker can brute-force common nicknames or birth cities for a target email.
- **Blast Radius**: Full bypass of password protection via the secondary recovery flow, leading to account takeover.
- **Mitigation**: Implement a progressive delay or lockout mechanism (e.g., locking the security question path for 1 hour after 5 failed attempts).

### [Medium] Challenge 2: User Account Enumeration Vector
- **Assumption Challenged**: Username/email lists are confidential.
- **Attack Scenario**: Calling `POST /api/auth/forgot-password/initiate` with an unregistered email returns an HTTP 404 with `"Email address not found"`.
- **Blast Radius**: Attackers can programmatically query the endpoint with a list of emails to identify which users are registered on the Agritrace platform.
- **Mitigation**: Return a generic, successful response for all initiation requests, stating: *"If this email is registered, a passcode recovery email has been sent."*

---

## 5-Component Handoff Details

### 1. Observation
- **Models & Schemas**: Confirmed `security_question` and `security_question_answer` are defined as nullable String columns on `Farmer` and `Buyer` tables (`models.py`, lines 53-54, 74-75). Confirmed schemas enforce non-empty fields during registration (`schemas.py`, lines 11-14, 115-118).
- **Authentication Recovery**: The router `auth.py` implements password resets using database-backed OTPs (`OTPStore`) and case/whitespace-insensitive security answer verification (`auth.py`, lines 426-444).
- **Coordinates Parsing**: Confirmed that `validate_coordinates` correctly parses coordinate strings, checks ranges (`[-90, 90]` and `[-180, 180]`), and raises a 400 HTTP exception with details `"wrong location"` (`auth.py`, lines 39-52).
- **Location Fuzzing**: Checked `buyer.py` (lines 25-36) and `verify_service.py` (lines 11-23) for location fuzzing. Both successfully round decimal coordinates to 2 decimal places, and keep non-coordinate locations unchanged. Verified that `verify_service.py` restricts exact coordinates to admins and farmers, fuzzing them for buyers or anonymous consumers (`verify_service.py`, lines 71-72).
- **Execution Log**: Execution of local E2E tests `pytest tests/e2e -v` timed out awaiting user command authorizations, preventing runtime validation.

### 2. Logic Chain
- Since the `ResetPasswordQuestionRequest` schema requires `security_question_answer` (Pydantic `Field(..., min_length=1)`), but the `PROJECT.md` specification dictates client payloads should use the key `"answer"`, it is logically impossible for clients complying with `PROJECT.md` to successfully use `/forgot-password/reset-question` without triggering a Pydantic Validation Error (422 Unprocessable Entity).
- Because `admin.py`'s `get_farmer_profile` returns a `FarmerResponse` but only initiates `id`, `name`, `email`, `location`, `verified`, `rejected`, `suspended`, `status`, `status_change_reason`, and `created_at`, it means `exact_location` remains its default value (`None`). This logically breaks the exact coordinates visibility contract for administrators.
- As the code compiles successfully under static checks (correct imports, standard class references), the code is free of syntax errors.

### 3. Caveats
- Static analysis was performed in lieu of dynamic runtime execution due to the user prompt timeout for command authorization. No actual database triggers or live HTTP traffic assertions were performed during this review.

### 4. Conclusion
- The Backend Core implementation for Milestone 2 contains robust geofencing validation and coordinates fuzzing code. However, it requires changes to resolve interface payload mismatches, missing admin profile coordinate fields, and security/privacy concerns in the forgot password recovery handlers.

### 5. Verification Method
- Independent reviewers or implementers can verify these findings by:
  1. Reading the schema definitions in `backend/app/schemas/schemas.py` and comparing them against `PROJECT.md` recovery payload specs.
  2. Inspecting the field initialization block inside the `get_farmer_profile` function in `backend/app/routers/admin.py` to confirm `exact_location` is omitted.
  3. Testing the endpoint `POST /api/auth/forgot-password/reset-question` with the request body format:
     ```json
     {
       "email": "test@e2e.test",
       "answer": "Test Answer",
       "new_password": "NewPassword123"
     }
     ```
     and asserting whether it returns a 422 validation error or a 200 OK.
