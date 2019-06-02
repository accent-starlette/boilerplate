import sqlalchemy as sa
from sqlalchemy import orm
from starlette_admin import AdminSite, ModelAdmin
from starlette_auth.tables import Scope, User
from wtforms import fields, form, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.ext.sqlalchemy.orm import model_form


class ScopeAdmin(ModelAdmin):
    section_name = "Authentication"
    collection_name = "Scopes"
    model_class = Scope
    list_field_names = ["code", "description"]
    create_form = model_form(Scope)
    update_form = model_form(Scope)
    delete_form = form.Form

    @classmethod
    def get_default_ordering(cls, qs):
        return qs.order_by("code")


class UserBaseForm(form.Form):
    first_name = fields.StringField(validators=[validators.InputRequired()])
    last_name = fields.StringField(validators=[validators.InputRequired()])
    email = fields.html5.EmailField(validators=[validators.InputRequired()])


class UserCreateForm(UserBaseForm):
    password = fields.PasswordField(validators=[validators.InputRequired()])
    confirm_password = fields.PasswordField(
        validators=[
            validators.InputRequired(),
            validators.EqualTo("password", message="The passwords do not match."),
        ]
    )


class UserUpdateForm(UserBaseForm):
    scopes = QuerySelectMultipleField()
    is_active = fields.BooleanField()


class UserAdmin(ModelAdmin):
    section_name = "Authentication"
    collection_name = "Users"
    model_class = User
    list_field_names = ["email", "first_name", "last_name"]
    paginate_by = 10
    order_enabled = True
    search_enabled = True
    create_form = UserCreateForm
    update_form = UserUpdateForm
    delete_form = form.Form

    @classmethod
    def get_default_ordering(cls, qs):
        return qs.order_by("email")

    @classmethod
    def get_search_results(cls, qs, term):
        return qs.filter(
            sa.or_(
                User.email.like(f"%{term}%"),
                User.first_name.like(f"%{term}%"),
                User.last_name.like(f"%{term}%"),
            )
        )

    @classmethod
    def get_form(cls, form_cls, **kwargs):
        form = super().get_form(form_cls, **kwargs)
        if isinstance(form, UserUpdateForm):
            form.scopes.query = Scope.query.order_by("code")
        return form

    @classmethod
    def do_create(cls, form):
        instance = cls.model_class()
        form.populate_obj(instance)
        instance.set_password(form.password.data)
        instance.save()
        return instance


# create an admin site
adminsite = AdminSite(name="admin", permission_scopes=["authenticated", "admin"])

# register admins
adminsite.register(ScopeAdmin)
adminsite.register(UserAdmin)
