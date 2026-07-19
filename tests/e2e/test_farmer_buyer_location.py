import pytest
from sqlalchemy import select
from app.models.models import Farmer, Buyer, CropBatch
from conftest import seed_verified_farmer

@pytest.mark.asyncio
async def test_exact_vs_fuzzed_coordinates(api_client, db_session):
    """F5 & F6: Verify exact coordinates for Farmer/Admin and fuzzed coordinates for Buyer/Scan."""
    # 1. Seed a verified farmer with exact coordinates
    farmer_email = "coords_farmer@e2e.test"
    exact_lat_lon = "12.971638,77.594621"
    approx_lat_lon = "12.9716,77.5946"
    
    # We will delete any existing farmer to be clean
    farmer = await seed_verified_farmer(
        db_session, 
        email=farmer_email, 
        name="Coords Farmer", 
        location=approx_lat_lon
    )
    # Update to have exact location
    farmer.exact_location = exact_lat_lon
    db_session.add(farmer)
    await db_session.commit()
    await db_session.refresh(farmer)

    # Seed a crop batch for this farmer
    crop = CropBatch(
        batch_id="batch-e2e-coords-test",
        farmer_id=farmer.id,
        crop_name="E2E Wheat",
        harvest_date="2026-07-01",
        farming_method="Organic",
        image_url="http://localhost:8000/static/wheat.jpg",
        image_file_hash="dummyhash",
        data_hash="dummyhash",
        blockchain_hash="dummyhash",
        blockchain_tx_hash="0xdummy",
        verification_status="AUTHENTIC",
        qr_url="http://localhost:8000/static/qr/batch-e2e-coords-test.png",
        quantity=200.0
    )
    db_session.add(crop)
    await db_session.commit()

    # 2. Login as the Farmer and view their profile -> should be EXACT/unfuzzed
    login_resp = await api_client.post("/api/auth/login", json={
        "email": farmer_email,
        "password": "Password@123"
    })
    assert login_resp.status_code == 200
    farmer_token = login_resp.json()["access_token"]
    
    farmer_profile_resp = await api_client.get(
        "/api/farmer/profile",
        headers={"Authorization": f"Bearer {farmer_token}"}
    )
    assert farmer_profile_resp.status_code == 200
    farmer_profile = farmer_profile_resp.json()
    assert farmer_profile["location"] == approx_lat_lon
    assert farmer_profile["exact_location"] == exact_lat_lon

    # 3. Login as Admin and view farmer profile -> should be EXACT/unfuzzed
    admin_login_resp = await api_client.post("/api/auth/admin/login", json={
        "email": "admin@agritrace.com",
        "password": "Admin@123"
    })
    assert admin_login_resp.status_code == 200
    admin_token = admin_login_resp.json()["access_token"]

    admin_profile_resp = await api_client.get(
        f"/api/admin/farmers/{farmer.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_profile_resp.status_code == 200
    admin_view = admin_profile_resp.json()
    assert admin_view["location"] == approx_lat_lon  # Admins see the exact value saved in location

    # 4. Register a Buyer, log in, search farmers -> should be FUZZED (rounded to 2 decimal places)
    buyer_email = "coords_buyer@e2e.test"
    buyer_reg_resp = await api_client.post("/api/auth/buyer/register", json={
        "name": "Coords Buyer",
        "email": buyer_email,
        "password": "Password@123",
        "phone_number": "+919876543210",
        "address": "Buyer Street",
        "security_question": "What was your childhood nickname?",
        "security_question_answer": "coordy"
    })
    assert buyer_reg_resp.status_code in (200, 201)
    buyer_token = buyer_reg_resp.json()["access_token"]

    buyer_search_resp = await api_client.get(
        "/api/buyer/farmers?search=Coords",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert buyer_search_resp.status_code == 200
    buyer_farmers = buyer_search_resp.json()
    assert len(buyer_farmers) >= 1
    
    # Find our specific seeded farmer in the list
    seeded_farmer_buyer_view = next(f for f in buyer_farmers if f["id"] == str(farmer.id))
    # Fuzzed check (12.9716 -> 12.97, 77.5946 -> 77.59)
    assert seeded_farmer_buyer_view["location"] == "12.97,77.59"
    assert seeded_farmer_buyer_view["exact_location"] == "12.97,77.59"

    # 5. Verify anonymous QR scan -> should be FUZZED
    scan_anon_resp = await api_client.get(f"/api/verify/{crop.batch_id}")
    assert scan_anon_resp.status_code == 200
    anon_scan = scan_anon_resp.json()
    assert anon_scan["farmer_location"] == "12.97,77.59"

    # 6. Verify scan as Buyer -> should be FUZZED
    scan_buyer_resp = await api_client.get(
        f"/api/verify/{crop.batch_id}",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert scan_buyer_resp.status_code == 200
    buyer_scan = scan_buyer_resp.json()
    assert buyer_scan["farmer_location"] == "12.97,77.59"

    # 7. Verify scan as Farmer/Admin -> should be EXACT/unfuzzed
    scan_farmer_resp = await api_client.get(
        f"/api/verify/{crop.batch_id}",
        headers={"Authorization": f"Bearer {farmer_token}"}
    )
    assert scan_farmer_resp.status_code == 200
    farmer_scan = scan_farmer_resp.json()
    assert farmer_scan["farmer_location"] == approx_lat_lon
