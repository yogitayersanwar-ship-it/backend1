import enum
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    OFFICER = "officer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    complaints = relationship("Complaint", back_populates="user")
    officer_profile = relationship("Officer", back_populates="user", uselist=False)