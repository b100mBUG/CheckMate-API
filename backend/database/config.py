from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv(".env")

database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///checkmate.db")
engine = create_async_engine(url=database_url, echo=False)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)