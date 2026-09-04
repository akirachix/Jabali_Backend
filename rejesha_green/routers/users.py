import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from rejesha_green.models.user import UserRole

from rejesha_green.repositories.user_repository import UserRepository
from rejesha_green.schemas.users import UserCreate, UserResponse, UserUpdate, OfficialCreate, MemberCreate, CommunityForestAssociationOfficialCreate
from rejesha_green.security import require_role, require_roles
from rejesha_green.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.SUPER_ADMIN))): 
    return user_service.create_user(db, data)

@router.get("/", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.SUPER_ADMIN, UserRole.KENYA_FOREST_SERVICE_OFFICIAL,UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL,))): 
    return UserRepository(db).get_all_users(skip, limit)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.SUPER_ADMIN, UserRole.KENYA_FOREST_SERVICE_OFFICIAL,UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL,))):
    user = UserRepository(db).get_user(user_id)
    if not user: raise HTTPException(404, "User not found")
    return user

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: uuid.UUID, data: UserUpdate, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.SUPER_ADMIN, UserRole.KENYA_FOREST_SERVICE_OFFICIAL,UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL,))): 
    return user_service.update_user(db, user_id, data, current_user)

@router.delete("/{user_id}")
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.KENYA_FOREST_SERVICE_OFFICIAL, UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL,))): 
    return user_service.delete_user(db, user_id)

@router.post("/kenya-forest-service-official", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_kenya_forest_service_official(data: OfficialCreate, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.SUPER_ADMIN))): 
    return user_service.register_kenya_forest_service_official(db, data, current_user)

@router.post("/community-forest-association-official", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_community_forest_association_official(data: CommunityForestAssociationOfficialCreate, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.KENYA_FOREST_SERVICE_OFFICIAL))): return user_service.register_community_forest_association_official(db, data, current_user)

@router.post("/member", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_member(data: MemberCreate, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL))): 
    return user_service.register_member(db, data, current_user)