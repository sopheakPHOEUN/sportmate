from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.profile import Profile
from app.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


@router.get("/me", response_model=ProfileRead)
def get_my_profile(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.id == user["sub"]).first()
    if not profile:
        # Shouldn't happen given the Day 11 trigger, but handle defensively
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
@router.patch("/me", response_model=ProfileRead)
def update_my_profile(
    payload: ProfileUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.id == user["sub"]).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile