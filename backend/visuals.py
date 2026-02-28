import os
import requests
import subprocess
import asyncio
import edge_tts
import requests

HF_TOKEN = os.getenv("HF_TOKEN")

# Generate image from prompt
# use the new router endpoint per HF deprecation notice



def generate_image(prompt: str, filename: str) -> str:
    """
    Fetch a vertical-ish stock image from Pexels based on the prompt.
    Saves it as filename and returns filename.
    """
    

    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        raise Exception("Missing PEXELS_API_KEY in .env")

    # Search photos
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": api_key},  # Pexels expects key directly (no Bearer)
        params={
            "query": prompt,
            "per_page": 1,
            "orientation": "portrait",  # best for Shorts
            "size": "large"
        },
        timeout=30
    )

    if r.status_code != 200:
        raise Exception(f"Pexels API error {r.status_code}: {r.text}")

    data = r.json()
    photos = data.get("photos", [])
    if not photos:
        # fallback query if prompt too long/complex
        r2 = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": "technology abstract background", "per_page": 1, "orientation": "portrait"},
            timeout=30
        )
        r2.raise_for_status()
        photos = r2.json().get("photos", [])
        if not photos:
            raise Exception("Pexels returned no photos for both prompt and fallback.")

    # Pick a good size URL
    img_url = photos[0]["src"].get("portrait") or photos[0]["src"].get("large2x") or photos[0]["src"].get("large")
    if not img_url:
        raise Exception("Pexels photo src missing.")

    img = requests.get(img_url, timeout=30)
    img.raise_for_status()

    with open(filename, "wb") as f:
        f.write(img.content)

    return filename


# Convert image to cinematic vertical clip
def image_to_video(image_path, output_path, duration=5):
    command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-vf",
        "zoompan=z='min(zoom+0.0015,1.5)':d=125:s=1080x1920",
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    subprocess.run(command, check=True)
    return output_path


# Text to speech using Edge TTS
async def text_to_speech(text, output_file):
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
    await communicate.save(output_file)


def generate_audio(script):
    audio_path = "audio.mp3"
    asyncio.run(text_to_speech(script, audio_path))
    return audio_path


# Merge clips into one video
def stitch_clips(clip_files, output="merged.mp4"):
    with open("clips.txt", "w") as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")

    subprocess.run([
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "clips.txt",
        "-c", "copy",
        output
    ], check=True)

    return output


# Add audio to video
def add_audio(video_path, audio_path, final_output="final.mp4"):
    subprocess.run([
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-shortest",
        "-c:v", "copy",
        "-c:a", "aac",
        final_output
    ], check=True)

    return final_output