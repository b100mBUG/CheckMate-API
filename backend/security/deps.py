from fastapi import HTTPException, status, Depends
from backend.security.jwt_handler import verify_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer()


def get_current_user(token: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    payload = verify_access_token(token.credentials)

    return payload


def allow_roles(roles: list[str]):
    def role_checker(current_user = Depends(get_current_user)):
        if not roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide at least one role"
            )
        
        user_role = current_user.get("role")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Resources restricted to role(s): {roles}"
            )
        
        return current_user
        
    return role_checker