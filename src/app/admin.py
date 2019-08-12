import sqlalchemy as sa
from starlette_admin import AdminSite

from app.auth import admin as auth_admin

# create an admin site
adminsite = AdminSite(name="admin", permission_scopes=["authenticated", "admin"])

# register admins
adminsite.register(auth_admin.ScopeAdmin)
adminsite.register(auth_admin.UserAdmin)
