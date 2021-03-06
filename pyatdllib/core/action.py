"""Defines Action, the smallest atomic unit of work, something to do
that can be checked off your list.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from absl import flags  # type: ignore
from google.protobuf import message
from typing import Type, TypeVar

from . import auditable_object
from . import common
from . import pyatdl_pb2

FLAGS = flags.FLAGS


T = TypeVar('T', bound='Action')


class Action(auditable_object.AuditableObject):
  """The smallest unit of work, something to do that can be checked
  off your list.

  Fields:
    uid: int
    ctime: float  # seconds since the epoch
    dtime: float|None  # seconds since the epoch, or None if not deleted.
    mtime: float  # seconds since the epoch
    is_complete: bool
    is_deleted: bool
    name: None|basestring  # e.g., "Buy milk"
    note: basestring
    ctx_uid: None|int  # UID of the Context, e.g. -5983155992228943816 which might refer to "@the store"
  """

  def __init__(self, the_uid: int = None, name: str = None, ctx_uid: int = None, note: str = '') -> None:
    super().__init__(the_uid=the_uid)
    self.is_complete = False
    self.name = name
    self.note = note
    assert (ctx_uid is None) or ((-2**63 <= ctx_uid < 0) or (0 < ctx_uid < 2**63)), ctx_uid
    self.ctx_uid = ctx_uid

  def __unicode__(self) -> str:
    uid_str = '' if not FLAGS.pyatdl_show_uid else ' uid=%s' % self.uid
    return '<action%s is_deleted="%s" is_complete="%s" name="%s" ctx="%s"/>' % (
      uid_str,
      self.is_deleted,
      self.is_complete,
      '' if self.name is None else self.name,
      '' if self.ctx_uid is None else 'uid=%s' % self.ctx_uid)

  def __repr__(self) -> str:
    return '<action_proto>\n%s\n</action_proto>' % str(self.AsProto())

  def IsDone(self) -> bool:
    return self.is_complete or self.is_deleted

  def MergeFromProto(self, other: pyatdl_pb2.Action) -> None:
    if not isinstance(other, pyatdl_pb2.Action):
      raise TypeError
    if common.MaxTimeOfPb(other) <= common.MaxTime(self):
      return
    self.name = other.common.metadata.name
    self.note = other.common.metadata.note
    self.is_complete = other.is_complete if other.HasField('is_complete') else False
    self.ctx_uid = other.ctx_uid if other.HasField('ctx_uid') else None
    self.MergeCommonFrom(other)

  def AlmostPurge(self) -> None:
    """Almost purges. A complete removal would be disastrous if you are using multiple devices. The next time some other
    device syncs it will seem that it has new items. So we leave the UID in place but clear all metadata and remove
    from the context, if any.

    To truly purge the data, once you're certain that everyone is in sync, call PurgeDeleted().
    """
    self.name = ''
    self.is_deleted = True
    self.ctx_uid = None

  def AsProto(self, pb: message.Message = None) -> message.Message:
    if pb is None:
      pb = pyatdl_pb2.Action()
    if not isinstance(pb, pyatdl_pb2.Action):
      raise TypeError
    # pylint: disable=maybe-no-member
    super().AsProto(pb.common)
    pb.is_complete = self.is_complete
    if self.name:
      pb.common.metadata.name = self.name
    if self.note:
      pb.common.metadata.note = self.note
    if self.ctx_uid is not None:
      pb.ctx_uid = self.ctx_uid
    return pb

  @classmethod
  def DeserializedProtobuf(cls: Type[T], bytestring: bytes) -> T:
    """Deserializes a Action from the given protocol buffer."""
    assert bytestring
    pb = pyatdl_pb2.Action.FromString(bytestring)  # pylint: disable=no-member
    ctx_uid = pb.ctx_uid if pb.HasField('ctx_uid') else None
    assert (ctx_uid is None) or ((-2**63 <= ctx_uid < 0) or (0 < ctx_uid < 2**63)), ctx_uid
    a = cls(the_uid=pb.common.uid,
            name=pb.common.metadata.name,
            note=pb.common.metadata.note,
            ctx_uid=ctx_uid)
    a.is_complete = pb.is_complete
    a.SetFieldsBasedOnProtobuf(pb.common)  # must be last mutation
    return a
