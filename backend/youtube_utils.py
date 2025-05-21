from sqlalchemy.orm import Session
from fastapi import HTTPException
from googleapiclient.discovery import build
import google.auth.exceptions
from google.auth.transport.requests import Request as GoogleAuthRequest

# Assuming crud.py is in the same directory or accessible via python path
# If backend/ is a package, it would be from .crud import get_full_credentials_for_user
# For now, assuming direct import works based on typical FastAPI project structure.
# If this causes an import error later, it might need adjustment (e.g., to `from .crud ...`)
from .crud import get_full_credentials_for_user 


def fetch_user_youtube_activity(db: Session, google_id: str) -> list[dict]:
    """
    Fetches a list of the authenticated user's liked YouTube videos.
    Handles credential retrieval and token refresh.
    """
    credentials = get_full_credentials_for_user(db=db, google_id=google_id)

    if not credentials or not credentials.token:
        raise HTTPException(status_code=404, detail="User or credentials not found. Please authenticate.")

    try:
        # Handle token refresh
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(GoogleAuthRequest())
                # Note: In a production system, you might want to re-save the updated credentials
                # back to the database here (e.g., by calling create_or_update_user).
            except google.auth.exceptions.RefreshError as e:
                # Log the error for server-side review
                print(f"RefreshError for user {google_id}: {str(e)}")
                raise HTTPException(status_code=401, detail=f"Failed to refresh token: {str(e)}. Please re-authenticate.")
        
        if not credentials.valid:
            # This case can happen if the token was expired and there was no refresh token,
            # or if refresh was attempted but failed and didn't raise RefreshError immediately.
            print(f"Invalid credentials for user {google_id} after refresh attempt.")
            raise HTTPException(status_code=401, detail="Authentication token is invalid or expired. Please re-authenticate.")

        youtube_service = build('youtube', 'v3', credentials=credentials)
        
        api_request = youtube_service.videos().list(
            part='snippet,contentDetails,statistics',
            myRating='like',
            maxResults=25 
        )
        response = api_request.execute() # Synchronous call
        
        videos = []
        for item in response.get('items', []):
            video_data = {
                "id": item["id"],
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"].get("default", {}).get("url"),
                "duration": item["contentDetails"].get("duration", "N/A"),
                "viewCount": item.get("statistics", {}).get("viewCount", "0"),
                "likeCount": item.get("statistics", {}).get("likeCount", "0"),
                "channelTitle": item["snippet"].get("channelTitle", "N/A")
            }
            videos.append(video_data)
        
        return videos

    except google.auth.exceptions.RefreshError as e:
        # This handles cases where the token was already expired AND refresh failed.
        print(f"RefreshError (outer try-except) for user {google_id}: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication token expired or invalid, and refresh failed: {str(e)}. Please re-authenticate.")
    except google.auth.exceptions.GoogleAuthError as e:
        print(f"GoogleAuthError for user {google_id}: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Google authentication error: {str(e)}. Please re-authenticate.")
    except Exception as e:
        print(f"Generic error fetching YouTube activity for user {google_id}: {e}")
        # Check for specific API client errors if possible, e.g., from googleapiclient.errors.HttpError
        if hasattr(e, 'resp') and hasattr(e.resp, 'status'):
             if e.resp.status == 403:
                error_content = getattr(e, 'content', b'').decode()
                if "quotaExceeded" in error_content or "youtube.quota" in error_content:
                    raise HTTPException(status_code=429, detail="YouTube API quota exceeded. Please try again later.")
                raise HTTPException(status_code=403, detail=f"Access to YouTube API forbidden. Check API permissions or scopes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching YouTube activity: {str(e)}")
