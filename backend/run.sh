#!/bin/bash

# SAP TestOS Backend Startup Script

echo "🚀 Starting SAP TestOS Backend..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Initialize database
echo "🗄️  Initializing database..."
python startup.py

# Start the server
echo "🌐 Starting FastAPI server on http://0.0.0.0:8000"
echo "📖 API Docs available at http://0.0.0.0:8000/docs"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
