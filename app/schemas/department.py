from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str
    code: str


class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True
