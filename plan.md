# Implementation Track Plan

This plan details the implementation strategy for the AgriTrace enhancements, following the Project Orchestration pattern.

## Implementation Milestones & Timeline

### Milestone 2: Backend Core (M2)
- **Scope**:
  - Extend DB models (`Farmer`, `Buyer`) to support `security_question` and `security_question_answer` (or hash/encrypted representation) fields.
  - Require `phone_number` and `address` on registration schemas (validate no empty/null values).
  - Implement `/api/auth/forgot-password/initiate` endpoint (dual recovery info).
  - Implement `/api/auth/forgot-password/reset-otp` endpoint (OTP reset).
  - Implement `/api/auth/forgot-password/reset-question` endpoint (Security question reset).
  - Implement location coordinate validation (lat range `[-90, 90]`, lon range `[-180, 180]`) and error handling returning HTTP 400 `"wrong location"`.
  - Implement location fuzzing/approximation in Buyer API crop details responses.
- **Dependencies**: None.
- **Verification Criteria**:
  - Python unittest/pytest or API calls verifying endpoint correctness.
  - Verification of coordinate format validation.
  - Verification that fuzzed coordinates are returned for Buyers, and exact coordinates are returned for Farmers and Admins.

### Milestone 3: Frontend Auth & Recovery UI (M3)
- **Scope**:
  - Update Farmer and Buyer registration forms to include mandatory fields: phone number, address, security questions (select from at least 3 pre-defined questions), and answers.
  - Create the Forgot Password recovery portal UI (handling the dual OTP and security question reset flows).
  - Integrate UI components with the backend auth endpoints.
- **Dependencies**: M2 (Backend Core must be completed first).
- **Verification Criteria**:
  - Manual or programmatic UI interaction test results showing registration rejection of invalid inputs.
  - Password reset flows working end-to-end via OTP or Security Question.

### Milestone 4: Frontend Maps & Onboarding (M4)
- **Scope**:
  - Add "View Map" button to Farmer portal dashboard top section.
  - Integrate Leaflet map widget displaying exact coordinates boundary for Farmer and Admin.
  - Restrict Buyer view to approximate crop coordinates (no exact lat/lon in client browser).
  - Build first-time login/register Guideline Manual modal interceptor. Locking dashboard until Terms & Conditions checkbox is checked and user clicks OK.
  - Compile Guideline Manual contents to a static PDF in assets.
  - Redesign "About" page to render Guideline Manual content beautifully.
  - Implement step-by-step interactive onboarding tour (Next, Back, Skip, Finish) explaining sidebar menu panels.
  - Conduct theme accessibility audit to verify contrast/visibility under light and dark modes.
- **Dependencies**: M2 (Backend Core must be completed first).
- **Verification Criteria**:
  - Leaflet maps display as expected.
  - Dashboard lock/unlock works correctly.
  - Onboarding tour is step-by-step interactive and matches requirements.
  - Offline access to manual PDF is confirmed.
  - Legible contrast in light/dark themes.

### Milestone 5: E2E Test Pass & Hardening (M5)
- **Scope**:
  - Wait for E2E Testing Track to publish `TEST_READY.md`.
  - Run all Tier 1-4 tests, identify and resolve any failures.
  - Execute Phase 2: Adversarial Coverage Hardening (Tier 5). Challenger analyzes codebase, generates gap report, writes adversarial tests, Worker fixes bugs, Reviewer verifies.
- **Dependencies**: M1 (E2E Test Track), M3, M4.
- **Verification Criteria**:
  - 100% pass on all E2E test cases.
  - Forensic Auditor CLEAN report.

---

## Execution Framework

For each milestone, a **sub-orchestrator** will be spawned with the designated `SCOPE.md` definition. The sub-orchestrator will:
1. Decompose the milestone scope.
2. Run the iteration loop: Explorer -> Worker -> Reviewer -> Challenger/Auditor -> Gate.
3. Verify changes with unit/integration testing.
4. Report back when done.
