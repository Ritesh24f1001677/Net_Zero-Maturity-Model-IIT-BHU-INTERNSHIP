# suggestion_engine1.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CUSTOM_BASE_URL = "https://aipipe.org/openai/v1"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY, base_url=CUSTOM_BASE_URL)

def generate_dynamic_suggestion_knowledge(score, max_score):
    """
    Generate personalized suggestions for Knowledge & Capabilities level.
    """
    prompt = f"""
    The user has scored {score} out of {max_score} in Knowledge & Capabilities.
    Generate 3-5 personalized sustainability recommendations for this user.
    Make them clear, actionable, and motivating.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # your AI Pipe model
        messages=[
            {"role": "system", "content": "You are a helpful sustainability advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()
