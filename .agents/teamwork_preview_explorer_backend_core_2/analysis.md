# AgriTrace Backend Core Milestone Analysis Report

## Executive Summary
This analysis outlines the necessary design and code changes required to implement security questions, password recovery endpoints, phone/address requirements during registration, latitude/longitude coordinate validation, and location fuzzing for buyers across the AgriTrace backend.

---

## 1. Database Model Updates (`backend/app/models/models.py`)

### Target Location
- `Farmer` class: `backend/app/models/models.py` (around line 28)
- `Buyer` class: `backend/app/models/models.py` (around line 55)

### Proposed Changes
To store the security question and its corresponding answer, we need to add columns to both `Farmer` and `Buyer` tables. 

```python
# In backend/app/models/models.py

# Inside Farmer class:
security_question = Column(String, nullable=True)
security_question_answer = Column(String, nullable=True)

# Inside Buyer class:
security_question = Column(String, nullable=True)
security_question_answer = Column(String, nullable=True)
```

**Design Recommendation**: 
Using `nullable=True` prevents migration failures on databases with existing user records. However, new registrations must enforce these fields. Storing the security question answer as a lowercase, stripped, and hashed string is highly recommended for security.

---

## 2. Pydantic Schema Updates (`backend/app/schemas/schemas.py`)

### Target Location
- `FarmerRegister` Pydantic model (lines 6-17)
- `BuyerRegister` Pydantic model (lines 106-110)

### Proposed Changes
1. **Require Phone and Address**: Add `phone_number` and `address` fields using Pydantic's `Field(..., min_length=1)` to ensure they are mandatory and cannot be empty strings.
2. **Security Question Fields**: Add `security_question` and `security_question_answer` fields, also validated to prevent empty inputs.

```python
# Proposed Pydantic Model Changes in backend/app/schemas/schemas.py

class FarmerRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    location: str = Field(..., min_length=2, max_length=200)
    soil_type: str = Field(..., min_length=2)
    phone_number: str = Field(..., min_length=1)  # Required & non-empty
    address: str = Field(..., min_length=1)       # Required & non-empty
    security_question: str = Field(..., min_length=1)
    security_question_answer: str = Field(..., min_length=1)
    land_document: Optional[str] = None
    exact_location: Optional[str] = None
    water_availability: str = Field("Yes")
    previous_crops: Optional[str] = None
    loan_amount: Optional[float] = 0.0


class BuyerRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone_number: str = Field(..., min_length=1)  # Required & non-empty
    address: str = Field(..., min_length=1)       # Required & non-empty
    security_question: str = Field(..., min_length=1)
    security_question_answer: str = Field(..., min_length=1)
```

---

## 3. Registration Endpoint Updates (`backend/app/routers/auth.py`)

### Predefined Security Questions
For compliance and consistency, we define a list of valid security questions:
```python
PREDEFINED_QUESTIONS = [
    "What was the name of your first pet?",
    "What is your mother's maiden name?",
    "In which city were you born?"
]
```

### Proposed Endpoint Changes
We must update `register_farmer` and `register_buyer` to validate that the provided security question is one of the predefined options and persist the phone, address, and security question values into the database.

```python
# In backend/app/routers/auth.py

# Inside register_farmer:
@router.post("/register", response_model=TokenResponse)
async def register_farmer(data: FarmerRegister, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(Farmer).where(Farmer.email == data.email.lower()))).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if data.security_question not in PREDEFINED_QUESTIONS:
        raise HTTPException(status_code=400, detail="Invalid security question")

    new_farmer = Farmer(
        name=data.name,
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        location=data.location,
        phone_number=data.phone_number,
        address=data.address,
        security_question=data.security_question,
        # Store a case-insensitive hashed answer for privacy and security
        security_question_answer=hash_password(data.security_question_answer.strip().lower()),
        verified=False,
        soil_type=data.soil_type,
        land_document=data.land_document,
        exact_location=data.exact_location,
        water_availability=data.water_availability,
        previous_crops=data.previous_crops,
        loan_amount=data.loan_amount
    )
    db.add(new_farmer)
    await db.commit()
    # ... rest of token creation ...

# Inside register_buyer:
@router.post("/buyer/register", response_model=TokenResponse)
async def register_buyer(data: BuyerRegister, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(Buyer).where(Buyer.email == data.email.lower()))).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if data.security_question not in PREDEFINED_QUESTIONS:
        raise HTTPException(status_code=400, detail="Invalid security question")

    new_buyer = Buyer(
        name=data.name,
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        phone_number=data.phone_number,
        address=data.address,
        security_question=data.security_question,
        security_question_answer=hash_password(data.security_question_answer.strip().lower())
    )
    db.add(new_buyer)
    await db.commit()
    # ... rest of token creation ...
```

---

## 4. Forgot Password Recovery Endpoints (`backend/app/routers/auth.py`)

### Existing OTP Logic Review
The backend stores OTP verification codes in an `OTPStore` model mapping `email` (PK) to `otp` and `expires_at` (10 minutes lifetime).
- `/send-otp`: generates and emails code to any registered user.
- `/verify-otp`: checks OTP and logs user in directly via JWT token.

### Proposed Password Recovery Endpoints
We implement three recovery endpoints in `backend/app/routers/auth.py`:
1. `/forgot-password/initiate`: Verifies if the email exists, triggers an OTP via email, and returns the user's registered security question.
2. `/forgot-password/reset-otp`: Resets the password if a valid OTP is supplied.
3. `/forgot-password/reset-question`: Resets the password if the correct security question answer is supplied.

#### Additional Pydantic Schemas to add to `backend/app/schemas/schemas.py`:
```python
class InitiateResetRequest(BaseModel):
    email: EmailStr

class InitiateResetResponse(BaseModel):
    security_question: str
    message: str

class ResetOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6)

class ResetQuestionRequest(BaseModel):
    email: EmailStr
    security_question_answer: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)
```

#### Router implementation in `backend/app/routers/auth.py`:
```python
@router.post("/forgot-password/initiate", response_model=InitiateResetResponse)
async def initiate_password_reset(data: InitiateResetRequest, db: AsyncSession = Depends(get_db)):
    email_lower = data.email.lower()
    farmer = (await db.execute(select(Farmer).where(Farmer.email == email_lower))).scalars().first()
    buyer = (await db.execute(select(Buyer).where(Buyer.email == email_lower))).scalars().first()
    
    user = farmer or buyer
    if not user:
        raise HTTPException(status_code=404, detail="Email address not registered")

    # Generate and send OTP using existing OTPStore
    import random
    otp = f"{random.randint(100000, 999999)}"
    from app.models.models import OTPStore
    from datetime import timedelta

    otp_record = await db.get(OTPStore, email_lower)
    if otp_record:
        otp_record.otp = otp
        otp_record.expires_at = datetime.utcnow() + timedelta(minutes=10)
    else:
        otp_record = OTPStore(email=email_lower, otp=otp, expires_at=datetime.utcnow() + timedelta(minutes=10))
        db.add(otp_record)
    await db.commit()

    # Dispatch email
    try:
        from app.services.email_service import send_otp_email
        send_otp_email(email_lower, user.name, otp)
    except Exception as email_err:
        pass

    return InitiateResetResponse(
        security_question=getattr(user, "security_question", "No security question set"),
        message="OTP sent to email. You can reset using either OTP or security question."
    )


@router.post("/forgot-password/reset-otp", response_model=MessageResponse)
async def reset_password_via_otp(data: ResetOTPRequest, db: AsyncSession = Depends(get_db)):
    email_lower = data.email.lower()
    from app.models.models import OTPStore
    otp_record = await db.get(OTPStore, email_lower)
    if not otp_record or otp_record.otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    if otp_record.expires_at.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP code has expired")

    farmer = (await db.execute(select(Farmer).where(Farmer.email == email_lower))).scalars().first()
    buyer = (await db.execute(select(Buyer).where(Buyer.email == email_lower))).scalars().first()
    user = farmer or buyer
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(data.new_password)
    await db.delete(otp_record)
    await db.commit()
    return MessageResponse(message="Password reset successfully.")


@router.post("/forgot-password/reset-question", response_model=MessageResponse)
async def reset_password_via_question(data: ResetQuestionRequest, db: AsyncSession = Depends(get_db)):
    email_lower = data.email.lower()
    farmer = (await db.execute(select(Farmer).where(Farmer.email == email_lower))).scalars().first()
    buyer = (await db.execute(select(Buyer).where(Buyer.email == email_lower))).scalars().first()
    user = farmer or buyer
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stored_answer_hash = getattr(user, "security_question_answer", None)
    if not stored_answer_hash:
        raise HTTPException(status_code=400, detail="Security question not configured for this account")

    if not verify_password(data.security_question_answer.strip().lower(), stored_answer_hash):
        raise HTTPException(status_code=400, detail="Incorrect answer to security question")

    user.password_hash = hash_password(data.new_password)
    await db.commit()
    return MessageResponse(message="Password reset successfully.")
```

---

## 5. Farmer Coordinate Validation (`backend/app/routers/farmer.py` and `auth.py`)

### Location and Range Check
Farmer exact coordinates are stored in the database string field `exact_location`. They must follow the format `"latitude,longitude"`.
- **Latitude Range**: `[-90, 90]`
- **Longitude Range**: `[-180, 180]`
- If invalid, return HTTP `400` status with the message `"wrong location"`.

### Proposed Implementation Helper
Add a helper in `backend/app/utils/helpers.py`:
```python
def validate_coordinates(exact_location_str: Optional[str]) -> None:
    if not exact_location_str:
        return
    try:
        parts = exact_location_str.split(",")
        if len(parts) != 2:
            raise ValueError()
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=400, detail="wrong location")
```

### Call Locations
1. **In Registration (`backend/app/routers/auth.py`)**:
   Add coordinate validation inside `register_farmer` prior to database insertion:
   ```python
   # Inside register_farmer:
   from app.utils.helpers import validate_coordinates
   validate_coordinates(data.exact_location)
   ```
2. **In Update Profile (`backend/app/routers/farmer.py`)**:
   Add coordinate validation inside `update_profile` around line 102:
   ```python
   # Inside update_profile:
   if data.exact_location is not None:
       from app.utils.helpers import validate_coordinates
       validate_coordinates(data.exact_location)
       farmer.exact_location = data.exact_location
   ```

---

## 6. Buyer Location Fuzzing (`backend/app/routers/buyer.py` and `verify.py`)

### Objective
Coordinates (`exact_location`) must be fuzzed/approximated for Buyers and general public (QR scanners), but exact coordinates are returned to Farmers/Admins.

### Proposed Fuzzing Helper
Add this to `backend/app/utils/helpers.py`:
```python
def fuzz_coordinates(exact_location_str: Optional[str]) -> Optional[str]:
    if not exact_location_str:
        return None
    try:
        parts = exact_location_str.split(",")
        if len(parts) != 2:
            return exact_location_str
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        # Rounding to 2 decimal places keeps accuracy within ~1.1km (standard fuzzing approach)
        return f"{round(lat, 2)},{round(lon, 2)}"
    except ValueError:
        return exact_location_str
```

### Schema Changes (`backend/app/schemas/schemas.py`)
Add `exact_location: Optional[str] = None` to `CropResponse` and `VerificationResponse` schemas.

### Route Changes
1. **Buyer Crops Route (`backend/app/routers/buyer.py` - line 100)**:
   In `get_farmer_crops_for_buyer`, retrieve the farmer's coordinates, apply fuzzing, and populate the `exact_location` in the returned `CropResponse`:
   ```python
   from app.utils.helpers import fuzz_coordinates
   fuzzed_coords = fuzz_coordinates(farmer.exact_location)
   # Return CropResponse using exact_location=fuzzed_coords
   ```

2. **Verification Logic (`backend/app/services/verify_service.py` and `backend/app/routers/verify.py`)**:
   Modify `verify_batch` to accept a `requester_role` parameter and return the appropriate coordinates:
   ```python
   # In backend/app/services/verify_service.py
   async def verify_batch(
       db: AsyncSession,
       batch_id: str,
       ip_address: str,
       buyer_id: str | None = None,
       device_type: str = "Unknown",
       requester_role: str | None = None  # New parameter
   ) -> dict:
       # ...
       coords = farmer.exact_location if farmer else None
       if requester_role not in ["farmer", "admin"]:
           from app.utils.helpers import fuzz_coordinates
           coords = fuzz_coordinates(coords)
           
       return {
           # ...
           "exact_location": coords
       }
   ```
   Modify `verify_crop` route in `backend/app/routers/verify.py` and `log_buyer_scan` route in `backend/app/routers/buyer.py` to pass the token's decoded role (`requester_role`) to `verify_batch`.
