import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from pydantic import BaseModel
from typing import Optional

load_dotenv()

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://adcpdkadrnzjcugumseo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_KEY:
    print("WARNING: SUPABASE_KEY not set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
security = HTTPBearer(auto_error=False)


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None


class AuthResponse(BaseModel):
    user: UserResponse
    session: dict


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user from Supabase JWT"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        token = credentials.credentials
        user = supabase.auth.get_user(token)

        if not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Optional user - returns None if not authenticated"""
    if not credentials:
        return None

    try:
        token = credentials.credentials
        user = supabase.auth.get_user(token)
        return user.user
    except:
        return None


class TokenVerifyRequest(BaseModel):
    token: str


@router.post("/verify", response_model=UserResponse)
async def verify_token(request: TokenVerifyRequest):
    """Verify Supabase token from frontend and return user info"""
    try:
        user = supabase.auth.get_user(request.token)

        if not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return UserResponse(
            id=user.user.id,
            email=user.user.email,
            name=user.user.user_metadata.get("full_name"),
            picture=user.user.user_metadata.get("avatar_url")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """Get current authenticated user"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.user_metadata.get("full_name"),
        picture=current_user.user_metadata.get("avatar_url")
    )


@router.get("/session")
async def get_session(current_user = Depends(get_current_user)):
    """Get user session info"""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "metadata": current_user.user_metadata
    }


@router.get("/users")
async def get_users(current_user = Depends(get_current_user)):
    """Get all users from profiles table (requires auth)"""
    try:
        result = supabase.table("profiles").select("*").execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
async def get_user(user_id: str, current_user = Depends(get_current_user)):
    """Get specific user profile"""
    try:
        result = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "data": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/profile")
async def create_or_update_profile(
    name: Optional[str] = None,
    picture: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Create or update user profile in profiles table"""
    try:
        profile_data = {
            "id": current_user.id,
            "email": current_user.email,
            "updated_at": "now()"
        }
        if name:
            profile_data["name"] = name
        if picture:
            profile_data["picture"] = picture

        result = supabase.table("profiles").upsert(profile_data).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/signout")
async def sign_out(current_user = Depends(get_current_user)):
    """Sign out current user"""
    try:
        supabase.auth.sign_out()
        return {"success": True, "message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))