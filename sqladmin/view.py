from urllib.parse import parse_qsl

from starlette.requests import Request
from starlette.responses import (
    HTMLResponse, PlainTextResponse, RedirectResponse
)
from starlette_login.decorator import login_required
from starlette_login.utils import login_user, logout_user

from model import User


HOME_PAGE = """
You are logged in as {username}<br/>Links:
<ul>
    <li><a href="/">Home</a></li>
    <li><a href="/admin">Admin</a></li>
    <li><a href="/logout">Logout</a></li>
<ul>
"""
LOGIN_PAGE = """
<h4>{error}<h4>
<form method="POST">
<label>username <input name="username"></label>
<label>Password <input name="password" type="password"></label>
<button type="submit">Login</button>
</form>
"""


async def login_page(request: Request):
    db = request.state.db
    error = ''
    if request.method == 'POST':
        body = (await request.body()).decode()
        data = dict(parse_qsl(body))
        username = data.get('username')
        password = data.get('password')

        if username is None or password is None:
            error = "Invalid username or password"
        else:
            user = await User.get_user_by_username(db, username)
            if user:
                if user.check_password(password) is True:
                    await login_user(request, user)
                    return RedirectResponse('/', status_code=302)
                else:
                    error = "Invalid password"
            else:
                error = "User not found"
    return HTMLResponse(LOGIN_PAGE.format(error=error))


async def logout_page(request: Request):
    if request.user.is_authenticated:
        content = 'Logged out'
        await logout_user(request)
    else:
        content = 'You not logged in'
    return PlainTextResponse(content)


@login_required
async def home_page(request: Request):
    user = request.user
    return HTMLResponse(HOME_PAGE.format(username=user.username))
