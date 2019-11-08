"""Defines Ctx, a context within which an action is possible.

E.g., "home" or "the store".
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import six

import gflags as flags

from . import auditable_object
from . import common
from . import container
from . import errors
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
    ctime: float  # seconds since the epoch
    dtime: float|None  # seconds since the epoch, or None if not deleted.
    mtime: float  # seconds since the epoch
    is_deleted: bool
    is_active: bool  # "someday/maybe" would be inactive.  Most are active.
    name: None|basestring
    note: basestring
  """

  def __init__(self, the_uid=None, name=None, is_active=True, note=''):
    super().__init__(the_uid=the_uid)
    if not name:
      raise errors.DataError("Every Context must have a name.")  # TODO(chandler37): why?
    self.name = name
    self.note = note
    self.is_active = is_active

  def __unicode__(self):
    uid_str = '' if not FLAGS.pyatdl_show_uid else ' uid=%s' % self.uid
    return '<context%s is_deleted="%s" is_active="%s" name="%s"/>' % (
      uid_str,
      self.is_deleted,
      self.is_active,
      self.name if self.name else 'uid=%s' % self.uid)

  def __repr__(self):
    return '<ctx_proto>\n%s\n</ctx_proto>' % str(self.AsProto())

  def IsDone(self):
    return self.is_deleted

  def AsProto(self, pb=None):
    # pylint: disable=maybe-no-member
    if pb is None:
      pb = pyatdl_pb2.Context()
    super().AsProto(pb.common)
    pb.common.metadata.name = self.name if self.name else ""
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
    if not bytestring:
      raise errors.DataError("A Context must be nonempty -- add a UID and name.")
    pb = pyatdl_pb2.Context.FromString(bytestring)  # pylint: disable=no-member
    c = cls(the_uid=pb.common.uid,
            name=pb.common.metadata.name,
            is_active=pb.is_active,
            note=pb.common.metadata.note)
    c.SetFieldsBasedOnProtobuf(pb.common)  # must be last
    assert c.uid == pb.common.uid
    return c


class CtxList(container.Container):
  """A list of Contexts.

  Fields:
    uid: int
    ctime: float  # seconds since the epoch
    dtime: float|None  # seconds since the epoch, or None if not deleted.
    mtime: float  # seconds since the epoch
    is_deleted: bool
    name: None|str|unicode
    items: [Ctx]
  """

  __pychecker__ = 'unusednames=cls'

  @classmethod
  def TypesContained(cls):
    return (Ctx,)

  def __init__(self, the_uid=None, name=None, items=None):  # items=[] is a python foible
    super().__init__(the_uid=the_uid, items=items)
    self.name = name

  def __unicode__(self):
    uid_str = '' if not FLAGS.pyatdl_show_uid else ' uid=%s' % self.uid
    ctx_strs = []
    for c in self.items:
      ctx_strs.append(six.text_type(c))
    return """
<context_list%s is_deleted="%s" name="%s">
%s
</context_list>
""".strip() % (uid_str, self.is_deleted, self.name,
               common.Indented('\n'.join(ctx_strs)))

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
    super().AsProto(pb.common)
    assert self.uid == pb.common.uid
    pb.common.metadata.name = self.name if self.name else ""
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
    if not bytestring:
      raise errors.DataError("A ContextList must be nonempty -- add a UID.")
    pb = pyatdl_pb2.ContextList.FromString(bytestring)  # pylint: disable=no-member
    assert pb.common.metadata.name, (
      'No name for ContextList. pb=<%s> len(bytestring)=%s'  # TODO(chandler37): why require it?
      % (str(pb), len(bytestring)))
    cl = cls(the_uid=pb.common.uid, name=pb.common.metadata.name)
    for pbc in pb.contexts:
      cl.items.append(Ctx.DeserializedProtobuf(pbc.SerializeToString()))
    cl.SetFieldsBasedOnProtobuf(pb.common)  # must be last mutation
    cl.CheckIsWellFormed()
    return cl
