import os
import shutil
from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import Complaint, ComplaintStatus
from app.models.user import User, UserRole
from app.schemas.complaint import ComplaintResponse, ComplaintStatusUpdate
from app.services.ocr_service import OCRService
from app.services.pdf_service import PDFService
from app.services.ai_classifier import ai_classifier
from app.services.notification_service import NotificationService
from app.dependencies import get_current_active_user, require_officer_or_admin

router = APIRouter(prefix="/complaints", tags=["Complaints"])

IMAGE_UPLOAD_DIR = "uploads/images"
PDF_UPLOAD_DIR = "uploads/pdf"


# ─── Create Complaint ────────────────────────────────────────────────────────

@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(
    title: str = Form(...),
    description: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit a new grievance/complaint.
    - Optionally attach an image or PDF file.
    - OCR / PDF text extraction runs automatically.
    - AI classifier auto-routes the complaint to the appropriate department.
    """
    file_path = None
    extracted_text = ""

    if file and file.filename:
        filename = f"{current_user.id}_{file.filename}"
        ext = os.path.splitext(file.filename)[1].lower()

        if ext == ".pdf":
            os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)
            file_path = os.path.join(PDF_UPLOAD_DIR, filename)
        else:
            os.makedirs(IMAGE_UPLOAD_DIR, exist_ok=True)
            file_path = os.path.join(IMAGE_UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text from uploaded document
        extracted_text = OCRService.extract_text(file_path)

    # Use AI to predict the right department
    full_text = f"{title} {description} {extracted_text}".strip()
    predicted_dept_id = ai_classifier.predict_department(full_text)

    complaint = Complaint(
        title=title,
        description=description,
        user_id=current_user.id,
        file_path=file_path,
        extracted_text=extracted_text,
        department_id=predicted_dept_id
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


# ─── List Complaints ─────────────────────────────────────────────────────────

@router.get("/", response_model=List[ComplaintResponse])
def list_complaints(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[ComplaintStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List complaints:
    - Citizens see only their own complaints.
    - Officers and Admins see all complaints (optionally filtered by status).
    """
    query = db.query(Complaint)

    if current_user.role == UserRole.CITIZEN:
        query = query.filter(Complaint.user_id == current_user.id)

    if status_filter:
        query = query.filter(Complaint.status == status_filter)

    return query.order_by(Complaint.id.desc()).offset(skip).limit(limit).all()


# ─── Get Single Complaint ─────────────────────────────────────────────────────

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Fetch a single complaint by ID. Citizens can only view their own."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if current_user.role == UserRole.CITIZEN and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return complaint


# ─── Update Complaint Status ──────────────────────────────────────────────────

@router.put("/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: int,
    body: ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer_or_admin)
):
    """
    Update the status of a complaint (Officer/Admin only).
    Triggers an email notification to the complaint owner.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = body.status
    db.commit()
    db.refresh(complaint)

    # Notify the user via email
    if complaint.user and complaint.user.email:
        NotificationService.notify_user_status_change(
            user_email=complaint.user.email,
            complaint_id=complaint.id,
            status=body.status.value
        )

    return complaint


# ─── Download PDF Report ──────────────────────────────────────────────────────

@router.get("/{complaint_id}/pdf")
def download_complaint_pdf(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate and download a PDF report for a complaint.
    Citizens can only download their own complaint PDFs.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if current_user.role == UserRole.CITIZEN and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    pdf_path = PDFService.generate_complaint_pdf(
        complaint_id=complaint.id,
        title=complaint.title,
        description=complaint.description,
        status=complaint.status.value
    )

    return FileResponse(
        path=pdf_path,
        filename=f"complaint_{complaint_id}_report.pdf",
        media_type="application/pdf"
    )