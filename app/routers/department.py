from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.department import DepartmentCreate, DepartmentResponse
from app.services.department_service import DepartmentService
from app.dependencies import get_current_active_user, require_admin

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("/", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    """List all departments. Public endpoint — no auth required."""
    return DepartmentService.get_all(db)


@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    """Get a specific department by ID."""
    dept = DepartmentService.get_by_id(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    dept: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """Create a new department (Admin only)."""
    existing = DepartmentService.get_by_code(db, dept.code)
    if existing:
        raise HTTPException(status_code=400, detail="Department code already exists")
    return DepartmentService.create_department(db, dept)


@router.delete("/{dept_id}", status_code=204)
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """Delete a department (Admin only)."""
    dept = DepartmentService.get_by_id(db, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    DepartmentService.delete_department(db, dept_id)