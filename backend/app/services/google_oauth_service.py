from fastapi import HTTPException
import httpx
from ..config import settings

async def verify_google_token(id_token: str) -> dict:
    """Verify Google ID token and extract user info"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Google token")
            
            token_info = response.json()
            
            # Verify the token is for our app
            if token_info.get('aud') != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(status_code=401, detail="Token audience mismatch")
            
            return {
                'google_id': token_info['sub'],
                'email': token_info['email'],
                'name': token_info.get('name', ''),
                'avatar_url': token_info.get('picture')
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=401, detail=f"Failed to verify token: {str(e)}")


async def get_google_user_info(access_token: str) -> dict:
    """Get user info from Google using access token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Failed to get user info")
            
            user_info = response.json()
            
            return {
                'google_id': user_info['id'],
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'avatar_url': user_info.get('picture')
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=401, detail=f"Failed to get user info: {str(e)}")