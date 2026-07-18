# Plan - AgriTrace Enhancements

## Project Plan
We will use the **Project Pattern** to implement the requested enhancements for AgriTrace, executing parallel E2E Testing and Implementation tracks.

### Track 1: E2E Testing Track
The E2E Testing Track will design a comprehensive, opaque-box test suite independent of the implementation, producing a `TEST_READY.md` file. It will cover:
- Tier 1: Feature Coverage (>= 5 cases per feature)
- Tier 2: Boundary & Corner Cases (>= 5 cases per feature)
- Tier 3: Cross-Feature Combinations (pairwise coverage)
- Tier 4: Real-World Application Scenarios (>= 5 scenarios)

### Track 2: Implementation Track
The Implementation Track will build the features across 5 sequential/parallel milestones:
1. **Milestone 1 (Backend Auth)**: Registration expansion database schemas, security question setup, forgot password recovery (OTP and security questions).
2. **Milestone 2 (Backend Location)**: Coordinates validation with "wrong location" error, and role-based fuzzed location coordinates for buyers.
3. **Milestone 3 (Frontend Auth UI)**: Phone/address/security questions registration forms, and Forgot Password recovery flow.
4. **Milestone 5 (Frontend Map widget and accessibility)**: Leaflet/OpenStreetMap coordinates mapping, role-based exact/fuzzed location displays, theme-based accessibility contrast check.
5. **Milestone 6 (Frontend Walkthrough, Terms Modal & Guidelines PDF)**: Pop-up guidelines manual modal locking dashboard, About page, static PDF in assets, and sidebar onboarding tour.

Wait, we renamed the last ones to simplify. Let's check the milestone mapping in `PROJECT.md` to keep it consistent.

## Verification & Validation
- **Phase 1**: Pass 100% of the E2E test suite (Tiers 1-4).
- **Phase 2**: Adversarial Coverage Hardening (Tier 5) - Challenger runs coverages, exposes gaps, worker patches until zero gaps.
- **Forensic Auditing**: Every iteration is audited for integrity.
