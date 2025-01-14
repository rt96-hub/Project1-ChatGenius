from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import models, schemas
from ..database import get_db
from ..auth0 import get_current_user
from ..crud.users import (
    get_user,
    get_users,
    get_users_by_last_dm,
    update_user_bio,
    update_user_name
)

# Configure logging for errors only
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    request: Request,
    current_user: models.User = Depends(get_current_user)
):
    """Get the current authenticated user's information"""
    try:
        return current_user
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting current user: {str(e)}"
        )

@router.get("/by-last-dm", response_model=List[schemas.UserWithLastDM])
def read_users_by_last_dm(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all users ordered by their last DM interaction with the current user.
    Users with no DM history appear first, followed by users with DMs ordered by ascending date
    (most recent DM appears last)."""
    return get_users_by_last_dm(
        db,
        current_user_id=current_user.id,
        skip=skip,
        limit=limit
    )

@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/me/bio", response_model=schemas.User)
async def update_user_bio(
    bio_update: schemas.UserBioUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update the current user's bio"""
    try:
        updated_user = update_user_bio(db, user_id=current_user.id, bio=bio_update.bio)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user bio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user bio: {str(e)}"
        )

@router.put("/me/name", response_model=schemas.User)
async def update_user_name(
    name_update: schemas.UserNameUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update the current user's name"""
    try:
        updated_user = update_user_name(db, user_id=current_user.id, name=name_update.name)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user name: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user name: {str(e)}"
        ) 