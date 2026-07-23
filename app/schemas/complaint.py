from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.complaint import ComplaintStatus


class ComplaintCreate(BaseModel):
    title: str
    description: str


class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus


class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    status: ComplaintStatus
    extracted_text: Optional[str] = None
    file_path: Optional[str] = None
    department_id: Optional[int] = None
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True