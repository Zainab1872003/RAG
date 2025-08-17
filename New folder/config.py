import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Document RAG API"
    API_URL: str = ""  # Add this field
    
    # File Upload Settings
    UPLOAD_DIR: str = "./uploaded_docs"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # MongoDB Settings
    MONGODB_URL: str = ""
    DATABASE_NAME: str = ""
    
    # Pinecone Settings (for vector storage)
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "rag"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    
    # Mistral Settings
    MISTRAL_BASE_URL: str = "http://localhost:11434"
    MISTRAL_MODEL: str = "mistral"
    
    # Chunking Settings
    PDF_CHUNK_SIZE: int = 1000
    PDF_CHUNK_OVERLAP: int = 100
    EXCEL_ROWS_PER_CHUNK: int = 5
    PPT_CHARS_PER_CHUNK: int = 1000
    PPT_OVERLAP: int = 100
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
