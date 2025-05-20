import google.generativeai as genai
import json
import os
from typing import List, Dict

# Configure Gemini API Key at the module level.
# This will be executed once when the module is first imported.
# In a larger application, this might be handled in a central configuration spot (e.g., main.py startup).
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Gemini API configured successfully in recommendation_logic.py.")
    except Exception as e:
        print(f"Error configuring Gemini API in recommendation_logic.py: {e}")
else:
    print("Warning: GEMINI_API_KEY not found in environment variables. Gemini recommendations will not work.")


def _determine_meal_type_heuristic(food_tags: List[str]) -> str:
    """
    A simple heuristic to determine meal_type based on food tags.
    This is a placeholder and can be expanded.
    """
    snack_keywords = ["chip", "chips", "cookie", "cookies", "popcorn", "candy", "fruit", "nuts", "yogurt", "cracker"]
    meal_keywords = ["pizza", "pasta", "steak", "burger", "salad", "soup", "curry", "rice bowl", "taco", "burrito", "sandwich"]
    
    for tag in food_tags:
        tag_lower = tag.lower()
        if any(keyword in tag_lower for keyword in snack_keywords):
            return "snack"
        if any(keyword in tag_lower for keyword in meal_keywords):
            return "meal"
    return "unknown"


def construct_recommendation_prompt(food_tags: List[str], youtube_activity: List[Dict], meal_type: str = "unknown") -> str:
    """
    Constructs a detailed prompt for Gemini to recommend YouTube videos.
    """
    
    if not food_tags and not youtube_activity:
        # Or handle this case by returning a specific message or raising an error
        return "Cannot generate recommendations without any food tags or YouTube activity."

    # Determine meal_type if not provided or 'unknown'
    if meal_type == "unknown" and food_tags:
        meal_type = _determine_meal_type_heuristic(food_tags)

    # Format YouTube activity
    formatted_youtube_activity_parts = []
    # Limit to, for example, top 10 videos to keep the prompt concise
    for video in youtube_activity[:10]: 
        title = video.get('title', 'N/A')
        channel = video.get('channelTitle', 'N/A')
        duration = video.get('duration', 'N/A') # Assuming duration is already formatted (e.g., "PT15M3S")
        formatted_youtube_activity_parts.append(
            f"- Title: {title}, Channel: {channel}, Duration: {duration}"
        )
    
    if not formatted_youtube_activity_parts:
        formatted_youtube_activity_string = "User has no recent YouTube activity provided, or it could not be formatted."
    else:
        formatted_youtube_activity_string = "\n".join(formatted_youtube_activity_parts)

    food_tags_string = ', '.join(food_tags) if food_tags else "no specific food characteristics"

    prompt = f"""You are SnackSync, a YouTube video recommendation assistant that suggests videos to watch while eating.

The user is eating food with these characteristics: {food_tags_string}.
They are having a '{meal_type}'. Please suggest videos of an appropriate length: typically shorter (under 15 mins) for a snack, and medium (15-45 mins) or longer (45+ mins) for a meal. If the meal type is 'unknown', use your best judgment.

Here's a summary of some of their recently liked YouTube videos:
{formatted_youtube_activity_string}

Based on the food, the meal context, and their viewing history, please recommend 1 to 3 YouTube videos.
For each recommendation, provide the YouTube Video ID, the video title, and a short 1-2 sentence reason explaining why this video is a good match, considering the food and their viewing vibe.

Output your recommendations ONLY as a valid JSON list of objects. Each object in the list should have the following keys: "video_id", "title", "reason".
Example: [{"video_id": "dQw4w9WgXcQ", "title": "Never Gonna Give You Up", "reason": "This classic song is great for any meal!"}]
If you cannot find any suitable recommendations, return an empty JSON list [].
"""
    return prompt


async def get_gemini_recommendations(prompt: str) -> List[Dict]:
    """
    Gets video recommendations from Gemini based on the constructed prompt.
    Returns a list of recommendation dictionaries or an empty list if issues occur.
    """
    if not GEMINI_API_KEY:
        print("Gemini API key not configured. Cannot fetch recommendations.")
        return []

    try:
        # Initialize the model. Ensure 'gemini-1.5-flash-latest' or your desired model is available.
        # Using 'gemini-1.5-flash' for potentially better stability over 'latest' alias
        model = genai.GenerativeModel('gemini-1.5-flash') 

        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        
        # generate_content_async is the correct method for async calls with the Python SDK
        response = await model.generate_content_async(
            prompt,
            generation_config=generation_config
        )
        
        response_text = response.text
        
        try:
            recommendations = json.loads(response_text)
            if not isinstance(recommendations, list):
                print(f"Gemini response was valid JSON but not a list: {recommendations}")
                return [] # Or handle as an error
            # Optionally, validate structure of each dict in the list here
            return recommendations
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gemini JSON response: {e}")
            print(f"Raw Gemini response text: {response_text}")
            return [] # Or raise a custom exception

    except Exception as e:
        # Catching a broad exception here to handle any errors during the API call or processing.
        # Specific exceptions from genai library can be caught if needed (e.g., genai.types.BlockedPromptError)
        print(f"Error getting recommendations from Gemini: {e}")
        return []
