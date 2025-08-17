from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.database = mongodb.client[settings.DATABASE_NAME]
    
    # Import models here to avoid circular imports
    from app.models.mongo_models import DocumentCollection, VectorMetadata
    
    # Initialize Beanie with document models
    await init_beanie(
        database=mongodb.database,
        document_models=[DocumentCollection, VectorMetadata]
    )
    print("✅ Connected to MongoDB")


async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        print("❌ MongoDB connection closed")

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return mongodb.database
