import sys, re
path = sys.argv[1]
text = open(path).read()

# Fix _parse_json_array to strip "Thinking Process" and other prefixes
old_parse = '''    def _parse_json_array(self, text: str) -> list:
        """Extract JSON array from LLM response."""
        text = text.strip()
        # Remove markdown fences
        if text.startswith("```"):
            lines = text.splitlines()
            while lines and (lines[0].startswith("```") or not lines[0].strip()):
                lines.pop(0)
            while lines and (lines[-1].startswith("```") or not lines[-1].strip()):
                lines.pop()
            text = "\\n".join(lines)
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [str(item) for item in data]
        except json.JSONDecodeError:
            pass
        # Fallback: parse bullet points / numbered lines
        actions = []
        for line in text.splitlines():
            line = line.strip().lstrip("-*0123456789. ").strip()'''

new_parse = '''    def _parse_json_array(self, text: str) -> list:
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
        for line in text.splitlines():
            line = line.strip().lstrip("-*0123456789. ").strip()'''

text = text.replace(old_parse, new_parse)
open(path, "w").write(text)
print("PARSING_FIXED")
