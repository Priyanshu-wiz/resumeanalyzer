import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are an expert ATS Resume Analyzer.

Analyze the following resume for the role of:

{user_goal}

Strict rules:
- Do not provide any explanations or additional text.
- remove irrelevant tools like excel, word, etc.

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
    "interview_questions": [
        "...",
        "...",
        "..."
    ]
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a professional ATS Resume Analyzer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    result = response.choices[0].message.content

    if isinstance(result, str):
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            try:
                cleaned = result.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.strip("`")
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:].strip()
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return {
                    "score": 70,
                    "strengths": ["Resume contains relevant experience"],
                    "weaknesses": ["AI returned non-JSON content"],
                    "missing_skills": ["Check your resume content"],
                    "interview_questions": ["What are your key technical strengths?"],
                }

    return result