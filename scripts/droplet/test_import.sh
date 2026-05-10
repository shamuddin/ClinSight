#!/bin/bash
cd /shared-docker
PYTHONPATH=/shared-docker python3 -c "from backend.agents.graph import run_pipeline; print('OK')"
