import google.generativeai as genai
import os
from dotenv import load_dotenv
import asyncio
import edge_tts
import subprocess

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



async def text_to_speech(text, output_file):
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
    await communicate.save(output_file)

def generate_audio(script):
    output = "audio.mp3"
    asyncio.run(text_to_speech(script, output))
    return output



def generate_video(script):
    audio_path = generate_audio(script)
    video_path = "output.mp4"

    # ensure ffmpeg is available
    import shutil
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg binary not found; please install ffmpeg and add to PATH")

    command = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "color=c=black:s=1080x1920:d=45",
        "-i", audio_path,
        "-shortest",
        "-vf", "format=yuv420p",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        video_path
    ]

    subprocess.run(command, check=True)
    return video_path

def run_workflow(topic):
    """
    Main workflow that generates script and video for a given topic.
    """
    try:
        script = generate_script(topic)
        video_path = generate_video(script)
        
        return {
            "topic": topic,
            "script": script,
            "video": video_path
        }
    except Exception as e:
        return {"error": str(e)}