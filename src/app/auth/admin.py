import sqlalchemy as sa
from starlette_admin import ModelAdmin
from starlette_auth.tables import Scope, User
from wtforms import form

from .forms import ScopeForm, UserCreateForm, UserUpdateForm


class ScopeAdmin(ModelAdmin):
    section_name = "Authentication"
    collection_name = "Scopes"
    model_class = Scope
    list_field_names = ["code", "description"]
    create_form = ScopeForm
    update_form = ScopeForm
    delete_form = form.Form

    @classmethod
    def get_default_ordering(cls, qs):
        return qs.order_by("code")


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
    async def do_create(cls, form, request):
        instance = cls.model_class()
        form.populate_obj(instance)
        instance.set_password(form.password.data)
        instance.save()
        return instance
