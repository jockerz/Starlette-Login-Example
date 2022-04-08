from starlette.templating import Jinja2Templates
from starlette_login.login_manager import LoginManager


login_manager = LoginManager(redirect_to='login', secret_key='no_secret_here')
template = Jinja2Templates(directory='templates')
