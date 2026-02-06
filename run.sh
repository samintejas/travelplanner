#!/bin/bash

# Travel Concierge - Run Script

cd "$(dirname "$0")"

echo "==================================="
echo "  Travel Concierge AI"
echo "==================================="
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "No .env file found and OPENAI_API_KEY not set."
        echo ""
        read -p "Enter your OpenAI API key: " api_key
        if [ -n "$api_key" ]; then
            echo "OPENAI_API_KEY=$api_key" > .env
            echo "Created .env file with API key."
        else
            echo "Warning: No API key provided. AI features will be disabled."
        fi
        echo ""
    else
        echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
    fi
fi

# Check for docker-compose
if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
    echo "Starting with Docker Compose..."
    echo ""
    echo "This will start:"
    echo "  - PostgreSQL (database)"
    echo "  - ChromaDB (vector store)"
    echo "  - Backend (FastAPI)"
    echo ""

    # Use docker compose (new) or docker-compose (old)
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose up --build
    else
        docker-compose up --build
    fi
else
    echo "Docker not found. Running in development mode (no persistence)..."
    echo ""

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    echo "Installing dependencies..."
    pip install -q -r backend/requirements.txt

    # Load .env if exists
    if [ -f ".env" ]; then
        export $(cat .env | xargs)
    fi

    echo ""
    echo "Starting server..."
    echo "Open http://localhost:8000 in your browser"
    echo ""
    echo "Customer: http://localhost:8000"
    echo "Admin:    http://localhost:8000/admin"
    echo ""
    echo "Note: Running without Docker. Data will not persist."
    echo "Press Ctrl+C to stop"
    echo ""

    # Run the server
    cd backend
    python main.py
fi
