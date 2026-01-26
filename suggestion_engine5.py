# suggestion_engine5.py

import os
from dotenv import load_dotenv
from openai import OpenAI

# ===============================
# Environment Setup
# ===============================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CUSTOM_BASE_URL = "https://aipipe.org/openai/v1"

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=CUSTOM_BASE_URL
)

# ===============================
# Tips & Resources Generator
# ===============================

def generate_tips_and_resources(total_score, max_total_score):
    """
    Generates maturity-based tips, government schemes,
    tools, and learning resources for MSMEs.
    """

    percentage = round((total_score / max_total_score) * 100, 1)

    # ---------- Maturity Mapping ----------
    if percentage < 30:
        maturity = "Basic"
        focus = "Awareness, basic measurement, cost control"
    elif percentage < 60:
        maturity = "Developing"
        focus = "Structured monitoring and early investments"
    elif percentage < 85:
        maturity = "Mature"
        focus = "Optimization, reporting, and certifications"
    else:
        maturity = "Advanced"
        focus = "Net Zero alignment and leadership practices"

    # ---------- Prompt ----------
    prompt = f"""
You are an expert advisor helping Indian MSMEs improve Net Zero readiness.

Context:
- Sustainability Score: {percentage}%
- Maturity Level: {maturity}
- Focus Area: {focus}

Generate CONTENT ONLY FOR A "TIPS & RESOURCES" PAGE.

STRICT OUTPUT STRUCTURE:

1. Maturity-Specific Practical Tips
   - 5–6 concise, actionable bullet points
   - Focus on operations, energy, water, waste, digital records

2. Recommended Government Policies & Schemes (India)
   - 4–5 schemes
   - Mention WHY each is useful at this maturity level

3. Tools & Resources MSMEs Can Use
   - Calculators, audits, portals, dashboards, standards
   - Practical and low-cost where possible

4. Quick Wins (Low Cost, High Impact)
   - 4–5 actions MSMEs can implement immediately

5. Next 90-Day Action Checklist
   - Clear checklist items
   - Suitable for MSME owner / plant manager

Rules:
- Bullet points only
- No long paragraphs
- No motivational language
- Practical and MSME-realistic
- India-focused
"""

    # ---------- API Call ----------
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a Net Zero, ESG, and MSME sustainability expert for India."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5,
        max_tokens=900
    )

    # ---------- Return Structured Output ----------
    return {
        "percentage": percentage,
        "maturity_level": maturity,
        "tips_focus": focus,
        "tips_and_resources": response.choices[0].message.content.strip()
    }
