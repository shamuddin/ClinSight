#!/bin/bash
cd /shared-docker
pip list 2>/dev/null | grep -E "fastapi|uvicorn|langgraph"
