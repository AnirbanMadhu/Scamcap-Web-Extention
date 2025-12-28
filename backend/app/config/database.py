from motor.motor_asyncio import AsyncIOMotorClient
from .settings import get_settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    settings = get_settings()
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]

        # Test the connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")

        # Create indexes
        await create_indexes()

    except Exception as e:
        logger.warning(f"Failed to connect to MongoDB: {e}")
        logger.warning("Running without database - some features will be disabled")
        db.client = None
        db.database = None

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        await db.database.users.create_index("email", unique=True)
        await db.database.users.create_index("created_at")
        
        # Threat logs collection indexes
        await db.database.threat_logs.create_index("timestamp")
        await db.database.threat_logs.create_index("user_id")
        await db.database.threat_logs.create_index("threat_type")
        await db.database.threat_logs.create_index("risk_score")
        
        # MFA sessions collection indexes
        await db.database.mfa_sessions.create_index("session_id", unique=True)
        await db.database.mfa_sessions.create_index("expires_at")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Failed to create some indexes: {e}")

def get_database():
    """Get database instance"""
    return db.database
