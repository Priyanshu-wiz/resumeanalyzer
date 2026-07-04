from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Create OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are an expert ATS Resume Analyzer.

Analyze the following resume for the role of:

{user_goal}

Strict rules:
- Do not provide any explanations or additional text.
- remove irrelevnt tools like excel, word, etc.

{resume_text}

Return ONLY valid JSON in the following format:
{{
    "score": 85,
    "strengths": [
        "...",
        "...",
        "..."
    ],
    "weaknesses": [
        "...",
        "...",
        "..."
    ],
    "missing_skills": [
        "...",
        "...",
        "..."
    ],
    "suggestions": [
        "...",
        "...",
        "..."
    ]
}}
"""

    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",      # You can change this model
        
        messages=[
            {
                "role": "system",
                "content": "You are a professional ATS Resume Analyzer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )
    result = response.choices[0].message.content

    return json.loads(result)