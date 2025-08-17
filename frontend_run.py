#!/usr/bin/env python3
"""
Start the Gradio frontend interface.
"""
import sys
import requests
import time
from frontend.gradio_app import create_gradio_app

def check_api_connection():
    """Check if the API server is running."""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🎨 Starting Gradio Frontend...")
    
    # Check API connection
    if not check_api_connection():
        print("⚠️  WARNING: Cannot connect to API server!")
        print("🔧 Please make sure the API server is running:")
        print("   python start_api.py")
        print("=" * 50)
        print("🚀 Starting frontend anyway...")
    else:
        print("✅ API server connection verified")
    
    print("🌐 Frontend URL: http://127.0.0.1:7860")
    print("=" * 50)
    
    demo = create_gradio_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
