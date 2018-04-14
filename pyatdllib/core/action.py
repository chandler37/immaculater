"""Defines Action, the smallest atomic unit of work, something to do
that can be checked off your list.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import gflags as flags

from . import auditable_object
from . import ctx
from . import pyatdl_pb2

FLAGS = flags.FLAGS


class Action(auditable_object.AuditableObject):
  """The smallest unit of work, something to do that can be checked
  off your list.

  Fields:
    uid: int
    ctime: int  # seconds since the epoch
    dtime: int|None  # seconds since the epoch, or None if not deleted.
    mtime: int  # seconds since the epoch
    is_complete: bool
    is_deleted: bool
    name: None|unicode|str  # e.g., "Buy milk"
    note: unicode|str
    ctx: None|ctx.Ctx  # the context, e.g. "Grocery store"
  """

  def __init__(self, the_uid=None, name=None, context=None, note=''):
    super(Action, self).__init__(the_uid=the_uid)
    self.is_complete = False
    self.name = name
    self.note = note
    self.ctx = context

  def __unicode__(self):
    uid_str = '' if not FLAGS.pyatdl_show_uid else ' uid=%s' % self.uid
    return '<action%s is_deleted="%s" is_complete="%s" name="%s" ctx="%s"/>' % (
      uid_str,
      self.is_deleted,
      self.is_complete,
      '' if self.name is None else self.name,
      '' if self.ctx is None else 'uid=%s' % self.ctx.uid)

  def __repr__(self):
    return '<action_proto>\n%s\n</action_proto>' % str(self.AsProto())

  def AsProto(self, pb=None):
    if pb is None:
      pb = pyatdl_pb2.Action()
    # pylint: disable=maybe-no-member
    super(Action, self).AsProto(pb.common)
    pb.is_complete = self.is_complete
    pb.common.metadata.name = self.name
    if self.note:
      pb.common.metadata.note = self.note
    if self.ctx is not None:
      pb.ctx.common.uid = self.ctx.uid
    return pb

  @classmethod
  def DeserializedProtobuf(cls, bytestring):
    """Deserializes a Action from the given protocol buffer.

    Args:
      bytestring: str
    Returns:
      Action
    """
    assert bytestring
    pb = pyatdl_pb2.Action.FromString(bytestring)  # pylint: disable=no-member
    s = pb.ctx.SerializeToString()
    the_context = None
    if s:
      the_context = ctx.Ctx.DeserializedProtobuf(s)
    a = cls(the_uid=pb.common.uid,
            name=pb.common.metadata.name,
            note=pb.common.metadata.note,
            context=the_context)
    a.SetFieldsBasedOnProtobuf(pb.common)
    a.is_complete = pb.is_complete
    return a
