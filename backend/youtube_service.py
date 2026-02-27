import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_to_youtube(video_path, title, description):
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        # Use a fixed port that matches the registered redirect URI
        creds = flow.run_local_server(port=8000)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["AI", "Shorts"],
                "categoryId": "22"
            },
            "status": {"privacyStatus": "private"}
        },
        media_body=MediaFileUpload(video_path)
    )

    response = request.execute()
    return response