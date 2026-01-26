# suggestion_engine3.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CUSTOM_BASE_URL = "https://aipipe.org/openai/v1"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY, base_url=CUSTOM_BASE_URL)

def generate_dynamic_suggestion_advanced(score, max_score):
    """
    Generate detailed sustainability improvement suggestions
    based on energy usage, carbon tracking, EV usage, circular economy,
    repair services, and resource reuse.
    """
    
    prompt = f"""
    The user has scored {score} out of {max_score} for the section:
    **Energy, Resource Management & Circular Economy Initiatives**.

    Discuss improvement strategies in a detailed manner for the following areas:

    1️⃣ Do employees actively use renewable sources of energy?
    2️⃣ Do employees actively use sustainable or alternative fuels?
    3️⃣ Are energy efficiency measures implemented in your MSME?
    4️⃣ Does your MSME have a system to monitor and reduce carbon emissions?
    5️⃣ Does your MSME regularly implement environmental initiatives?
    6️⃣ Whether MSME uses electric vehicles?
    7️⃣ Does the MSME support post-purchase repair services to increase a product's lifespan?
    8️⃣ MSMEs retrieve the items that their customers no longer utilize.
    9️⃣ Employees tend to reuse office stationery materials and other reusable things.
    🔟 MSME measures its overall emissions.

    Based on the score, assume lower score means basic stage and higher means advanced.
    
    Provide a detailed response including:
    - Current possible state (what MSME might be doing now)
    - Why each area is important
    - 2–3 improvement steps per category
    - Realistic, low-cost implementation examples

    Write the answer in structured bullet points and short paragraphs.
    Avoid generic sentences.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert sustainability and industrial strategy advisor for MSMEs."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=700
    )

    return response.choices[0].message.content.strip()
