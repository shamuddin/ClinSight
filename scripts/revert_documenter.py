import sys
path = sys.argv[1]
text = open(path).read()

# Revert: restore LLM calls
text = text.replace(
    """    # Use deterministic actions (skip LLM for speed)
    actions = suggest_actions_deterministic(state)""",
    """    # Generate suggested actions via LLM (or mock fallback)
    try:
        actions = await _text_client().generate_actions(state)
    except Exception:
        actions = suggest_actions_deterministic(state)"""
)

text = text.replace(
    """    # Use deterministic report (skip LLM for speed)
    report = generate_report_deterministic(state)""",
    """    # Generate structured report
    try:
        report = await _text_client().generate_report(state)
    except Exception:
        report = generate_report_deterministic(state)"""
)

open(path, "w").write(text)
print("REVERTED")
