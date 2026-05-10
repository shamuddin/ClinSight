#!/bin/bash
for i in {1..30}; do
  vision_ready=0
  text_ready=0
  curl -s http://localhost:8000/v1/models > /dev/null 2>&1 && vision_ready=1
  curl -s http://localhost:30000/v1/models > /dev/null 2>&1 && text_ready=1
  if [ "$vision_ready" -eq 1 ] && [ "$text_ready" -eq 1 ]; then
    echo "Both vLLM servers ready after $i attempts"
    exit 0
  fi
  echo "Attempt $i: vision=$vision_ready text=$text_ready"
  sleep 15
done
echo "Timeout waiting for vLLM servers"
exit 1
