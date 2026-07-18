# Original User Request

## Initial Request — 2026-07-18T09:04:35Z

Implement enhanced registration fields (phone, address, security questions), multi-factor forgot-password recovery (email OTP & security question challenge), land boundary coordinates mapping using Leaflet/OpenStreetMap with role-based approximation controls (farmer/admin exact, buyer fuzzed), first-time registration guideline modal + manual PDF, and interactive onboarding tour for AgriTrace.

Working directory: d:\Agriculture project
Integrity mode: development

## Requirements

### R1. Registration & Auth Recovery Enhancements
- Expand user registration schemas, databases, and forms (both Farmer and Buyer) to require:
  - Phone number
  - Physical address
  - Security question selection (choose from at least 3 pre-defined questions)
  - Security question answer
- Redesign the "Forgot Password" portal to support a dual recovery path:
  - Primary path: Send email-based OTP, verify OTP, then allow password reset.
  - Secondary path ("Try another way"): Present the user's security question, check their answer (case-insensitive), and allow password reset if matching.

### R2. Coordinates Verification & Role-Based Land Boundaries Map
- Farmer coordinates validation: Profile location coordinates (Latitude, Longitude) must be validated. If invalid format, out of boundary ranges, or un-parseable, return HTTP 400 with the error message "wrong location".
- Map viewer dashboard widget:
  - Add a "View Map" button at the top of the Farmer's portal dashboard. Clicking it renders an interactive map showing their exact coordinate boundaries.
  - Admin view: Allows administrators in the fraud monitoring section to see the exact coordinate boundaries of the farmer.
  - Buyer view: Restricted to fuzzed/approximate crop coordinates (district/village level only; exact latitude/longitude must not be exposed to the buyer browser client).

### R3. Onboarding Tour, Terms Modal & Guidelines Manual
- Register/First-login interceptor: First-time registrants must be presented with a modern pop-up Guideline Manual detailing system operations, AI agents, Telegram ID configuration instructions, suspension rules, analytics, and fraud monitor.
- Access to dashboard is locked until the user checks the Terms & Conditions checkbox and clicks "OK".
- PDF documentation: Compile the Guideline Manual content into a static PDF file stored in the project assets, and redesign the "About" page to render the manual text beautifully.
- Interactive onboarding tour: Implement a step-by-step guided layout tour (with Next, Back, Skip, Finish options) explaining key sidebar menu panels to newly registered farmers or buyers.
- Theme accessibility: Ensure all newly added UI elements (registration inputs, forgot password screens, Leaflet map widget, terms modal, guideline text, and tour components) have fully optimized contrast and legible text visible in both the light and dark themes of the app.

## Acceptance Criteria

### Authentication & Recovery Compliance
- [ ] User registrations reject empty phone number, address, or security questions.
- [ ] Password reset is successful via both OTP email validation and security question answers.

### Geospatial Boundary Constraints
- [ ] Profile coordinates reject invalid inputs (e.g. invalid text or out of range) with "wrong location" error.
- [ ] Exact coordinate details are filtered from buyer API responses, but fully visible to farmers and administrators.

### User Experience & Guidelines Interceptor
- [ ] First-time registered users must complete terms validation before entering portals.
- [ ] Interactive walkthrough tour functions correctly with Next, Back, and Skip actions.
- [ ] Guideline manual PDF is generated and accessible offline.
- [ ] All text elements in new forms, maps, modals, and tours remain highly legible under both light and dark modes.
