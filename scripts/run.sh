#!/bin/bash
# Start the Multi-Agent Research System locally

echo "Starting Multi-Agent Research System..."

# Start backend
cd backend
source ../venv/bin/activate
uvicorn api.main:app --reload &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "App running at http://localhost:5173"
echo "API docs at  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait and cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
