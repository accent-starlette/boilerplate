import typing

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy_utils import Ltree, LtreeType
from starlette_core.database import Base

from .exceptions import PageMoveError


class PageManager:
    @classmethod
    def from_slug_parts(cls, slugs: typing.List[str]) -> "Page":
        """ returns a page from its slug path from root > page """

        assert len(slugs) > 0, "must be at least one slug in list"

        page = cls.root().filter(Page.slug == slugs[0]).one()

        if len(slugs) == 1:
            return page

        for slug in slugs[1:]:
            page = Page.query.filter(
                Page.path.descendant_of(page.path),
                sa.func.nlevel(Page.path) == len(page.path) + 1,
                Page.slug == slug,
            ).one()

        return page

    @classmethod
    def root(cls) -> orm.Query:
        """ Get all root pages """

        return Page.query.filter(sa.func.nlevel(Page.path) == 1).order_by(Page.order)

    @classmethod
    def get_next_available_order(cls, parent: "Page" = None) -> int:
        """ Returns the next available order for a page's children """

        if parent:
            try:
                last = parent.children[-1]
                max_order = last.order
            except IndexError:
                max_order = 0

        else:
            try:
                last = cls.root()[-1]
                max_order = last.order
            except IndexError:
                max_order = 0

        return max_order + 16384 if max_order else 16384


class Page(Base):
    id_seq = sa.Sequence("page_id_seq")

    id = sa.Column(sa.Integer, id_seq, primary_key=True)
    title = sa.Column(sa.String(150), nullable=False)
    slug = sa.Column(sa.String(150), nullable=False)
    path = sa.Column(LtreeType, nullable=False)
    meta_description = sa.Column(sa.String(255), nullable=True)
    order = sa.Column(sa.types.Float, nullable=False, default=16384)

    # ancestors of this page that excludes the current page
    ancestors = orm.relationship(
        "Page",
        primaryjoin=sa.and_(
            orm.remote(path).op("@>", is_comparison=True)(orm.foreign(path)),
            orm.remote(path) != orm.foreign(path),
        ),
        viewonly=True,
        order_by=path,
        uselist=True,
    )

    # descendants of this page that excludes the current page
    descendants = orm.relationship(
        "Page",
        primaryjoin=sa.and_(
            orm.remote(path).op("<@", is_comparison=True)(orm.foreign(path)),
            orm.remote(path) != orm.foreign(path),
        ),
        viewonly=True,
        order_by=path,
        uselist=True,
    )

    # parent of this page, backref is the children
    parent = orm.relationship(
        "Page",
        primaryjoin=(orm.remote(path) == orm.foreign(sa.func.subpath(path, 0, -1))),
        backref=orm.backref("children", order_by=order),
        viewonly=True,
    )

    # get all siblings of this page
    siblings = orm.relationship(
        "Page",
        primaryjoin=sa.and_(
            orm.remote(path).op("<@", is_comparison=True)(
                orm.foreign(sa.func.subpath(path, 0, -1))
            ),
            orm.remote(sa.func.nlevel(path)) == orm.foreign(sa.func.nlevel(path)),
        ),
        viewonly=True,
        order_by=order,
        uselist=True,
    )

    __table_args__ = (sa.Index("ix_page_path", path, postgresql_using="gist"),)

    def __init__(
        self, title: str, slug: str = None, parent: "Page" = None, order: float = None
    ) -> None:
        """ Sets various defaults for the page """

        from app.db import db

        _id = db.engine.execute(self.id_seq)
        _ltree_id = Ltree(str(_id))

        self.id = _id
        self.title = title
        self.slug = slug if slug else "-".join(self.title.split()).lower()
        self.path = _ltree_id if parent is None else parent.path + _ltree_id
        self.order = order or PageManager.get_next_available_order(parent)

    def __str__(self):
        return self.title

    @property
    def depth(self) -> int:
        """ the depth of this page (zero based) """

        return len(self.path) - 1

    @property
    def is_root_page(self) -> int:
        """ is this a root page """

        return self.depth == 0

    @property
    def url(self) -> str:
        """ returns the url path of the page """

        if self.is_root_page:
            return self.slug
        url = "/".join([page.slug for page in self.ancestors])
        return f"{url}/{self.slug}"

    def is_ancestor_of(self, page: "Page") -> bool:
        """ check if this page is an ancestor of a page """

        if len(self.path) >= len(page.path):
            return False
        return page.path[: len(self.path)] == self.path

    def is_descendant_of(self, page: "Page") -> bool:
        """ check if this page is a descendant of a page """

        if len(self.path) <= len(page.path):
            return False
        return self.path[: len(page.path)] == page.path

    def move_to(self, new_parent: "Page") -> None:
        """ move this page to a new parent page """

        if new_parent.id == self.id:
            raise PageMoveError("cannot move a page to itself")
        if new_parent.is_descendant_of(self):
            raise PageMoveError("cannot move a page to one of its descendants")

        new_path = new_parent.path + self.path[1:]
        for page in self.descendants:
            page.path = new_path + page.path[len(self.path) :]
        self.path = new_path
