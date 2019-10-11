from app.merlin.core.tables import Page


def create_test_data(pages_per_level: int = 1):
    for x in range(1, pages_per_level + 1):
        root = Page(
            title=f"Page {x}",
            slug=f"page-{x}"
        )
        root.save()
        for y in range(1, pages_per_level + 1):
            next = Page(
                title=f"{root.title}.{y}",
                slug=f"{root.slug}-{y}",
                parent=root
            )
            next.save()
            for z in range(1, pages_per_level + 1):
                sub = Page(
                    title=f"{next.title}.{z}",
                    slug=f"{next.slug}-{z}",
                    parent=next
                )
                sub.save()