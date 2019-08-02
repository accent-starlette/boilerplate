import asyncio
import typing

import sqlalchemy as sa
from sqlalchemy import event, orm
from sqlalchemy.dialects.postgresql import JSON
from starlette_core.database import Base
from starlette_files.fields import ImageAttachment, ImageRenditionAttachment
from starlette_files.storages import FileSystemStorage

from . import config


class ImageStore(ImageAttachment):
    storage = FileSystemStorage(config.root_directory)
    directory = config.image_directory
    allowed_content_types = config.allowed_image_types
    max_length = config.max_upload_size


class Image(Base):
    title = sa.Column(sa.String(255), nullable=True)
    file = sa.Column(ImageStore.as_mutable(JSON))
    renditions = orm.relationship("ImageRendition", cascade="delete")

    def __str__(self):
        return self.title or self.file.original_filename

    def get_rendition(self, filter_specs: typing.List[str]) -> "ImageRendition":
        filter_specs_str = "|".join(filter_specs)

        rendition = ImageRendition.query.filter(
            ImageRendition.image_id == self.id,
            ImageRendition.filter_spec == filter_specs_str,
            ImageRendition.file["cache_key"].astext == self.file.cache_key,
        ).one_or_none()

        if rendition:
            return rendition

        try:
            rendition = ImageRendition(
                image_id=self.id,
                file=ImageRenditionStore.create_from(self.file, filter_specs),
                filter_spec=filter_specs_str,
            )

            session = sa.inspect(self).session
            session.add(rendition)
            session.commit()
        except FileNotFoundError:
            # TODO: return an empty rendition that wont break the site
            rendition = self

        return rendition


class ImageRenditionStore(ImageRenditionAttachment):
    storage = FileSystemStorage(config.root_directory)
    directory = config.image_rendition_directory


class ImageRendition(Base):
    file = sa.Column(ImageRenditionStore.as_mutable(JSON))
    image_id = sa.Column(sa.Integer, sa.ForeignKey("image.id"))
    filter_spec = sa.Column(sa.Text)


async def delete_one(target):
    try:
        target.file.storage.delete(target.file.path)
        print(f"deleted: {target.file.path}")
    except:
        print(f"cannot delete: {target.file.path}")


async def delete_many(targets):
    await asyncio.sleep(5)  #  small sleep to give the view a chance to load
    statements = [delete_one(target) for target in targets]
    asyncio.gather(*statements)


@event.listens_for(Image, "after_delete")
@event.listens_for(ImageRendition, "after_delete")
def remove_from_storage(mapper, connection, target):
    asyncio.ensure_future(delete_one(target))
