import google.generativeai as genai
import os
from dotenv import load_dotenv
import asyncio
import edge_tts
import subprocess
from visuals import generate_image, image_to_video, generate_audio, stitch_clips, add_audio
import uuid


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_script(topic):
    prompt = f"""
    Create a highly engaging 45-second YouTube Shorts script about:
    {topic}

    Start with a strong hook.
    Don't add any explanations or disclaimers of scene - just the script.
    For example, if the topic is "The Power of AI", a scene could be:
"Scene 1: A person struggling to find information, then discovering an AI assistant that provides
instant answers, showcasing the transformative power of AI in everyday life."

    Keep the script concise, energetic, and focused on capturing attention quickly.
    Divide the script into 4 distinct scenes that can be visually represented.
    Don't mention seconds or timing in the script - just the content of each scene.
    Keep it concise and energetic.
    """

    response = model.generate_content(prompt)
    return response.text



# async def text_to_speech(text, output_file):
#     communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
#     await communicate.save(output_file)

# def generate_audio(script):
#     output = "audio.mp3"
#     asyncio.run(text_to_speech(script, output))
#     return output



# def _format_srt_time(seconds: float) -> str:
#     # convert float seconds to SRT timestamp (hh:mm:ss,ms)
#     hrs = int(seconds // 3600)
#     mins = int((seconds % 3600) // 60)
#     secs = int(seconds % 60)
#     ms = int((seconds - int(seconds)) * 1000)
#     return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"


# def _create_subtitles(script: str, duration: float = 45.0) -> str:
#     """Write an SRT file dividing the script into equal-duration captions.
#     Returns the filepath of the subtitle file.
#     """
#     # split into sentences; fallback to whole text if none found
#     sentences = [s.strip() for s in script.replace("\n", " ").split('.') if s.strip()]
#     if not sentences:
#         sentences = [script.strip()]
#     count = len(sentences)
#     per = duration / count

#     srt_lines = []
#     for idx, sent in enumerate(sentences, start=1):
#         start = (idx - 1) * per
#         end = start + per
#         srt_lines.append(str(idx))
#         srt_lines.append(f"{_format_srt_time(start)} --> {_format_srt_time(end)}")
#         srt_lines.append(sent)
#         srt_lines.append("")

#     subtitle_path = "subs.srt"
#     with open(subtitle_path, "w", encoding="utf-8") as f:
#         f.write("\n".join(srt_lines))
#     return subtitle_path


# def generate_video(script):
#     audio_path = generate_audio(script)
#     video_path = "output.mp4"

#     # ensure ffmpeg is available
#     import shutil
#     if shutil.which("ffmpeg") is None:
#         raise RuntimeError("ffmpeg binary not found; please install ffmpeg and add to PATH")

#     # generate subtitles for script so the viewer sees text
#     subtitle_file = _create_subtitles(script)

#     command = [
#         "ffmpeg",
#         "-f", "lavfi",
#         "-i", "color=c=black:s=1080x1920:d=45",
#         "-i", audio_path,
#         "-vf", f"subtitles={subtitle_file}:force_style='Fontsize=48,PrimaryColour=&Hffffff&,Alignment=2'",
#         "-shortest",
#         "-c:v", "libx264",
#         "-c:a", "aac",
#         "-pix_fmt", "yuv420p",
#         video_path
#     ]

#     subprocess.run(command, check=True)
#     return video_path



def run_workflow(topic):
    try:
        script = generate_script(topic)

        # Split script into 4 scenes
        scenes = [s.strip() for s in script.split("\n") if s.strip()][:4]

        clip_files = []

        for i, scene in enumerate(scenes):
            image_file = f"scene_{i}.png"
            clip_file = f"clip_{i}.mp4"

            clean_prompt = scene.replace("\n", " ").replace(":", "")
            generate_image(clean_prompt, image_file)

            image_to_video(image_file, clip_file, duration=5)

            clip_files.append(clip_file)

        merged_video = stitch_clips(clip_files)

        audio_path = generate_audio(script)

        final_video = add_audio(merged_video, audio_path)

        return {
            "topic": topic,
            "script": script,
            "video": final_video
        }

    except Exception as e:
        return {"error": str(e)}