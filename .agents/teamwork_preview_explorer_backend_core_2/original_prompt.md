## 2026-07-18T09:08:17Z
You are teamwork_preview_explorer. Your working directory is d:\Agriculture project\.agents\teamwork_preview_explorer_backend_core_2.
Task: Explore the codebase for Milestone 2: Backend Core of AgriTrace.
Please analyze:
1. backend/app/models/models.py: How to add security_question and security_question_answer columns to Farmer and Buyer models.
2. backend/app/schemas/schemas.py: How to update FarmerRegister and BuyerRegister Pydantic models to require phone_number and address, and validate that they are not empty/null. Also add security question and answer fields.
3. backend/app/routers/auth.py: How to update registration endpoints (register_farmer, register_buyer) to handle and persist these new fields. Choose at least 3 predefined security questions.
4. backend/app/routers/auth.py: How to implement forgot-password recovery endpoints (initiate, reset-otp, reset-question). Check existing OTP logic.
5. Farmer coordinate validation: Where Farmer coordinates are validated or updated (e.g., backend/app/routers/farmer.py). Verify the range: Latitude [-90, 90], Longitude [-180, 180]. If invalid, return HTTP 400 "wrong location".
6. Buyer location fuzzing: Where crop detail responses are handled (e.g., backend/app/routers/buyer.py). Ensure crop coordinates are fuzzed/approximated for Buyers but exact for Farmers/Admins.

Write your findings in analysis.md in your working directory. Do NOT write or modify code.
