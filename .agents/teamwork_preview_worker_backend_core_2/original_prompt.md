## 2026-07-19T00:32:31Z
You are teamwork_preview_worker. Your working directory is d:\Agriculture project\.agents\teamwork_preview_worker_backend_core_2.

Objective: Implement quality fixes and integration alignment for Milestone 2 (Backend Core).

Please read the quality review findings in d:\Agriculture project\.agents\teamwork_preview_reviewer_backend_core_2\handoff.md and perform the following implementation fixes:

1. Request Payload Key Alignment (backend/app/schemas/schemas.py & backend/app/routers/auth.py):
   - The Pydantic schema ResetPasswordQuestionRequest uses a field name security_question_answer. However, the PROJECT.md interface contract specifies the request payload key should be "answer".
   - Modify the ResetPasswordQuestionRequest schema to accept "answer" (either rename the field to answer or add an alias "answer" and ensure it is parsed correctly).
   - Update the forgot-password security question reset handler in backend/app/routers/auth.py to expect and use this field.

2. Response Payload Alignment (backend/app/routers/auth.py):
   - In POST /api/auth/forgot-password/initiate, the response must match the PROJECT.md specification:
     {"email": user.email, "security_question": user.security_question, "message": "Dual recovery paths available."}
   - In POST /api/auth/forgot-password/reset-otp and POST /api/auth/forgot-password/reset-question, the responses must match the specification:
     {"message": "Password reset successful.", "success": true}

3. Admin Farmer Profile Retrieval Alignment (backend/app/routers/admin.py):
   - In endpoints /api/admin/farmers and /api/admin/farmers/{id}, populate the custom farmer profile fields (exact_location, soil_type, land_document, water_availability, previous_crops, and loan_amount) in the returning FarmerResponse so that admins can retrieve exact coordinates and custom profile data.

4. Retention of Coordinates Validation & Fuzzing:
   - Ensure the coordinate range validation check (Latitude [-90, 90], Longitude [-180, 180], HTTP 400 "wrong location" on failure) and buyer coordinate fuzzing (rounding coordinates to 2 decimal places for buyer/anonymous users) are fully preserved and functional.

5. Verification:
   - Run compilation check / python run.py to verify uvicorn starts successfully without import or syntax errors.
   - Run any local unit/integration tests to confirm everything works.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Please write your implementation report and findings in handoff.md in your working directory.
