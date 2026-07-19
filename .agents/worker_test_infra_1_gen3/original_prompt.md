## 2026-07-18T14:18:28Z
You are the replacement teamwork_preview_worker (generation 3) for Milestone 1 (Test Infra Setup).
Your working directory is: d:\Agriculture project\.agents\worker_test_infra_1_gen3

Objective:
Implement the E2E test infrastructure directory structure and files, and write the TEST_INFRA.md document at the project root.

Tasks:
1. Read the explorer handoff report at d:\Agriculture project\.agents\teamwork_preview_explorer_test_infra_1_gen2\handoff.md.
2. Create the directory `tests/e2e/` at the project root.
3. Write `tests/e2e/requirements-e2e.txt` with python testing dependencies.
4. Write `tests/e2e/conftest.py` with pytest async fixtures, database session helper (reading credentials from backend/app/config.py), and test data setup/teardown functions.
5. Create a comprehensive `TEST_INFRA.md` file at the project root (`d:\Agriculture project\TEST_INFRA.md`) based on the template in the system instructions. Map the 10 features identified below into the Feature Inventory:
   - F1: Registration fields & validation (reject empty/invalid inputs)
   - F2: Forgot password primary path (email OTP reset)
   - F3: Forgot password secondary path (security question challenge reset)
   - F4: Farmer coordinates validation check (Latitude [-90,90], Longitude [-180,180], HTTP 400 "wrong location")
   - F5: Exact coordinate view on map (Farmer and Admin access)
   - F6: Fuzzed coordinate view on map (Buyer crop list / scan access)
   - F7: Onboarding Guideline manual pop-up interceptor (locking dashboard, OK checkbox validate)
   - F8: Guideline manual PDF assets & About page rendering
   - F9: Interactive walkthrough onboarding tour (Next, Back, Skip, Finish)
   - F10: Theme accessibility contrast legibility audit
6. Ensure that the E2E tests have database utilities (like connecting to agritrace_db using SQLAlchemy/asyncpg) to clean up test data with email pattern `%@e2e.test` and fetch verification OTPs directly from the database for forgot-password tests.
7. Run lint/checks on the written files if possible or verify they are created correctly.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Send a message back to f8c0b15f-b8cd-4d59-bb1c-b104fa2c789e when your work is complete and handoff.md is ready.
