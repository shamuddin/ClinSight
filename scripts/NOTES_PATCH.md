# Patches for droplet runtime

## 1. Documenter: skip LLM, use deterministic only (~50ms vs 60s)
## 2. Image: add image_url to initial response so it renders immediately

--- Patch 1: backend/agents/clinical_documenter.py ---
In clinical_documenter_agent(), replace:
    try:
        actions = await _text_client().generate_actions(state)
    except Exception:
        actions = suggest_actions_deterministic(state)
With:
    actions = suggest_actions_deterministic(state)  # skip LLM for speed

And replace:
    try:
        report = await _text_client().generate_report(state)
    except Exception:
        report = generate_report_deterministic(state)
With:
    report = generate_report_deterministic(state)  # skip LLM for speed

--- Patch 2: backend/api/demo.py ---
In _build_response(), image_url is already there:
    "image_url": f"/demo/image/{final['case_id']}",

But for streaming, we need it in the first chunk. In the SSE stream, send image_url with stage=coordinator output so frontend has it immediately.

--- Patch 3: frontend ---
The frontend already falls back to /demo-images/{case_id}.png when image_url is missing. But the EvidenceRow only renders when result exists (after pipeline completes). 

Better fix: don't wait for Documenter. The image should be in the initial payload.
