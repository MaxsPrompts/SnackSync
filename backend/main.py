from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Depends, Response # Added Response
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import timedelta # Added timedelta
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import io
from sqlalchemy.orm import Session
from pydantic import BaseModel # For request body model

from .database import create_db_and_tables, get_db
from .crud import create_or_update_user, get_db_session
from .youtube_utils import fetch_user_youtube_activity
from .recommendation_logic import construct_recommendation_prompt, get_gemini_recommendations
from .auth_utils import create_access_token, get_current_active_user_google_id # Added get_current_active_user_google_id
from typing import List

# Google Auth specific imports
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
# Removed: from google.auth.transport.requests import Request as GoogleAuthRequest
# Removed: import google.auth.exceptions
# Removed: from googleapiclient.discovery import build

import requests # For requests.Session() used in verify_oauth2_token

load_dotenv() # Load environment variables from .env file

# --- Environment Variable Checks ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
CLIENT_SECRET_FILE = "client_secret.json"
JWT_SECRET_KEY_ENV = os.getenv("JWT_SECRET_KEY") # For check
JWT_ALGORITHM_ENV = os.getenv("JWT_ALGORITHM") # For check


if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY is not set. Image analysis will fail.")
if not DATABASE_URL:
    print("Warning: DATABASE_URL is not set. Database operations will fail.")
if not ENCRYPTION_KEY:
    print("Warning: ENCRYPTION_KEY is not set. Token encryption/decryption will fail.")
if not GOOGLE_CLIENT_ID: 
    print("Warning: GOOGLE_CLIENT_ID is not set. Google OAuth login may fail at token verification.")
if not GOOGLE_REDIRECT_URI:
    print("Warning: GOOGLE_REDIRECT_URI is not set. Google OAuth login will fail.")
if not os.path.exists(CLIENT_SECRET_FILE):
    print(f"Warning: {CLIENT_SECRET_FILE} not found. Google OAuth login will fail if it's the primary method for client secrets.")
if not JWT_SECRET_KEY_ENV:
    print("CRITICAL: JWT_SECRET_KEY is not set. Authentication will fail.")
if not JWT_ALGORITHM_ENV:
    print("Warning: JWT_ALGORITHM is not set. Defaulting to HS256, but this should be explicitly defined.")
# --- End Environment Variable Checks ---

# Configure Gemini API Key (only if set, to allow startup without it for other tasks)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    pass 


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Running startup event: Creating database and tables if they don't exist.")
    if DATABASE_URL:
        create_db_and_tables()
    else:
        print("DATABASE_URL not set, skipping table creation.")

# Pydantic model for the /auth/google/login request body
class AuthCodeRequest(BaseModel):
    code: str

# Google OAuth Scopes
SCOPES = ['openid', 'email', 'profile', 'https://www.googleapis.com/auth/youtube.readonly']


@app.post("/auth/google/login")
async def auth_google_login(auth_request: AuthCodeRequest, response: Response, db: Session = Depends(get_db)): # Added response: Response
    if not JWT_SECRET_KEY_ENV: # Re-check here to ensure app doesn't run with this broken
        raise HTTPException(status_code=500, detail="JWT_SECRET_KEY is not configured on the server.")
    if not os.path.exists(CLIENT_SECRET_FILE):
         raise HTTPException(status_code=500, detail=f"{CLIENT_SECRET_FILE} not found. Please ensure it is present in the backend directory.")
    if not GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="GOOGLE_REDIRECT_URI is not configured on the server.")

    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI
        )
    except FileNotFoundError:
        # This check is somewhat redundant due to the one above, but good for safety.
        raise HTTPException(status_code=500, detail=f"{CLIENT_SECRET_FILE} not found.")
    except Exception as e:
        print(f"Error initializing Google Auth flow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initializing Google Auth flow: {str(e)}")

    try:
        flow.fetch_token(code=auth_request.code)
        credentials = flow.credentials
    except Exception as e:
        print(f"Error fetching token from Google: {e}") # Log full error
        raise HTTPException(status_code=400, detail=f"Failed to fetch token from Google: {str(e)}. Ensure the auth code is valid and GOOGLE_REDIRECT_URI is correctly set and matches the one in Google Cloud Console.")

    if not credentials or not credentials.id_token:
        raise HTTPException(status_code=400, detail="Could not retrieve ID token from Google. Credentials might be incomplete.")

    try:
        # Use a requests.Session for the transport request, as it's synchronous
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google.auth.transport.requests.Request(session=requests.Session()),
            os.getenv("GOOGLE_CLIENT_ID") # Audience check
        )
        google_id = id_info['sub']
        email = id_info.get('email')
    except Exception as e:
        print(f"Error verifying ID token: {e}") # Log full error
        raise HTTPException(status_code=400, detail=f"Invalid ID token: {str(e)}")

    try:
        user = create_or_update_user(
            db=db,
            google_id=google_id,
            access_token=credentials.token, # Corrected: credentials.token is the access token
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id_g=credentials.client_id,
            client_secret_g=credentials.client_secret,
            scopes_g=credentials.scopes
        )
    except Exception as e:
        # This could be a database error or encryption error
        print(f"Error creating or updating user: {e}") # Log full error
        raise HTTPException(status_code=500, detail=f"Database or encryption error: {str(e)}")
    
    # Generate JWT
    jwt_payload = {"sub": user.google_id, "email": email}
    session_jwt = create_access_token(data=jwt_payload)

    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_jwt,
        httponly=True,
        samesite="Lax", 
        secure=False, # Set to False for HTTP localhost testing, True for HTTPS production
        max_age= int(timedelta(minutes=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7)).total_seconds()), # Use env var or default
        path="/"
    )
    return {"message": "User authenticated successfully", "email": email, "google_id": user.google_id}


@app.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="session_token", 
        httponly=True, 
        samesite="Lax", 
        secure=False, # Match secure flag from set_cookie
        path="/"
    )
    return {"message": "Successfully logged out"}


@app.get("/api/youtube_activity")
async def get_youtube_activity(db: Session = Depends(get_db_session), current_google_id: str = Depends(get_current_active_user_google_id)):
    """
    Fetches liked YouTube videos for the authenticated user.
    The core logic, including credential fetching, token refresh, and YouTube API interaction,
    is handled by fetch_user_youtube_activity.
    This endpoint remains async to align with FastAPI best practices, even if the underlying
    utility function is currently synchronous. If fetch_user_youtube_activity involved
    significant blocking I/O not suitable for an event loop, it would be run
    in a thread pool (e.g., using await asyncio.to_thread(fetch_user_youtube_activity, ...)).
    For now, direct call is fine as the blocking part (API call) is relatively short.
    """
    try:
        # Since fetch_user_youtube_activity is synchronous, we call it directly.
        # If it were to become truly async (e.g., using an async HTTP client for YouTube),
        # then 'await' would be used here.
        # If it remained synchronous but was very long-running, we might use:
        # videos = await asyncio.to_thread(fetch_user_youtube_activity, db, current_google_id)
        videos = fetch_user_youtube_activity(db=db, google_id=current_google_id)
        return videos
    except HTTPException as e:
        # Re-raise HTTPException directly as it's already an appropriate FastAPI response
        raise e
    except Exception as e:
        # Catch any other unexpected errors from the utility function
        # (though it's designed to raise HTTPExceptions itself for known error cases)
        print(f"Unexpected error in /api/youtube_activity endpoint for user {current_google_id}: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching YouTube activity.")


@app.post("/api/suggest_video") # This endpoint remains unprotected as it doesn't require user context
async def suggest_video(file: UploadFile = File(...)):
    try:
        # Instantiate the generative model
        # Using gemini-1.5-flash as it's generally available and suitable for this kind of task.
        # Changed from 'gemini-1.5-flash-latest' to specific version 'gemini-1.5-flash' for stability
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Read the image content
        image_bytes = await file.read()
        
        # Open the image using Pillow
        # This also helps to validate if it's a valid image file
        try:
            img = Image.open(io.BytesIO(image_bytes))
            # You might want to check img.format here to ensure it's a supported type by Gemini
            # For now, we assume Gemini can handle common web formats like JPEG, PNG.
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

        # Create the prompt for Gemini
        prompt = "Analyze the food items in this image and return a comma-separated list of descriptive tags. Examples: 'pizza, cheese, tomato', 'burger, fries, soda'. If no food is detected, or if the image does not contain recognizable food items, return an empty string or 'No food detected'."

        # Make the API call
        # The model.generate_content_async expects a list of parts
        response = await model.generate_content_async([prompt, img])
        
        tags_text = response.text

        # Process tags_text to create a list of tags
        if tags_text.strip().lower() == "no food detected" or not tags_text.strip():
            detected_tags = []
        else:
            detected_tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            # Filter out any potential "no food detected" if it's part of a list somehow
            detected_tags = [tag for tag in detected_tags if tag.lower() != "no food detected"]


        return JSONResponse(content={
            "filename": file.filename,
            "content_type": file.content_type,
            "detected_tags": detected_tags
        })

    except Exception as e:
        # Log the exception for server-side review
        print(f"Error processing image with Gemini: {str(e)}")
        # Check if the exception is from genai and if it has specific error details
        if hasattr(e, 'message'):
            error_detail = e.message
        else:
            error_detail = str(e)
        raise HTTPException(status_code=500, detail=f"Error processing image with Gemini: {error_detail}")

if __name__ == "__main__":
    # Enhanced warnings for missing env vars
    missing_vars = []
    if not GEMINI_API_KEY: missing_vars.append("GEMINI_API_KEY")
    if not DATABASE_URL: missing_vars.append("DATABASE_URL")
    if not ENCRYPTION_KEY: missing_vars.append("ENCRYPTION_KEY")
    if not GOOGLE_CLIENT_ID: missing_vars.append("GOOGLE_CLIENT_ID")
    if not GOOGLE_REDIRECT_URI: missing_vars.append("GOOGLE_REDIRECT_URI")
    if not JWT_SECRET_KEY_ENV: missing_vars.append("JWT_SECRET_KEY") # Added JWT key check
    # JWT_ALGORITHM_ENV can default, so not critical to list if missing, but good to set.
    if not os.path.exists(CLIENT_SECRET_FILE) and not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        missing_vars.append(f"{CLIENT_SECRET_FILE} (or GOOGLE_CLIENT_ID/SECRET if applicable for other flows)")


    if missing_vars:
        print("---------------------------------------------------------------------")
        print("Warning: Critical environment variables or files are missing:")
        for var in missing_vars:
            print(f"  - {var}")
        print("Application functionality will be significantly limited or fail.")
        print("Please check your .env file and ensure client_secret.json is present.")
        print("---------------------------------------------------------------------")
    uvicorn.run(app, host="0.0.0.0", port=8000)


# --- Pydantic Models for API Requests ---
class RecommendationRequest(BaseModel):
    food_tags: List[str]
    # google_id: str # Removed, will use current_google_id from JWT
    # meal_type: Optional[str] = "unknown" 

# --- API Endpoints ---

@app.post("/api/recommend_video")
async def recommend_video(request_data: RecommendationRequest, db: Session = Depends(get_db_session), current_google_id: str = Depends(get_current_active_user_google_id)):
    youtube_activity = [] # Default to empty list
    try:
        # Fetch YouTube activity for the authenticated user.
        youtube_activity = fetch_user_youtube_activity(db=db, google_id=current_google_id)
        if not youtube_activity:
            print(f"No YouTube activity found for user {current_google_id} or user not found. Proceeding with food tags only.")
            youtube_activity = [] 
    except HTTPException as e:
        print(f"HTTPException while fetching YouTube activity for {current_google_id}: {e.detail} (status: {e.status_code}). Proceeding without activity.")
        youtube_activity = []
    except Exception as e:
        print(f"Unexpected error fetching YouTube activity for {current_google_id}: {str(e)}. Proceeding without activity.")
        youtube_activity = []

    # Construct the prompt
    prompt = construct_recommendation_prompt(
        food_tags=request_data.food_tags,
        youtube_activity=youtube_activity
        # meal_type=request_data.meal_type if hasattr(request_data, 'meal_type') and request_data.meal_type else "unknown"
    )
    if prompt == "Cannot generate recommendations without any food tags or YouTube activity." and not request_data.food_tags:
         raise HTTPException(status_code=400, detail="Cannot generate recommendations without food tags if YouTube activity is also unavailable.")


    # Get recommendations from Gemini
    try:
        gemini_recs = await get_gemini_recommendations(prompt)
        if not gemini_recs: # Handles empty list from Gemini (e.g., if it genuinely found nothing or internal Gemini issue)
            # This could be a 200 OK with an empty list, or a 404 if we consider "no recommendations" an error.
            # For now, let's return 200 with empty list as per get_gemini_recommendations design.
            # If get_gemini_recommendations itself raised an error (e.g. API key issue), it would be caught below.
            print(f"Gemini returned no recommendations for user {current_google_id} with food tags {request_data.food_tags}.")
            # If an empty list is a valid "no recommendations found" scenario from Gemini:
            return [] # Or: return {"message": "No suitable recommendations found.", "recommendations": []}
            # If we want to treat an empty list from Gemini as more of an issue:
            # raise HTTPException(status_code=404, detail="Gemini could not provide recommendations based on the input.")

    except Exception as e: # Catch errors from get_gemini_recommendations itself (e.g. API key not set)
        print(f"Error getting recommendations from Gemini for user {current_google_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations from Gemini: {str(e)}")

    # Data Enrichment step would go here if implemented.
    # For this iteration, we assume Gemini provides video_id, title, and reason.

    return gemini_recs
