# SnackSync

SnackSync helps you find the perfect YouTube video to watch while you eat, based on a photo of your meal and your YouTube preferences!

## Core Features

*   **Food Photo Analysis**: Upload a photo of your meal, and SnackSync (using Google's Gemini AI) will identify key food items and tags.
*   **YouTube Integration**: Securely link your YouTube account (via Google Sign-In) to allow SnackSync to access your viewing history and liked videos (read-only).
*   **Personalized Video Recommendations**: Get 1-3 video suggestions that match your food and the "vibe" of your YouTube activity, powered by Gemini AI.
*   **Session Management**: Secure JWT-based session management using HTTP-only cookies.
*   **Custom Branding**: A fun, playful interface inspired by the essence of enjoying snacks and content.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

*   **Git**: For cloning the repository.
*   **Node.js**: LTS version (e.g., 18.x or 20.x) for the frontend. Includes `npm` (or `yarn`).
*   **Python**: Version 3.9+ for the backend. Includes `pip`.
*   **PostgreSQL**: A running instance of PostgreSQL.
*   **Google Cloud Platform (GCP) Project**:
    *   YouTube Data API v3 enabled.
    *   Relevant APIs for Google Sign-In enabled (usually handled by OAuth consent screen setup).
    *   OAuth 2.0 Client ID credentials (for "Web application" type).
    *   A Gemini API Key.
*   **Web Browser**: For testing the application (e.g., Chrome, Firefox).

## Project Setup

1.  **Clone the repository:**
    ```bash
    git clone <YOUR_REPOSITORY_URL>
    cd <YOUR_PROJECT_DIRECTORY>
    ```

## Environment Variables

Before running the application, you'll need to set up your environment variables. Copy the `.env.example` file in both the `/backend` and `/frontend` directories to a new file named `.env` in their respective directories. Then, fill in the required values in each `.env` file.

**Backend (`/backend/.env`):**

*   `DATABASE_URL`: Your PostgreSQL connection string.
    *   Format: `postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@YOUR_DB_HOST:YOUR_DB_PORT/YOUR_DB_NAME`
    *   Example for local setup: `postgresql://postgres:admin@localhost:5432/snacksync_db`
    *   *Ensure the specified database exists on your PostgreSQL server.*
*   `ENCRYPTION_KEY`: A secret key for encrypting sensitive data like OAuth tokens.
    *   Generate using Python: `from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())`
*   `GEMINI_API_KEY`: Your API key for Google Gemini.
*   **Google OAuth Credentials (`client_secret.json`)**:
    *   Download your OAuth 2.0 client credentials as `client_secret.json` from the Google Cloud Console.
    *   Place this file directly inside the `/backend` directory.
*   `GOOGLE_REDIRECT_URI`: The redirect URI for your backend.
    *   For local development: `http://localhost:8000/auth/google/login` (This URI is used by the backend during token exchange. The frontend's redirect URI for Google Sign-In itself will be the one configured in Google Cloud Console, e.g., `http://localhost:5173`)
    *   *This must exactly match an "Authorized redirect URI" in your GCP OAuth client settings, specifically the one your backend uses.*
*   `JWT_SECRET_KEY`: A strong, random secret key for signing session JWTs.
    *   Generate using: `openssl rand -hex 32`
*   `JWT_ALGORITHM`: Algorithm for JWTs.
    *   Example: `HS256`

**Frontend (`/frontend/.env`):**

*   `VITE_GOOGLE_CLIENT_ID`: Your Google Cloud OAuth 2.0 Client ID (same Client ID as in `client_secret.json`).
*   `VITE_API_BASE_URL`: Base URL for your backend API.
    *   For local development: `http://localhost:8000`

## Running the Application Locally

**1. Backend Server (FastAPI):**

*   Navigate to the backend directory:
    ```bash
    cd backend
    ```
*   Create and activate a Python virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
*   Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
*   **Database Setup:**
    *   Ensure your PostgreSQL server is running.
    *   Manually create the database specified in `DATABASE_URL` if it doesn't exist (e.g., `createdb snacksync_db`).
    *   The application will attempt to create tables on startup.
*   Run the FastAPI application:
    ```bash
    uvicorn main:app --reload --port 8000
    ```
    The backend server will run on `http://localhost:8000`.

**2. Frontend Application (React + Vite):**

*   Navigate to the frontend directory (in a new terminal):
    ```bash
    cd frontend
    ```
*   Install dependencies:
    ```bash
    npm install
    ```
*   Run the frontend development server:
    ```bash
    npm run dev
    ```
    The frontend will typically be available at `http://localhost:5173`.

## Local Testing Guide

Once both servers are running:

1.  Open the frontend URL (e.g., `http://localhost:5173`) in your browser.
2.  **Sign In**: Use the "Sign in with Google" button. Grant permissions.
3.  **Analyze Food**: Upload an image and get food tags.
4.  **Fetch YouTube Activity**: Click "Fetch My Liked YouTube Videos".
5.  **Get Recommendations**: Click "Get Video Recommendations".
6.  **Sign Out**: Test the sign-out functionality.

**Troubleshooting Tips:**
*   Check your browser's Developer Console (Network and Console tabs).
*   Monitor the backend terminal output for logs and errors.

## API Documentation

For detailed information about the API endpoints, request/response formats, and authentication, please refer to the [API_CONTRACT.MD](./API_CONTRACT.MD) file.
