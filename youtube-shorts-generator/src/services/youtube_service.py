"""
YouTube Data API v3: OAuth, upload video, metadata, token refresh.
"""
import os
from pathlib import Path
from typing import Optional

def get_authenticated_service():
    """Build authenticated YouTube API service (OAuth)."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
    creds = None
    token_path = Path("youtube_token.json")
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("YOUTUBE_CREDENTIALS_JSON", "client_secrets.json"), scopes
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def upload_video(
    file_path: Path,
    title: str,
    description: str = "",
    tags: Optional[list] = None,
    privacy: str = "private",
) -> str:
    """Upload video; return YouTube video ID."""
    service = get_authenticated_service()
    from googleapiclient.http import MediaFileUpload
    body = {"snippet": {"title": title, "description": description, "tags": tags or []}, "status": {"privacyStatus": privacy}}
    media = MediaFileUpload(str(file_path), mimetype="video/mp4", resumable=True)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response["id"]
