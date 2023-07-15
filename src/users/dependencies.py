from typing import Optional
import uuid

from jose import jwt
from fastapi import Depends, HTTPException, status

from .schemas import User
from .utils import OAuth2PasswordBearerWithCookie
from .service import UserService
from ..exceptions import InvalidTokenException
from ..config import settings

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    try:
        payload = jwt.decode(token,
                             settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException
    except Exception:
        raise InvalidTokenException
    return await UserService.get_user(uuid.UUID(user_id))


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return current_user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")
    return current_user
