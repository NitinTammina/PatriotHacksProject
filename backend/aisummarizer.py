import os
import openai
from dotenv import load_dotenv

# Load .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_feedback(feedback_json: dict) -> str:
    # Convert JSON to string so the model can read it
    feedback_str = str(feedback_json)

    prompt = (
        "You are a fitness coach AI. Read the following exercise feedback data "
        "from a user's shoulder press workout and summarize it in 3-4 sentences, "
        "giving actionable recommendations for improving form:\n\n"
        f"{feedback_str}\n\nSummary:"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7
    )

    summary = response['choices'][0]['message']['content'].strip()
    return summary
