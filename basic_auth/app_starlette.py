from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route

from starlette_login.backends import SessionAuthBackend
from starlette_login.decorator import login_required
from starlette_login.middleware import AuthenticationMiddleware
from starlette_login.utils import login_user, logout_user

from extensions import login_manager, template
from models import USERS, User

login_manager.set_user_loader(User.get_user_by_id)


async def home_page(request: Request):
    return template.TemplateResponse(
        'home.html', context={'request': request}
    )


async def login_page(request: Request):
    if request.user.is_authenticated:
        return RedirectResponse('/', status_code=302)

    error = None
    if request.method == 'POST':
        form = await request.form()
        user = USERS.get(form['username'])
        if user is None:
            error = "Invalid username"
        elif user.check_password(form['password']) is True:
            # Login user - create user session
            await login_user(request, user)
            return RedirectResponse('/', status_code=302)
        else:
            error = "Invalid username password"
    return template.TemplateResponse(
        'login.html', context={'request': request, 'error': error}
    )


@login_required
async def logout_page(request: Request):
    if request.method == 'POST':
        # Logout user
        await logout_user(request)
        return RedirectResponse('/', status_code=302)

    return template.TemplateResponse(
        'logout.html', context={'request': request}
    )


@login_required
async def protected_page(request: Request):
    return template.TemplateResponse(
        'protected.html', context={'request': request}
    )


@login_required
async def admin_page(request: Request):
    # Authenticated user have `is_admin` property
    if not request.user.is_admin:
        # Not and admin user
        return RedirectResponse('/', status_code=302)
    return template.TemplateResponse(
        'admin.html', context={'request': request}
    )


SECRET_KEY = 'no_secret_here'

app = Starlette(
    debug=True,
    routes=[
        Route('/', home_page, name='home'),
        Route('/login', login_page, methods=['GET', 'POST'], name='login'),
        Route('/logout', logout_page, methods=['GET', 'POST'], name='logout'),
        Route('/protected', protected_page),
        Route('/admin', admin_page),
    ],
    middleware=[
        Middleware(SessionMiddleware, secret_key=SECRET_KEY),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(login_manager),
            login_manager=login_manager,
            login_route='login',
            secret_key=SECRET_KEY,
            excluded_dirs=['/favicon.ico']
        )
    ]
)
app.state.login_manager = login_manager
