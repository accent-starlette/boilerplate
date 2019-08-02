import asyncio

import sqlalchemy as sa
from starlette.authentication import has_required_scope
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, RedirectResponse
from starlette_admin.admin import ModelAdmin
from starlette_admin.config import config as admin_config
from starlette_admin.exceptions import MissingFormError
from starlette_core.database import Session
from starlette_core.messages import message
from wtforms.form import Form

from .forms import ImageCreateForm, ImageUpdateForm
from .tables import Image, ImageRendition, ImageStore, delete_many


class ImageAdmin(ModelAdmin):
    section_name = "Media"
    collection_name = "Images"
    model_class = Image
    paginate_by = 30
    search_enabled = True
    list_template = "media/admin/image_list.html"
    create_template = "media/admin/image_create.html"
    update_template = "media/admin/image_update.html"
    delete_cache_template = "media/admin/image_cache_delete.html"
    create_form = ImageCreateForm
    update_form = ImageUpdateForm
    delete_form = Form

    @classmethod
    def get_default_ordering(cls, qs):
        return qs.order_by(sa.desc(Image.file["uploaded_on"].astext))

    @classmethod
    def get_search_results(cls, qs, term):
        return qs.filter(
            sa.or_(
                Image.file["original_filename"].astext.ilike(f"%{term}%"),
                Image.file["width"].astext.ilike(f"%{term}%"),
                Image.file["height"].astext.ilike(f"%{term}%"),
                Image.file["content_type"].astext.ilike(f"%{term}%"),
                Image.title.ilike(f"%{term}%"),
            )
        )

    @classmethod
    async def do_create(cls, form, request):
        images = form["choose_images"].data
        for i in images:
            if i.filename:
                instance = cls.model_class()
                instance.file = ImageStore.create_from(i.file, i.filename)
                instance.save()
        return None

    @classmethod
    async def do_update(cls, instance, form, request):
        instance.title = form.title.data

        has_focal_points = any(
            [
                form.focal_point_x.data,
                form.focal_point_y.data,
                form.focal_point_width.data,
                form.focal_point_height.data,
            ]
        )

        new_file = form["change_image"].data

        if new_file.filename:
            instance.file = ImageStore.create_from(new_file.file, new_file.filename)
            # set to false so the old focal points get cleared
            has_focal_points = False
            # remove all existing renditions
            for ob in instance.renditions:
                ob.delete()

        if has_focal_points:
            instance.file.focal_point_x = int(form.focal_point_x.data)
            instance.file.focal_point_y = int(form.focal_point_y.data)
            instance.file.focal_point_width = int(form.focal_point_width.data)
            instance.file.focal_point_height = int(form.focal_point_height.data)
        else:
            instance.file.focal_point_x = None
            instance.file.focal_point_y = None
            instance.file.focal_point_width = None
            instance.file.focal_point_height = None

        instance.save()

        return instance

    @classmethod
    async def do_cache_delete(cls):
        renditions = ImageRendition.query.all()
        session = Session()
        session.query(ImageRendition).delete()
        session.commit()
        asyncio.ensure_future(delete_many(renditions))

    @classmethod
    async def create_view(cls, request):
        if not has_required_scope(request, cls.permission_scopes):
            raise HTTPException(403)

        if not cls.create_form:
            raise MissingFormError()

        context = cls.get_context(request)

        if request.method == "GET":
            form = cls.get_form(cls.create_form)
            context.update({"form": form})
            return admin_config.templates.TemplateResponse(cls.create_template, context)

        data = await request.form()
        form = cls.get_form(cls.create_form, formdata=data)

        if not form.validate():
            return JSONResponse({"status": "error"}, status_code=400)

        await cls.do_create(form, request)

        return JSONResponse({"status": "ok"}, status_code=201)

    @classmethod
    async def delete_cache_view(cls, request):
        if not has_required_scope(request, cls.permission_scopes):
            raise HTTPException(403)

        if not cls.delete_form:
            raise MissingFormError()

        context = cls.get_context(request)
        form_kwargs = {"form_cls": cls.delete_form}

        if request.method == "GET":
            form = cls.get_form(**form_kwargs)
            context.update({"form": form})
            return admin_config.templates.TemplateResponse(
                cls.delete_cache_template, context
            )

        data = await request.form()
        form = cls.get_form(**form_kwargs, formdata=data)

        if not form.validate():
            context.update({"form": form})
            return admin_config.templates.TemplateResponse(
                cls.delete_cache_template, context
            )

        await cls.do_cache_delete()

        message(request, "Deleted successfully", "success")

        return RedirectResponse(
            url=request.url_for(cls.url_names()["list"]), status_code=302
        )

    @classmethod
    def url_names(cls):
        names = super().url_names()
        mount = cls.mount_name()
        names.update({"delete_cache": f"{cls.site.name}:{mount}_delete_cache"})
        return names

    @classmethod
    def routes(cls):
        routes = super().routes()
        mount = cls.mount_name()
        routes.add_route(
            "/delete-cache",
            endpoint=cls.delete_cache_view,
            methods=["GET", "POST"],
            name=f"{mount}_delete_cache",
        )
        return routes
