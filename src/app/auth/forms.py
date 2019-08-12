from starlette_auth.tables import Scope, User
from wtforms import fields, validators
from wtforms_alchemy.fields import QuerySelectMultipleField

from app.forms import ModelForm


def all_scopes():
    return Scope.query.order_by("code")


class ScopeForm(ModelForm):
    class Meta:
        model = Scope


class UserBaseForm(ModelForm):
    class Meta:
        model = User
        only = ["first_name", "last_name", "email"]


class UserCreateForm(UserBaseForm):
    password = fields.PasswordField(validators=[validators.InputRequired()])
    confirm_password = fields.PasswordField(
        validators=[
            validators.InputRequired(),
            validators.EqualTo("password", message="The passwords do not match."),
        ]
    )


class UserUpdateForm(UserBaseForm):
    scopes = QuerySelectMultipleField(query_factory=all_scopes)

    class Meta:
        model = User
        only = ["first_name", "last_name", "email", "is_active"]
