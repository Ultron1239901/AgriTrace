import sys
import os

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.path.join(os.getcwd(), "backend"))
sys.path.append(os.getcwd())

import asyncio
import uuid
from sqlalchemy import select
from app.database import SessionLocal
from app.models.models import Farmer, CropBatch, Notification
from app.services.verify_service import verify_batch
from app.utils.hashing import compute_crop_blockchain_hash

async def run_demo():
    print("==========================================================")
    print("          AgriTrace Tampering Demo Simulation             ")
    print("==========================================================")
    
    # Generate parameters
    farmer_id = uuid.uuid4()
    batch_id = f"BATCH_{uuid.uuid4().hex[:6].upper()}"
    image_hash = "valid_hash_signature"
    
    # Compute the AUTHENTIC initial signature
    blockchain_hash = compute_crop_blockchain_hash(
        batch_id=batch_id,
        crop_name="Tomato",
        harvest_date="2026-07-22",
        farming_method="Organic",
        image_hash=image_hash,
        farmer_id=str(farmer_id)
    )
    
    async with SessionLocal() as db:
        # Create a fresh verified farmer and verified crop to guarantee exact authentic vs tampered flow
        farmer = Farmer(
            id=farmer_id,
            name="Demo Security Farmer",
            email=f"security.farmer.{uuid.uuid4().hex[:4]}@agritrace.com",
            password_hash="nohash",
            location="13.0827,80.2707", # Chennai coordinates
            phone_number="+919876543210",
            verified=True,
            suspended=False
        )
        db.add(farmer)
        
        crop = CropBatch(
            id=uuid.uuid4(),
            batch_id=batch_id,
            crop_name="Tomato",
            harvest_date="2026-07-22",
            farming_method="Organic",
            image_url="/uploads/images/sample.jpg",
            image_file_hash=image_hash,
            data_hash="legacy_hash_signature",
            blockchain_hash=blockchain_hash,
            blockchain_tx_hash="0xblockchain_tx_hash",
            verification_status="VERIFIED",
            farmer_id=farmer_id,
            qr_url="http://mockqr.url",
            quantity=100.0
        )
        db.add(crop)
        await db.commit()
        
        print(f"Targeting Crop Batch: {batch_id}")
        print(f"Original Name: Tomato")
        print(f"Initial Blockchain Hash: {blockchain_hash}")
        print("----------------------------------------------------------")
        
        # 2. Scan the crop before tampering
        print("1. Scanning BEFORE tampering...")
        scan_before = await verify_batch(
            db=db,
            batch_id=batch_id,
            ip_address="127.0.0.1",
            device_type="Web Browser"
        )
        print(f"Result Status: {scan_before['status']}")
        print(f"Result Message: {scan_before['message']}")
        print("----------------------------------------------------------")
        
        # 3. Simulate Tampering (Manually changing crop name directly in SQL without rebuilding hash)
        print("2. TAMPERING: Modifying crop name in database directly...")
        # Re-fetch crop to attach to current transaction context
        stmt_crop = select(CropBatch).where(CropBatch.batch_id == batch_id)
        crop_ref = (await db.execute(stmt_crop)).scalars().first()
        crop_ref.crop_name = "Tampered Gold Tomato"
        db.add(crop_ref)
        await db.commit()
        print("Database crop_name changed to: 'Tampered Gold Tomato'.")
        print("----------------------------------------------------------")
        
        # 4. Scan the crop after tampering
        print("3. Scanning AFTER tampering...")
        scan_after = await verify_batch(
            db=db,
            batch_id=batch_id,
            ip_address="127.0.0.1",
            device_type="Web Browser"
        )
        print(f"Result Status: {scan_after['status']}")
        print(f"Result Message: {scan_after['message']}")
        print("----------------------------------------------------------")
        
        # 5. Check Farmer notifications
        stmt_notif = select(Notification).where(Notification.user_id == str(farmer_id)).order_by(Notification.created_at.desc())
        res_notif = await db.execute(stmt_notif)
        notifs = res_notif.scalars().all()
        if notifs:
            msg_clean = notifs[0].message.encode('ascii', 'ignore').decode('ascii')
            print(f"Farmer Notification Triggered: '{msg_clean}'")
            
        print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_demo())
