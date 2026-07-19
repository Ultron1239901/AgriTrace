import pytest
from sqlalchemy import select
from app.models.models import Farmer, Buyer, OTPStore
from conftest import seed_verified_farmer, get_otp_from_db

@pytest.mark.asyncio
async def test_db_connection_and_cleanup(db_session):
    """Test that db_session fixture is working and we can query the database."""
    # Count farmers before seeding
    result_before = await db_session.execute(select(Farmer).where(Farmer.email.like("%@e2etest.com")))
    farmers_before = result_before.scalars().all()
    assert len(farmers_before) == 0

    # Seed a verified farmer
    test_email = "test_farmer_auth@e2etest.com"
    farmer = await seed_verified_farmer(db_session, test_email, "Test Auth Farmer")
    assert farmer.id is not None
    assert farmer.email == test_email

    # Count farmers after seeding
    result_after = await db_session.execute(select(Farmer).where(Farmer.email.like("%@e2etest.com")))
    farmers_after = result_after.scalars().all()
    assert len(farmers_after) == 1


@pytest.mark.asyncio
async def test_get_otp_from_db(db_session):
    """Test retrieving OTP helper from the database."""
    test_email = "test_otp@e2etest.com"
    # Insert a dummy OTP into the store
    import datetime
    otp_record = OTPStore(
        email=test_email,
        otp="123456",
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    )
    db_session.add(otp_record)
    await db_session.commit()

    # Query using the helper
    otp = await get_otp_from_db(db_session, test_email)
    assert otp == "123456"


@pytest.mark.asyncio
async def test_farmer_registration_validation(api_client):
    """F1 & F4: Verify registration input validation and coordinate bounds check for Farmers."""
    # Valid payload base template
    valid_payload = {
        "name": "E2E Farmer F1",
        "email": "farmer_f1@e2etest.com",
        "password": "Password@123",
        "location": "12.97,77.59",
        "phone_number": "+919876543210",
        "address": "Test Farm Address",
        "security_question": "What was your childhood nickname?",
        "security_question_answer": "farmernick",
        "soil_type": "Clay",
        "exact_location": "12.9716,77.5946"
    }

    # 1. Test missing required fields (empty strings)
    payload_missing = valid_payload.copy()
    payload_missing["phone_number"] = ""
    response = await api_client.post("/api/auth/register", json=payload_missing)
    assert response.status_code in (400, 422)

    # 2. Test invalid security question selection (must be in predefined questions)
    payload_bad_question = valid_payload.copy()
    payload_bad_question["security_question"] = "What is your favorite color?"
    response = await api_client.post("/api/auth/register", json=payload_bad_question)
    assert response.status_code == 400
    assert "security question" in response.json().get("detail", "").lower()

    # 3. Test coordinate bounds (Latitude [-90, 90], Longitude [-180, 180])
    # Case A: Latitude out of bounds
    payload_bad_lat = valid_payload.copy()
    payload_bad_lat["exact_location"] = "95.0,77.5946"
    response = await api_client.post("/api/auth/register", json=payload_bad_lat)
    assert response.status_code == 400
    assert response.json().get("detail") == "wrong location"

    # Case B: Longitude out of bounds
    payload_bad_lon = valid_payload.copy()
    payload_bad_lon["exact_location"] = "12.9716,181.0"
    response = await api_client.post("/api/auth/register", json=payload_bad_lon)
    assert response.status_code == 400
    assert response.json().get("detail") == "wrong location"

    # Case C: Non-numeric coordinate format
    payload_bad_format = valid_payload.copy()
    payload_bad_format["exact_location"] = "lat,lon"
    response = await api_client.post("/api/auth/register", json=payload_bad_format)
    assert response.status_code == 400
    assert response.json().get("detail") == "wrong location"

    # 4. Successful registration
    response = await api_client.post("/api/auth/register", json=valid_payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "farmer"


@pytest.mark.asyncio
async def test_buyer_registration_validation(api_client):
    """F1: Verify registration input validation for Buyers."""
    valid_payload = {
        "name": "E2E Buyer F1",
        "email": "buyer_f1@e2etest.com",
        "password": "Password@123",
        "phone_number": "+919876543211",
        "address": "Test Buyer Address",
        "security_question": "What was your childhood nickname?",
        "security_question_answer": "buyernick"
    }

    # 1. Test missing required fields
    payload_missing = valid_payload.copy()
    payload_missing["address"] = ""
    response = await api_client.post("/api/auth/buyer/register", json=payload_missing)
    assert response.status_code in (400, 422)

    # 2. Test invalid security question
    payload_bad_question = valid_payload.copy()
    payload_bad_question["security_question"] = "What is your favorite food?"
    response = await api_client.post("/api/auth/buyer/register", json=payload_bad_question)
    assert response.status_code == 400

    # 3. Successful registration
    response = await api_client.post("/api/auth/buyer/register", json=valid_payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "buyer"


@pytest.mark.asyncio
async def test_forgot_password_email_otp_flow(api_client, db_session):
    """F2: Verify forgot password recovery primary path using email OTP reset."""
    # 1. Register a user
    email = "forgot_otp@e2etest.com"
    register_payload = {
        "name": "Forgot OTP User",
        "email": email,
        "password": "OldPassword@123",
        "location": "12.97,77.59",
        "phone_number": "+919876543212",
        "address": "Test Address",
        "security_question": "What was your childhood nickname?",
        "security_question_answer": "nick",
        "soil_type": "Clay"
    }
    reg_response = await api_client.post("/api/auth/register", json=register_payload)
    assert reg_response.status_code in (200, 201)

    # 2. Initiate forgot password
    init_response = await api_client.post("/api/auth/forgot-password/initiate", json={"email": email})
    assert init_response.status_code == 200
    assert init_response.json().get("security_question") == "What was your childhood nickname?"

    # 3. Get OTP directly from database to bypass email
    otp = await get_otp_from_db(db_session, email)
    assert otp is not None
    assert len(otp) == 6

    # 4. Reset password using OTP
    new_password = "NewPassword@123"
    reset_payload = {
        "email": email,
        "otp": otp,
        "new_password": new_password
    }
    reset_response = await api_client.post("/api/auth/forgot-password/reset-otp", json=reset_payload)
    assert reset_response.status_code == 200
    assert "success" in reset_response.json().get("message", "").lower() or "updated" in reset_response.json().get("message", "").lower()

    # 5. Attempt login with new password
    login_response = await api_client.post("/api/auth/login", json={"email": email, "password": new_password})
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


@pytest.mark.asyncio
async def test_forgot_password_security_question_flow(api_client):
    """F3: Verify forgot password recovery secondary path using security question challenge."""
    # 1. Register a user
    email = "forgot_q@e2etest.com"
    register_payload = {
        "name": "Forgot Question User",
        "email": email,
        "password": "OldPassword@123",
        "location": "12.97,77.59",
        "phone_number": "+919876543213",
        "address": "Test Address",
        "security_question": "What was your childhood nickname?",
        "security_question_answer": "MySuperSecretAnswer",
        "soil_type": "Clay"
    }
    reg_response = await api_client.post("/api/auth/register", json=register_payload)
    assert reg_response.status_code in (200, 201)

    # 2. Initiate recovery
    init_response = await api_client.post("/api/auth/forgot-password/initiate", json={"email": email})
    assert init_response.status_code == 200

    # 3. Try resetting password with incorrect security answer
    bad_reset_payload = {
        "email": email,
        "security_question_answer": "WrongAnswer",
        "new_password": "NewPassword@123"
    }
    bad_response = await api_client.post("/api/auth/forgot-password/reset-question", json=bad_reset_payload)
    assert bad_response.status_code == 400

    # 4. Reset password with correct security answer
    good_reset_payload = {
        "email": email,
        "security_question_answer": "MySuperSecretAnswer",
        "new_password": "NewPassword@123"
    }
    good_response = await api_client.post("/api/auth/forgot-password/reset-question", json=good_reset_payload)
    assert good_response.status_code == 200

    # 5. Attempt login with new password
    login_response = await api_client.post("/api/auth/login", json={"email": email, "password": "NewPassword@123"})
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
