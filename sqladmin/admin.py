from sqladmin import ModelView
from starlette.requests import Request

from model import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id, User.username,
        User.first_name, User.last_name,
        User.is_admin
    ]
    form_excluded_columns = [User.password]

    def is_accessible(self, request: Request) -> bool:
        """Restrict access only by admin"""
        user = request.user
        return user and user.is_authenticated and user.is_admin
