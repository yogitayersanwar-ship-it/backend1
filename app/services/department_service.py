from sqlalchemy.orm import Session
from app.models.department import Department
from app.schemas.department import DepartmentCreate


class DepartmentService:
    @staticmethod
    def create_department(db: Session, dept_data: DepartmentCreate) -> Department:
        dept = Department(name=dept_data.name, code=dept_data.code)
        db.add(dept)
        db.commit()
        db.refresh(dept)
        return dept

    @staticmethod
    def get_all(db: Session):
        return db.query(Department).all()

    @staticmethod
    def get_by_id(db: Session, dept_id: int) -> Department | None:
        return db.query(Department).filter(Department.id == dept_id).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Department | None:
        return db.query(Department).filter(Department.code == code).first()

    @staticmethod
    def delete_department(db: Session, dept_id: int) -> None:
        dept = db.query(Department).filter(Department.id == dept_id).first()
        if dept:
            db.delete(dept)
            db.commit()