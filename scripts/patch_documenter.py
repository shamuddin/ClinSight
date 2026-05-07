import sys
path = sys.argv[1]
text = open(path).read()

old_actions = """    # Generate suggested actions via LLM (or mock fallback)
    try:
        actions = await _text_client().generate_actions(state)
    except Exception:
        actions = suggest_actions_deterministic(state)"""

new_actions = """    # Use deterministic actions (skip LLM for speed)
    actions = suggest_actions_deterministic(state)"""

text = text.replace(old_actions, new_actions)

old_report = """    # Generate structured report
    try:
        report = await _text_client().generate_report(state)
    except Exception:
        report = generate_report_deterministic(state)"""

new_report = """    # Use deterministic report (skip LLM for speed)
    report = generate_report_deterministic(state)"""

text = text.replace(old_report, new_report)

open(path, "w").write(text)
print("PATCHED")
