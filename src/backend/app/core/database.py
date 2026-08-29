import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

logger = logging.getLogger("lokiini-db")

db_url = settings.DATABASE_URL
engine_kwargs = {}

# Check available async drivers
driver_found = False
try:
    import asyncpg
    engine_kwargs = {"pool_size": 20, "max_overflow": 10}
    driver_found = True
except ImportError:
    pass

if not driver_found:
    try:
        import aiosqlite
        db_url = "sqlite+aiosqlite:///./lokiini_dev.db"
        driver_found = True
    except ImportError:
        pass

if driver_found:
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        **engine_kwargs
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
else:
    # Dummy mock engine for local syntax and schema inspection without drivers
    class DummyEngine:
        def begin(self):
            class DummyConnCtx:
                async def __aenter__(self):
                    class DummyConn:
                        async def run_sync(self, fn): pass
                    return DummyConn()
                async def __aexit__(self, *args): pass
            return DummyConnCtx()
    engine = DummyEngine()
    
    class DummySessionLocal:
        def __call__(self):
            class DummySessionCtx:
                async def __aenter__(self):
                    class DummySession:
                        async def execute(self, *args, **kwargs):
                            class DummyResult:
                                def scalars(self):
                                    class DummyScalars:
                                        def first(self): return None
                                        def all(self): return []
                                    return DummyScalars()
                            return DummyResult()
                        async def flush(self): pass
                        async def commit(self): pass
                        async def rollback(self): pass
                        async def close(self): pass
                        def add(self, obj): pass
                        def add_all(self, objs): pass
                    return DummySession()
                async def __aexit__(self, *args): pass
            return DummySessionCtx()
    AsyncSessionLocal = DummySessionLocal()

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
