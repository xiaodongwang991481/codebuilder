import logging

from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from sqlalchemy import String

from codebuilder.utils import util


BASE = declarative_base()
logger = logging.getLogger(__name__)


class GroupRelation(BASE):
    __tablename__ = 'group_relation'
    _parent = Column(
        'parent',
        String(36),
        ForeignKey('group.name', onupdate='RESTRICT', ondelete='CASCADE'),
        primary_key=True
    )
    _child = Column(
        'child',
        String(36),
        ForeignKey('group.name', onupdate='RESTRICT', ondelete='CASCADE'),
        primary_key=True
    )
    parent = relationship(
        'Group',
        passive_deletes=True,
        foreign_keys=[_parent],
        uselist=False
    )
    child = relationship(
        'Group',
        passive_deletes=True,
        foreign_keys=[_child],
        uselist=False
    )

    def __init__(self, parent, child):
        super(GroupRelation, self).__init__(
            _parent=parent, _child=child
        )

    def __str__(self):
        return '[GroupRelation %s -> %s]' % (self._parent, self._child)


class Group(BASE):
    """Group table."""
    __tablename__ = 'group'
    name = Column(
        String(36), primary_key=True
    )
    _parents = relationship(
        GroupRelation,
        passive_deletes=True,
        cascade='all, delete-orphan',
        foreign_keys=[GroupRelation._child]
    )
    _children = relationship(
        GroupRelation,
        passive_deletes=True,
        cascade='all, delete-orphan',
        foreign_keys=[GroupRelation._parent]
    )

    def __init__(self, name):
        super(Group, self).__init__(
            name=name
        )

    def __str__(self):
        return '[Group %s]' % self.name

    @property
    def parents(self):
        return [relation.parent for relation in self._parents]

    @property
    def children(self):
        return [relation.child for relation in self._children]

    def add_parent(self, value):
        self._parents.append(GroupRelation(value.name, self.name))

    def add_child(self, value):
        self._children.append(GroupRelation(self.name, value.name))

    def remove_parent(self, value):
        self._parents = [
            relation
            for relation in self._parents
            if relation._parent == value.name
        ]

    def remove_child(self, value):
        self._children = [
            relation
            for relation in self._children
            if relation._child == value.name
        ]


class User(BASE):
    """User table."""
    __tablename__ = 'user'
    name = Column(
        String(36), primary_key=True
    )
    group_name = Column(
        String(36),
        ForeignKey('group.name', onupdate='RESTRICT', ondelete='CASCADE')
    )
    attrs = Column(JSON)
    group = relationship(
        Group,
        passive_deletes=True,
        foreign_keys=[group_name],
        uselist=False
    )

    def __init__(self, name=None, **kwargs):
        if not name:
            name = util.generate_uuid()
        super(User, self).__init__(name=name, attrs=kwargs)
        self.group = Group(name=name)

    def __str__(self):
        return '[User %s -> %s]' % (self.name, self.group_name)
