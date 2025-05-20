
SnackSync: Core Problem-Solving Gameplan (MVP Focus)
Core Problem: Finding the right YouTube video to watch while eating is a hassle, leading to decision fatigue and cold food.

Core Solution: Instantly suggest relevant YouTube videos based on a photo of the user's current meal and their YouTube preferences.

1. Essential Core Features (MVP):
* Simplified Food Photo Upload & Basic Analysis: User uploads a photo. System extracts key food items/tags (e.g., "pizza," "coffee," "salad").
* YouTube Account Link (Read-Only): Securely connect to user's YouTube account (via Google Sign-In) to access viewing history/liked videos for taste preferences.
* Core Video Recommendation Logic: Match detected food tags with YouTube viewing history to find 1-3 highly relevant video suggestions.
* Display Recommendation & Play: Clearly show the top video suggestion with an option to play it (e.g., embedded or link to YouTube).

2. Lean Technology Stack:
* Frontend: React (or similar simple framework like Svelte/Vue) for the image upload and video display.
* Backend: Python with FastAPI (quick to develop, good for API).
* Image Analysis: Google Cloud Vision AI (for identifying items in the food photo).
* Database: PostgreSQL (to store user-YouTube links and basic snap-to-recommendation history for learning).
* YouTube Integration: YouTube Data API v3 (via Google API Client Libraries).
* Authentication: Google Sign-In (OAuth 2.0).

3. Minimal API Design:
* POST /auth/google/login: Authenticate user, get YouTube access.
* POST /api/suggest_video: User uploads food image.
* Request: Image file.
* Response: Top video suggestion(s) (title, thumbnail, YouTube link/ID).

4. Barebones Database Schema:
* Users Table:
* user_id (PK)
* google_id (Unique)
* youtube_access_token (Encrypted)
* youtube_refresh_token (Encrypted)
* Snaps Table (Optional for MVP, but good for future learning):
* snap_id (PK)
* user_id (FK to Users)
* image_identifier (e.g., path to stored image or hash)
* detected_tags (Array of Strings)
* recommended_video_id (String)
* timestamp

5. Core UI/UX Focus:
* One-Click Google Sign-In.
* Prominent "Snap Food" Button: Dead simple image capture/upload.
* Instant Gratification: Quickly show the top recommended video. Minimal loading.
* Clear "Watch Now" Action: No ambiguity on how to play the video.
* No Clutter: Focus solely on the snap -> recommend -> watch flow.

6. Simple Deployment Strategy:
* Frontend: Firebase Hosting (easy static hosting).
* Backend & Image Analysis: Google Cloud Run for the FastAPI backend (integrates easily with Vision AI).
* Database: Google Cloud SQL for PostgreSQL (managed instance).

7. Post-MVP (After Core Problem is Solved & Validated):
* Refine recommendation algorithm based on user feedback (implicit like watching full video, explicit like "thumbs up/down" on suggestion).
* Introduce user preferences (e.g., preferred video length, auto-play).
* Expand context awareness (time of day, etc.).
* All other previously listed "Future Enhancements."

