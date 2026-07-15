from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv(".env")


SECRET_KEY = os.getenv("SECRET_KEY", "")
ACCESS_KEY_EXPIRE_MINUTES = int(os.getenv("ACCESS_KEY_EXPIRE_MINUTES", 0))
ALGORITHM = os.getenv("ALGORITHM", "")


def create_access_token(data: dict, expire_delta: timedelta = 15) -> str:
    now = datetime.now(timezone.utc)
    to_encode = data.copy()

    iat = now

    to_encode.update(
        {
            "iat":iat,
            "exp": expire_delta or (now + timedelta(minutes=15))
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
    except JWTError:
        raise HTTPException("Unable to verify the access token")
    
    return payload



