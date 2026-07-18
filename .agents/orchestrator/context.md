# Context - AgriTrace Enhancements

## Core Tech Stack
- **Frontend**: React + Vite + Tailwind CSS, routing via React Router.
- **Backend**: FastAPI with async SQLAlchemy, communicating with PostgreSQL.
- **Database**: PostgreSQL (connection url configured in `.env`).
- **Integrity Mode**: development.

## DB Models Reference (`backend/app/models/models.py`)
- `Farmer`: table `farmers`. Has name, email, password_hash, location, phone_number, address, verified, status, created_at, exact_location, etc.
- `Buyer`: table `buyers`. Has name, email, password_hash, phone_number, address, location, suspended, status, created_at.
- `OTPStore`: table `otps`. Stores email, otp, expires_at.

## Workspace Directories
- Working directory: `d:\Agriculture project`
- Metadata directory: `d:\Agriculture project\.agents\orchestrator`
- Backend application: `d:\Agriculture project\backend`
- Frontend application: `d:\Agriculture project\frontend`
