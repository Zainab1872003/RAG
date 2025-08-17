#!/usr/bin/env python3
"""
Start the FastAPI backend server.
"""
import multiprocessing
import uvicorn

# Set multiprocessing start method for compatibility
multiprocessing.set_start_method("spawn", force=True)

if __name__ == "__main__":
    print("🚀 Starting FastAPI RAG API Server...")
    print("📚 API Documentation: http://127.0.0.1:8000/docs")
    print("🔍 Health Check: http://127.0.0.1:8000/health")
    print("📋 API Base URL: http://127.0.0.1:8000/api/v1")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000
    )
    
    
