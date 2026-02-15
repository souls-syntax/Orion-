import google.generativeai as genai
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound
from pygments import highlight
from pygments.formatters import TerminalFormatter
import json

# ✅ Configure Gemini
GOOGLE_API_KEY = "Enter your Google API key here"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 🎯 Detect programming language
def detect_language(code):
    fallback_map = {
        "scdoc": "Python", "Text only": "Python", "INI": "Python",
        "Batchfile": "C", "Markdown": "Python", "HTML": "JavaScript",
        "CSS": "JavaScript", "Makefile": "C", "ShellSession": "Bash",
        "JavaScript": "JavaScript", "Go": "Go", "C++": "C++",
        "C": "C", "Java": "Java", "Python": "Python"
    }
    try:
        lexer = guess_lexer(code)
        return fallback_map.get(lexer.name, lexer.name)
    except ClassNotFound:
        return "Unknown"

# 🤖 Ask Gemini to explain and optimize the code
def explain_and_optimize_code(code, language):
    prompt = f"""
You are a professional coding assistant.

Analyze the following code written in {language}.

Return the output strictly in valid JSON format with the following structure:

{{
  "DetectedLanguage": "The programming language detected based on the syntax.",
  "Explanation": "A brief explanation of what the code does.",
  "Issues": ["List of issues, bugs, or inefficiencies found in the code."],
  "OptimizedCode": ["Line-by-line optimized code as an array of strings with inline comments."]
}}

⚠️ IMPORTANT INSTRUCTIONS:
- Do NOT include markdown formatting.
- Do NOT wrap the response in code fences.
- Each line of the optimized code MUST be a single string within the 'OptimizedCode' array. Include inline comments explaining the optimizations or logic.
- Ensure all quotes within the JSON, especially within string values, are properly escaped using a backslash (\\").
- The ENTIRE response MUST be valid, properly formatted JSON. Ensure there are no trailing commas in lists or objects.

Here is the code:

{code}
"""
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text.strip())
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON response from Gemini.",
            "raw_output": response.text
        }

def codebot_api_handler(code: str, language: str = None) -> dict:
    if not language or language.lower() == "auto":
        language = detect_language(code)
        if language == "Unknown":
            return {"error": "Could not detect programming language."}

    return explain_and_optimize_code(code, language)
