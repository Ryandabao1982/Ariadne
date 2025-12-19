"""Database connection and configuration for Ariadne backend."""

import logging
from typing import Optional, AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Base for SQLAlchemy models
Base = declarative_base()

# Database engine and session maker (will be initialized in database startup)
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def initialize_database():
    """Initialize database connection and session makers."""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    try:
        # For now, use SQLite in development mode
        # In production, this will be PostgreSQL with async support
        database_url = settings.database_url_async if hasattr(settings, 'database_url_async') else "sqlite:///./ariadne.db"
        
        if database_url.startswith("postgresql"):
            # PostgreSQL with async support
            async_engine = create_async_engine(
                database_url,
                echo=settings.debug,
                pool_pre_ping=True,
                pool_recycle=300,
            )
            
            AsyncSessionLocal = async_sessionmaker(
                bind=async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("Initialized PostgreSQL database connection")
        else:
            # SQLite for development
            engine = create_engine(
                "sqlite:///./ariadne.db",
                echo=settings.debug,
                connect_args={"check_same_thread": False}
            )
            
            SessionLocal = sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False
            )
            
            logger.info("Initialized SQLite database connection")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency for FastAPI."""
    if AsyncSessionLocal is None:
        initialize_database()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_database_session():
    """Get synchronous database session (for development)."""
    if SessionLocal is None:
        initialize_database()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    try:
        if engine:
            Base.metadata.create_all(bind=engine)
        elif async_engine:
            import asyncio
            
            async def create_async_tables():
                async with async_engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
            
            asyncio.run(create_async_tables())
            
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def get_database_info() -> dict:
    """Get database connection information."""
    return {
        "database_type": "PostgreSQL" if async_engine else "SQLite",
        "connection_status": "connected" if (engine or async_engine) else "disconnected",
        "debug_mode": settings.debug,
        "database_url_configured": bool(getattr(settings, 'database_url_async', None))
    }


# Health check for database
async def check_database_health() -> dict:
    """Check database connection health."""
    try:
        if async_engine:
            async with async_engine.begin() as conn:
                result = await conn.execute("SELECT 1")
                result.fetchone()
        elif engine:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
        else:
            return {"status": "error", "message": "Database not initialized"}
        
        return {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}


# Initialize database on module import
initialize_database()
