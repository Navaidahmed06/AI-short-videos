import os
import pickle
import socket
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _find_free_port():
    """Return an available port number on localhost.
    Using port=0 with run_local_server usually works, but explicitly
    finding a free port avoids clashes on Windows when a previous
    server hasn't released the port yet.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def upload_to_youtube(video_path, title, description):
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        # pick a free port instead of hardcoding to avoid socket errors
        port = _find_free_port()
        try:
            creds = flow.run_local_server(port=port)
        except OSError as exc:
            # fallback: let the library pick any available port
            creds = flow.run_local_server(port=0)

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