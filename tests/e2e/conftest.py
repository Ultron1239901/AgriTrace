import sys
import os
import asyncio
from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, delete, text

# Add backend directory to Python path
backend_path = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_path))

# Make sure we can import from app
from app.config import get_settings
from app.models.models import Base, Farmer, Buyer, OTPStore, CropBatch, PurchaseRequest, VerificationLog, AIFraudReport, VisionAnalysis

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def db_engine():
    """Create database engine using credentials from backend settings."""
    settings = get_settings()
    db_url = settings.database_url
    # Ensure the URL starts with postgresql+asyncpg for SQLAlchemy async compatibility
    if "asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(db_url, echo=False)
    
    # Run automatic test database migrations to ensure all columns from latest models exist
    async with engine.begin() as conn:
        # Add new columns to farmers
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS soil_type VARCHAR;"))
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS land_document VARCHAR;"))
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS exact_location VARCHAR;"))
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS water_availability VARCHAR;"))
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS previous_crops VARCHAR;"))
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS loan_amount DOUBLE PRECISION;"))
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS security_question VARCHAR;"))
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS security_question_answer VARCHAR;"))
        
        # Add new columns to buyers
        await conn.execute(text("ALTER TABLE buyers ADD COLUMN IF NOT EXISTS security_question VARCHAR;"))
        await conn.execute(text("ALTER TABLE buyers ADD COLUMN IF NOT EXISTS security_question_answer VARCHAR;"))
        
        # Make sure all tables defined in Base.metadata exist
        await conn.run_sync(Base.metadata.create_all)
        
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine):
    """Provide a database session to the test."""
    async_session = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session

# Helper function to clean up E2E test data
async def clean_e2e_test_data(session: AsyncSession):
    """Deletes all test entries from the database that match %@e2etest.com."""
    # 1. Fetch IDs of e2e farmers and buyers
    farmers_res = await session.execute(select(Farmer.id).where(Farmer.email.like("%@e2etest.com")))
    farmer_ids = farmers_res.scalars().all()
    
    buyers_res = await session.execute(select(Buyer.id).where(Buyer.email.like("%@e2etest.com")))
    buyer_ids = buyers_res.scalars().all()
    
    # 2. Delete dependent tables to avoid foreign key violations
    if farmer_ids:
        await session.execute(delete(CropBatch).where(CropBatch.farmer_id.in_(farmer_ids)))
        await session.execute(delete(AIFraudReport).where(AIFraudReport.farmer_id.in_(farmer_ids)))
        await session.execute(delete(VisionAnalysis).where(VisionAnalysis.farmer_id.in_(farmer_ids)))
        await session.execute(delete(PurchaseRequest).where(PurchaseRequest.farmer_id.in_(farmer_ids)))
        
    if buyer_ids:
        await session.execute(delete(PurchaseRequest).where(PurchaseRequest.buyer_id.in_(buyer_ids)))
        await session.execute(delete(VerificationLog).where(VerificationLog.verified_by_buyer_id.in_(buyer_ids)))
        
    # 3. Clean up verification OTP records for %@e2etest.com
    await session.execute(delete(OTPStore).where(OTPStore.email.like("%@e2etest.com")))
    
    # 4. Delete the core Farmer and Buyer records
    await session.execute(delete(Farmer).where(Farmer.email.like("%@e2etest.com")))
    await session.execute(delete(Buyer).where(Buyer.email.like("%@e2etest.com")))
    
    await session.commit()

@pytest_asyncio.fixture(autouse=True)
async def cleanup_e2e_data(db_session):
    """Automatically run cleanup before and after every single test."""
    await clean_e2e_test_data(db_session)
    yield
    await clean_e2e_test_data(db_session)

# Database utility functions to fetch OTPs and seed data directly in tests

async def get_otp_from_db(session: AsyncSession, email: str) -> str | None:
    """Fetch the verification OTP for a specific email directly from the database."""
    res = await session.execute(select(OTPStore.otp).where(OTPStore.email == email.lower()))
    return res.scalar_one_or_none()

async def seed_verified_farmer(session: AsyncSession, email: str, name: str = "E2E Farmer", location: str = "12.97,77.59") -> Farmer:
    """Seed a pre-verified farmer into the database to allow subsequent operations like adding crops."""
    from app.utils.auth import hash_password
    
    existing = await session.execute(select(Farmer).where(Farmer.email == email.lower()))
    f = existing.scalars().first()
    if f:
        return f
        
    farmer = Farmer(
        email=email.lower(),
        password_hash=hash_password("Password@123"),
        name=name,
        location=location,
        phone_number="+919876543210",
        address="123 Farm Road",
        verified=True,
        soil_type="Clay",
        exact_location=location,
        security_question="What is your mother's maiden name?",
        security_question_answer=hash_password("mother")
    )
    session.add(farmer)
    await session.commit()
    await session.refresh(farmer)
    return farmer

@pytest_asyncio.fixture
async def api_client(db_session):
    """Fixture that provides an asynchronous HTTP client for testing API endpoints."""
    import httpx
    from app.main import app
    
    # Override get_db dependency to use the test db_session
    from app.database import get_db
    async def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db
    
    async with httpx.AsyncClient(app=app, base_url="http://test", timeout=10.0) as client:
        yield client
        
    app.dependency_overrides.clear()
