from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import HTTPException, status
import os

load_dotenv(".env")


SECRET_KEY = os.getenv("SECRET_KEY", "")
ACCESS_KEY_EXPIRE_MINUTES = int(os.getenv("ACCESS_KEY_EXPIRE_MINUTES", 0))
ALGORITHM = os.getenv("ALGORITHM", "")


def create_access_token(data: dict) -> str:
    now = datetime.now(timezone.utc)
    to_encode = data.copy()

    iat = now

    to_encode.update(
        {
            "iat":iat,
            "exp": (now + timedelta(minutes=ACCESS_KEY_EXPIRE_MINUTES))
        }
    )
    try:
        token = jwt.encode(
            to_encode,
            key=SECRET_KEY,
            algorithm=ALGORITHM
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not generate access token"
        )
    
    return token

def verify_access_token(token: str) -> dict:
    print("About to verify token: ", token)
    try:
        payload = jwt.decode(
            token, 
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "The provided access token has expired"
        )
    except JWTError as e:
        raise e
        """raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to verify the access token")"""
    
    return payload



