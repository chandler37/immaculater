"""Defines Ctx, a context within which an action is possible.

E.g., "home" or "the store".
"""

import gflags as flags

from . import auditable_object
from . import common
from . import container
from . import pyatdl_pb2

FLAGS = flags.FLAGS


class Error(Exception):
  """Base class for this module's exceptions."""

class NoSuchNameError(Error):
  """No Context by that name exists."""

class Ctx(auditable_object.AuditableObject):
  """A context within which an action is possible.

  E.g., "home" or "the store".

  Fields:
    uid: int
    ctime: int  # seconds since the epoch
    dtime: int|None  # seconds since the epoch, or None if not deleted.
    mtime: int  # seconds since the epoch
    is_deleted: bool
    is_active: bool  # "someday/maybe" would be inactive.  Most are active.
    name: None|unicode|str
    note: unicode|str
  """

  def __init__(self, the_uid=None, name=None, is_active=True, note=''):
    super(Ctx, self).__init__(the_uid=the_uid)
    self.name = name
    self.note = note
    self.is_active = is_active

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    uid_str = u'' if not FLAGS.pyatdl_show_uid else u' uid=%s' % self.uid
    return u'<context%s is_deleted="%s" is_active="%s" name="%s"/>' % (
      uid_str,
      self.is_deleted,
      self.is_active,
      self.name if self.name else u'uid=%s' % self.uid)

  def __repr__(self):
    return '<ctx_proto>\n%s\n</ctx_proto>' % str(self.AsProto())

  def AsProto(self, pb=None):
    # pylint: disable=maybe-no-member
    if pb is None:
      pb = pyatdl_pb2.Context()
    super(Ctx, self).AsProto(pb.common)
    assert self.name
    pb.common.metadata.name = self.name
    if self.note:
      pb.common.metadata.note = self.note
    pb.is_active = self.is_active
    assert pb.common.uid == self.uid
    return pb

  @classmethod
  def DeserializedProtobuf(cls, bytestring):
    """Deserializes a Ctx from the given protocol buffer.

    Args:
      bytestring: str
    Returns:
      Ctx
    """
    assert bytestring
    pb = pyatdl_pb2.Context.FromString(bytestring)  # pylint: disable=no-member
    c = cls(the_uid=pb.common.uid,
            name=pb.common.metadata.name,
            is_active=pb.is_active,
            note=pb.common.metadata.note)
    c.SetFieldsBasedOnProtobuf(pb.common)
    assert c.uid == pb.common.uid
    return c


class CtxList(container.Container):
  """A list of Contexts.

  Fields:
    uid: int
    ctime: int  # seconds since the epoch
    dtime: int|None  # seconds since the epoch, or None if not deleted.
    mtime: int  # seconds since the epoch
    is_deleted: bool
    name: None|str|unicode
    items: [Ctx]
  """

  __pychecker__ = 'unusednames=cls'
  @classmethod
  def TypesContained(cls):
    return (Ctx,)

  def __init__(self, the_uid=None, name=None, items=None):  # items=[] is a python foible
    super(CtxList, self).__init__(the_uid=the_uid, items=items)
    self.name = name

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    uid_str = u'' if not FLAGS.pyatdl_show_uid else u' uid=%s' % self.uid
    ctx_strs = []
    for c in self.items:
      ctx_strs.append(unicode(c))
    return u"""
<context_list%s is_deleted="%s" name="%s">
%s
</context_list>
""".strip() % (uid_str, self.is_deleted, self.name,
               common.Indented(u'\n'.join(ctx_strs)))

  def Projects(self):
    """See Container.Projects."""
    raise AssertionError('Should this be an abstract method? I doubt it is called.')

  def ContextUIDFromName(self, name):
    """Returns the UID of an arbitrary but deterministic Context with the given name.

    This module is ignorant of FLAGS.no_context_display_string.

    Args:
      name: str
    Returns:
      int
    Raises:
      NoSuchNameError
    """
    for c in self.items:
      if c.name == name:
        return c.uid
    raise NoSuchNameError('No Context is named "%s"' % name)

  def AsProto(self, pb=None):
    # pylint: disable=maybe-no-member
    if pb is None:
      pb = pyatdl_pb2.ContextList()
    super(CtxList, self).AsProto(pb.common)
    assert self.uid == pb.common.uid
    assert self.name
    pb.common.metadata.name = self.name
    for c in self.items:
      c.AsProto(pb.contexts.add())
    return pb

  @classmethod
  def DeserializedProtobuf(cls, bytestring):
    """Deserializes a CtxList from the given protocol buffer.

    Args:
      bytestring: str
    Returns:
      CtxList
    """
    assert bytestring
    pb = pyatdl_pb2.ContextList.FromString(bytestring)  # pylint: disable=no-member
    assert pb.common.metadata.name, (
      'No name for ContextList. pb=<%s> len(bytestring)=%s'
      % (str(pb), len(bytestring)))
    cl = cls(the_uid=pb.common.uid, name=pb.common.metadata.name)
    for pbc in pb.contexts:
      cl.items.append(Ctx.DeserializedProtobuf(pbc.SerializeToString()))
    cl.CheckIsWellFormed()
    return cl
