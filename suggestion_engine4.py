# suggestion_engine4.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CUSTOM_BASE_URL = "https://aipipe.org/openai/v1"

client = OpenAI(api_key=OPENAI_API_KEY, base_url=CUSTOM_BASE_URL)

def generate_total_suggestion(total_score, max_total_score):

    percentage = (total_score / max_total_score) * 100

    if percentage < 30:
        maturity = "Basic / Initial Stage"
    elif percentage < 60:
        maturity = "Developing / Intermediate"
    elif percentage < 85:
        maturity = "Mature / Optimizing"
    else:
        maturity = "Advanced / Leading Practice"

    prompt = f"""
    The MSME business scored {total_score} out of {max_total_score} in total sustainability index.
    Provide a full sustainability transformation roadmap for MSMEs including:
    - Governance & Policy
    - Training & Employee Behavior
    - Investment & Budgeting
    - Energy & Resource Management
    - ESG data tracking, reporting, certifications
    - Community and global supply chain improvements

    Provide:
    - A maturity explanation in 2–3 bullet points
    - 6–8 step roadmap (short-term, mid-term, long-term)
    - Business risks if sustainability roadmap is not implemented
    - Templates / checklists / dashboard items they can replicate
    - Suggested KPIs for ESG tracking

    Write in bullet points and short paragraphs. Avoid generic motivation sentences.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a sustainability and ESG strategy expert advising MSMEs."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_tokens=1200
    )

    return response.choices[0].message.content.strip()
