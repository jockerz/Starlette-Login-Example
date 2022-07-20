import logging

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from sqladmin import Admin

from starlette_login.backends import SessionAuthBackend
from starlette_login.login_manager import LoginManager
from starlette_login.middleware import AuthenticationMiddleware

from admin import UserAdmin
from model import Base, User
from view import register_page, login_page, logout_page, home_page


SECRET_KEY = 'our_webapp_secret_key'
DB_URL = 'sqlite+aiosqlite:///./sqlite.db'

logger = logging.getLogger('uvicorn.error')
db_engine = create_async_engine(DB_URL, poolclass=NullPool)
LocalDBSession = sessionmaker(
    db_engine, class_=AsyncSession, expire_on_commit=False
)

login_manager = LoginManager(
    redirect_to='/login', secret_key=SECRET_KEY
)
login_manager.set_user_loader(User.get_user_by_id)

middleware = [
    Middleware(SessionMiddleware, secret_key=SECRET_KEY),
    Middleware(
        AuthenticationMiddleware,
        backend=SessionAuthBackend(login_manager),
        login_manager=login_manager,
        secret_key=SECRET_KEY,
        excluded_dirs=['/static']
    )
]

app = FastAPI(
    middleware=middleware,
    routes=[
        Route('/', home_page, name='home'),
        Route('/login', login_page, methods=['GET', 'POST'], name='login'),
        Route('/logout', logout_page, name='logout'),
    ]
)
app.state.login_manager = login_manager

# Use `SessionMiddleware` and `AuthenticationMiddleware`
# to secure admin pages
admin = Admin(app, db_engine, middlewares=middleware)
admin.register_model(UserAdmin)


@app.middleware('http')
async def extensions(request: Request, call_next):
    try:
        request.state.db = LocalDBSession()
        response = await call_next(request)
    except Exception as exc:
        logger.exception(exc)
        response = PlainTextResponse(f'error: {exc}')
    finally:
        return response


@app.on_event('startup')
async def startup():
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # create admin user
    db = LocalDBSession()
    if not await User.get_user_by_username(db, 'admin'):
        await User.create_user(
            db, 'admin', 'password', is_admin=True
        )
        await User.create_user(
            db, 'user', 'password', is_admin=False
        )
    await db_engine.dispose()
