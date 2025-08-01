#!/bin/bash
# Simple startup script for EduConsult

echo "🎯 Starting EduConsult Server"
echo "=============================="

# Kill any existing process on port 5001
echo "🔍 Checking for existing processes on port 5001..."
if lsof -ti:5001 > /dev/null 2>&1; then
    echo "🔪 Killing existing processes on port 5001..."
    lsof -ti:5001 | xargs kill -9
    sleep 2
    echo "✅ Cleared port 5001"
else
    echo "✅ Port 5001 is free"
fi

# Navigate to the correct directory
cd "/Users/amanjha/Documents/untitled folder 4/Consultancy_ChatBot"

# Activate virtual environment and start server
echo "🚀 Starting server..."
if [ -f "../env/bin/activate" ]; then
    source ../env/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️ Virtual environment not found, using system Python"
fi

# Start the Flask server
python app.py
