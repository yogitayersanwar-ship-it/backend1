from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.officer import Officer
from app.schemas.officer import OfficerCreate, OfficerResponse, OfficerDetailResponse
from app.dependencies import get_current_active_user, require_admin

router = APIRouter(prefix="/officers", tags=["Officers"])


@router.post("/", response_model=OfficerResponse)
def assign_officer(
    data: OfficerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """Assign an existing user as an Officer in a department (Admin only)."""
    existing = db.query(Officer).filter(Officer.user_id == data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already assigned as an officer")

    existing_badge = db.query(Officer).filter(Officer.badge_number == data.badge_number).first()
    if existing_badge:
        raise HTTPException(status_code=400, detail="Badge number already exists")

    officer = Officer(
        user_id=data.user_id,
        department_id=data.department_id,
        badge_number=data.badge_number
    )
    db.add(officer)
    db.commit()
    db.refresh(officer)
    return officer


@router.get("/", response_model=List[OfficerDetailResponse])
def list_officers(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """List all officers with their department and user details."""
    officers = db.query(Officer).all()
    result = []
    for officer in officers:
        result.append(OfficerDetailResponse(
            id=officer.id,
            user_id=officer.user_id,
            department_id=officer.department_id,
            badge_number=officer.badge_number,
            department_name=officer.department.name if officer.department else None,
            officer_name=officer.user.full_name if officer.user else None,
            officer_email=officer.user.email if officer.user else None
        ))
    return result


@router.get("/{officer_id}", response_model=OfficerDetailResponse)
def get_officer(
    officer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """Get a specific officer's details by ID."""
    officer = db.query(Officer).filter(Officer.id == officer_id).first()
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")

    return OfficerDetailResponse(
        id=officer.id,
        user_id=officer.user_id,
        department_id=officer.department_id,
        badge_number=officer.badge_number,
        department_name=officer.department.name if officer.department else None,
        officer_name=officer.user.full_name if officer.user else None,
        officer_email=officer.user.email if officer.user else None
    )


@router.delete("/{officer_id}", status_code=204)
def remove_officer(
    officer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """Remove an officer assignment (Admin only)."""
    officer = db.query(Officer).filter(Officer.id == officer_id).first()
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")

    db.delete(officer)
    db.commit()