#!/bin/bash
python3 -c "import vllm.entrypoints.openai.api_server; print('vllm import ok')" 2>&1
