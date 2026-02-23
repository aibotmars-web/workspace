#!/bin/bash
API_KEY="sk-cp-zBE1lcRUibZCRRYCuwSJv_HIpvekBW0YsZTEL17h1giYy2KqDOwJ4QoaBtuExUmuE8NQWOHz-P1dtBAF3jKkBrKEs3336Gpr0e6L-wRlMROa4-3V-dwc5Ws"

response=$(curl -s -X POST 'https://api.minimaxi.com/v1/usage' \
  -H "Authorization: Bearer $API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"abab6.5s-chat"}')

echo "$response" | jq '.' 2>/dev/null || echo "$response"
