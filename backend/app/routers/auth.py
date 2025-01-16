from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging
from typing import Dict
from jose import jwt
from jose.exceptions import JWTError
import requests
from functools import lru_cache
import os
from dotenv import load_dotenv

from .. import models, schemas
from ..database import get_db
from ..auth0 import verify_token, get_current_user
from ..crud.users import get_user_by_auth0_id, sync_auth0_user
from ..crud.channels import get_or_create_ai_dm

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create router
router = APIRouter()


@router.post("/sync", response_model=schemas.User)
async def sync_auth0_user_endpoint(
    request: Request,
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Sync Auth0 user data with local database"""
    try:
        # Verify the token first
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header"
            )
        if not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Must start with 'Bearer '"
            )
        
        token = auth_header.split(' ')[1]
        payload = await verify_token(token)
        
        # Ensure the Auth0 ID matches
        if payload['sub'] != user_data.auth0_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token subject does not match provided Auth0 ID"
            )
        
        return sync_auth0_user(db, user_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error syncing user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing user: {str(e)}"
        )

@router.get("/verify", response_model=Dict)
async def verify_auth(
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify Auth0 token and return user data"""
    try:
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header"
            )
        if not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Must start with 'Bearer '"
            )
        
        token = auth_header.split(' ')[1]
        payload = await verify_token(token)
        
        # Get user from database
        user = get_user_by_auth0_id(db, payload['sub'])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "valid": True,
            "user": user
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error verifying user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying user: {str(e)}"
        )