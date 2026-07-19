import asyncio
import sys
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add backend directory to Python path
backend_path = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_path))

from app.config import get_settings

async def main():
    settings = get_settings()
    db_url = settings.database_url
    if "asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
    print(f"Connecting to: {db_url}")
    engine = create_async_engine(db_url, echo=True)
    
    async with engine.connect() as conn:
        # Check current columns of farmers
        print("Checking columns of table 'farmers'...")
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'farmers';
        """))
        columns = result.fetchall()
        for col in columns:
            print(col)
            
        print("\nRunning ALTER TABLE statements...")
        try:
            await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS security_question VARCHAR;"))
            await conn.execute(text("ALTER TABLE farmers ADD COLUMN IF NOT EXISTS security_question_answer VARCHAR;"))
            await conn.commit()
            print("Alters executed and committed successfully.")
        except Exception as e:
            print(f"Error during alters: {e}")
            
        # Re-check columns
        print("\nRe-checking columns of table 'farmers'...")
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'farmers';
        """))
        columns = result.fetchall()
        for col in columns:
            print(col)
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
