import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def get_carbon_news_llm():
    prompt = """
    Provide a list of 5 recent news articles related to 'carbon footprint' or 'Green India'.
    For each article, give:
    - title
    - short description
    - URL (if possible)
    - image URL (if possible)
    Format the output as a JSON list of objects.
    """
    
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides news summaries."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    
    # Extract the LLM output
    content = response.choices[0].message.content
    
    # Try to parse JSON if the model returns JSON
    import json
    try:
        news_list = json.loads(content)
    except json.JSONDecodeError:
        news_list = [{"type": "news", "title": "Error parsing LLM response", "description": content}]
    
    return news_list

# Test
if __name__ == "__main__":
    news = get_carbon_news_llm()
    for n in news:
        print(n)
