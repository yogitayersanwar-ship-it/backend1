from pydantic import BaseModel
from typing import Optional


class OfficerCreate(BaseModel):
    user_id: int
    department_id: int
    badge_number: str


class OfficerResponse(BaseModel):
    id: int
    user_id: int
    department_id: int
    badge_number: str

    class Config:
        from_attributes = True


class OfficerDetailResponse(BaseModel):
    id: int
    user_id: int
    department_id: int
    badge_number: str
    department_name: Optional[str] = None
    officer_name: Optional[str] = None
    officer_email: Optional[str] = None

    class Config:
        from_attributes = True
