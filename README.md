SnackSync 🍕📺

To test locally, you'll need to:

Set up prerequisites: Node.js, Python, PostgreSQL, and Google Cloud credentials (OAuth Client ID with correct localhost URIs, Gemini API key).
Configure .env files in both frontend (with VITE_GOOGLE_CLIENT_ID, VITE_API_BASE_URL) and backend (with DATABASE_URL, GEMINI_API_KEY, ENCRYPTION_KEY, Google OAuth details if not using client_secret.json directly for all parts).
Run the backend: cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000.
Run the frontend: cd frontend && npm install && npm run dev.
Then, test each feature: Sign-In, Image Upload & Tagging, YouTube Activity Fetching, and Recommendations. Check browser console and backend terminal for errors.

Tired of your food getting cold while you search for the perfect YouTube video? SnackSync instantly pairs your meal with the ideal vibe.

Snap a photo of your food, and SnackSync analyzes it—what you’re eating, where, and when. Then, it taps into your YouTube account to recommend or auto-play the best-matching video: a calming vlog for your morning coffee, a fast-paced mukbang for your takeout, or something educational for your study snack.

The goal: Mood-based content syncing, triggered by your snack, for zero-effort enjoyment.

The Problem We Solve
People love eating while watching YouTube, but finding the perfect video quickly is tough.

Decision fatigue: Endless scrolling while hunger grows.
Misaligned moods: Random recommendations don't match your mealtime vibe.
Lack of context: YouTube doesn't know what you're eating right now.
Our Solution: SnackSync
SnackSync is your zero-effort content matcher. It creates the right atmosphere for your meal by understanding your snack and syncing it with your YouTube taste.

Food Photo as Context: A quick snap provides rich, real-time information about your meal.
Personalized from Your YouTube: Leverages your watch history and subscriptions to know your preferences.
Instant Vibe Delivery: One action, and the perfect video starts playing.
Why SnackSync?
We're bridging the gap between your immediate craving for food and your desire for perfectly paired content. SnackSync aligns with how we live now:

Micro-moments: Ideal for those 5-15 minute content bursts.
Context-aware AI: Smart software that understands your "right now."
Media/Food Fusion: Eating and watching are becoming a unified experience.
SnackSync solves the hunger gap—not of food, but of content harmony.
Because when your food’s hot, your video shouldn’t be cold.

Perfect. Let’s rebuild the first principles analysis around **that core problem statement**:

> **“People love eating while watching YouTube videos, but it’s becoming increasingly more difficult to find the perfect video to munch to.”**


### 1. **Core Human Behavior (Base Reality)**

* **People pair food with content**. It’s comforting, habitual, and emotionally soothing.
* **YouTube is the default background** for solo eating. Not just entertainment, but companionship.
* **The "perfect" video is hard to find when you’re hungry and impatient**. Search fatigue kicks in. Time is wasted. Mood slips.

---

### 2. **Root Problems**

* **Decision fatigue**: Scrolling through options while food gets cold.
* **Misalignment**: Random video recommendations don’t match the vibe of the meal or mood.
* **Lack of context** in algorithms: YouTube doesn’t know what you’re eating *right now*.

---

### 3. **Core Truths**

* A photo of food is a strong real-time context cue (type of meal, time of day, mood).
* YouTube watch history and subs are a proxy for taste and personality.
* Good content syncing should be **low effort**, **real-time**, and **emotionally resonant**.

---

### 4. **What SnackSync *is* at its essence**

SnackSync is a **zero-effort content matcher**.
It creates **the right vibe for your meal** by reading your snack and syncing it with your YouTube taste.

---

### 5. **Principle-Level System**

| Component       | Principle                         |
| --------------- | --------------------------------- |
| Food photo      | Real-time emotional context       |
| YouTube account | Taste and identity graph          |
| Video matching  | Mood-aligned media syncing        |
| UX              | One action, instant vibe delivery |

---

### 6. **What Makes This *Inevitable***

SnackSync aligns three growing trends:

* **Micro-moments**: People want 5–15 minute content bursts.
* **Context-aware AI**: Devices and software that know “what’s going on right now.”
* **Media/food fusion**: Eating and watching are converging into a unified experience.

---

### Final Statement:

**SnackSync solves the hunger gap—not of food, but of *content harmony*.**
Because when your food’s hot, your video shouldn’t be cold.

