from app.globals import templates


async def not_found(request, exc):
    template = "404.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=404)


async def server_error(request, exc):
    template = "500.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=500)
