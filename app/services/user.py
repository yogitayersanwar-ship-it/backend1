from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.utils.password import hash_password

class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        """Fetch a single user by primary key ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        """Fetch a user record by unique email address."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """Get paginated list of all registered users."""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_role(db: Session, role: UserRole) -> list[User]:
        """Fetch all users matching a specific role (e.g., Citizen, Officer, Admin)."""
        return db.query(User).filter(User.role == role).all()

    @staticmethod
    def create_user(db: Session, user_data: UserCreate, role: UserRole = UserRole.CITIZEN) -> User:
        """Hashes password and creates a new User in the database."""
        hashed_pwd = hash_password(user_data.password)
        db_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hashed_pwd,
            role=role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user_status(db: Session, user_id: int, is_active: bool) -> User | None:
        """Activate or deactivate a user account."""
        user = UserService.get_by_id(db, user_id)
        if not user:
            return None
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        return user