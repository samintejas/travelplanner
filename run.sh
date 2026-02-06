#!/bin/bash

# Travel Concierge - Run Script

cd "$(dirname "$0")"

echo "==================================="
echo "  Travel Concierge AI"
echo "==================================="
echo ""

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "WARNING: OPENAI_API_KEY not set!"
    echo ""
    echo "To use AI features, set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
    if [ -n "$api_key" ]; then
        export OPENAI_API_KEY="$api_key"
        echo "API key set!"
    else
        echo "Continuing without AI features..."
    fi
    echo ""
fi

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

echo ""
echo "Starting server..."
echo "Open http://localhost:8000 in your browser"
echo ""
echo "Customer: http://localhost:8000"
echo "Admin:    http://localhost:8000/admin"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run the server
cd backend
python main.py
