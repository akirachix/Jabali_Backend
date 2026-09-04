import hashlib
import logging
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from rejesha_green.models.password_reset import PasswordReset
from rejesha_green.models.user import UserRole

from rejesha_green.repositories.user_repository import UserRepository

from rejesha_green.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
)
from rejesha_green.services.sms_service import SMSService


logger = logging.getLogger(__name__)


OFFICIAL_ROLES = {
    UserRole.KENYA_FOREST_SERVICE_OFFICIAL,
    UserRole.COMMUNITY_FOREST_ASSOCIATION_OFFICIAL,
}


def login(db: Session, email: str, password: str):
    user = UserRepository(db).get_by_email(email)

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return {
        "access_token": create_access_token(
            str(user.user_id),
            user.role.value,
        ),
        "refresh_token": create_refresh_token(
            str(user.user_id),
        ),
        "token_type": "bearer",
    }


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


def request_password_reset(
    db: Session,
    phone: str,
):
    repository = UserRepository(db)

    user = repository.get_by_phone(phone)

    # Don't reveal whether the phone number exists.
    if not user:
        return {
            "message": "If the phone number is registered, an OTP has been sent."
        }

    # Only officials can use this password-reset flow.
    if user.role not in OFFICIAL_ROLES:
        return {
            "message": "If the phone number is registered, an OTP has been sent."
        }

    if not user.is_active:
        return {
            "message": "If the phone number is registered, an OTP has been sent."
        }

    otp = generate_otp()

    # Invalidate previous OTPs for this phone number.
    previous_otps = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.phone == phone,
            PasswordResetOTP.used == False,
        )
        .all()
    )

    for previous_otp in previous_otps:
        previous_otp.used = True

    reset_otp = PasswordResetOTP(
        phone=phone,
        otp_hash=hash_otp(otp),
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        attempts=0,
        used=False,
    )

    db.add(reset_otp)
    db.commit()

    message = (
        f"REJESHA: Your password reset OTP is {otp}. "
        "It expires in 5 minutes. Do not share this code."
    )

    sms_sent = send_sms(
        phone=phone,
        message=message,
    )

    if not sms_sent:
        reset_otp.used = True
        db.commit()

        logger.error(
            "Failed to send password reset OTP to phone ending %s",
            phone[-4:],
        )

        raise HTTPException(
            status_code=503,
            detail="Unable to send OTP. Please try again later.",
        )

    return {
        "message": "If the phone number is registered, an OTP has been sent."
    }


def reset_password(
    db: Session,
    phone: str,
    otp: str,
    new_password: str,
):
    repository = UserRepository(db)

    user = repository.get_by_phone(phone)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP or phone number",
        )

    if user.role not in OFFICIAL_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP or phone number",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP or phone number",
        )

    reset_otp = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.phone == phone,
            PasswordResetOTP.used == False,
        )
        .order_by(
            PasswordResetOTP.created_at.desc()
        )
        .first()
    )

    if not reset_otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP",
        )

    if reset_otp.expires_at < datetime.utcnow():
        reset_otp.used = True
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="OTP has expired",
        )

    if reset_otp.attempts >= 5:
        reset_otp.used = True
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Too many OTP attempts",
        )

    if not secrets.compare_digest(
        reset_otp.otp_hash,
        hash_otp(otp),
    ):
        reset_otp.attempts += 1
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invalid OTP",
        )

    user.password_hash = hash_password(new_password)

    # OTP can never be reused.
    reset_otp.used = True

    db.commit()

    return {
        "message": "Password reset successfully.",
    }