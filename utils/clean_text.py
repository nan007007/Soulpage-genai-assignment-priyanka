import re
'''
 a small utility to normalize LLM/tool/user text before displaying, logging, or composing prompts so responses don't contain excessive blank lines.
 '''
def clean_text(text: str):
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
