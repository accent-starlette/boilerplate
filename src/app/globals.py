import jinja2
from starlette_core.templating import Jinja2Templates

templates = Jinja2Templates(
    loader=jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader("templates"),
            jinja2.PackageLoader("starlette_admin", "templates"),
        ]
    )
)
