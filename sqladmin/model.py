from passlib.hash import pbkdf2_sha256
from sqlalchemy import Boolean, Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from starlette.requests import Request
from starlette_login.mixins import UserMixin


@as_declarative()
class Base:
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class User(Base, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True)
    password = Column(String(128))
    first_name = Column(String(256))
    last_name = Column(String(256))
    is_admin = Column(Boolean, default=False)

    @property
    def identity(self):
        return self.id

    def set_password(self, password: str):
        self.password = pbkdf2_sha256.hash(password)

    def check_password(self, password: str):
        return pbkdf2_sha256.verify(password, self.password)

    @classmethod
    async def get_user_by_id(cls, request: Request, user_id: int):
        db = request.state.db
        return await db.get(User, user_id)

    @classmethod
    async def get_user_by_username(cls, db: AsyncSession, username: str):
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        if result is None:
            return None
        else:
            return result.scalars().first()

    @classmethod
    async def create_user(
        cls, db: AsyncSession,
        username: str, password: str, first_name: str = None,
        last_name: str = None, is_admin: bool = False
    ):
        user = cls(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_admin=is_admin
        )
        user.set_password(password)
        db.add(user)
        await db.commit()
        return user
