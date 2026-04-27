# backend/auth.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
import google.auth.transport.requests
import google.oauth2.id_token
from google_auth_oauthlib.flow import Flow
import pathlib
import json

from models import TokenData, GoogleOAuthURL, UserInfo

load_dotenv()

router = APIRouter()

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/drive.file"
]

# In production, use a proper database or cache for token storage
# For simplicity, we'll use a dictionary (not suitable for production)
user_tokens = {}

@router.get("/google", response_model=GoogleOAuthURL)
async def login_google():
    """Generate Google OAuth URL"""
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    # Store state in user session (in production, use proper session management)
    # For simplicity, we're returning state in the URL and will validate in callback
    return {"auth_url": authorization_url}

@router.get("/google/callback")
async def auth_google_callback(request: Request, state: str = None, code: str = None):
    """Handle Google OAuth callback"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")

    try:
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES,
            state=state,
        )
        flow.redirect_uri = REDIRECT_URI

        # Exchange authorization code for tokens
        flow.fetch_token(code=code)

        # Get user info
        credentials = flow.credentials
        request_session = google.auth.transport.requests.Request()
        id_info = google.oauth2.id_token.verify_oauth2_token(
            credentials.id_token, request_session, GOOGLE_CLIENT_ID
        )

        user_info = UserInfo(
            id=id_info["sub"],
            email=id_info["email"],
            name=id_info.get("name", ""),
            picture=id_info.get("picture"),
        )

        # Store tokens (in production, encrypt and store in database)
        token_data = TokenData(
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            expires_at=credentials.expiry,
        )

        # For simplicity, we're storing in memory with user ID as key
        # In production, use a secure, persistent store
        user_tokens[user_info.id] = token_data

        # Redirect to frontend with user info (or create JWT)
        # For now, we'll just return the user info
        return {
            "user": user_info.dict(),
            "access_token": token_data.access_token,
            "refresh_token": token_data.refresh_token,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/me")
async def get_user_info(token: str = None):
    """Get current user info (placeholder for JWT validation)"""
    # In a real app, validate the JWT token and return user info
    # For now, we'll return a placeholder
    return {"message": "User info endpoint - implement JWT validation"}