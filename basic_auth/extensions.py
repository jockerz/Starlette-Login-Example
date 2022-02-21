from starlette.templating import Jinja2Templates
from starlette_login.login_manager import LoginManager


login_manager = LoginManager()
template = Jinja2Templates(directory='templates')
