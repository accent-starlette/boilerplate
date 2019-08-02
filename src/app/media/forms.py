from wtforms import fields, form, validators

from . import config as media_config


class ImageCreateForm(form.Form):
    choose_images = fields.MultipleFileField(
        label="Choose the images you want to upload",
        render_kw={"accept": ", ".join(media_config.allowed_image_types)},
    )


class ImageUpdateForm(form.Form):
    title = fields.StringField(validators=[validators.optional()])
    focal_point_x = fields.IntegerField(validators=[validators.optional()])
    focal_point_y = fields.IntegerField(validators=[validators.optional()])
    focal_point_width = fields.IntegerField(validators=[validators.optional()])
    focal_point_height = fields.IntegerField(validators=[validators.optional()])
    change_image = fields.FileField(
        label="Choose an image to replace the existing one",
        render_kw={"accept": ", ".join(media_config.allowed_image_types)},
        validators=[validators.optional()],
    )
