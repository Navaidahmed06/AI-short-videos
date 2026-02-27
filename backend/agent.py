import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_script(topic):
    prompt = f"""
    Create a highly engaging 45-second YouTube Shorts script about:
    {topic}

    Start with a strong hook.
    Keep it concise and energetic.
    """

    response = model.generate_content(prompt)
    return response.text

def run_workflow(topic):
    """
    Main workflow that generates script and video for a given topic.
    """
    try:
        script = generate_script(topic)
        
        return {
            "topic": topic,
            "script": script,
            "video": None  # Placeholder for video generation
        }
    except Exception as e:
        return {"error": str(e)}