import os
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError
import requests
from functools import lru_cache
from sqlalchemy.orm import Session
import crud
from database import SessionLocal
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# Auth0 settings
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_IDENTIFIER = os.getenv("AUTH0_API_IDENTIFIER")

if not AUTH0_DOMAIN or not AUTH0_API_IDENTIFIER:
    raise ValueError("Auth0 environment variables not set")

security = HTTPBearer()

@lru_cache(maxsize=1)
def get_auth0_public_key():
    """Fetch and cache Auth0 public key for token verification"""
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    try:
        response = requests.get(jwks_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching Auth0 public key: {str(e)}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_token(token: str) -> dict:
    """Verify the Auth0 token and return its payload"""
    try:
        jwks = get_auth0_public_key()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=AUTH0_API_IDENTIFIER,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload

    except JWTError as e:
        logger.error(f"JWT Error during token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get the current user from the database based on the Auth0 token"""
    try:
        token = credentials.credentials
        payload = await verify_token(token)
        auth0_id = payload["sub"]
        
        user = crud.get_user_by_auth0_id(db, auth0_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise 