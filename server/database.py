import os

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv

class BaseModel(DeclarativeBase):
    pass

class Database:
    def __init__(self):
        self.engine = None
        self.sessionmaker = None
        self.database = BaseModel

    async def connect(self, *args, **kwargs):
        load_dotenv()
        DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT_EXTERNAL')}/{os.getenv('DB_NAME')}"
        self.engine = create_async_engine(DATABASE_URL, echo=False)
        self.sessionmaker = async_sessionmaker(self.engine, expire_on_commit=False)

    def get_session(self) -> AsyncSession:
        if self.sessionmaker is None:
            raise Exception("Database not connected")
        return self.sessionmaker()
    
    async def session_getter(self):
        if self.sessionmaker is None:
            raise Exception("Database not connected")
        async with self.sessionmaker() as session:
            yield session
    
    async def disconnect(self, *args, **kwargs):
        if self.engine is not None:
            await self.engine.dispose()

database = Database()