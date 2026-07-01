# AGRITRACE

**Blockchain-Based QR Verification System for Agricultural Supply Chains**

AGRITRACE enables farmers to register crop batches, generate cryptographic hashes stored on the Polygon blockchain, and issue QR codes that consumers can scan to verify produce authenticity.

---

## Features

- **Farmer Portal** — Register, upload crop batches with images, generate QR codes
- **Admin Panel** — Verify farmers, monitor batches, view verification logs
- **Consumer Verification** — Scan QR or enter batch ID to verify AUTHENTIC / TAMPERED status
- **Blockchain Integration** — SHA-256 hashes stored on Polygon Amoy via Solidity smart contract
- **Multilingual UI** — English, Hindi (हिंदी), and Kannada (ಕನ್ನಡ)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Vite, Tailwind CSS, React Router, Axios, i18next |
| Backend | FastAPI, Pydantic, Uvicorn, Motor (async MongoDB) |
| Database | MongoDB Atlas |
| Blockchain | Solidity, Polygon Amoy, Web3.py |
| Security | SHA-256 hashing, JWT authentication |
| QR | qrcode library, html5-qrcode scanner |

---

## Project Structure

```
Agriculture project/
├── frontend/          # React + Vite application
├── backend/           # FastAPI REST API
├── blockchain/        # Solidity contract, ABI, deploy script
├── uploads/
│   ├── images/        # Crop image uploads
│   └── qr/            # Generated QR code PNGs
├── docs/              # API documentation
├── .env.example       # Environment variable template
└── README.md
```

---

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **MongoDB Atlas** account (connection string provided)
- **Polygon Amoy** testnet wallet (optional, for blockchain storage)

---

## Installation

### 1. Clone and enter project

```bash
cd "Agriculture project"
```

### 2. Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Copy environment file (already configured with MongoDB Atlas):

```bash
# backend/.env is pre-configured — edit if needed
```

### 3. Frontend setup

```bash
cd ../frontend
npm install
```

### 4. Blockchain setup (optional)

Deploy the CropTrace smart contract to Polygon Amoy:

```bash
cd ../blockchain
pip install -r requirements.txt

# Set in backend/.env:
# WEB3_PROVIDER=https://rpc-amoy.polygon.technology
# DEPLOYER_PRIVATE_KEY=your_wallet_private_key

python deploy.py
# Copy the printed CONTRACT_ADDRESS to backend/.env
```

---

## Environment Variables

See `.env.example` for all variables. Key settings in `backend/.env`:

| Variable | Description |
|----------|-------------|
| `MONGO_URL` | MongoDB Atlas connection string |
| `DATABASE_NAME` | Database name (`agritrust_db`) |
| `JWT_SECRET` | Secret key for JWT tokens |
| `JWT_ALGORITHM` | JWT algorithm (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (60) |
| `ADMIN_EMAIL` | Admin login email |
| `ADMIN_PASSWORD` | Admin login password |
| `WEB3_PROVIDER` | Polygon Amoy RPC URL |
| `CONTRACT_ADDRESS` | Deployed CropTrace contract address |
| `DEPLOYER_PRIVATE_KEY` | Wallet private key for storing hashes |
| `UPLOAD_DIR` | Path to uploads folder (`../uploads`) |
| `CORS_ORIGINS` | Allowed frontend origins |

---

## Run Instructions

### Start Backend (Terminal 1)

```bash
cd backend
venv\Scripts\activate    # Windows
python run.py
```

API runs at: **http://localhost:8000**  
API docs: **http://localhost:8000/docs**

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

App runs at: **http://localhost:5173**

---

## Default Credentials

### Admin
- **Email:** `admin@agritrace.com`
- **Password:** `Admin@123`

### Farmer
Register a new account at `/farmer/register`. Admin must verify the farmer before crop batches can be added.

---

## User Workflows

### Farmer
1. Register at `/farmer/register`
2. Wait for admin verification
3. Login and add crop batch with image
4. System generates hash, stores on blockchain, creates QR code
5. View and download QR from "My Crops"

### Admin
1. Login at `/admin/login`
2. Verify pending farmers
3. Monitor all crop batches
4. Review verification scan logs

### Consumer
1. Visit `/scan` or scan physical QR code
2. View verification result: **AUTHENTIC** or **TAMPERED**
3. See full crop and farmer details

---

## API Documentation

Full API reference: [docs/API.md](docs/API.md)

Interactive docs available at `http://localhost:8000/docs` when backend is running.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Farmer registration |
| POST | `/api/auth/login` | Farmer login |
| POST | `/api/auth/admin/login` | Admin login |
| POST | `/api/farmer/crops` | Add crop batch |
| GET | `/api/farmer/crops` | List farmer crops |
| GET | `/api/admin/farmers` | List all farmers |
| PATCH | `/api/admin/verify/{id}` | Verify farmer |
| GET | `/api/admin/crops` | List all batches |
| GET | `/api/verify/{batch_id}` | Verify authenticity |
| GET | `/api/qr/{batch_id}` | Get QR code PNG |

---

## Hashing Logic

SHA-256 hash computed from:

```
crop_name | harvest_date | farming_method | image_file_hash
```

The resulting `data_hash` is stored in MongoDB and on the Polygon blockchain.

---

## MongoDB Collections

- **farmers** — Farmer accounts with verification status
- **crop_batches** — Crop data, hashes, blockchain TX, image URLs
- **qr_logs** — Verification scan logs with status and IP

---

## License

Academic project — AGRITRACE © 2025
