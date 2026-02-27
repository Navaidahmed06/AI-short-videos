from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_workflow
from youtube_service import upload_to_youtube
from db import collection
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str

@app.post("/generate")
def generate(data: TopicRequest):
    result = run_workflow(data.topic)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    video_path = result.get("video")

    if video_path:
        if not os.path.exists(video_path):
            result["youtube"] = {"error": "video file not found, upload skipped"}
        else:
            try:
                upload = upload_to_youtube(
                    video_path,
                    result.get("topic"),
                    result.get("script")
                )
                result["youtube"] = upload
            except Exception as e:
                result["youtube"] = {"error": str(e)}
    else:
        result["youtube"] = {"skipped": "no video generated"}

    db_result = collection.insert_one(result)
    result["_id"] = str(db_result.inserted_id)
    return result