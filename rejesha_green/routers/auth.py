from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db

from rejesha_green.services.auth_service import (
    login,
    request_password_reset,
    reset_password,
)

from rejesha_green.schemas.users import (
    UserLogin,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    return login(
        db,
        data.email,
        data.password,
    )


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    return request_password_reset(
        db,
        data.phone,
    )


@router.post("/reset-password")
def reset_password_user(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    return reset_password(
        db,
        data.phone,
        data.otp,
        data.new_password,
    )