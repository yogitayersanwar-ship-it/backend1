from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base


class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    badge_number = Column(String, unique=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="officer_profile")
    department = relationship("Department", back_populates="officers")