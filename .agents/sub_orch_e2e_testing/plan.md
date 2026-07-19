# Scope: E2E Testing Track

## Architecture
The E2E test suite operates as an opaque-box verification layer. It will:
- Run independently of the application components.
- Interact with the backend API or frontend GUI.
- Be structured in a clean, modular format.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Test Infra Setup | Choose test runner, design directory layout, establish mock/test database helpers if needed, write `TEST_INFRA.md`. | None | DONE (Conv: 194e449b-e68b-46b1-a2d8-350206c7bcd5) |
| 2 | Tier 1 Features | Implement Feature Coverage tests (happy path, >=5 per feature). | M1 | PLANNED |
| 3 | Tier 2 Boundaries | Implement Boundary & Corner case tests (limits, errors, invalid inputs, >=5 per feature). | M1 | PLANNED |
| 4 | Tier 3 Combinations | Implement Cross-Feature Interaction tests (pairwise coverage). | M1 | PLANNED |
| 5 | Tier 4 Real-World | Implement Real-World Application scenarios (>=5 complex user workflows). | M1 | PLANNED |
| 6 | Validation & Test | Run and validate test suite correctness. Check positive/negative behaviors. | M2, M3, M4, M5 | PLANNED |
| 7 | Publish TEST_READY | Write and publish `TEST_READY.md` at the project root directory. | M6 | PLANNED |

## Interface Contracts
The test suite will exercise the interfaces defined in `PROJECT.md`:
- `POST /api/auth/forgot-password/initiate`
- `POST /api/auth/forgot-password/reset-otp`
- `POST /api/auth/forgot-password/reset-question`
- Farmer registration input validation (phone, address, security questions)
- Farmer exact coordinate boundaries map endpoint validation
- Buyer/admin view filtering validation
- Registration modal and interactive walkthrough UI behaviors (using Playwright or backend mocks)
