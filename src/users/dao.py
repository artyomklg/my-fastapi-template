from .models import UserModel, RefreshSessionModel
from .schemas import UserCreateDB, UserUpdateDB, RefreshSessionCreate, RefreshSessionUpdate
from ..dao import BaseDAO


class UserDAO(BaseDAO[UserModel, UserCreateDB, UserUpdateDB]):
    model = UserModel


class RefreshSessionDAO(BaseDAO[RefreshSessionModel, RefreshSessionCreate, RefreshSessionUpdate]):
    model = RefreshSessionModel
