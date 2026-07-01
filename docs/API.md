# AGRITRACE API Documentation

Base URL: `http://localhost:8000`

## Authentication

### POST /api/auth/register
Register a new farmer account.

**Body (JSON):**
```json
{
  "name": "Rajesh Kumar",
  "email": "rajesh@farm.com",
  "password": "password123",
  "location": "Mandya, Karnataka"
}
```

**Response:** JWT token with role `farmer`

---

### POST /api/auth/login
Farmer login.

**Body (JSON):**
```json
{
  "email": "rajesh@farm.com",
  "password": "password123"
}
```

---

### POST /api/auth/admin/login
Administrator login (credentials from environment variables).

---

## Farmer APIs

All farmer endpoints require `Authorization: Bearer <token>` header.

### POST /api/farmer/crops
Add a new crop batch with image upload.

**Body (multipart/form-data):**
- `crop_name` (string)
- `harvest_date` (string, YYYY-MM-DD)
- `farming_method` (string)
- `image` (file)

**Process:**
1. Saves image to `/uploads/images/`
2. Computes SHA-256 hash from crop data + image hash
3. Stores hash on Polygon blockchain (if configured)
4. Generates QR code PNG in `/uploads/qr/`

---

### GET /api/farmer/crops
List all crop batches for the authenticated farmer.

---

### GET /api/farmer/crops/{id}
Get a specific crop batch by MongoDB ID.

---

## Admin APIs

All admin endpoints require admin JWT token.

### GET /api/admin/farmers
List all registered farmers.

### PATCH /api/admin/verify/{id}
Verify a farmer by MongoDB ID.

### GET /api/admin/crops
List all crop batches across all farmers.

### GET /api/admin/logs
List recent QR verification scan logs.

---

## Verification API

### GET /api/verify/{batch_id}
Public endpoint. Verifies crop authenticity.

**Process:**
1. Fetches crop data from MongoDB
2. Recomputes SHA-256 hash
3. Fetches hash from blockchain contract
4. Compares hashes
5. Logs scan to `qr_logs` collection

**Response:**
```json
{
  "status": "AUTHENTIC",
  "batch_id": "AGR-ABC123DEF456",
  "crop_name": "Organic Rice",
  "harvest_date": "2025-06-01",
  "farming_method": "Organic",
  "image_url": "/uploads/images/abc.jpg",
  "farmer_name": "Rajesh Kumar",
  "farmer_location": "Mandya, Karnataka",
  "data_hash": "...",
  "blockchain_hash": "...",
  "message": "..."
}
```

Status is either `AUTHENTIC` or `TAMPERED`.

---

## QR API

### GET /api/qr/{batch_id}
Returns QR code PNG image for the given batch ID.

---

## Health Check

### GET /api/health
Returns service health status.

---

## Buyer APIs

All buyer endpoints require `Authorization: Bearer <token>` header with role `buyer`.

### POST /api/auth/buyer/register
Register a new buyer account.

### POST /api/auth/buyer/login
Buyer login.

### GET /api/buyer/profile
Get authenticated buyer profile details.

### PUT /api/buyer/profile
Update buyer name.

### GET /api/buyer/farmers
List all verified farmers.

### POST /api/buyer/favourites/{farmer_id}
Toggle bookmark for a farmer.

### GET /api/buyer/favourites
List all bookmarked farmers.

### POST /api/buyer/purchase-requests
Send a crop purchase request.

**Body (JSON):**
```json
{
  "batch_id": "AGR-ABC123DEF456",
  "message": "Inquiry about purchasing 50kg."
}
```

### GET /api/buyer/purchase-requests
List sent purchase requests and status.

### GET /api/buyer/scans
List previous QR codes scanned by the authenticated buyer.

---

## Extra Farmer APIs

### GET /api/farmer/profile
Get farmer profile.

### PUT /api/farmer/profile
Update farmer name or location.

### PUT /api/farmer/crops/{id}
Edit crop details and recompute hash (re-stores on blockchain if configured).

### DELETE /api/farmer/crops/{id}
Delete crop batch and delete its image & QR code from local disk storage.

### GET /api/farmer/logs
List verification logs for crops belonging to this farmer.

### GET /api/farmer/purchase-requests
List incoming buyer purchase requests.

### PATCH /api/farmer/purchase-requests/{id}
Accept or reject an incoming purchase request.

**Body (JSON):**
```json
{
  "status": "ACCEPTED" // or "REJECTED"
}
```

### GET /api/farmer/notifications
List notifications (unread and read).

### PATCH /api/farmer/notifications/{id}/read
Mark notification as read.

### POST /api/farmer/ai-assistant
Crop disease diagnosis advisor. If Gemini is configured, retrieves dynamic responses; otherwise runs rule-based classification.

**Body (JSON):**
```json
{
  "symptoms": "Leaf spots with brown centers",
  "crop_type": "rice"
}
```

**Response (JSON):**
```json
{
  "possible_disease": "Rice Leaf Blast",
  "reason": "...",
  "treatment": "...",
  "prevention": "...",
  "organic_treatment": "...",
  "chemical_treatment": "...",
  "confidence_level": 0.92
}
```

---

## Extra Admin APIs

### PATCH /api/admin/reject/{farmer_id}
Reject farmer verification status.

### GET /api/admin/buyers
List all registered buyers.

### DELETE /api/admin/farmers/{farmer_id}
Delete a farmer, their crops, and all files from disk.

### DELETE /api/admin/buyers/{buyer_id}
Delete a buyer profile.

### GET /api/admin/stats
Get dashboard analytics stats (total counts, scan distributions).

