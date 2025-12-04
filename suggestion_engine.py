import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CUSTOM_BASE_URL = "https://aipipe.org/openai/v1"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY, base_url=CUSTOM_BASE_URL)

def generate_dynamic_suggestion(user, responses):
    if not responses:
        html = f"""
        <div style="
            font-family: 'Poppins', sans-serif;
            color:#555;
            background:#f0f8ff;
            padding:20px;
            border-radius:15px;
            max-width:600px;
        ">
            <h3 style="color:#2c3e50;">Hello {user.name or 'User'}!</h3>
            <p>Complete your questionnaires to get <strong>personalized sustainability suggestions</strong>.</p>
        </div>
        """
        return html

    # Build performance sections
    performance_text = ""
    for r in responses:
        performance_text += f"""
LEVEL {r.level}
Score: {r.score}
Maturity: {r.maturity_level}
---------------------------------------
"""

    # Profile details
    profile_details = f"""
Organization Name: {user.step1}
Industry Type: {user.step2}
Number of Employees: {user.step3}
Main Fuel Type: {user.step4}
Primary Concern: {user.step5}
"""

    # UPDATED PROMPT WITH ADVANCED FEATURES
    prompt = f"""
You are an expert Sustainability Advisor.
Create HTML ONLY. No plain text.

==============================
ORGANIZATION PROFILE
==============================
{profile_details}

==============================
LEVELS & SCORES
==============================
{performance_text}

==============================
YOUR TASK
==============================

Create a clean UI styled HTML containing:

1. <h3>Overview</h3>
   - Summary of performance trends and maturity.

2. <h3>Level-wise Insights</h3>
   - For each level: interpretation.
   - Use ✔ icon if score > 70.
   - Use ⚠ warning if score < 40.

3. <h3>Action Plan Roadmap</h3>
   - Short Term (0–6 months)
   - Mid Term (6–18 months)
   - Long Term (18+ months)

4. <h3>Estimated CO₂ Reduction Impact</h3>
   - Display qualitative Low/Medium/High impact.

5. <h3>ROI Benefit Table</h3>
   - Columns: Action | Cost Level | Potential Savings | Break-even Time.
   - Use approximate qualitative values only.

6. <h3>Risk Alerts</h3>
   - Highlight risks if score < 35 or maturity shows beginner.
   - Use ⚠ + red text.

7. <h3>ISO & Certification Readiness</h3>
   - Provide readiness percentage based ONLY on score averages.
   - Display visually using a CSS Circular Progress Ring.

8. <h3>Recommended Automation Technology</h3>
   - Provide card styled boxes recommending AI, IoT, solar, predictive maintenance.

VISUAL RULES:
- Use fade-in scroll animation.
- Use CSS progress ring.
- Use rounded glass-like cards for tech list.
- No assumptions for missing values.

"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert sustainability advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7
        )

        suggestion_html = completion.choices[0].message.content.strip()

        # Final UI Wrapped HTML
        final_html = f"""
        <div style="
            font-family:'Poppins',sans-serif;
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 25px;
            border-radius: 20px;
            max-width: 800px;
            color: #333;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            line-height:1.6;
            animation: fadeInUp 0.8s ease-in-out;
        ">

            {suggestion_html}

        </div>

<style>
.section-animate {{
    opacity: 0;
    transform: translateY(20px);
    animation: fadeInUp 0.8s forwards;
}}

@keyframes fadeInUp {{
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.progress-ring {{
    width:120px; height:120px;
    border-radius:50%;
    position:relative;
    display:flex;
    justify-content:center;
    align-items:center;
    background:conic-gradient(#36d1dc calc(var(--value) * 1%), #dcdcdc 0);
}}
.progress-ring span {{
    font-size:20px; font-weight:bold;
    position:absolute;
}}

.tech-card {{
    background:white;
    padding:12px;
    border-radius:15px;
    box-shadow:0 4px 10px rgba(0,0,0,0.2);
    margin:10px;
    display:inline-block;
    min-width:140px;
    text-align:center;
    transition:.3s;
}}
.tech-card:hover {{
    transform:scale(1.05);
}}
</style>
        """

        return final_html

    except Exception as e:
        return f"""
        <div style='font-family: Arial, sans-serif; color:red;'>
            Sorry! Personalized suggestions are temporarily unavailable. ({str(e)})
        </div>
        """
