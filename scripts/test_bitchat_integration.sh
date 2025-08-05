#!/bin/bash

echo "Starting Bitchat integration smoke test..."

# Add the project root to PYTHONPATH
export PYTHONPATH="/workspaces/yaz:$PYTHONPATH"

# Start the Surgify app
echo "Starting Surgify communication API..."
python3 /workspaces/yaz/src/surgify/api/v1/communication.py &
APP_PID=$!

# Wait for the app to start
echo "Waiting for app to start..."
sleep 5

# Check network status
echo "Checking network status..."
curl -s -X GET http://127.0.0.1:5000/network/status | python3 -m json.tool

# Send a test medical data message
echo "Sending test medical data message..."
curl -s -X POST http://127.0.0.1:5000/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "peer1", 
    "message": {
      "patient_id": "P123456",
      "diagnosis": "Gastric adenocarcinoma", 
      "stage": "T2N1M0"
    },
    "type": "medical_data"
  }' | python3 -m json.tool

# Send a test case consultation message
echo "Sending test case consultation message..."
curl -s -X POST http://127.0.0.1:5000/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "peer2",
    "case_id": "CASE_789",
    "message": {
      "patient_age": 65,
      "symptoms": "Dysphagia, weight loss",
      "urgency": "high"
    },
    "type": "case_consultation"
  }' | python3 -m json.tool

# Wait a moment for message processing
sleep 2

# Poll for message sync
echo "Polling for message sync..."
curl -s -X GET http://127.0.0.1:5000/message/sync | python3 -m json.tool

# Check network status again
echo "Final network status check..."
curl -s -X GET http://127.0.0.1:5000/network/status | python3 -m json.tool

# Kill the app process
echo "Stopping application..."
kill $APP_PID

echo "Bitchat integration smoke test completed!"
