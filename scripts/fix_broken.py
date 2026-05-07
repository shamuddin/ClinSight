import sys, re
path = sys.argv[1]
text = open(path).read()

# Fix broken multiline string from bad patch
# The broken line has: text = re.sub(r"(?i)thinking process:?.*?\n...
# We need to replace the entire broken _parse_json_array method

old_method = '''    def _parse_json_array(self, text: str) -> list:
        """Extract JSON array from LLM response. Strip reasoning text."""
        text = text.strip()
        # Remove markdown fences
        if text.startswith("```"):
            lines = text.splitlines()
            while lines and (lines[0].startswith("```") or not lines[0].strip()):
                lines.pop(0)
            while lines and (lines[-1].startswith("```") or not lines[-1].strip()):
                lines.pop()
            text = "\\n".join(lines)
        # Strip common reasoning prefixes (Qwen3.5 thinking mode)
        text = re.sub(r"(?i)thinking process:?.*?\n\s*\d?\s*\*?\*?analyze the request:?\*?\*?", "", text, flags=re.DOTALL)
        text = re.sub(r"(?i)\*?\*?role:?.*?\*?\*?", "", text)
        text = re.sub(r"(?i)\*?\*?input:?.*?\*?\*?", "", text)
        text = re.sub(r"(?i)\*?\*?output constraint:?.*?\*?\*?", "", text)
        text = re.sub(r"(?i)\*?\*?return only.*?\*?\*?", "", text)
        # Find JSON array in text
        m = re.search(r"\[.*?\]", text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group())
                if isinstance(data, list):
                    return [str(item) for item in data]
            except json.JSONDecodeError:
                pass
        # Fallback: parse bullet points / numbered lines
        actions = []
        for line in text.splitlines():'''

new_method = '''    def _parse_json_array(self, text: str) -> list:
        """Extract JSON array from LLM response. Strip reasoning text."""
        text = text.strip()
        # Remove markdown fences
        if text.startswith("```"):
            lines = text.splitlines()
            while lines and (lines[0].startswith("```") or not lines[0].strip()):
                lines.pop(0)
            while lines and (lines[-1].startswith("```") or not lines[-1].strip()):
                lines.pop()
            text = "\\n".join(lines)
        # Strip reasoning prefixes and find JSON
        text = re.sub(r"(?i)thinking process:.*?(?=\[|\Z)", "", text, flags=re.DOTALL)
        text = re.sub(r"(?i)analyze the request:.*?(?=\[|\Z)", "", text, flags=re.DOTALL)
        text = re.sub(r"(?i)role:.*?(?=\[|\Z)", "", text, flags=re.DOTALL)
        # Find JSON array
        m = re.search(r"\[.*?\]", text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group())
                if isinstance(data, list):
                    return [str(item) for item in data]
            except json.JSONDecodeError:
                pass
        # Fallback: parse bullet points / numbered lines
        actions = []
        for line in text.splitlines():'''

text = text.replace(old_method, new_method)
open(path, "w").write(text)
print("FIXED")
