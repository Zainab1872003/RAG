# Document RAG Chat System

A FastAPI-based Retrieval-Augmented Generation (RAG) system for document processing and querying.

## Features

- 📄 Support for multiple document formats (PDF, DOC, DOCX, Excel, PowerPoint)
- 🔍 OCR for extracting text from images within documents
- 🧠 Vector embeddings using SentenceTransformers
- 🗄️ Vector storage with Pinecone
- 🤖 AI responses using local Mistral via Ollama
- 🎨 User-friendly Gradio web interface
- 🚀 Fast and scalable FastAPI backend

## Quick Start

1. **Install dependencies:**

pip install -r requirements.txt

2. **Set up environment variables:**

cp .env.example .env


3. **Start the API server:**
python backend_run.py


4. **Start the frontend (in another terminal):**
python frontend_run.py


5. **Access the application:**
- Frontend: http://127.0.0.1:7860
- API Docs: http://127.0.0.1:8000/docs

## Project Structure

rag_project/
├── app/ # FastAPI application
│ ├── api/v1/ # API version 1 endpoints
│ ├── core/ # Configuration and settings
│ ├── models/ # Pydantic schemas
│ ├── services/ # Business logic
│ └── utils/ # Utility functions
├── frontend/ # Gradio web interface
├── start_api.py # API startup script
└── start_frontend.py # Frontend startup script


## API Endpoints

- `POST /api/v1/upload/` - Upload documents
- `POST /api/v1/query/` - Query documents
- `GET /api/v1/files/` - List files
- `DELETE /api/v1/files/{filename}` - Delete files
- `GET /api/v1/health/` - Health check

## Environment Variables

rag_project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── health.py
│   │           ├── upload.py
│   │           ├── query.py
│   │           └── files.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embedding_service.py
│   │   ├── document_service.py
│   │   ├── query_service.py
│   │   └── file_service.py
│   └── utils/
│       ├── __init__.py
│       ├── doc_loader.py
│       ├── mistral_client.py
│       └── ppt_converter.py
├── frontend/
│   ├── __init__.py
│   └── gradio_app.py
├── uploaded_docs/
├── start_api.py
├── start_frontend.py
├── requirements.txt
├── README.md
├── .env
└── venv/
