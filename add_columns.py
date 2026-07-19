import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import get_settings

async def main():
    settings = get_settings()
    db_url = settings.database_url
    if "asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    print(f"Connecting to: {db_url}")
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS security_question VARCHAR;"))
        await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS security_question_answer VARCHAR;"))
        await conn.execute(text("ALTER TABLE buyers ADD COLUMN IF NOT EXISTS security_question VARCHAR;"))
        await conn.execute(text("ALTER TABLE buyers ADD COLUMN IF NOT EXISTS security_question_answer VARCHAR;"))
        print("Columns added successfully!")

if __name__ == "__main__":
    asyncio.run(main())
