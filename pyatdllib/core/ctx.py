"""Defines Ctx, a context within which an action is possible.

E.g., "home" or "the store".
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import six

from absl import flags  # type: ignore
from google.protobuf import message
from typing import Sequence, Type, TypeVar

from . import auditable_object
from . import common
from . import errors
from . import pyatdl_pb2
from . import uid

FLAGS = flags.FLAGS


class Error(Exception):
  """Base class for this module's exceptions."""


class NoSuchNameError(Error):
  """No Context by that name exists."""


T = TypeVar('T', bound='Ctx')


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

  def __init__(self, the_uid: int = None, name: str = None, is_active: bool = True, note: str = '') -> None:
    super().__init__(the_uid=the_uid)
    if not name:
      raise errors.DataError("Every Context must have a name.")  # TODO(chandler37): why?
    self.name = name
    self.note = note
    self.is_active = is_active

  def __unicode__(self) -> str:
    uid_str = '' if not FLAGS.pyatdl_show_uid else ' uid=%s' % self.uid
    return '<context%s is_deleted="%s" is_active="%s" name="%s"/>' % (
      uid_str,
      self.is_deleted,
      self.is_active,
      self.name if self.name else 'uid=%s' % self.uid)

  def __repr__(self) -> str:
    return '<ctx_proto>\n%s\n</ctx_proto>' % str(self.AsProto())

  def IsDone(self) -> bool:
    return self.is_deleted

  def AsProto(self, pb: message.Message = None) -> message.Message:
    # pylint: disable=maybe-no-member
    if pb is None:
      pb = pyatdl_pb2.Context()
    if not isinstance(pb, pyatdl_pb2.Context):
      raise TypeError
    super().AsProto(pb.common)
    pb.common.metadata.name = self.name if self.name else ""
    if self.note:
      pb.common.metadata.note = self.note
    pb.is_active = self.is_active
    assert pb.common.uid == self.uid
    return pb

  @classmethod
  def DeserializedProtobuf(cls: Type[T], bytestring: bytes) -> T:
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


U = TypeVar('U', bound='CtxList')


class CtxList(object):
  """A list of Contexts.

  Fields:
    items: [Ctx]
  """

  def __init__(self, items: Sequence[Ctx] = None, *, deserializing: bool = False) -> None:
    # this just simplifies the unittests because, once upon a time, a pyatdl_pb2.ContextList had a 'Common' message that had a UID:
    if not deserializing:
      uid.singleton_factory.NextUID()

    self.items = list(items) if items is not None else []

  def __unicode__(self) -> str:
    indented = common.Indented('\n'.join(six.text_type(c) for c in self.items))
    return f"<context_list>\n{indented}\n</context_list>"

  def __repr__(self) -> str:
    return self.__unicode__()

  def ContextUIDFromName(self, name: str) -> int:
    """Returns the UID of an arbitrary but deterministic Context with the given name.

    This module is ignorant of FLAGS.no_context_display_string.

    Raises:
      NoSuchNameError
    """
    for c in self.items:
      if c.name == name:
        return c.uid
    raise NoSuchNameError('No Context is named "%s"' % name)

  def PurgeDeleted(self) -> None:
    self.items[:] = [item for item in self.items if not item.is_deleted]

  def AsProto(self, pb: pyatdl_pb2.ContextList = None) -> pyatdl_pb2.ContextList:
    if pb is None:
      pb = pyatdl_pb2.ContextList()
    if not isinstance(pb, pyatdl_pb2.ContextList):
      raise TypeError
    for c in self.items:
      c.AsProto(pb.contexts.add())
    return pb

  @classmethod
  def DeserializedProtobuf(cls: Type[U], bytestring: bytes) -> U:
    """Deserializes a CtxList from the given protocol buffer."""
    if not bytestring:
      raise errors.DataError("A ContextList must be nonempty -- add a UID.")
    pb = pyatdl_pb2.ContextList.FromString(bytestring)
    cl = cls(deserializing=True)
    for pbc in pb.contexts:
      cl.items.append(Ctx.DeserializedProtobuf(pbc.SerializeToString()))
    return cl
