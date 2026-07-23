from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import Complaint, ComplaintStatus
from app.models.department import Department
from app.models.user import User, UserRole
from app.dependencies import get_current_active_user, require_officer_or_admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(require_officer_or_admin)
):
    """
    Get overall system statistics (Officer/Admin only).
    Returns complaint counts by status, department breakdown, and totals.
    """
    total_complaints = db.query(Complaint).count()
    pending = db.query(Complaint).filter(Complaint.status == ComplaintStatus.PENDING).count()
    in_progress = db.query(Complaint).filter(Complaint.status == ComplaintStatus.IN_PROGRESS).count()
    resolved = db.query(Complaint).filter(Complaint.status == ComplaintStatus.RESOLVED).count()
    rejected = db.query(Complaint).filter(Complaint.status == ComplaintStatus.REJECTED).count()

    total_users = db.query(User).count()
    total_citizens = db.query(User).filter(User.role == UserRole.CITIZEN).count()
    total_officers = db.query(User).filter(User.role == UserRole.OFFICER).count()
    total_departments = db.query(Department).count()

    # Per-department complaint breakdown
    departments = db.query(Department).all()
    dept_breakdown = []
    for dept in departments:
        dept_complaints = db.query(Complaint).filter(Complaint.department_id == dept.id).count()
        dept_breakdown.append({
            "department_id": dept.id,
            "department_name": dept.name,
            "department_code": dept.code,
            "complaint_count": dept_complaints
        })

    # Recent 10 complaints
    recent_complaints = db.query(Complaint).order_by(Complaint.id.desc()).limit(10).all()
    recent = [
        {
            "id": c.id,
            "title": c.title,
            "status": c.status.value,
            "user_id": c.user_id,
            "department_id": c.department_id,
            "created_at": str(c.created_at) if c.created_at else None
        }
        for c in recent_complaints
    ]

    return {
        "summary": {
            "total_complaints": total_complaints,
            "pending": pending,
            "in_progress": in_progress,
            "resolved": resolved,
            "rejected": rejected,
            "total_users": total_users,
            "total_citizens": total_citizens,
            "total_officers": total_officers,
            "total_departments": total_departments
        },
        "department_breakdown": dept_breakdown,
        "recent_complaints": recent
    }