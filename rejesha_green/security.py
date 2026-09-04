import os
from datetime import datetime,timedelta,timezone
from pathlib import Path
import bcrypt,jwt
from fastapi import Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from rejesha_green.config import settings

bearer_scheme=HTTPBearer()

# PRIVATE_KEY=os.getenv("JWT_PRIVATE_KEY")
# PUBLIC_KEY=os.getenv("JWT_PUBLIC_KEY")
PRIVATE_KEY = (settings.JWT_PRIVATE_KEY)
PUBLIC_KEY = (settings.JWT_PUBLIC_KEY)


def hash_password(password:str): return bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")

def verify_password(password:str,password_hash:str): return bcrypt.checkpw(password.encode("utf-8"),password_hash.encode("utf-8"))

def create_access_token(user_id:str,role:str):
    now=datetime.now(timezone.utc)
    payload={"sub":user_id,"role":role,"type":"access","iat":now,"exp":now+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(payload,PRIVATE_KEY,algorithm="RS256")

def create_refresh_token(user_id:str):
    now=datetime.now(timezone.utc)
    payload={"sub":user_id,"type":"refresh","iat":now,"exp":now+timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)}
    return jwt.encode(payload,PRIVATE_KEY,algorithm="RS256")

def verify_access_token(token:str):
    try:
        payload=jwt.decode(token,PUBLIC_KEY,algorithms=["RS256"])
        if payload.get("type")!="access": raise HTTPException(status_code=401,detail="Invalid access token")
        return payload
    except jwt.ExpiredSignatureError: raise HTTPException(status_code=401,detail="Token expired")
    except jwt.InvalidTokenError: raise HTTPException(status_code=401,detail="Invalid token")

def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(bearer_scheme)): return verify_access_token(credentials.credentials)

def require_role(*allowed_roles):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles: raise HTTPException(status_code=403,detail="Insufficient permissions")
        return current_user
    return role_checker
def require_roles(*allowed_roles):
    def role_checker(
        current_user=Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker