## 2026-07-18T09:35:35Z
You are teamwork_preview_worker. Your working directory is d:\\Agriculture project\\.agents\\teamwork_preview_worker_backend_core_1.

Objective: Implement Milestone 2 (Backend Core) enhancements for AgriTrace.

Context: The models.py file in the repository was accidentally overwritten with markdown content. A backup of the original python code has been prepared for you at:
d:\\Agriculture project\\.agents\\sub_orch_backend_core\\models_backup.md

Please perform the following implementation tasks:

1. Restore & Extend Models (backend/app/models/models.py):
   - First, restore the full python code of models.py from the backup file d:\\Agriculture project\\.agents\\sub_orch_backend_core\\models_backup.md.
   - Add security_question = Column(String, nullable=True) and security_question_answer = Column(String, nullable=True) to both the Farmer and Buyer classes.

2. Require & Validate Schemas (backend/app/schemas/schemas.py):
   - Update Pydantic schemas FarmerRegister and BuyerRegister to require phone_number and address (i.e. ensure no empty/null values by setting type annotation to str and using Field(..., min_length=1)).
   - Add required security_question (str, min_length=1) and security_question_answer (str, min_length=1) fields to both registration schemas.

3. Update Registration & Encryption (backend/app/routers/auth.py):
   - Predefine a list of at least 3 security questions, e.g., PREDEFINED_SECURITY_QUESTIONS = ["What was your childhood nickname?", "What is the name of your first school?", "In which city were you born?"].
   - During farmer and buyer registration, validate that the submitted security_question belongs to PREDEFINED_SECURITY_QUESTIONS. If not, raise HTTP 400 Bad Request.
   - Standardize and hash the answer using the existing hash_password helper:
     user.security_question_answer = hash_password(data.security_question_answer.strip().lower())
   - Persist all these new fields to the database.

4. Implement Forgot Password Endpoints (backend/app/routers/auth.py):
   - POST /api/auth/forgot-password/initiate: Receives email. Look up user (Farmer or Buyer) by email. If not found, raise HTTP 404. Generate a 6-digit OTP passcode, save it using the OTPStore table (set expiry), and optionally trigger email delivery if configured. Return a JSON response:
     {"email": user.email, "security_question": user.security_question, "message": "Verification passcode sent to email. Answer security question to reset password."}
   - POST /api/auth/forgot-password/reset-otp: Receives email, otp passcode, and new_password. Look up OTPStore, verify code matches and is not expired. If valid, update the user's password (hash it using hash_password), delete the OTP store entry, commit, and return a success message.
   - POST /api/auth/forgot-password/reset-question: Receives email, security_question_answer, and new_password. Look up user by email. Verify that security question answer matches the hashed answer using verify_password(data.security_question_answer.strip().lower(), user.security_question_answer). If correct, update the user's password (hash it using hash_password), commit, and return a success message.

5. Coordinate Validation (backend/app/routers/farmer.py and backend/app/routers/auth.py):
   - Create a validation helper that parses coordinates in "latitude,longitude" format.
   - Validate ranges: Latitude must be in [-90, 90] and Longitude in [-180, 180].
   - If coordinates fail format or range validation, raise HTTP 400 Bad Request with detail "wrong location".
   - Integrate this validation into:
     - Register farmer endpoint in backend/app/routers/auth.py (validate exact_location, and validate location if it contains coordinates).
     - Update farmer profile endpoint in backend/app/routers/farmer.py (validate exact_location if updated, and validate location if it contains coordinates).

6. Location Fuzzing for Buyers (backend/app/routers/buyer.py, backend/app/routers/verify.py and backend/app/services/verify_service.py):
   - Define a helper fuzz_location(location_str: str | None) -> str | None that fuzzes coordinates (latitude, longitude) by rounding each to 2 decimal places. Text locations (without a comma) are returned as-is.
   - Apply fuzz_location to location and exact_location fields in search_farmers and get_favourites endpoints in buyer.py.
   - Pass the requester's role (decoded from Authorization header jwt token if present) from the verify endpoint in verify.py to verify_batch in verify_service.py. If the user's role is not "admin" or "farmer", fuzz the returned farmer_location.

7. Verification:
   - Run python run.py or syntax checks to ensure there are no imports or syntax errors.
   - Document verification commands and results in your handoff report.
