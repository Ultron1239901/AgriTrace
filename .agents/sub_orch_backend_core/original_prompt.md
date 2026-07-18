## 2026-07-18T09:07:21Z
Objective: Coordinate and implement all backend core enhancements for AgriTrace:
1. Extend database models (Farmer, Buyer) in backend/app/models/models.py to require/include phone_number, address, security_question, and security_question_answer.
2. Require and validate phone_number and address on registration schemas (validate no empty/null values) in backend/app/schemas/schemas.py.
3. Update backend/app/routers/auth.py to register user profiles with phone number, address, security question selection (from at least 3 pre-defined questions), and answers.
4. Implement the dual forgot-password recovery API endpoints in backend/app/routers/auth.py:
   - POST /api/auth/forgot-password/initiate (returns email, security question, and recovery message)
   - POST /api/auth/forgot-password/reset-otp (resets password via OTP)
   - POST /api/auth/forgot-password/reset-question (resets password via security question answer challenge, case-insensitive)
5. Implement coordinates verification on Farmer profile location coordinates: Latitude range [-90, 90], Longitude range [-180, 180]. If invalid, return HTTP 400 with detail "wrong location".
6. Location fuzzing API: Fuzz or approximate crop coordinates in crop details API responses for Buyers (so exact lat/lon are not exposed in buyer client responses), but keep them exact/unfuzzed for Farmers and Admins.
