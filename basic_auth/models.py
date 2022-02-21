from dataclasses import dataclass

from starlette.requests import Request
from starlette_login.mixins import BaseUser


@dataclass
class User(BaseUser):
    identifier: int
    username: str
    password: str = 'password'
    is_admin: bool = False

    def check_password(self, password: str):
        return self.password == password

    def is_authenticated(self) -> bool:
        return False

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> int:
        return self.identifier

    @classmethod
    async def get_user_by_id(cls, request: Request, user_id: int):
        for user in USERS.values():
            if user.identity == user_id:
                return user


user_regular = User(identifier=1, username='user')
user_admin = User(identifier=2, username='admin', is_admin=True)

USERS = {
    user_regular.username: user_regular,
    user_admin.username: user_admin,
}