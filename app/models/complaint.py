import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ComplaintStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.PENDING)

    extracted_text = Column(Text, nullable=True)   # Text extracted via OCR / PDF parsing
    file_path = Column(String, nullable=True)       # Uploaded document path

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="complaints")
    department = relationship("Department", back_populates="complaints")